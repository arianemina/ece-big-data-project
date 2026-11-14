"""Open question: have the most popular films become more international?

Among the first three principals of the top 10 feature films per (genre,
year) for 1980-2025 (the enrichment targets), how has the share of people
born outside the United States changed, which countries grew, does it
differ by genre and by job (cast vs crew), and do films whose principals
were born abroad perform differently from films with only US-born
principals?

Inputs (all built by earlier steps, joined here in Spark):
- data/enrichment/targets/films and principals (IMDb selection),
- data/enrichment/raw/wikidata_links.jsonl (IMDb nconst -> Wikidata item),
- data/open_question/raw/birth_countries.jsonl (item -> birth country,
  from fetch_birth_countries).

Outputs: output/open_question/*.{csv,md}.

Usage: python -m imdb.open_question.foreign_born
"""

from pyspark.sql import Window
from pyspark.sql import functions as F
from pyspark.sql import types as T

from imdb.common import get_spark, write_output
from imdb.enrichment import config as E
from imdb.open_question import config as C

COUNTRY_SCHEMA = T.StructType([
    T.StructField("wikidata_id", T.StringType()),
    T.StructField("birth_place_uri", T.StringType()),
    T.StructField("country_uri", T.StringType()),
    T.StructField("country_iso", T.StringType()),
    T.StructField("country_label", T.StringType()),
    T.StructField("source_uri", T.StringType()),
    T.StructField("retrieved_at", T.StringType()),
])
LINK_SCHEMA = T.StructType([
    T.StructField("imdb_id", T.StringType()),
    T.StructField("entity_type", T.StringType()),
    T.StructField("wikidata_uri", T.StringType()),
])
# States that no longer exist: when a birthplace has both a historical and
# a current country (e.g. Soviet Union and Ukraine), the current one wins.
HISTORICAL = ["SU", "YU", "CS", "DD", "CSHH", "SUHH", "YUCS", "DDDE"]
CAST = ["actor", "actress", "self"]


def birth_country(countries):
    """One birth country per Wikidata item.

    Rules: a country with an ISO code beats one without; a current state
    beats a historical one; remaining ties (a place claimed by two current
    states, e.g. Kosovo / Serbia) are broken alphabetically and flagged.
    """
    known = countries.where(F.col("country_uri").isNotNull())
    w = Window.partitionBy("wikidata_id").orderBy(
        F.col("country_iso").isNull(),
        F.col("country_iso").isin(HISTORICAL),
        "country_iso", "country_uri")
    current = known.where(~F.coalesce(
        F.col("country_iso").isin(HISTORICAL), F.lit(False)))
    n_current = current.groupBy("wikidata_id").agg(
        F.countDistinct("country_uri").alias("n_current"))
    best = (known.withColumn("_rn", F.row_number().over(w))
            .where("_rn = 1").drop("_rn")
            .join(n_current, "wikidata_id", "left"))
    return best.select(
        "wikidata_id", "country_iso", "country_label", "country_uri",
        "birth_place_uri",
        (F.coalesce("n_current", F.lit(0)) > 1).alias("ambiguous_country"))


def principals_with_country(principals, links, countries, home=None):
    """Enriched principals with their birth country and a born_abroad flag.

    born_abroad is null when the country is unknown (no Wikidata item, no
    place of birth, or a place without country).
    """
    home = home or C.HOME_COUNTRY
    items = (links.where(F.col("entity_type") == "person")
             .where(F.col("wikidata_uri").isNotNull())
             .select(F.col("imdb_id").alias("nconst"),
                     F.element_at(F.split("wikidata_uri", "/"), -1)
                     .alias("wikidata_id"))
             .dropDuplicates(["nconst"]))
    return (
        principals.join(items, "nconst", "left")
        .join(birth_country(countries), "wikidata_id", "left")
        .withColumn("born_abroad",
                    F.when(F.col("country_iso").isNotNull(),
                           F.col("country_iso") != home))
        .withColumn("role", F.when(F.col("category").isin(CAST), "cast")
                    .otherwise("crew"))
    )


def with_period(df, year_col="year", width=None):
    width = width or C.PERIOD_YEARS
    start = (F.floor((F.col(year_col) - 1980) / width) * width + 1980) \
        .cast("int")
    end = F.least(start + width - 1, F.lit(2025))
    return df.withColumn("period", F.concat_ws("-", start, end))


def share(df, *keys):
    """Share of principals born abroad among those with a known country."""
    return df.groupBy(*keys).agg(
        F.count("*").alias("principals"),
        F.sum(F.col("born_abroad").isNotNull().cast("int"))
        .alias("known_country"),
        F.sum(F.col("born_abroad").cast("int")).alias("born_abroad"),
    ).withColumn("pct_born_abroad", F.round(
        100 * F.col("born_abroad") / F.col("known_country"), 1)
    ).withColumn("pct_known", F.round(
        100 * F.col("known_country") / F.col("principals"), 1))


def film_profiles(films, people, min_known=None):
    """Classify each distinct film by where its known principals were born.

    us_only: every known principal born in the home country; abroad_only:
    none; mixed: both. Films with fewer than ``min_known`` known countries
    are left out.
    """
    min_known = min_known or C.MIN_KNOWN_PRINCIPALS
    per_film = people.groupBy("tconst").agg(
        F.sum(F.col("born_abroad").isNotNull().cast("int")).alias("known"),
        F.sum(F.col("born_abroad").cast("int")).alias("abroad"))
    film_info = films.select("tconst", "year", "averageRating",
                             "numVotes").dropDuplicates(["tconst"])
    return (
        per_film.where(F.col("known") >= min_known)
        .withColumn("profile",
                    F.when(F.col("abroad") == 0, "us_only")
                    .when(F.col("abroad") == F.col("known"), "abroad_only")
                    .otherwise("mixed"))
        .join(film_info, "tconst")
    )


def performance(profiles):
    """Rating and votes per profile, overall and inside each year.

    The ``*_vs_year`` columns compare each film with the average of the
    selected films of the same year, which removes the effect of the
    year mix (recent films have more votes, and more foreign principals).
    """
    year_avg = Window.partitionBy("year")
    scored = (
        profiles
        .withColumn("log_votes", F.log10("numVotes"))
        .withColumn("rating_vs_year",
                    F.col("averageRating")
                    - F.avg("averageRating").over(year_avg))
        .withColumn("log_votes_vs_year",
                    F.col("log_votes") - F.avg("log_votes").over(year_avg))
    )
    return scored.groupBy("profile").agg(
        F.count("*").alias("films"),
        F.round(F.avg("averageRating"), 2).alias("avg_rating"),
        F.round(F.expr("percentile_approx(numVotes, 0.5)"), 0)
        .alias("median_votes"),
        F.round(F.avg("rating_vs_year"), 3).alias("rating_vs_year"),
        F.round(F.avg("log_votes_vs_year"), 3).alias("log10_votes_vs_year"),
    ).orderBy("profile")


def top_countries(people, top_n=5):
    """Most frequent foreign birth countries per decade (distinct people)."""
    decade = (F.floor(F.col("year") / 10) * 10).cast("int")
    counts = (people.where(F.col("born_abroad"))
              .withColumn("decade", F.concat(decade.cast("string"),
                                             F.lit("s")))
              .groupBy("decade", "country_iso", "country_label")
              .agg(F.countDistinct("nconst").alias("people")))
    w = Window.partitionBy("decade").orderBy(F.desc("people"),
                                             "country_iso")
    return (counts.withColumn("rank", F.row_number().over(w))
            .where(F.col("rank") <= top_n)
            .orderBy("decade", "rank"))


def main():
    spark = get_spark("open-question-foreign-born")
    films = spark.read.parquet(E.TARGET_FILMS)
    principals = spark.read.parquet(E.TARGET_PRINCIPALS)
    links = spark.read.schema(LINK_SCHEMA).json(E.RAW_LINKS)
    countries = spark.read.schema(COUNTRY_SCHEMA).json(C.RAW_COUNTRIES)

    people = principals_with_country(principals, links, countries).cache()
    # (film, principal) pairs with the release year of the film
    pairs = people.join(films.select("tconst", "year")
                        .dropDuplicates(["tconst"]), "tconst")
    pairs = with_period(pairs).cache()

    coverage = share(pairs.withColumn("scope", F.lit("all")),
                     "scope").join(
        pairs.agg(
            F.sum(F.col("wikidata_id").isNull().cast("int"))
            .alias("no_wikidata_item"),
            F.sum((F.col("wikidata_id").isNotNull()
                   & F.col("country_iso").isNull()).cast("int"))
            .alias("no_birth_country"),
            F.sum(F.coalesce(F.col("ambiguous_country"), F.lit(False))
                  .cast("int")).alias("ambiguous_country"),
        ))
    write_output(coverage, C.SECTION, "coverage")

    trend = share(pairs, "period").orderBy("period")
    write_output(trend, C.SECTION, "trend_by_period")
    # Crew members are only ~1 % of the top-3 credits, so the split is done
    # on the two acting categories, which have large samples.
    write_output(share(pairs, "role").orderBy("role"), C.SECTION,
                 "share_by_role")
    trend_gender = share(pairs.where(F.col("category")
                                     .isin("actor", "actress")),
                         "period", "category") \
        .groupBy("period").pivot("category", ["actor", "actress"]) \
        .agg(F.first("pct_born_abroad")).orderBy("period") \
        .withColumnRenamed("actor", "actors_pct_born_abroad") \
        .withColumnRenamed("actress", "actresses_pct_born_abroad")
    write_output(trend_gender, C.SECTION, "trend_actors_actresses")

    genre_pairs = with_period(people.join(
        films.select("tconst", "year", "genre"), "tconst"))
    early = F.col("year") <= 1989
    late = F.col("year") >= 2016
    by_genre = (
        share(genre_pairs, "genre")
        .join(share(genre_pairs.where(early), "genre")
              .select("genre", F.col("pct_born_abroad").alias("pct_1980s")),
              "genre", "left")
        .join(share(genre_pairs.where(late), "genre")
              .select("genre",
                      F.col("pct_born_abroad").alias("pct_2016_2025")),
              "genre", "left")
        .withColumn("change_pts",
                    F.round(F.col("pct_2016_2025") - F.col("pct_1980s"), 1))
        .where(F.col("known_country") >= 100)
        .select("genre", "known_country", "pct_born_abroad", "pct_1980s",
                "pct_2016_2025", "change_pts")
        .orderBy(F.desc("change_pts"))
    )
    write_output(by_genre, C.SECTION, "by_genre", preview_rows=30)

    write_output(top_countries(pairs), C.SECTION, "top_countries_by_decade",
                 preview_rows=30)

    profiles = film_profiles(films, people).cache()
    write_output(performance(profiles), C.SECTION, "performance_by_profile")
    write_output(with_period(profiles).groupBy("period")
                 .pivot("profile", ["us_only", "mixed", "abroad_only"])
                 .count().orderBy("period"),
                 C.SECTION, "profiles_by_period")
    trend.show(truncate=False)
    spark.stop()


if __name__ == "__main__":
    main()

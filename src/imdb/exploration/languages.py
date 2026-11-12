"""Infer the original language of a title from title.akas.

IMDb has no "original language" column. The akas whose title equals the
original title (or flagged isOriginalTitle) are used: an explicit language
code wins, otherwise the region is mapped to its main language. When several
akas match, the language with the most votes wins, ties broken by ordering.
"""

from itertools import chain

from pyspark.sql import Window
from pyspark.sql import functions as F

from imdb.common import read_clean

# Main language of a region (ISO 3166 alpha-2 -> ISO 639-1).
REGION_LANGUAGE = {
    "US": "en", "GB": "en", "CA": "en", "AU": "en", "NZ": "en", "IE": "en",
    "ZA": "en", "IN": "hi", "FR": "fr", "BE": "fr", "CH": "de", "LU": "fr",
    "DE": "de", "AT": "de", "IT": "it", "ES": "es", "MX": "es", "AR": "es",
    "CO": "es", "CL": "es", "PE": "es", "VE": "es", "UY": "es", "CU": "es",
    "PT": "pt", "BR": "pt", "NL": "nl", "SE": "sv", "NO": "no", "DK": "da",
    "FI": "fi", "IS": "is", "PL": "pl", "CZ": "cs", "SK": "sk", "HU": "hu",
    "RO": "ro", "BG": "bg", "GR": "el", "TR": "tr", "RU": "ru", "SUHH": "ru",
    "UA": "uk", "RS": "sr", "HR": "hr", "SI": "sl", "EE": "et", "LV": "lv",
    "LT": "lt", "IL": "he", "EG": "ar", "IR": "fa", "JP": "ja", "KR": "ko",
    "CN": "zh", "TW": "zh", "HK": "zh", "TH": "th", "VN": "vi", "ID": "id",
    "PH": "tl", "MY": "ms", "PK": "ur", "BD": "bn", "NG": "en", "XWG": "de",
    "DDDE": "de", "YUCS": "sr", "CSHH": "cs",
}


def original_languages(spark):
    """Return (tconst, original_language)."""
    basics = read_clean(spark, "title_basics") \
        .select("tconst", "originalTitle")
    akas = read_clean(spark, "title_akas")
    region_map = F.create_map(
        *[F.lit(x) for x in chain(*REGION_LANGUAGE.items())])
    candidates = (
        akas.join(basics, "tconst")
        .where((F.col("isOriginalTitle") == 1)
               | (F.col("title") == F.col("originalTitle")))
        .withColumn("lang", F.coalesce(F.col("language"),
                                       region_map[F.col("region")]))
        .where(F.col("lang").isNotNull())
    )
    votes = candidates.groupBy("tconst", "lang").agg(
        F.count("*").alias("n"),
        F.max(F.col("language").isNotNull()).alias("explicit"),
        F.min("ordering").alias("first_ordering"))
    best = Window.partitionBy("tconst").orderBy(
        F.desc("explicit"), F.desc("n"), "first_ordering")
    return votes.withColumn("r", F.row_number().over(best)) \
        .where(F.col("r") == 1) \
        .select("tconst", F.col("lang").alias("original_language"))

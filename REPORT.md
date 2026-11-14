# Report

## Data preparation

Results computed on the IMDb non-commercial datasets downloaded on 2026-11-12.

### Missing values per column

Full table: `output/preparation/null_profile.md`.

<!-- RESULTS: null_profile -->

| table | column | total_rows | missing_rows | missing_pct |
| --- | --- | --- | --- | --- |
| name.basics | birthYear | 15811387 | 15125575 | 95.66 |
| name.basics | deathYear | 15811387 | 15545911 | 98.32 |
| name.basics | knownForTitles | 15811387 | 1916998 | 12.12 |
| name.basics | nconst | 15811387 | 0 | 0.00 |
| name.basics | primaryName | 15811387 | 89 | 0.00 |
| name.basics | primaryProfession | 15811387 | 3219428 | 20.36 |
| title.akas | attributes | 60353877 | 60036655 | 99.47 |
| title.akas | isOriginalTitle | 60353877 | 0 | 0.00 |
| title.akas | language | 60353877 | 19649615 | 32.56 |
| title.akas | ordering | 60353877 | 0 | 0.00 |
| title.akas | region | 60353877 | 12993626 | 21.53 |
| title.akas | title | 60353877 | 0 | 0.00 |
| title.akas | titleId | 60353877 | 0 | 0.00 |
| title.akas | types | 60353877 | 40349110 | 66.85 |
| title.basics | endYear | 12952978 | 12788607 | 98.73 |
| title.basics | genres | 12952978 | 547694 | 4.23 |
| title.basics | isAdult | 12952978 | 0 | 0.00 |
| title.basics | originalTitle | 12952978 | 0 | 0.00 |
| title.basics | primaryTitle | 12952978 | 0 | 0.00 |
| title.basics | runtimeMinutes | 12952978 | 8053022 | 62.17 |
| title.basics | startYear | 12952978 | 1487813 | 11.49 |
| title.basics | tconst | 12952978 | 0 | 0.00 |
| title.basics | titleType | 12952978 | 0 | 0.00 |
| title.crew | directors | 12952978 | 5785224 | 44.66 |
| title.crew | tconst | 12952978 | 0 | 0.00 |
| title.crew | writers | 12952978 | 6426884 | 49.62 |
| title.episode | episodeNumber | 10026289 | 2120813 | 21.15 |
| title.episode | parentTconst | 10026289 | 0 | 0.00 |
| title.episode | seasonNumber | 10026289 | 2120813 | 21.15 |
| title.episode | tconst | 10026289 | 0 | 0.00 |
| title.principals | category | 102704599 | 0 | 0.00 |
| title.principals | characters | 102704599 | 52664813 | 51.28 |
| title.principals | job | 102704599 | 82843110 | 80.66 |
| title.principals | nconst | 102704599 | 0 | 0.00 |
| title.principals | ordering | 102704599 | 0 | 0.00 |
| title.principals | tconst | 102704599 | 0 | 0.00 |
| title.ratings | averageRating | 1731454 | 0 | 0.00 |
| title.ratings | numVotes | 1731454 | 0 | 0.00 |
| title.ratings | tconst | 1731454 | 0 | 0.00 |

_39 rows in total._

### Five columns with the highest percentage of missing values

<!-- RESULTS: null_profile_top5 -->

| table | column | total_rows | missing_rows | missing_pct |
| --- | --- | --- | --- | --- |
| title.akas | attributes | 60353877 | 60036655 | 99.47 |
| title.basics | endYear | 12952978 | 12788607 | 98.73 |
| name.basics | deathYear | 15811387 | 15545911 | 98.32 |
| name.basics | birthYear | 15811387 | 15125575 | 95.66 |
| title.principals | job | 102704599 | 82843110 | 80.66 |

_5 rows in total._

### Other data quality issues

<!-- RESULTS: dq_summary -->

| check | table | description | affected_rows | affected_pct |
| --- | --- | --- | --- | --- |
| duplicate_nconst | name.basics | Same nconst appears more than once | 0 | 0.00 |
| duplicate_tconst | title.basics | Same tconst appears more than once | 0 | 0.00 |
| null_primary_key_title | title.basics | tconst is missing | 0 | 0.00 |
| death_before_birth | name.basics | deathYear is earlier than birthYear | 28 | 0.00 |
| lifespan_over_120 | name.basics | deathYear - birthYear is greater than 120 | 2 | 0.00 |
| alive_over_120 | name.basics | No deathYear but born more than 120 years ago | 2796 | 0.02 |
| birth_or_death_in_future | name.basics | birthYear or deathYear after 2026 | 0 | 0.00 |
| credit_before_birth | title.principals | Principal credited on a title released before their birth | 3105 | 0.00 |
| credit_long_after_death | title.principals | Principal (not archive footage) credited more than 10 years after death | 165389 | 0.16 |
| end_before_start | title.basics | endYear is earlier than startYear | 0 | 0.00 |
| start_year_in_future | title.basics | startYear after 2026 (announced titles) | 6095 | 0.05 |
| non_positive_runtime | title.basics | runtimeMinutes is zero or negative | 4 | 0.00 |
| invalid_is_adult | title.basics | isAdult is not 0 or 1 | 0 | 0.00 |
| more_than_three_genres | title.basics | More than three genres (IMDb allows at most three) | 0 | 0.00 |
| rating_out_of_range | title.ratings | averageRating outside [1, 10] or numVotes below 1 | 0 | 0.00 |
| episode_missing_numbers | title.episode | seasonNumber or episodeNumber is missing | 2120813 | 21.15 |
| episode_parent_not_series | title.episode | Parent title exists but is not a tvSeries or tvMiniSeries | 4 | 0.00 |
| orphan_principal_title | title.principals | tconst not found in title.basics | 0 | 0.00 |
| orphan_principal_name | title.principals | nconst not found in name.basics | 7403 | 0.01 |
| orphan_rating_title | title.ratings | tconst not found in title.basics | 0 | 0.00 |
| orphan_aka_title | title.akas | titleId not found in title.basics | 4927 | 0.01 |
| orphan_crew_title | title.crew | tconst not found in title.basics | 0 | 0.00 |
| orphan_crew_director | title.crew | Director nconst not found in name.basics | 433 | 0.00 |
| orphan_crew_writer | title.crew | Writer nconst not found in name.basics | 1156 | 0.01 |
| orphan_episode_title | title.episode | Episode tconst not found in title.basics | 817 | 0.01 |
| orphan_episode_parent | title.episode | parentTconst not found in title.basics | 53 | 0.00 |
| orphan_known_for_title | name.basics | knownForTitles entry not found in title.basics | 1775 | 0.01 |

_27 rows in total._

### Handling of the issues

<!-- RESULTS: clean_summary -->

| table | raw_rows | clean_rows | removed_rows |
| --- | --- | --- | --- |
| name_basics | 15811387 | 15811387 | 0 |
| title_basics | 12952978 | 12952978 | 0 |
| title_akas | 60353877 | 60348950 | 4927 |
| title_crew | 12952978 | 12952978 | 0 |
| title_episode | 10026289 | 10025467 | 822 |
| title_principals | 102704599 | 102697196 | 7403 |
| title_ratings | 1731454 | 1731454 | 0 |

_7 rows in total._

### Methodological explanation

We first read the raw TSV files with every column as a string, so we could
see the missing values as they really are. A value counts as missing if it is
null, `\N` or an empty string. We also had to turn off the quote option,
because some titles have a single `"` that broke the lines. After that we
gave each column its real type (numbers, arrays for the lists like genres).

For the quality checks we looked for things that can't be true: duplicated
ids, people who die before they are born or live more than 120 years,
credits before the person's birth, runtimes of 0, ratings outside 1-10, and
ids that point to nothing in another table (orphans).

When cleaning, we tried not to throw away rows that are still useful. Wrong
years are set to null and the row gets a `dq_` flag instead of being deleted.
Rows that link to a title or a person that doesn't exist are removed, which
is why akas, episodes and principals lose a few thousand rows. The clean
tables are saved in Parquet so the next steps run faster.

## Data exploration

### Q1: Movies with an unusual length for their genre

<!-- RESULTS: q1_outliers_by_genre, q1_runtime_outliers -->

**q1_outliers_by_genre**

| genre | outliers | longer | shorter | movies | outlier_pct |
| --- | --- | --- | --- | --- | --- |
| Action | 732 | 396 | 336 | 40345 | 1.81 |
| Adventure | 663 | 392 | 271 | 24018 | 2.76 |
| Animation | 77 | 77 | 0 | 8328 | 0.92 |
| Biography | 32 | 32 | 0 | 16102 | 0.20 |
| Comedy | 3928 | 1107 | 2821 | 95735 | 4.10 |
| Crime | 579 | 248 | 331 | 34401 | 1.68 |
| Documentary | 505 | 505 | 0 | 116086 | 0.44 |
| Drama | 1854 | 811 | 1043 | 196063 | 0.95 |
| Family | 67 | 64 | 3 | 15947 | 0.42 |
| Fantasy | 271 | 110 | 161 | 12590 | 2.15 |
| History | 75 | 75 | 0 | 13633 | 0.55 |
| Horror | 1441 | 355 | 1086 | 30543 | 4.72 |
| Music | 66 | 66 | 0 | 13972 | 0.47 |
| Musical | 37 | 37 | 0 | 8496 | 0.44 |
| Mystery | 271 | 84 | 187 | 16425 | 1.65 |
| News | 17 | 17 | 0 | 1409 | 1.21 |
| Reality-TV | 4 | 4 | 0 | 297 | 1.35 |
| Romance | 393 | 126 | 267 | 42189 | 0.93 |
| Sci-Fi | 302 | 90 | 212 | 9772 | 3.09 |
| Sport | 36 | 36 | 0 | 6811 | 0.53 |
| Thriller | 899 | 199 | 700 | 34038 | 2.64 |
| War | 86 | 83 | 3 | 8049 | 1.07 |
| Western | 44 | 44 | 0 | 6354 | 0.69 |

_23 rows in total._

**q1_runtime_outliers**

| genre | tconst | primaryTitle | startYear | runtimeMinutes | genre_median_runtime | robust_z | direction |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Comedy | tt5136218 | London EC1 | 2015 | 5460 | 91.00 | 26.49 | longer |
| Mystery | tt5136218 | London EC1 | 2015 | 5460 | 92.00 | 21.63 | longer |
| Documentary | tt8273150 | Logistics | 2012 | 51420 | 74.00 | 21.05 | longer |
| Documentary | tt3854496 | Ambiancé | 2020 | 43200 | 74.00 | 20.49 | longer |
| Drama | tt5068890 | Hunger! | 2015 | 6000 | 93.00 | 20.34 | longer |
| Drama | tt1806963 | Matrjoschka | 2006 | 5700 | 93.00 | 20.09 | longer |
| Drama | tt5136218 | London EC1 | 2015 | 5460 | 93.00 | 19.88 | longer |
| Horror | tt7521772 | 24 Hour Psycho | 1993 | 1440 | 88.00 | 19.36 | longer |
| Documentary | tt12277054 | Carnets Filmés (Liste Complète) | 2019 | 28643 | 74.00 | 19.16 | longer |
| Comedy | tt1885195 | Azgrab: The Documentary | 2011 | 1669 | 91.00 | 18.82 | longer |
| Comedy | tt45643419 | Ooio Aifujairea: Lifedesign | 2025 | 1440 | 91.00 | 17.87 | longer |
| Drama | tt3837350 | A 2nd generation film | 2013 | 3077 | 93.00 | 17.08 | longer |
| Documentary | tt2659636 | Modern Times Forever | 2011 | 14400 | 74.00 | 16.95 | longer |
| Drama | tt0342707 | The Longest Most Meaningless Movie in the World | 1970 | 2880 | 93.00 | 16.76 | longer |
| Action | tt7321476 | h36: | 2017 | 2160 | 94.00 | 16.32 | longer |
| Comedy | tt8677246 | Bullfighting Memories | 2017 | 1100 | 91.00 | 16.12 | longer |
| Sci-Fi | tt6127010 | Funusion | 2016 | 1440 | 90.00 | 15.88 | longer |
| Mystery | tt1745901 | How Does David Lynch Do It? | 2010 | 1800 | 92.00 | 15.75 | longer |
| Family | tt1866307 | World Peace & Prayer Day | 2011 | 2400 | 90.00 | 15.48 | longer |
| Documentary | tt2355497 | Beijing 2003 | 2004 | 9000 | 74.00 | 15.44 | longer |
| Fantasy | tt0165127 | Burning of the Red Lotus Temple | 1928 | 1620 | 91.00 | 15.07 | longer |
| Adventure | tt45643419 | Ooio Aifujairea: Lifedesign | 2025 | 1440 | 90.00 | 14.94 | longer |
| Drama | tt0387271 | A Twist of Fate | 1970 | 1970 | 93.00 | 14.91 | longer |
| Action | tt0165127 | Burning of the Red Lotus Temple | 1928 | 1620 | 94.00 | 14.82 | longer |
| Comedy | tt19711676 | Kahrlton Heights North | 2022 | 900 | 91.00 | 14.82 | longer |
| Music | tt0284020 | The Cure for Insomnia | 1987 | 5220 | 87.00 | 14.69 | longer |
| Fantasy | tt6127010 | Funusion | 2016 | 1440 | 91.00 | 14.46 | longer |
| Action | tt45643419 | Ooio Aifujairea: Lifedesign | 2025 | 1440 | 94.00 | 14.21 | longer |
| Action | tt0004052 | The Hazards of Helen | 1914 | 1428 | 94.00 | 14.17 | longer |
| Documentary | tt5068890 | Hunger! | 2015 | 6000 | 74.00 | 14.14 | longer |
| Horror | tt1433078 | Amy's Night Out | 2007 | 675 | 88.00 | 14.11 | longer |
| Drama | tt0165127 | Burning of the Red Lotus Temple | 1928 | 1620 | 93.00 | 13.95 | longer |
| Drama | tt5942280 | The Nothing Movie | 2016 | 1559 | 93.00 | 13.76 | longer |
| Documentary | tt0284020 | The Cure for Insomnia | 1987 | 5220 | 74.00 | 13.69 | longer |
| Drama | tt0179184 | **** | 1967 | 1500 | 93.00 | 13.58 | longer |
| Horror | tt7442346 | Fan | 2017 | 623 | 88.00 | 13.56 | longer |
| Drama | tt2008009 | The Clock | 2010 | 1440 | 93.00 | 13.38 | longer |
| Horror | tt40792136 | Growth | 2026 | 587 | 88.00 | 13.15 | longer |
| Crime | tt9900018 | His Last Stand |  | 990 | 93.00 | 13.14 | longer |
| Drama | tt35509411 | Our First Day | 2025 | 1311 | 93.00 | 12.92 | longer |
| Comedy | tt33336291 | Phonetag | 2023 | 659 | 91.00 | 12.81 | longer |
| Sport | tt1885195 | Azgrab: The Documentary | 2011 | 1669 | 90.00 | 12.78 | longer |
| Drama | tt7156814 | The Innocence | 2019 | 1260 | 93.00 | 12.72 | longer |
| Drama | tt7549254 | Sakhi |  | 1179 | 93.00 | 12.40 | longer |
| Musical | tt22445582 | Sigur rós: Route One | 2016 | 1440 | 94.00 | 12.37 | longer |
| Drama | tt4567170 | Breaking Yop | 2015 | 1151 | 93.00 | 12.28 | longer |
| Documentary | tt5135246 | Saynatakuna: Masks | 2013 | 2905 | 74.00 | 11.80 | longer |
| Documentary | tt0342707 | The Longest Most Meaningless Movie in the World | 1970 | 2880 | 74.00 | 11.78 | longer |
| Drama | tt0821950 | A Mosca cieca | 1921 | 1035 | 93.00 | 11.76 | longer |
| Sci-Fi | tt0131597 | Split | 2004 | 700 | 90.00 | 11.75 | longer |

_12379 rows in total, first 50 shown._

### Q2: Top three genres per year (1980-2025)

<!-- RESULTS: q2_top3_genres_compact -->

| year | top3_genres |
| --- | --- |
| 1980 | Drama, Adventure, Horror |
| 1981 | Adventure, Drama, Horror |
| 1982 | Drama, Sci-Fi, Action |
| 1983 | Drama, Action, Adventure |
| 1984 | Action, Drama, Adventure |
| 1985 | Comedy, Adventure, Drama |
| 1986 | Drama, Adventure, Comedy |
| 1987 | Drama, Comedy, Action |
| 1988 | Drama, Comedy, Action |
| 1989 | Comedy, Drama, Adventure |
| 1990 | Drama, Comedy, Crime |
| 1991 | Drama, Crime, Comedy |
| 1992 | Drama, Comedy, Crime |
| 1993 | Drama, Comedy, Crime |
| 1994 | Drama, Crime, Comedy |
| 1995 | Drama, Crime, Comedy |
| 1996 | Drama, Comedy, Crime |
| 1997 | Drama, Action, Comedy |
| 1998 | Drama, Comedy, Crime |
| 1999 | Drama, Comedy, Crime |
| 2000 | Drama, Comedy, Adventure |
| 2001 | Drama, Comedy, Adventure |
| 2002 | Drama, Adventure, Action |
| 2003 | Drama, Action, Comedy |
| 2004 | Drama, Action, Comedy |
| 2005 | Drama, Comedy, Action |
| 2006 | Drama, Comedy, Thriller |
| 2007 | Drama, Comedy, Action |
| 2008 | Drama, Action, Comedy |
| 2009 | Drama, Comedy, Action |
| 2010 | Drama, Action, Adventure |
| 2011 | Drama, Action, Comedy |
| 2012 | Drama, Action, Comedy |
| 2013 | Drama, Action, Comedy |
| 2014 | Drama, Action, Adventure |
| 2015 | Drama, Action, Adventure |
| 2016 | Drama, Action, Adventure |
| 2017 | Drama, Action, Comedy |
| 2018 | Drama, Action, Adventure |
| 2019 | Drama, Action, Comedy |
| 2020 | Drama, Comedy, Action |
| 2021 | Drama, Action, Adventure |
| 2022 | Drama, Action, Comedy |
| 2023 | Drama, Action, Comedy |
| 2024 | Drama, Action, Comedy |
| 2025 | Drama, Action, Comedy |

_46 rows in total._

### Q3: Top three genres compared to the other genres

<!-- RESULTS: q3_top3_vs_rest, q3_top3_frequency -->

**q3_top3_vs_rest**

| year | top3_genres | rest_genres | top3_vote_share_pct | top3_movie_share_pct | top3_votes_per_movie | rest_votes_per_movie | top3_rating | rest_rating |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1980 | 3 | 20 | 44.30 | 39.00 | 5873.00 | 4721.00 | 7.73 | 7.50 |
| 1981 | 3 | 18 | 46.56 | 38.41 | 3990.00 | 2856.00 | 7.24 | 6.86 |
| 1982 | 3 | 18 | 43.76 | 40.92 | 5141.00 | 4577.00 | 7.56 | 7.15 |
| 1983 | 3 | 18 | 45.90 | 43.42 | 4434.00 | 4009.00 | 7.43 | 7.11 |
| 1984 | 3 | 18 | 44.17 | 42.02 | 6311.00 | 5781.00 | 7.35 | 7.19 |
| 1985 | 3 | 18 | 51.56 | 49.40 | 6191.00 | 5680.00 | 7.39 | 7.02 |
| 1986 | 3 | 18 | 46.22 | 49.19 | 5117.00 | 5762.00 | 7.20 | 7.05 |
| 1987 | 3 | 18 | 42.63 | 54.71 | 4490.00 | 7301.00 | 7.09 | 7.06 |
| 1988 | 3 | 18 | 46.84 | 52.60 | 5211.00 | 6561.00 | 7.17 | 7.07 |
| 1989 | 3 | 18 | 49.46 | 46.64 | 5900.00 | 5269.00 | 7.22 | 6.78 |
| 1990 | 3 | 18 | 45.58 | 51.56 | 6523.00 | 8288.00 | 7.30 | 7.07 |
| 1991 | 3 | 18 | 44.16 | 50.71 | 6022.00 | 7835.00 | 7.36 | 7.49 |
| 1992 | 3 | 18 | 46.30 | 50.90 | 6977.00 | 8389.00 | 7.23 | 7.00 |
| 1993 | 3 | 18 | 44.75 | 49.99 | 8536.00 | 10533.00 | 7.31 | 7.39 |
| 1994 | 3 | 18 | 58.26 | 51.05 | 13582.00 | 10152.00 | 7.87 | 7.32 |
| 1995 | 3 | 18 | 48.96 | 48.70 | 13042.00 | 12907.00 | 7.59 | 7.28 |
| 1996 | 3 | 19 | 44.90 | 49.45 | 8299.00 | 9961.00 | 6.98 | 6.78 |
| 1997 | 3 | 18 | 44.07 | 52.36 | 10792.00 | 15055.00 | 7.09 | 7.13 |
| 1998 | 3 | 18 | 51.48 | 50.94 | 11944.00 | 11689.00 | 7.40 | 6.80 |
| 1999 | 3 | 18 | 43.64 | 51.36 | 12284.00 | 16748.00 | 7.53 | 7.32 |
| 2000 | 3 | 18 | 44.97 | 46.07 | 11653.00 | 12182.00 | 7.21 | 6.98 |
| 2001 | 3 | 18 | 42.37 | 46.73 | 12494.00 | 14908.00 | 7.36 | 7.16 |
| 2002 | 3 | 21 | 42.41 | 37.89 | 15342.00 | 12708.00 | 7.22 | 7.04 |
| 2003 | 3 | 20 | 45.50 | 50.67 | 11493.00 | 14141.00 | 7.11 | 7.22 |
| 2004 | 3 | 20 | 41.32 | 48.91 | 11914.00 | 16195.00 | 7.02 | 7.11 |
| 2005 | 3 | 20 | 40.37 | 48.09 | 9313.00 | 12745.00 | 6.79 | 6.87 |
| 2006 | 3 | 19 | 42.70 | 47.16 | 10569.00 | 12657.00 | 7.12 | 6.95 |
| 2007 | 3 | 20 | 38.33 | 45.06 | 9945.00 | 13124.00 | 6.96 | 6.91 |
| 2008 | 3 | 19 | 40.38 | 45.38 | 9486.00 | 11639.00 | 6.75 | 7.10 |
| 2009 | 3 | 19 | 41.34 | 44.83 | 8573.00 | 9885.00 | 6.98 | 6.88 |
| 2010 | 3 | 20 | 39.98 | 33.00 | 10758.00 | 7956.00 | 6.97 | 7.02 |
| 2011 | 3 | 20 | 46.09 | 42.76 | 9055.00 | 7911.00 | 6.84 | 6.75 |
| 2012 | 3 | 20 | 42.74 | 41.78 | 7964.00 | 7657.00 | 6.90 | 6.96 |
| 2013 | 3 | 20 | 41.53 | 41.11 | 8320.00 | 8179.00 | 6.84 | 6.95 |
| 2014 | 3 | 22 | 47.03 | 30.80 | 12007.00 | 6020.00 | 7.09 | 6.96 |
| 2015 | 3 | 20 | 46.61 | 31.78 | 9272.00 | 4949.00 | 6.98 | 6.77 |
| 2016 | 3 | 20 | 44.09 | 32.10 | 9161.00 | 5492.00 | 6.89 | 6.90 |
| 2017 | 3 | 21 | 45.04 | 41.75 | 6694.00 | 5854.00 | 6.93 | 6.80 |
| 2018 | 3 | 21 | 44.30 | 32.51 | 8049.00 | 4876.00 | 6.94 | 6.74 |
| 2019 | 3 | 21 | 43.63 | 41.88 | 6280.00 | 5848.00 | 7.00 | 6.85 |
| 2020 | 3 | 21 | 44.71 | 38.97 | 4250.00 | 3357.00 | 6.42 | 6.41 |
| 2021 | 3 | 21 | 46.43 | 32.26 | 7576.00 | 4163.00 | 6.78 | 6.54 |
| 2022 | 3 | 21 | 46.38 | 41.68 | 5363.00 | 4430.00 | 6.75 | 6.56 |
| 2023 | 3 | 21 | 44.75 | 42.88 | 4505.00 | 4175.00 | 6.67 | 6.66 |
| 2024 | 3 | 22 | 42.90 | 41.33 | 3779.00 | 3544.00 | 6.57 | 6.52 |
| 2025 | 3 | 21 | 39.31 | 41.41 | 3406.00 | 3717.00 | 6.51 | 6.46 |

_46 rows in total._

**q3_top3_frequency**

| genre | years_in_top3 | years_ranked_first |
| --- | --- | --- |
| Drama | 46 | 42 |
| Comedy | 34 | 2 |
| Action | 29 | 1 |
| Adventure | 16 | 1 |
| Crime | 9 | 0 |
| Horror | 2 | 0 |
| Sci-Fi | 1 | 0 |
| Thriller | 1 | 0 |

_8 rows in total._

### Q4: Directors with a single movie rated 8.0 or more

<!-- RESULTS: q4_one_hit_directors, q4_one_hit_directors_average -->

**q4_one_hit_directors**

| nconst | primaryName | hit_title | hit_year | hit_rating | movies_rated_6_or_less | avg_rating_of_low_movies | other_movies | avg_rating_of_other_movies | rated_movies |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| nm0861703 | Richard Thorpe | The Wizard of Oz | 1939 | 8.10 | 42 | 5.57 | 93 | 6.09 | 94 |
| nm0851537 | Norman Taurog | The Wizard of Oz | 1939 | 8.10 | 25 | 5.60 | 69 | 6.16 | 70 |
| nm0080315 | Mahesh Bhatt | Saaransh | 1984 | 8.10 | 23 | 5.08 | 35 | 5.69 | 36 |
| nm0002031 | Michael Curtiz | Casablanca | 1942 | 8.50 | 23 | 5.62 | 102 | 6.49 | 103 |
| nm0490487 | Wai Keung Lau | Infernal Affairs | 2002 | 8.00 | 22 | 4.97 | 43 | 5.72 | 44 |
| nm0700872 | Puri Jagannadh | Pokiri | 2006 | 8.00 | 21 | 4.73 | 33 | 5.52 | 34 |
| nm0909825 | Raoul Walsh | White Heat | 1949 | 8.10 | 20 | 5.51 | 80 | 6.38 | 81 |
| nm0030762 | Franz Antel | The Stubborn Mule | 1981 | 8.10 | 15 | 4.65 | 19 | 5.02 | 20 |
| nm3359146 | Rabi Kinagi | Suna Panjuri | 1995 | 9.00 | 15 | 5.39 | 23 | 5.77 | 24 |
| nm0435050 | Shaji Kailas | Aaram Thamburan | 1997 | 8.10 | 15 | 4.34 | 24 | 5.35 | 25 |
| nm0000814 | John G. Avildsen | Rocky | 1976 | 8.10 | 14 | 5.20 | 21 | 5.78 | 22 |
| nm0836328 | John Sturges | The Great Escape | 1963 | 8.20 | 14 | 5.71 | 41 | 6.39 | 42 |
| nm0002030 | George Cukor | The Wizard of Oz | 1939 | 8.10 | 13 | 5.61 | 59 | 6.58 | 60 |
| nm0132709 | Martin Campbell | Casino Royale | 2006 | 8.00 | 13 | 5.10 | 20 | 5.63 | 21 |
| nm0920074 | William A. Wellman | The Ox-Bow Incident | 1943 | 8.00 | 13 | 5.55 | 67 | 6.46 | 68 |
| nm1777967 | A.L. Vijay | Deiva Thirumagal | 2011 | 8.30 | 12 | 5.38 | 20 | 5.89 | 21 |
| nm0000361 | Brian De Palma | Scarface | 1983 | 8.30 | 12 | 5.26 | 29 | 6.19 | 30 |
| nm0503777 | Mervyn LeRoy | I Am a Fugitive from a Chain Gang | 1932 | 8.20 | 12 | 5.68 | 67 | 6.58 | 68 |
| nm1212770 | Wenn V. Deramas | Bekikang: Ang nanay kong beki | 2013 | 8.50 | 12 | 5.35 | 20 | 5.98 | 21 |
| nm0001675 | Robert Rodriguez | Sin City | 2005 | 8.00 | 11 | 4.79 | 23 | 5.90 | 24 |
| nm0814469 | Sion Sono | Love Exposure | 2008 | 8.00 | 11 | 5.22 | 35 | 6.16 | 36 |
| nm2321771 | Smeep Kang | Carry on Jatta | 2012 | 8.30 | 11 | 4.97 | 22 | 5.84 | 23 |
| nm0677951 | Daniel Petrie | A Raisin in the Sun | 1961 | 8.00 | 10 | 5.38 | 18 | 5.91 | 19 |
| nm0062614 | Harry Baweja | Chaar Sahibzaade 2: Rise of Banda Singh Bahadur | 2016 | 8.60 | 10 | 4.62 | 11 | 4.91 | 12 |
| nm0430782 | Joshiy | Dhruvam | 1993 | 8.10 | 10 | 4.25 | 34 | 6.19 | 35 |
| nm0695937 | Otto Preminger | Anatomy of a Murder | 1959 | 8.00 | 10 | 5.61 | 39 | 6.48 | 40 |
| nm1583171 | R. Kannan | Jayam Kondaan | 2008 | 8.00 | 10 | 5.00 | 11 | 5.12 | 12 |
| nm11412226 | Sigrid Polon | Boys in Service | 2025 | 8.00 | 10 | 4.62 | 11 | 4.85 | 12 |
| nm0471452 | Suresh Krishna | Baasha | 1995 | 8.30 | 10 | 4.49 | 24 | 5.98 | 25 |
| nm0948159 | Wilson Yip | Ip Man | 2008 | 8.00 | 10 | 5.34 | 21 | 6.08 | 22 |
| nm0517768 | Dimitri Logothetis | Champions Forever | 1989 | 8.00 | 9 | 4.09 | 10 | 4.34 | 11 |
| nm2538739 | Hanung Bramantyo | Love Is Never on Time | 2024 | 8.10 | 9 | 5.29 | 32 | 6.48 | 33 |
| nm0155280 | Kaige Chen | Farewell My Concubine | 1993 | 8.10 | 9 | 5.69 | 22 | 6.33 | 23 |
| nm0002045 | Stanley Donen | Singin' in the Rain | 1952 | 8.30 | 9 | 5.58 | 27 | 6.39 | 28 |
| nm0001469 | Barry Levinson | Rain Man | 1988 | 8.00 | 8 | 5.44 | 25 | 6.33 | 26 |
| nm0567680 | Bruce McDonald | Music from the Big House | 2010 | 8.40 | 8 | 5.40 | 15 | 6.03 | 16 |
| nm1318819 | Ezhil | Thulladha Manamum Thullum | 1999 | 8.30 | 8 | 4.38 | 10 | 4.77 | 11 |
| nm0002120 | Lasse Hallström | Hachi: A Dog's Tale | 2009 | 8.10 | 8 | 5.66 | 27 | 6.51 | 28 |
| nm0796117 | M. Night Shyamalan | The Sixth Sense | 1999 | 8.20 | 8 | 5.13 | 15 | 5.87 | 16 |
| nm1500124 | M. Padmakumar | Joseph | 2018 | 8.00 | 8 | 4.45 | 16 | 5.59 | 17 |
| nm1688464 | Pedro Antonio | New Year's Special | 2023 | 8.40 | 8 | 5.44 | 10 | 5.61 | 11 |
| nm0149134 | Sinan Çetin | Abbas in Flower | 1982 | 8.00 | 8 | 4.45 | 10 | 4.89 | 11 |
| nm0000490 | Spike Lee | David Byrne's American Utopia | 2020 | 8.20 | 8 | 5.43 | 34 | 6.65 | 35 |
| nm0096539 | António Borges Correia | Antes de a Vida Começar | 2006 | 9.30 | 7 | 5.31 | 7 | 5.31 | 8 |
| nm0481838 | Edvin Laine | The Unknown Soldier | 1955 | 8.00 | 7 | 5.37 | 14 | 5.95 | 15 |
| nm0576554 | Hansal Mehta | Shahid | 2012 | 8.20 | 7 | 4.93 | 11 | 5.75 | 12 |
| nm0580669 | James Merendino | The Invisible Life of Thomas Lynch | 2009 | 9.10 | 7 | 4.59 | 10 | 5.30 | 11 |
| nm0001379 | John Huston | The Treasure of the Sierra Madre | 1948 | 8.20 | 7 | 5.41 | 43 | 6.68 | 44 |
| nm1434372 | Johny Antony | C.I.D. Moosa | 2003 | 8.10 | 7 | 4.71 | 9 | 5.09 | 10 |
| nm0846092 | Kamal Tabrizi | The Lizard | 2004 | 8.40 | 7 | 4.76 | 14 | 5.76 | 15 |

_348 rows in total, first 50 shown._

**q4_one_hit_directors_average**

| nconst | primaryName | hit_title | hit_year | hit_rating | movies_rated_6_or_less | avg_rating_of_low_movies | other_movies | avg_rating_of_other_movies | rated_movies |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| nm0490487 | Wai Keung Lau | Infernal Affairs | 2002 | 8.00 | 22 | 4.97 | 43 | 5.72 | 44 |
| nm0080315 | Mahesh Bhatt | Saaransh | 1984 | 8.10 | 23 | 5.08 | 35 | 5.69 | 36 |
| nm0700872 | Puri Jagannadh | Pokiri | 2006 | 8.00 | 21 | 4.73 | 33 | 5.52 | 34 |
| nm0435050 | Shaji Kailas | Aaram Thamburan | 1997 | 8.10 | 15 | 4.34 | 24 | 5.35 | 25 |
| nm0471452 | Suresh Krishna | Baasha | 1995 | 8.30 | 10 | 4.49 | 24 | 5.98 | 25 |
| nm3359146 | Rabi Kinagi | Suna Panjuri | 1995 | 9.00 | 15 | 5.39 | 23 | 5.77 | 24 |
| nm0001675 | Robert Rodriguez | Sin City | 2005 | 8.00 | 11 | 4.79 | 23 | 5.90 | 24 |
| nm2321771 | Smeep Kang | Carry on Jatta | 2012 | 8.30 | 11 | 4.97 | 22 | 5.84 | 23 |
| nm0000814 | John G. Avildsen | Rocky | 1976 | 8.10 | 14 | 5.20 | 21 | 5.78 | 22 |
| nm1777967 | A.L. Vijay | Deiva Thirumagal | 2011 | 8.30 | 12 | 5.38 | 20 | 5.89 | 21 |
| nm0132709 | Martin Campbell | Casino Royale | 2006 | 8.00 | 13 | 5.10 | 20 | 5.63 | 21 |
| nm1212770 | Wenn V. Deramas | Bekikang: Ang nanay kong beki | 2013 | 8.50 | 12 | 5.35 | 20 | 5.98 | 21 |
| nm0030762 | Franz Antel | The Stubborn Mule | 1981 | 8.10 | 15 | 4.65 | 19 | 5.02 | 20 |
| nm0677951 | Daniel Petrie | A Raisin in the Sun | 1961 | 8.00 | 10 | 5.38 | 18 | 5.91 | 19 |
| nm1500124 | M. Padmakumar | Joseph | 2018 | 8.00 | 8 | 4.45 | 16 | 5.59 | 17 |
| nm0000436 | Curtis Hanson | L.A. Confidential | 1997 | 8.20 | 6 | 4.78 | 15 | 6.00 | 16 |
| nm0796117 | M. Night Shyamalan | The Sixth Sense | 1999 | 8.20 | 8 | 5.13 | 15 | 5.87 | 16 |
| nm0481838 | Edvin Laine | The Unknown Soldier | 1955 | 8.00 | 7 | 5.37 | 14 | 5.95 | 15 |
| nm0846092 | Kamal Tabrizi | The Lizard | 2004 | 8.40 | 7 | 4.76 | 14 | 5.76 | 15 |
| nm1025280 | Anubhav Sinha | Article 15 | 2019 | 8.10 | 6 | 4.67 | 12 | 5.77 | 13 |
| nm0536705 | Ananth Mahadevan | Phule | 2025 | 8.10 | 6 | 4.40 | 11 | 5.60 | 12 |
| nm0954099 | Dejan Zecevic | Decak iz Junkovca | 1996 | 8.50 | 4 | 4.30 | 11 | 5.87 | 12 |
| nm0576554 | Hansal Mehta | Shahid | 2012 | 8.20 | 7 | 4.93 | 11 | 5.75 | 12 |
| nm0062614 | Harry Baweja | Chaar Sahibzaade 2: Rise of Banda Singh Bahadur | 2016 | 8.60 | 10 | 4.62 | 11 | 4.91 | 12 |
| nm1583171 | R. Kannan | Jayam Kondaan | 2008 | 8.00 | 10 | 5.00 | 11 | 5.12 | 12 |
| nm11412226 | Sigrid Polon | Boys in Service | 2025 | 8.00 | 10 | 4.62 | 11 | 4.85 | 12 |
| nm0059633 | Tunç Başaran | Don't Let Them Shoot the Kite | 1989 | 8.10 | 4 | 4.18 | 11 | 5.89 | 12 |
| nm0517768 | Dimitri Logothetis | Champions Forever | 1989 | 8.00 | 9 | 4.09 | 10 | 4.34 | 11 |
| nm1318819 | Ezhil | Thulladha Manamum Thullum | 1999 | 8.30 | 8 | 4.38 | 10 | 4.77 | 11 |
| nm0064961 | Gorman Bechard | A Dog Named Gucci | 2015 | 8.40 | 6 | 4.52 | 10 | 5.44 | 11 |
| nm0348015 | Gunasekhar | Okkadu | 2003 | 8.00 | 6 | 4.55 | 10 | 5.57 | 11 |
| nm0580669 | James Merendino | The Invisible Life of Thomas Lynch | 2009 | 9.10 | 7 | 4.59 | 10 | 5.30 | 11 |
| nm1688464 | Pedro Antonio | New Year's Special | 2023 | 8.40 | 8 | 5.44 | 10 | 5.61 | 11 |
| nm0803350 | Sangeeth Sivan | Yoddha | 1992 | 8.40 | 7 | 4.49 | 10 | 5.11 | 11 |
| nm0149134 | Sinan Çetin | Abbas in Flower | 1982 | 8.00 | 8 | 4.45 | 10 | 4.89 | 11 |
| nm0244892 | J.P. Dutta | Border | 1997 | 8.00 | 5 | 5.46 | 9 | 5.94 | 10 |
| nm1434372 | Johny Antony | C.I.D. Moosa | 2003 | 8.10 | 7 | 4.71 | 9 | 5.09 | 10 |
| nm0347728 | Melih Gülgen | Tatar Ramazan: Sürgünde | 1992 | 8.00 | 7 | 5.36 | 9 | 5.72 | 10 |
| nm1459905 | Raffi | Punjabi House | 1998 | 8.10 | 5 | 5.20 | 9 | 6.00 | 10 |
| nm4479905 | Billy Christian | The Sacred Riana 2: Bloody Mary | 2022 | 8.40 | 6 | 5.30 | 8 | 5.73 | 9 |
| nm0007144 | Santosh Sivan | Halo | 1996 | 8.30 | 2 | 3.15 | 8 | 5.96 | 9 |
| nm0096539 | António Borges Correia | Antes de a Vida Começar | 2006 | 9.30 | 7 | 5.31 | 7 | 5.31 | 8 |
| nm0787453 | Kundan Shah | Jaane Bhi Do Yaaro | 1983 | 8.30 | 5 | 4.56 | 7 | 5.21 | 8 |
| nm1098726 | Milorad Milinkovic | Frozen Stiff | 2002 | 8.30 | 4 | 5.18 | 7 | 5.63 | 8 |
| nm0002916 | Ray Brady | Egression | 2011 | 8.80 | 5 | 4.96 | 7 | 5.47 | 8 |
| nm1164861 | Seth Gordon | The King of Kong: A Fistful of Quarters | 2007 | 8.00 | 5 | 5.34 | 7 | 5.70 | 8 |
| nm4062141 | A. Venkatesh | Dhil Raja | 2024 | 8.40 | 4 | 4.90 | 6 | 5.70 | 7 |
| nm4299374 | Alex R. Wagner | Barbenheimer and the Cult of Walt Disney | 2024 | 9.10 | 2 | 3.95 | 6 | 5.93 | 7 |
| nm1896291 | Ashok Pati | Pabar | 2024 | 8.00 | 5 | 5.12 | 6 | 5.28 | 7 |
| nm2347386 | Bommarillu Baskar | Bommarillu | 2006 | 8.20 | 3 | 5.17 | 6 | 5.92 | 7 |

_167 rows in total, first 50 shown._

### Q5: Series whose worst episode is in the last season

<!-- RESULTS: q5_tv_series -->

| series_tconst | series_title | series_start | seasons | big_seasons | last_season | best_episode | best_season | best_rating | worst_episode | worst_season | worst_rating |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| tt8736020 | #LikeMe | 2019 | 7 | 6 | 2 | tt8894690 | 1 | 8.90 | tt11452850 | 2 | 6.90 |
| tt0759475 | 'Til Death | 2006 | 4 | 3 | 4 | tt0945610 | 1 | 8.20 | tt1617665 | 4 | 5.60 |
| tt1809413 | 1 Kadin 1 Erkek | 2008 | 8 | 8 | 1 | tt10197432 | 1 | 8.00 | tt10197436 | 1 | 7.90 |
| tt13444828 | 12 Words | 2020 | 3 | 3 | 1 | tt13490208 | 1 | 9.40 | tt13492154 | 1 | 8.60 |
| tt1837492 | 13 Reasons Why | 2017 | 4 | 4 | 4 | tt5174280 | 1 | 9.20 | tt11187066 | 4 | 5.10 |
| tt1307083 | 17 Kids and Counting | 2008 | 15 | 14 | 7 | tt1319202 | 1 | 4.60 | tt1967432 | 7 | 2.70 |
| tt0086660 | 1st & Ten | 1984 | 6 | 6 | 1 | tt0501360 | 1 | 5.70 | tt0501360 | 1 | 5.70 |
| tt0285331 | 24 | 2001 | 8 | 8 | 8 | tt0502164 | 1 | 9.30 | tt1463806 | 8 | 7.60 |
| tt1408430 | 30 for 30 | 2009 | 5 | 4 | 5 | tt2751904 | 2 | 8.50 | tt32368140 | 5 | 5.20 |
| tt0376364 | 31 Minutes | 2002 | 4 | 4 | 4 | tt5784196 | 2 | 9.60 | tt4790040 | 4 | 6.50 |
| tt0992966 | 7 Numara | 2000 | 3 | 3 | 1 | tt10948598 | 1 | 9.60 | tt8717460 | 1 | 9.00 |
| tt0192877 | 7 vidas | 1999 | 11 | 10 | 1 | tt0853290 | 1 | 6.70 | tt0853290 | 1 | 6.70 |
| tt16994878 | 7 vs. Wild | 2021 | 6 | 6 | 5 | tt25393396 | 2 | 8.80 | tt38772077 | 5 | 3.40 |
| tt3279494 | @midnight | 2013 | 4 | 4 | 1 | tt3292050 | 1 | 8.00 | tt3286812 | 1 | 7.50 |
| tt0090399 | A Better Life | 1987 | 3 | 3 | 1 | tt0935210 | 1 | 8.40 | tt0935203 | 1 | 8.30 |
| tt8611552 | A Day Before Us | 2018 | 3 | 3 | 1 | tt11467596 | 1 | 8.70 | tt11467596 | 1 | 8.70 |
| tt15007664 | A Professor | 2021 | 3 | 3 | 3 | tt15988290 | 1 | 8.70 | tt36042527 | 3 | 6.90 |
| tt0415313 | A White Ship | 2006 | 6 | 6 | 6 | tt1052440 | 1 | 8.80 | tt2207883 | 6 | 5.60 |
| tt13695606 | A Will Eternal | 2020 | 3 | 3 | 2 | tt13715526 | 1 | 9.70 | tt27407050 | 2 | 9.10 |
| tt11092482 | AEW Dark | 2019 | 5 | 5 | 2 | tt11137756 | 1 | 7.70 | tt12026362 | 2 | 5.60 |
| tt14738480 | AEW Rampage | 2021 | 4 | 4 | 4 | tt14961604 | 1 | 9.10 | tt30609344 | 4 | 5.60 |
| tt5759648 | Aber Bergen: Partners in Law | 2016 | 3 | 3 | 1 | tt6131064 | 1 | 8.10 | tt6058002 | 1 | 7.40 |
| tt13567344 | Acapulco | 2021 | 4 | 4 | 4 | tt19371324 | 2 | 8.90 | tt33296280 | 4 | 6.60 |
| tt0115084 | Ace Ventura: Pet Detective | 1995 | 3 | 3 | 3 | tt1016412 | 1 | 9.00 | tt1016421 | 3 | 6.40 |
| tt21057376 | Acting Good | 2022 | 5 | 4 | 1 | tt22486548 | 1 | 6.40 | tt22486548 | 1 | 6.40 |
| tt0227868 | Adventures from the Book of Virtues | 1996 | 3 | 3 | 1 | tt0505622 | 1 | 7.80 | tt0505622 | 1 | 7.80 |
| tt0052440 | Adventures in Paradise | 1959 | 3 | 3 | 1 | tt0505647 | 1 | 8.80 | tt0505672 | 1 | 6.60 |
| tt8593810 | Aikuiset | 2019 | 3 | 3 | 1 | tt9898212 | 1 | 7.20 | tt9897724 | 1 | 7.10 |
| tt1600931 | Akkara Kazhchakal | 2008 | 4 | 3 | 1 | tt1638006 | 1 | 9.10 | tt1638006 | 1 | 9.10 |
| tt1441404 | Al fondo hay sitio | 2009 | 13 | 13 | 1 | tt9645504 | 1 | 8.10 | tt9645504 | 1 | 8.10 |
| tt1531068 | Alaska State Troopers | 2009 | 10 | 7 | 1 | tt1536564 | 1 | 6.20 | tt1536564 | 1 | 6.20 |
| tt5520772 | Alex & Co. | 2015 | 3 | 3 | 1 | tt5625700 | 1 | 7.70 | tt5625700 | 1 | 7.70 |
| tt0088476 | Alfred Hitchcock Presents | 1985 | 4 | 4 | 4 | tt0508387 | 1 | 8.00 | tt0508407 | 4 | 5.10 |
| tt0285333 | Alias | 2001 | 5 | 5 | 5 | tt0508628 | 2 | 9.00 | tt0508622 | 5 | 7.10 |
| tt7414406 | All American | 2018 | 8 | 8 | 8 | tt10234774 | 2 | 9.00 | tt37156731 | 8 | 6.10 |
| tt14088994 | All American: Homecoming | 2022 | 3 | 3 | 3 | tt18569776 | 1 | 8.60 | tt32367820 | 3 | 6.20 |
| tt0118252 | All Dogs Go to Heaven: The Series | 1996 | 3 | 3 | 1 | tt0765857 | 1 | 7.80 | tt0765857 | 1 | 7.80 |
| tt14915596 | All Heart | 2021 | 3 | 3 | 1 | tt14925638 | 1 | 7.30 | tt14925638 | 1 | 7.30 |
| tt11737106 | All Inclusive | 2020 | 5 | 5 | 1 | tt11742492 | 1 | 9.00 | tt11742506 | 1 | 8.00 |
| tt10329042 | All Rise | 2019 | 3 | 3 | 3 | tt12194450 | 1 | 8.40 | tt15558894 | 3 | 4.70 |
| tt0215510 | All stars: De serie | 1999 | 3 | 3 | 2 | tt0510028 | 1 | 7.90 | tt0510034 | 2 | 6.70 |
| tt2469954 | Amazing Detective Di Renjie | 2004 | 5 | 5 | 3 | tt2579504 | 2 | 7.80 | tt2579506 | 3 | 7.10 |
| tt0098740 | America's Funniest Home Videos | 1989 | 37 | 35 | 1 | tt1294277 | 1 | 6.30 | tt1379753 | 1 | 6.20 |
| tt0319930 | American Dreams | 2002 | 3 | 3 | 3 | tt0511674 | 2 | 9.70 | tt0511676 | 3 | 3.50 |
| tt0096532 | American Gladiators | 1989 | 8 | 7 | 1 | tt1000787 | 1 | 7.30 | tt1000788 | 1 | 7.20 |
| tt1756927 | American Restoration | 2010 | 7 | 5 | 7 | tt1883454 | 2 | 8.20 | tt5284500 | 7 | 2.80 |
| tt12872884 | An Anatolian Tale | 2020 | 7 | 6 | 1 | tt13639714 | 1 | 9.00 | tt13450724 | 1 | 8.50 |
| tt7569724 | Ancient Civilizations | 2017 | 6 | 4 | 1 | tt9032160 | 1 | 7.40 | tt9032160 | 1 | 7.40 |
| tt13819960 | And Just Like That... | 2021 | 3 | 3 | 3 | tt27304686 | 2 | 7.60 | tt36587111 | 3 | 4.80 |
| tt6155146 | Ang probinsyano | 2015 | 9 | 9 | 1 | tt6476178 | 1 | 6.70 | tt6476162 | 1 | 5.20 |

_1025 rows in total, first 50 shown._

### Q6: Actors successful in several languages

<!-- RESULTS: q6_actors_2plus_languages, q6_actors_3plus_languages -->

**q6_actors_2plus_languages**

| nconst | primaryName | languages | language_list | successful_films |
| --- | --- | --- | --- | --- |
| nm0001536 | Toshirō Mifune | 7 | de,en,fr,it,ja,nl,sv | 8 |
| nm0814280 | Song Kang-ho | 6 | en,es,fr,it,ko,tr | 12 |
| nm0784038 | Şener Şen | 5 | de,en,fr,ja,tr | 21 |
| nm0344346 | Ayşen Gruda | 5 | de,fr,ja,th,tr | 12 |
| nm0004486 | Bruno Ganz | 5 | de,en,fr,it,sv | 12 |
| nm0226699 | Bogdan Diklic | 5 | en,es,hr,it,sr | 10 |
| nm1367681 | Oh Dal-su | 5 | de,en,fr,hi,ko | 9 |
| nm0245988 | Trine Dyrholm | 5 | da,en,fr,it,ja | 9 |
| nm0504897 | Tony Leung Chiu-wai | 5 | de,en,es,fr,yue | 8 |
| nm1488529 | Ahmet Mümtaz Taylan | 5 | de,en,fr,sv,th | 5 |
| nm1002038 | Çetin Tekindor | 5 | de,fr,ja,sv,tr | 5 |
| nm0000367 | Gérard Depardieu | 4 | en,es,fr,it | 21 |
| nm0001884 | Max von Sydow | 4 | da,en,fr,sv | 19 |
| nm0509263 | Nikolaj Lie Kaas | 4 | da,en,es,ja | 16 |
| nm0603402 | Jeanne Moreau | 4 | en,es,fr,it | 11 |
| nm0880521 | Liv Ullmann | 4 | da,en,fr,sv | 10 |
| nm2437361 | Cho Jin-woong | 4 | de,en,fr,ko | 9 |
| nm0001588 | Jack Palance | 4 | de,en,fr,it | 9 |
| nm0876300 | Ulrich Tukur | 4 | de,en,es,fr | 9 |
| nm0000761 | Bibi Andersson | 4 | da,en,fr,sv | 8 |
| nm0948000 | Cem Yılmaz | 4 | de,en,ja,tr | 8 |
| nm1978402 | Ha Jung-woo | 4 | de,en,fr,ko | 8 |
| nm1058565 | Hwang Jung-min | 4 | de,fr,hi,ko | 8 |
| nm0619938 | Tatsuya Nakadai | 4 | de,en,fr,sv | 8 |
| nm0458460 | Burghart Klaußner | 4 | de,en,fr,sv | 7 |
| nm0721073 | Fernando Rey | 4 | en,es,fr,it | 7 |
| nm0556399 | Giulietta Masina | 4 | en,fr,it,pt | 7 |
| nm0004462 | Jean-Louis Trintignant | 4 | en,es,fr,it | 7 |
| nm0159802 | Jesper Christensen | 4 | da,en,no,sv | 7 |
| nm0432601 | Jung Woo-sung | 4 | en,es,fr,ko | 7 |
| nm0001428 | Klaus Kinski | 4 | de,en,es,it | 7 |
| nm0634159 | Philippe Noiret | 4 | en,es,fr,it | 7 |
| nm0269419 | Pierfrancesco Favino | 4 | de,en,fr,it | 7 |
| nm1763577 | Serkan Keskin | 4 | de,ja,pt,tr | 7 |
| nm0945189 | Simon Yam | 4 | en,es,yue,zh | 7 |
| nm0000420 | Valeria Golino | 4 | en,es,fr,it | 7 |
| nm0456077 | Güven Kıraç | 4 | de,hi,th,tr | 6 |
| nm3362169 | Jeong Man-sik | 4 | de,en,hi,ko | 6 |
| nm0543547 | Miki Manojlović | 4 | bs,en,hr,sr | 6 |
| nm0322977 | Nebojša Glogovac | 4 | de,hr,ja,sr | 6 |
| nm1818216 | Payman Maadi | 4 | en,fa,fr,ko | 6 |
| nm1914298 | Pål Sverre Hagen | 4 | da,en,ja,sv | 6 |
| nm2440627 | Ryu Seung-ryong | 4 | de,en,it,ko | 6 |
| nm0865411 | Srdjan 'Zika' Todorovic | 4 | de,en,hr,sr | 6 |
| nm0009629 | Stefano Accorsi | 4 | de,fr,hi,it | 6 |
| nm0785842 | Toni Servillo | 4 | de,en,es,it | 6 |
| nm0951309 | Uğur Yücel | 4 | de,en,th,tr | 6 |
| nm0474492 | Agata Kulesza | 4 | de,en,fr,pl | 5 |
| nm1892960 | Cengiz Bozkurt | 4 | de,ja,pt,tr | 5 |
| nm0059941 | Cezmi Baskın | 4 | de,en,th,tr | 5 |

_2151 rows in total, first 50 shown._

**q6_actors_3plus_languages**

| nconst | primaryName | languages | language_list | successful_films |
| --- | --- | --- | --- | --- |
| nm0001536 | Toshirō Mifune | 7 | de,en,fr,it,ja,nl,sv | 8 |
| nm0814280 | Song Kang-ho | 6 | en,es,fr,it,ko,tr | 12 |
| nm0784038 | Şener Şen | 5 | de,en,fr,ja,tr | 21 |
| nm0344346 | Ayşen Gruda | 5 | de,fr,ja,th,tr | 12 |
| nm0004486 | Bruno Ganz | 5 | de,en,fr,it,sv | 12 |
| nm0226699 | Bogdan Diklic | 5 | en,es,hr,it,sr | 10 |
| nm1367681 | Oh Dal-su | 5 | de,en,fr,hi,ko | 9 |
| nm0245988 | Trine Dyrholm | 5 | da,en,fr,it,ja | 9 |
| nm0504897 | Tony Leung Chiu-wai | 5 | de,en,es,fr,yue | 8 |
| nm1488529 | Ahmet Mümtaz Taylan | 5 | de,en,fr,sv,th | 5 |
| nm1002038 | Çetin Tekindor | 5 | de,fr,ja,sv,tr | 5 |
| nm0000367 | Gérard Depardieu | 4 | en,es,fr,it | 21 |
| nm0001884 | Max von Sydow | 4 | da,en,fr,sv | 19 |
| nm0509263 | Nikolaj Lie Kaas | 4 | da,en,es,ja | 16 |
| nm0603402 | Jeanne Moreau | 4 | en,es,fr,it | 11 |
| nm0880521 | Liv Ullmann | 4 | da,en,fr,sv | 10 |
| nm2437361 | Cho Jin-woong | 4 | de,en,fr,ko | 9 |
| nm0001588 | Jack Palance | 4 | de,en,fr,it | 9 |
| nm0876300 | Ulrich Tukur | 4 | de,en,es,fr | 9 |
| nm0000761 | Bibi Andersson | 4 | da,en,fr,sv | 8 |
| nm0948000 | Cem Yılmaz | 4 | de,en,ja,tr | 8 |
| nm1978402 | Ha Jung-woo | 4 | de,en,fr,ko | 8 |
| nm1058565 | Hwang Jung-min | 4 | de,fr,hi,ko | 8 |
| nm0619938 | Tatsuya Nakadai | 4 | de,en,fr,sv | 8 |
| nm0458460 | Burghart Klaußner | 4 | de,en,fr,sv | 7 |
| nm0721073 | Fernando Rey | 4 | en,es,fr,it | 7 |
| nm0556399 | Giulietta Masina | 4 | en,fr,it,pt | 7 |
| nm0004462 | Jean-Louis Trintignant | 4 | en,es,fr,it | 7 |
| nm0159802 | Jesper Christensen | 4 | da,en,no,sv | 7 |
| nm0432601 | Jung Woo-sung | 4 | en,es,fr,ko | 7 |
| nm0001428 | Klaus Kinski | 4 | de,en,es,it | 7 |
| nm0634159 | Philippe Noiret | 4 | en,es,fr,it | 7 |
| nm0269419 | Pierfrancesco Favino | 4 | de,en,fr,it | 7 |
| nm1763577 | Serkan Keskin | 4 | de,ja,pt,tr | 7 |
| nm0945189 | Simon Yam | 4 | en,es,yue,zh | 7 |
| nm0000420 | Valeria Golino | 4 | en,es,fr,it | 7 |
| nm0456077 | Güven Kıraç | 4 | de,hi,th,tr | 6 |
| nm3362169 | Jeong Man-sik | 4 | de,en,hi,ko | 6 |
| nm0543547 | Miki Manojlović | 4 | bs,en,hr,sr | 6 |
| nm0322977 | Nebojša Glogovac | 4 | de,hr,ja,sr | 6 |
| nm1818216 | Payman Maadi | 4 | en,fa,fr,ko | 6 |
| nm1914298 | Pål Sverre Hagen | 4 | da,en,ja,sv | 6 |
| nm2440627 | Ryu Seung-ryong | 4 | de,en,it,ko | 6 |
| nm0865411 | Srdjan 'Zika' Todorovic | 4 | de,en,hr,sr | 6 |
| nm0009629 | Stefano Accorsi | 4 | de,fr,hi,it | 6 |
| nm0785842 | Toni Servillo | 4 | de,en,es,it | 6 |
| nm0951309 | Uğur Yücel | 4 | de,en,th,tr | 6 |
| nm0474492 | Agata Kulesza | 4 | de,en,fr,pl | 5 |
| nm1892960 | Cengiz Bozkurt | 4 | de,ja,pt,tr | 5 |
| nm0059941 | Cezmi Baskın | 4 | de,en,th,tr | 5 |

_367 rows in total, first 50 shown._

### Q7: Long careers that peaked early

<!-- RESULTS: q7_early_peak_actors -->

| nconst | primaryName | first_year | last_year | career_years | movies | best_movie | best_year | best_rating | early_avg_rating | late_avg_rating | rating_drop | early_avg_votes | late_avg_votes |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| nm0000043 | Veronica Lake | 1941 | 1970 | 29 | 20 | Sullivan's Travels | 1941 | 7.90 | 6.42 | 2.50 | 3.92 | 4278.00 | 808.00 |
| nm0025618 | Mahesh Anand | 1988 | 2019 | 31 | 32 | Abhimanyu | 1991 | 7.40 | 5.47 | 1.90 | 3.57 | 739.00 | 317.00 |
| nm0680927 | Philomina | 1983 | 2003 | 20 | 16 | Godfather | 1991 | 8.60 | 7.33 | 3.80 | 3.53 | 839.00 | 241.00 |
| nm0939961 | Robert Woods | 1966 | 2016 | 50 | 22 | My Name Is Pecos | 1966 | 6.10 | 5.12 | 1.70 | 3.42 | 340.00 | 477.00 |
| nm0738553 | Artur Rolén | 1918 | 1967 | 49 | 20 | The Outlaw and His Wife | 1918 | 7.20 | 7.20 | 3.85 | 3.35 | 2373.00 | 139.00 |
| nm0060692 | Aleksey Batalov | 1954 | 2007 | 53 | 16 | The Cranes Are Flying | 1957 | 8.30 | 7.35 | 4.05 | 3.30 | 3367.00 | 221.00 |
| nm0562770 | Ken Maynard | 1931 | 1970 | 39 | 19 | Harmony Trail | 1944 | 6.70 | 5.97 | 2.70 | 3.27 | 147.00 | 1084.00 |
| nm0936295 | Norman Wisdom | 1953 | 2002 | 49 | 18 | A Stitch in Time | 1963 | 6.90 | 6.31 | 3.20 | 3.11 | 979.00 | 280.00 |
| nm0767741 | Tom Savini | 1977 | 2015 | 38 | 20 | From Dusk Till Dawn | 1996 | 7.20 | 6.13 | 3.16 | 2.97 | 64898.00 | 701.00 |
| nm0007147 | Dev Anand | 1951 | 2003 | 52 | 41 | Guide | 1965 | 8.40 | 7.11 | 4.16 | 2.95 | 758.00 | 318.00 |
| nm0044600 | Saroja Devi B. | 1958 | 2023 | 65 | 16 | Babruvahana | 1977 | 8.90 | 8.01 | 5.07 | 2.94 | 259.00 | 3200.00 |
| nm0015629 | Tuncay Akça | 1975 | 2018 | 43 | 19 | The Chaos Class Failed the Class | 1975 | 8.30 | 6.74 | 3.90 | 2.84 | 4500.00 | 480.00 |
| nm0619870 | Reza Naji | 1997 | 2025 | 28 | 18 | Children of Heaven | 1997 | 8.20 | 7.30 | 4.52 | 2.78 | 21879.00 | 580.00 |
| nm0008206 | Akbar Abdi | 1987 | 2023 | 36 | 40 | Mother | 1990 | 8.40 | 6.46 | 3.69 | 2.77 | 1316.00 | 1176.00 |
| nm0351352 | Coşkun Göğen | 1975 | 2022 | 47 | 23 | Arkadasim | 1982 | 7.20 | 5.46 | 2.70 | 2.76 | 744.00 | 850.00 |
| nm0613098 | Caroline Munro | 1972 | 2020 | 48 | 19 | The Spy Who Loved Me | 1977 | 7.00 | 5.59 | 2.83 | 2.76 | 15932.00 | 698.00 |
| nm0499614 | Ari Lehman | 1978 | 2026 | 48 | 17 | Manny's Orphans | 1978 | 6.40 | 6.40 | 3.68 | 2.72 | 104.00 | 792.00 |
| nm0878597 | Deborah Twiss | 1997 | 2025 | 28 | 16 | Kick-Ass | 2010 | 7.60 | 6.60 | 3.88 | 2.72 | 209177.00 | 359.00 |
| nm0164967 | Robert Clarke | 1945 | 1990 | 45 | 28 | The Enchanted Cottage | 1945 | 7.50 | 5.49 | 2.87 | 2.62 | 857.00 | 1256.00 |
| nm0006370 | Manoj Kumar | 1962 | 1995 | 33 | 20 | My Name Is Joker | 1970 | 7.90 | 7.02 | 4.43 | 2.59 | 864.00 | 697.00 |
| nm0015145 | Halit Akçatepe | 1972 | 2005 | 33 | 35 | The Chaos Class | 1975 | 9.10 | 7.16 | 4.57 | 2.59 | 7578.00 | 5626.00 |
| nm0431889 | Arline Judge | 1931 | 1963 | 32 | 26 | From This Day Forward | 1946 | 6.40 | 5.88 | 3.30 | 2.58 | 409.00 | 2179.00 |
| nm0838517 | Sumalatha | 1980 | 2023 | 43 | 25 | Thoovanathumbikal | 1987 | 8.60 | 7.23 | 4.67 | 2.56 | 878.00 | 2177.00 |
| nm0042820 | Suzan Avcı | 1962 | 2003 | 41 | 40 | Before the Ice Thaws | 1965 | 7.60 | 5.82 | 3.27 | 2.55 | 328.00 | 897.00 |
| nm0518579 | Ulli Lommel | 1964 | 2020 | 56 | 25 | Chinese Roulette | 1976 | 7.20 | 5.64 | 3.10 | 2.54 | 1361.00 | 2752.00 |
| nm0454448 | Andrea King | 1944 | 1994 | 50 | 24 | Ride the Pink Horse | 1947 | 7.20 | 6.49 | 3.95 | 2.54 | 1483.00 | 631.00 |
| nm9969854 | Rekha | 1986 | 2026 | 40 | 28 | In Harihar Nagar | 1990 | 8.60 | 7.34 | 4.89 | 2.45 | 1557.00 | 582.00 |
| nm0006428 | Arlene Dahl | 1947 | 1991 | 44 | 26 | Journey to the Center of the Earth | 1959 | 7.00 | 6.20 | 3.80 | 2.40 | 1707.00 | 444.00 |
| nm0093921 | Derek Bond | 1947 | 1998 | 51 | 23 | Scott of the Antarctic | 1948 | 7.00 | 6.08 | 3.70 | 2.38 | 775.00 | 103.00 |
| nm0557625 | Raju Shrestha | 1972 | 2012 | 40 | 16 | Bawarchi | 1972 | 8.10 | 7.00 | 4.62 | 2.38 | 1211.00 | 295.00 |
| nm0450810 | Evelyn Keyes | 1939 | 1989 | 50 | 34 | Gone with the Wind | 1939 | 8.20 | 6.52 | 4.15 | 2.37 | 14070.00 | 4134.00 |
| nm0900568 | Rena Vlahopoulou | 1962 | 1982 | 20 | 21 | The Robber Cries Thief! | 1965 | 7.50 | 6.14 | 3.77 | 2.37 | 623.00 | 178.00 |
| nm0135988 | Lilli Carati | 1975 | 2015 | 40 | 17 | Highway Racer | 1977 | 6.40 | 5.07 | 2.70 | 2.37 | 474.00 | 361.00 |
| nm0449431 | András Kern | 1973 | 2016 | 43 | 22 | Cat City | 1986 | 8.20 | 7.19 | 4.83 | 2.36 | 1827.00 | 1023.00 |
| nm0129316 | Giuliana Calandra | 1973 | 2008 | 35 | 23 | Love & Anarchy | 1973 | 7.70 | 5.98 | 3.70 | 2.28 | 2888.00 | 945.00 |
| nm0200122 | William Daniels | 1963 | 2025 | 62 | 16 | The Graduate | 1967 | 8.00 | 6.55 | 4.30 | 2.25 | 34168.00 | 573.00 |
| nm0426958 | Johny | 1984 | 2022 | 38 | 17 | Rajavinte Makan | 1986 | 7.70 | 7.10 | 4.86 | 2.24 | 303.00 | 980.00 |
| nm0690450 | Kaviyoor Ponnamma | 1973 | 2021 | 48 | 45 | Sandesham | 1991 | 9.00 | 7.68 | 5.44 | 2.24 | 1758.00 | 667.00 |
| nm0639684 | Margaret O'Brien | 1942 | 2018 | 76 | 22 | Our Vines Have Tender Grapes | 1945 | 7.60 | 6.73 | 4.50 | 2.23 | 3851.00 | 685.00 |
| nm0215167 | Martin Dejdar | 1987 | 2020 | 33 | 15 | Tichá bolest | 1991 | 8.00 | 6.31 | 4.08 | 2.23 | 370.00 | 312.00 |
| nm0363055 | Harish | 1991 | 2017 | 26 | 16 | Rowdy Inspector | 1992 | 6.90 | 5.23 | 3.00 | 2.23 | 1041.00 | 465.00 |
| nm0052410 | Reggie Bannister | 1976 | 2017 | 41 | 25 | Kenny & Company | 1976 | 7.10 | 6.28 | 4.08 | 2.20 | 15484.00 | 3980.00 |
| nm1498467 | Kalasala Babu | 1988 | 2017 | 29 | 29 | Paadha Mudhra | 1988 | 7.40 | 7.40 | 5.20 | 2.20 | 198.00 | 572.00 |
| nm0200645 | Ray Danton | 1955 | 1975 | 20 | 26 | I'll Cry Tomorrow | 1955 | 7.20 | 6.10 | 3.90 | 2.20 | 707.00 | 551.00 |
| nm0831905 | Harold J. Stone | 1956 | 1980 | 24 | 18 | The Harder They Fall | 1956 | 7.50 | 6.43 | 4.25 | 2.18 | 5572.00 | 1958.00 |
| nm0451863 | Shobha Khote | 1955 | 2022 | 67 | 27 | Gol Maal | 1979 | 8.50 | 6.73 | 4.56 | 2.17 | 1848.00 | 1108.00 |
| nm0001947 | Turhan Bey | 1941 | 1994 | 53 | 20 | The Gay Falcon | 1941 | 6.50 | 5.94 | 3.80 | 2.14 | 1199.00 | 453.00 |
| nm0562920 | Virginia Mayo | 1943 | 1997 | 54 | 48 | The Best Years of Our Lives | 1946 | 8.10 | 6.19 | 4.06 | 2.13 | 4272.00 | 256.00 |
| nm0374974 | Helen | 1957 | 2012 | 55 | 56 | Jewel Thief | 1967 | 7.90 | 6.63 | 4.51 | 2.12 | 639.00 | 1476.00 |
| nm0226326 | Eileen Dietz | 1966 | 2026 | 60 | 24 | Road Movie | 1973 | 6.90 | 5.73 | 3.62 | 2.11 | 1326.00 | 885.00 |

_5513 rows in total, first 50 shown._

### Q8: Multi-talented film professionals

<!-- RESULTS: q8_summary, q8_performance_by_combination -->

**q8_summary**

| people_with_both_modes | better_with_multiple_roles | worse_with_multiple_roles | avg_rating_gain |
| --- | --- | --- | --- |
| 10708 | 4427 | 3870 | 0.05 |

_1 rows in total._

**q8_performance_by_combination**

| role_combination | people | person_movies | avg_rating | avg_votes |
| --- | --- | --- | --- | --- |
| single role (baseline) | 8644 | 78250 | 5.92 | 20245.00 |
| director+writer | 9410 | 45820 | 6.01 | 12262.00 |
| actor+director+writer | 2201 | 4896 | 5.66 | 7582.00 |
| actor+writer | 1501 | 3817 | 5.69 | 16304.00 |
| actor+director | 651 | 1158 | 5.76 | 13715.00 |

_5 rows in total._

### Methodological explanation

For every question we only used the cleaned tables. A "movie" here is a
non-adult title of type `movie` that lasts more than 40 minutes (the usual
feature film rule). We often added a minimum number of votes, because a
rating from five people doesn't mean much.

For Q1, runtimes are very skewed (some art films last days), so a normal
z-score only catches the extreme ones. We used a robust z-score on the log of
the runtime, with the median and the MAD of each genre, and kept films with
|z| >= 3.5. This way we also find films that are much shorter than usual.
For Q2 the popularity of a genre in a year is the total number of votes of
its movies, and we keep the three highest. For Q3 we compared these three
genres with the rest using their share of votes, votes per movie and a
rating weighted by votes.

For Q4 we kept directors with exactly one movie rated 8 or more and at least
two movies rated 6 or less (movies with 100+ votes). We also tried a second
reading of the question, where the average of the other movies is 6 or less.
For Q5 we counted episodes per season (season 0 is ignored), kept series with
at least three seasons of 10+ episodes, and checked where the best and worst
rated episodes are.

For Q6, IMDb has no original language, so we guessed it from the akas marked
as original title, using the language code or the main language of the
region. A film is a success with a rating of 7+ and 5,000+ votes. For Q7 we
split each career in two halves at its middle year, and an actor peaked early
if their best film and their best average rating are in the first half. For
Q8 we took the roles from principals and crew, kept people with at least two
roles (each on 3+ movies), and compared their movies with one role and with
several roles.

## Data enrichment

### Selected films and principals

<!-- RESULTS: targets_summary -->

**targets_summary**

| measure | value |
| --- | --- |
| (film, genre, year) rows | 9832 |
| distinct films | 6821 |
| (film, principal) rows | 20431 |
| distinct people | 10479 |

_4 rows in total._

### Coverage of the enrichment

<!-- RESULTS: coverage -->

**coverage**

| dataset | rows | enriched | from_plot_section | pct_enriched |
| --- | --- | --- | --- | --- |
| films (year, genre, rank) | 9832 | 9331 | 8903 | 94.90 |
| principals (film, person) | 20431 | 17738 |  | 86.80 |

_2 rows in total._

### Notes on missing information

<!-- RESULTS: film_notes, principal_notes -->

**film_notes**

| enrichment_note | count |
| --- | --- |
| none (fully enriched) | 8903 |
| Article has no plot/synopsis section; lead section used | 428 |
| No English Wikipedia article linked to the Wikidata item | 253 |
| No Wikidata item found for this IMDb ID | 247 |
| Article has no usable synopsis text | 1 |

_5 rows in total._

**principal_notes**

| enrichment_note | count |
| --- | --- |
| none (fully enriched) | 17738 |
| No Wikidata item found for this IMDb ID | 1804 |
| No English Wikipedia article linked to the Wikidata item | 879 |
| Article has no usable lead section | 10 |

_4 rows in total._

### Sample of enriched records

<!-- RESULTS: films_sample, principals_sample -->

**films_sample**

| year | genre | rank | tconst | primaryTitle | synopsis_source | synopsis_preview | source_url | enrichment_note |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1980 | Action | 1 | tt0081573 | Superman II | plot_section | Before the destruction of Krypton, the criminals General Zod, Ursa and Non are sentenced to banishment into the Phantom Zone. Years later, the Phantom Zone is shattered near Earth by the shockwave of ... | https://en.wikipedia.org/w/index.php?title=Superman_II&oldid=1383900393 |  |
| 1980 | Action | 2 | tt0080745 | Flash Gordon | plot_section | To relieve his boredom, Emperor Ming the Merciless of the planet Mongo begins Earth's destruction by remotely causing natural disasters. On Earth, football star Gregory "Flash" Gordon boards a small p... | https://en.wikipedia.org/w/index.php?title=Flash_Gordon_%28film%29&oldid=1385236838 |  |
| 1980 | Action | 3 | tt0080736 | The Final Countdown | plot_section | In 1980, the nuclear-powered aircraft carrier USS Nimitz departs Naval Station Pearl Harbor for exercises in the mid-Pacific Ocean. A civilian systems analyst for Tideman Industries named Warren Lasky... | https://en.wikipedia.org/w/index.php?title=The_Final_Countdown_%28film%29&oldid=1380482840 |  |
| 1980 | Adventure | 1 | tt0080684 | Star Wars: Episode V - The Empire Strikes Back | plot_section | Three years after the destruction of the Death Star, the Imperial fleet, led by Darth Vader, dispatches probe droids across the galaxy in search of the Rebel Alliance. One probe locates the Rebel base... | https://en.wikipedia.org/w/index.php?title=The_Empire_Strikes_Back&oldid=1384987356 |  |
| 1980 | Adventure | 2 | tt0080455 | The Blues Brothers | plot_section | Jake Blues, a blues vocalist and petty criminal, is paroled from Joliet Prison after serving three years of a five-year sentence for armed robbery and is picked up by his brother Elwood in a battered ... | https://en.wikipedia.org/w/index.php?title=The_Blues_Brothers_%28film%29&oldid=1385022778 |  |
| 1980 | Adventure | 3 | tt0081573 | Superman II | plot_section | Before the destruction of Krypton, the criminals General Zod, Ursa and Non are sentenced to banishment into the Phantom Zone. Years later, the Phantom Zone is shattered near Earth by the shockwave of ... | https://en.wikipedia.org/w/index.php?title=Superman_II&oldid=1383900393 |  |
| 1980 | Animation | 1 | tt0079820 | The King and the Mockingbird | plot_section | The huge kingdom of Takicardia is ruled by a king under the unwieldy title of Charles V + III = VIII + VIII = XVI. He is a heartless ruler, hated by his people as much as he hates them. The King is fo... | https://en.wikipedia.org/w/index.php?title=The_King_and_the_Mockingbird&oldid=1374618581 |  |
| 1980 | Animation | 2 | tt0080461 | Bon Voyage, Charlie Brown (and Don't Come Back!!) | plot_section | At Charlie Brown's school, Linus Van Pelt introduces to his class two French students, Babette and Jacques, who will be spending two weeks there to get accustomed to the United States. In exchange, Ch... | https://en.wikipedia.org/w/index.php?title=Bon_Voyage%2C_Charlie_Brown_%28and_Don%27t_Come_Back%21%21%29&oldid=1383439812 |  |
| 1980 | Animation | 3 | tt0078780 | Animalympics | plot_section | The film is a series of vignettes presented as the broadcast of the first animal Olympic Games through the fictional ZOO television network. The Games combine summer and winter Olympic events. The eve... | https://en.wikipedia.org/w/index.php?title=Animalympics&oldid=1372144226 |  |
| 1980 | Biography | 1 | tt0081398 | Raging Bull | plot_section | In 1941, Jake LaMotta is a young up-and-coming middleweight boxer who suffers his first loss to Jimmy Reeves after a controversial decision. Jake's brother Joey discusses a potential shot for the midd... | https://en.wikipedia.org/w/index.php?title=Raging_Bull&oldid=1380652135 |  |
| 1980 | Biography | 2 | tt0080678 | The Elephant Man | plot_section | Frederick Treves, a surgeon at the London Hospital, finds John Merrick in a Victorian freak show in London's East End, where he is kept by Mr. Bytes, the brutish ringmaster. Merrick's head is kept hoo... | https://en.wikipedia.org/w/index.php?title=The_Elephant_Man_%281980_film%29&oldid=1381585783 |  |
| 1980 | Biography | 3 | tt0080549 | Coal Miner's Daughter | plot_section | In 1945, 13-year-old Loretta Webb is one of eight children of Ted Webb, a Van Lear coal miner raising a family with his wife in the midst of grinding poverty in Butcher Hollow, Kentucky (pronounced by... | https://en.wikipedia.org/w/index.php?title=Coal_Miner%27s_Daughter_%28film%29&oldid=1383373870 |  |
| 1980 | Comedy | 1 | tt0080339 | Airplane! | plot_section | Ex–fighter pilot Ted Striker is a traumatized war veteran turned taxi driver. Because of his pathological fear of flying and subsequent "drinking problem"—he splashes beverages anywhere but into his m... | https://en.wikipedia.org/w/index.php?title=Airplane%21&oldid=1385188942 |  |
| 1980 | Comedy | 2 | tt0080455 | The Blues Brothers | plot_section | Jake Blues, a blues vocalist and petty criminal, is paroled from Joliet Prison after serving three years of a five-year sentence for armed robbery and is picked up by his brother Elwood in a battered ... | https://en.wikipedia.org/w/index.php?title=The_Blues_Brothers_%28film%29&oldid=1385022778 |  |
| 1980 | Comedy | 3 | tt0080487 | Caddyshack | plot_section | Teenager Danny Noonan is uncertain about his future, unsure whether to attend college but worried about becoming trapped in a menial job with few prospects. He works as a caddie at the exclusive Bushw... | https://en.wikipedia.org/w/index.php?title=Caddyshack&oldid=1385138051 |  |
| 1980 | Crime | 1 | tt0080455 | The Blues Brothers | plot_section | Jake Blues, a blues vocalist and petty criminal, is paroled from Joliet Prison after serving three years of a five-year sentence for armed robbery and is picked up by his brother Elwood in a battered ... | https://en.wikipedia.org/w/index.php?title=The_Blues_Brothers_%28film%29&oldid=1385022778 |  |
| 1980 | Crime | 2 | tt0080661 | Dressed to Kill | plot_section | Sexually frustrated housewife Kate Miller is attending therapy sessions with New York City psychiatrist Dr. Robert Elliott. During an appointment, Kate attempts to seduce him, but Elliott rejects her ... | https://en.wikipedia.org/w/index.php?title=Dressed_to_Kill_%281980_film%29&oldid=1383365391 |  |
| 1980 | Crime | 3 | tt0081562 | Stir Crazy | plot_section | In New York City, aspiring actor Harry Monroe is fired from his job as a waiter when cooks accidentally use his stash of marijuana as oregano at a dinner party. His friend, aspiring playwright Skip Do... | https://en.wikipedia.org/w/index.php?title=Stir_Crazy_%28film%29&oldid=1381466942 |  |
| 1980 | Documentary | 1 | tt0080813 | The Great Rock 'n' Roll Swindle | plot_section | Guitarist Steve Jones plays a shady private detective who through a series of set piece acts uncovers the truth about the band. Drummer Paul Cook and bass guitarist Sid Vicious play smaller roles, and... | https://en.wikipedia.org/w/index.php?title=The_Great_Rock_%27n%27_Roll_Swindle&oldid=1375407111 |  |
| 1980 | Documentary | 2 | tt0081055 | Lightning Over Water | plot_section | Lightning Over Water is a collaboration between Wenders and Ray to document Ray's last days due to terminal cancer in 1979. The film is partially an homage to Ray, who had a strong influence on Wender... | https://en.wikipedia.org/w/index.php?title=Lightning_Over_Water&oldid=1341592825 |  |
| 1980 | Documentary | 3 | tt0080321 | AC/DC: Let There Be Rock | lead_section | AC/DC: Let There Be Rock is a 1980 concert film featuring the Australian hard rock band AC/DC, released theatrically in September 1980 (and AC/DC's native Australia on New Year's Eve, 1981) and on vid... | https://en.wikipedia.org/w/index.php?title=AC/DC%3A_Let_There_Be_Rock&oldid=1365547584 | Article has no plot/synopsis section; lead section used |
| 1980 | Drama | 1 | tt0081505 | The Shining | plot_section | Jack Torrance takes a caretaker position to look after the remote Overlook Hotel in the Colorado Rocky Mountains while it is closed for the winter. On arrival, hotel manager Stuart Ullman informs Jack... | https://en.wikipedia.org/w/index.php?title=The_Shining_%28film%29&oldid=1383904140 |  |
| 1980 | Drama | 2 | tt0081398 | Raging Bull | plot_section | In 1941, Jake LaMotta is a young up-and-coming middleweight boxer who suffers his first loss to Jimmy Reeves after a controversial decision. Jake's brother Joey discusses a potential shot for the midd... | https://en.wikipedia.org/w/index.php?title=Raging_Bull&oldid=1380652135 |  |
| 1980 | Drama | 3 | tt0080678 | The Elephant Man | plot_section | Frederick Treves, a surgeon at the London Hospital, finds John Merrick in a Victorian freak show in London's East End, where he is kept by Mr. Bytes, the brutish ringmaster. Merrick's head is kept hoo... | https://en.wikipedia.org/w/index.php?title=The_Elephant_Man_%281980_film%29&oldid=1381585783 |  |
| 1980 | Family | 1 | tt0081353 | Popeye | plot_section | Popeye, a gruff but good-hearted sailor, arrives at the small coastal town of Sweethaven while searching for his missing father. He rents a room at the Oyl family's boarding house, where the Oyls plan... | https://en.wikipedia.org/w/index.php?title=Popeye_%28film%29&oldid=1384018450 |  |
| 1980 | Family | 2 | tt0081207 | My Bodyguard | plot_section | Clifford Peache lives in an upscale Chicago luxury hotel with his father, the hotel manager, and his grandmother. He is new to Fleer High School and arrives each day in a hotel limousine. Clifford is ... | https://en.wikipedia.org/w/index.php?title=My_Bodyguard&oldid=1382660627 |  |
| 1980 | Family | 3 | tt0081738 | The Watcher in the Woods | plot_section | Americans Helen and Paul Curtis and their daughters, Jan and Ellie, move into a manor in rural England. Mrs. Aylwood, the owner of the residence who now lives in the guest house next door, notices tha... | https://en.wikipedia.org/w/index.php?title=The_Watcher_in_the_Woods_%281980_film%29&oldid=1375242708 |  |
| 1980 | Fantasy | 1 | tt0080684 | Star Wars: Episode V - The Empire Strikes Back | plot_section | Three years after the destruction of the Death Star, the Imperial fleet, led by Darth Vader, dispatches probe droids across the galaxy in search of the Rebel Alliance. One probe locates the Rebel base... | https://en.wikipedia.org/w/index.php?title=The_Empire_Strikes_Back&oldid=1384987356 |  |
| 1980 | Fantasy | 2 | tt0081534 | Somewhere in Time | plot_section | In 1972, college theater student Richard Collier celebrates the debut of his new play. An elderly woman approaches him, places an ornate gold pocket watch in his hand, and pleads, "Come back to me." E... | https://en.wikipedia.org/w/index.php?title=Somewhere_in_Time_%28film%29&oldid=1383819270 |  |
| 1980 | Fantasy | 3 | tt0081777 | Xanadu | plot_section | Sonny Malone, a struggling self-employed illustrator residing in Los Angeles, has failed to find passion in his art. He tears up one of his sketches and tosses the pieces out his studio window; the wi... | https://en.wikipedia.org/w/index.php?title=Xanadu_%28film%29&oldid=1384969979 |  |

_3026 rows in total, first 30 shown._

**principals_sample**

| tconst | principal_rank | nconst | primaryName | category | birth_date | birth_place | biography_preview | source_url | enrichment_note |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| tt9893250 | 1 | nm0683253 | Rosamund Pike | actress | 1979-01-27 | Hammersmith | Rosamund Mary Ellen Pike (born 1979) is a British actress and producer. Known for her portrayals of complex and morally ambiguous women in independent cinema and psychological thrillers, her accolades... | https://en.wikipedia.org/w/index.php?title=Rosamund_Pike&oldid=1381714914 |  |
| tt9893250 | 2 | nm0227759 | Peter Dinklage | actor | 1969-06-11 | Morristown | Peter Hayden Dinklage (born June 11, 1969) is an American actor. Portraying Tyrion Lannister on the HBO television series Game of Thrones (2011–2019), he won the Primetime Emmy Award for Outstanding S... | https://en.wikipedia.org/w/index.php?title=Peter_Dinklage&oldid=1384730402 |  |
| tt9893250 | 3 | nm2555462 | Eiza González | actress | 1990-01-30 | Mexico City | Eiza González Reyna (born 30 January 1990) is a Mexican actress and singer. She gained popularity for starring in the Nickelodeon teen sitcom Sueña conmigo (2010–2011). As a singer, she released the a... | https://en.wikipedia.org/w/index.php?title=Eiza_Gonz%C3%A1lez&oldid=1385056542 |  |
| tt9883832 | 1 | nm0000309 | David Bowie | archive_footage | 1947-01-08 | Brixton | David Robert Jones (8 January 1947 – 10 January 2016), known as David Bowie, was an English singer, songwriter and actor. Regarded as among the most influential musicians of the 20th century, he was k... | https://en.wikipedia.org/w/index.php?title=David_Bowie&oldid=1384912277 |  |
| tt9883832 | 2 | nm0092783 | Trevor Bolder | archive_footage | 1950-06-09 | Kingston upon Hull | Trevor Bolder (9 June 1950 – 21 May 2013) was an English rock musician, songwriter and record producer. He is best known for his long association with Uriah Heep and his tenure with the Spiders from M... | https://en.wikipedia.org/w/index.php?title=Trevor_Bolder&oldid=1375231962 |  |
| tt9883832 | 3 | nm5123954 | Ken Fordham | archive_footage |  |  |  |  | No Wikidata item found for this IMDb ID |
| tt9873892 | 1 | nm3915784 | John Boyega | actor | 1992-03-17 | London | John Adedayo Bamidele Adegboyega (born 17 March 1992), known professionally as John Boyega, is an English actor and producer. He first gained recognition in Britain for his role as a teenage gang lead... | https://en.wikipedia.org/w/index.php?title=John_Boyega&oldid=1383093605 |  |
| tt9873892 | 2 | nm0004937 | Jamie Foxx | actor | 1967-12-13 | Terrell | Jamie Foxx (born Eric Marlon Bishop, December 13, 1967), is an American actor, comedian, singer, and film producer. He gained his career breakthrough as a featured player in the sketch comedy show In ... | https://en.wikipedia.org/w/index.php?title=Jamie_Foxx&oldid=1383093860 |  |
| tt9873892 | 3 | nm3500582 | Teyonah Parris | actress | 1987-09-22 | Hopkins | Teyonah Parris ( tee-ON-ə; born September 22, 1987) is an American actress. A graduate of Juilliard School, she began acting in 2010. Her first prominent roles were in the drama series Mad Men (2012–2... | https://en.wikipedia.org/w/index.php?title=Teyonah_Parris&oldid=1380124667 |  |
| tt9866072 | 1 | nm0731075 | Emma Roberts | actress | 1991-02-10 | Rhinebeck | Emma Rose Roberts (born February 10, 1991) is an American actress. Known for her performances spanning multiple genres of film and television, her work in the horror and thriller genres have establish... | https://en.wikipedia.org/w/index.php?title=Emma_Roberts&oldid=1383040790 |  |
| tt9866072 | 2 | nm3478396 | Luke Bracey | actor | 1989-04-26 | Sydney | Luke Bracey (born 26 April 1989) is an Australian actor. He is known for his work in films such as Monte Carlo (2011), G.I. Joe: Retaliation (2013), The November Man (2014), Point Break (2015), Hacksa... | https://en.wikipedia.org/w/index.php?title=Luke_Bracey&oldid=1381709140 |  |
| tt9866072 | 3 | nm0155693 | Kristin Chenoweth | actress | 1968-07-24 | Broken Arrow | Kristin Dawn Chenoweth (born Kristi Dawn Chenoweth; July 24, 1968) is an American actress and singer, with credits in musical theatre, film, and television. In 1999, she won a Tony Award for Best Feat... | https://en.wikipedia.org/w/index.php?title=Kristin_Chenoweth&oldid=1381361302 |  |
| tt9820556 | 1 | nm4181215 | Cody Kearsley | actor | 1991-03-10 | British Columbia | Cody Kearsley is a Canadian actor, best known for his portrayal of Moose Mason in the CW series Riverdale and Turbo Pokaski in the Netflix series Daybreak.... | https://en.wikipedia.org/w/index.php?title=Cody_Kearsley&oldid=1379373071 |  |
| tt9820556 | 2 | nm0000246 | Bruce Willis | actor | 1955-03-19 | Idar-Oberstein | Walter Bruce Willis (born March 19, 1955) is a retired American actor. Widely recognized as a Hollywood icon of the action genre, he first achieved fame with a leading role on the comedy-drama series ... | https://en.wikipedia.org/w/index.php?title=Bruce_Willis&oldid=1385136338 |  |
| tt9820556 | 3 | nm0629697 | Rachel Nichols | actress | 1980-01-08 | Augusta | Rachel Nichols (born 1979 or 1980) is an American actress and model. Nichols began modeling while attending Columbia University in New York City in the late 1990s, and transitioned into acting by the ... | https://en.wikipedia.org/w/index.php?title=Rachel_Nichols_%28actress%29&oldid=1373509917 |  |
| tt9784798 | 1 | nm3147751 | LaKeith Stanfield | actor | 1991-08-12 | San Bernardino | LaKeith Lee Stanfield (born August 12, 1991) is an American actor and musician. He made his feature film debut in Short Term 12 (2013), for which he was nominated for an Independent Spirit Award. He r... | https://en.wikipedia.org/w/index.php?title=LaKeith_Stanfield&oldid=1382156065 |  |
| tt9784798 | 2 | nm2257207 | Daniel Kaluuya | actor | 1989-02-24 | Camden Town | Daniel Kaluuya (born 24 February 1989) is an English actor. His work encompasses both screen and stage, and his accolades include an Academy Award, two BAFTAs, two Actor Awards, and a Golden Globe, in... | https://en.wikipedia.org/w/index.php?title=Daniel_Kaluuya&oldid=1383094376 |  |
| tt9784798 | 3 | nm0687146 | Jesse Plemons | actor | 1988-04-02 | Dallas | Jesse Plemons (born April 2, 1988) is an American actor. Known for his work with auteurs and portrayal of eccentric characters, his accolades include a Cannes Film Festival Award for Best Actor and no... | https://en.wikipedia.org/w/index.php?title=Jesse_Plemons&oldid=1383733732 |  |
| tt9779516 | 1 | nm6216001 | KJ Apa | actor | 1997-06-17 | Auckland | Keneti James Fitzgerald "KJ" Apa (born 17 June 1997) is a New Zealand actor and singer. He gained recognition for playing Kane Jenkins in the New Zealand soap opera Shortland Street (2013–2015) and Ar... | https://en.wikipedia.org/w/index.php?title=KJ_Apa&oldid=1384584244 |  |
| tt9779516 | 2 | nm1429380 | Britt Robertson | actress | 1990-04-18 | Charlotte | Brittany Leanna Robertson-Floyd (née Robertson; born April 18, 1990), known professionally as Britt Robertson, is an American actress. Raised in Greenville, South Carolina, at age 14, Robertson moved ... | https://en.wikipedia.org/w/index.php?title=Britt_Robertson&oldid=1384927757 |  |
| tt9779516 | 3 | nm1452155 | Nathan Parsons | actor | 1988-06-16 | Adelaide | Nathan Dean Parsons (born June 16, 1988), also known as Nathan Dean, is an American actor known for his work in daytime television on the ABC daytime soap opera General Hospital as the character of Et... | https://en.wikipedia.org/w/index.php?title=Nathan_Parsons&oldid=1380261717 |  |
| tt9777666 | 1 | nm0695435 | Chris Pratt | actor | 1979-06-21 | Virginia | Christopher Michael Pratt (born June 21, 1979) is an American actor and producer. His films as a leading actor have grossed over $15.2 billion worldwide, making him one of the highest-grossing film st... | https://en.wikipedia.org/w/index.php?title=Chris_Pratt&oldid=1382889282 |  |
| tt9777666 | 2 | nm2088803 | Yvonne Strahovski | actress | 1982-07-30 | Werrington Downs | Yvonne Jaqueline Strzechowski (born 30 July 1982), known professionally as Yvonne Strahovski, is an Australian actress. She is known for her roles as Sarah Walker in the spy comedy drama series Chuck ... | https://en.wikipedia.org/w/index.php?title=Yvonne_Strahovski&oldid=1384089871 |  |
| tt9777666 | 3 | nm0799777 | J.K. Simmons | actor | 1955-01-09 | Detroit | Jonathan Kimble Simmons (born January 9, 1955) is an American actor. Considered among the most established and enduring character actors of his generation, he has amassed over 200 screen and stage cre... | https://en.wikipedia.org/w/index.php?title=J._K._Simmons&oldid=1384932189 |  |
| tt9777644 | 1 | nm0005148 | Delroy Lindo | actor | 1952-11-18 |  | Delroy George Lindo (born 18 November 1952) is an English-American actor. Starting his career in the 1975 stage production of Of Mice and Men, he later earned a nomination for the Tony Award for Best ... | https://en.wikipedia.org/w/index.php?title=Delroy_Lindo&oldid=1384405312 |  |
| tt9777644 | 2 | nm3718007 | Jonathan Majors | actor | 1989-09-07 | Lompoc | Jonathan Michael Majors (born September 7, 1989) is an American actor. A graduate of the Yale School of Drama, Majors rose to prominence for starring in the drama films The Last Black Man in San Franc... | https://en.wikipedia.org/w/index.php?title=Jonathan_Majors&oldid=1382719105 |  |
| tt9777644 | 3 | nm0676370 | Clarke Peters | actor | 1952-04-07 | New York City | Peter Clarke (born April 7, 1952), known professionally as Clarke Peters, is an American actor, writer, and director, who has spent much of his adult life in the United Kingdom. He is best known for h... | https://en.wikipedia.org/w/index.php?title=Clarke_Peters&oldid=1383899322 |  |
| tt9770150 | 1 | nm0000531 | Frances McDormand | actress | 1957-06-23 | Gibson City | Frances Louise McDormand (born Cynthia Ann Smith; June 23, 1957) is an American actress and film producer. In a career spanning over four decades, McDormand has received numerous accolades, including ... | https://en.wikipedia.org/w/index.php?title=Frances_McDormand&oldid=1383092920 |  |
| tt9770150 | 2 | nm0000657 | David Strathairn | actor | 1949-01-26 | San Francisco | David Russell Strathairn (born January 26, 1949) is an American actor. Known for his leading roles on stage and screen, he has often portrayed historical figures including Edward R. Murrow, J. Robert ... | https://en.wikipedia.org/w/index.php?title=David_Strathairn&oldid=1382133732 |  |
| tt9770150 | 3 | nm9584508 | Linda May | actress |  |  |  |  | No Wikidata item found for this IMDb ID |

_20431 rows in total, first 30 shown._

### Methodological explanation

We added data from Wikipedia (synopses and biographies) and Wikidata (the
link between IMDb and Wikipedia, birth dates and birthplaces). We couldn't
take every IMDb title, so we kept the 10 most voted films of each year and
genre between 1980 and 2025, and the first three people credited on each
film. That gives 6,821 films and 10,479 people.

The download part is a normal Python script, not Spark. It finds the
Wikidata item of each IMDb id (property P345) with SPARQL, then gets the
Wikipedia article of the film and the introduction of each person's page. We
stayed under the Wikimedia rate limit and saved everything in JSON files, so
we could restart the script when it stopped.

Then Spark reads these files with a fixed schema, takes the "Plot" section
of each film (or the introduction if there is none), cleans the text and
joins it back to IMDb. Each row keeps its source (link, revision, date,
license) and a note explaining why some data is missing. About 95 % of the
films and 87 % of the people got a text.

## Streaming data processing

Test run of 2026-11-14, 20:43-21:16 UTC: the Spark job ran for 33 minutes,
the producer forwarded 63,496 live `recentchange` events for 30 minutes, and
3,000 events from 30 minutes earlier were replayed at minute 12 (late data).

### Overview of the test run

<!-- RESULTS: overview, query_metrics -->

**overview**

| first_event | last_event | matched_events | distinct_imdb_entities | delayed_beyond_watermark | avg_delay_s | max_delay_s |
| --- | --- | --- | --- | --- | --- | --- |
| 2026-11-14 20:24:42 | 2026-11-14 21:12:03 | 139 | 111 | 7 | 92.50 | 1791 |

_1 rows in total._

**query_metrics**

| query | batches | input_rows | avg_input_rows_per_s | max_processed_rows_per_s | avg_batch_ms | max_batch_ms | rows_dropped_by_watermark | last_watermark |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| matched_events | 62 | 66496 | 35.80 | 1687.80 | 2185.10 | 5410 | 0 |  |
| traffic_windows | 63 | 66496 | 35.30 | 2709.90 | 1511.90 | 2975 | 2 | 2026-11-14T21:02:05.000Z |
| entity_windows | 63 | 66496 | 35.30 | 1660.80 | 2166.90 | 5465 | 7 | 2026-11-14T21:02:03.000Z |

_3 rows in total._

### Matches by type and most edited IMDb entities

<!-- RESULTS: matches_by_type, top_entities -->

**matches_by_type**

| entity_type | match_type | bare_key | count |
| --- | --- | --- | --- |
| person | imdb_person | True | 74 |
| person | enriched_article | True | 25 |
| film | imdb_title | False | 14 |
| series | imdb_title | True | 7 |
| film | enriched_article | True | 5 |
| film | imdb_title | True | 4 |
| person | enriched_article | False | 3 |
| series | imdb_title | False | 3 |
| film | enriched_article | False | 3 |
| person | imdb_person | False | 1 |

_10 rows in total._

**top_entities**

| imdb_id | imdb_name | entity_type | edits | editors | bytes_delta |
| --- | --- | --- | --- | --- | --- |
| tt1679335 | Trolls | film | 5 | 2 | 7 |
| nm0004938 | Kirk Franklin | person | 4 | 1 | 165 |
| tt38672588 | Masterplan | film | 4 | 1 | 2584 |
| nm10806242 | Sharvari | person | 3 | 1 | -11 |
| tt34384661 | Godzilla Minus Zero | film | 3 | 3 | 4 |
| tt4378376 | Babylon Berlin | series | 3 | 1 | 309 |
| nm0001084 | Ice Cube | person | 2 | 1 | 15 |
| nm0001790 | Sharon Tate | person | 2 | 2 | 0 |
| nm0918633 | Stephnie Weir | person | 2 | 1 | 25 |
| nm1089685 | Vanessa Ferlito | person | 2 | 1 | 43 |
| nm1184886 | Jim Florentine | person | 2 | 1 | 51 |
| nm1261984 | Eddie George | person | 2 | 1 | 0 |
| nm1277102 | Queen | person | 2 | 1 | 23 |
| nm3584268 | James Norton | person | 2 | 1 | 62 |
| nm4731677 | Ayushmann Khurrana | person | 2 | 2 | 0 |
| nm7184459 | Saverio Raimondo | person | 2 | 1 | -2 |
| tt11680468 | Great Pretender | series | 2 | 1 | -18 |
| tt13542714 | House of Guinness | series | 2 | 1 | 97 |
| nm0000054 | Marilyn Monroe | person | 1 | 1 | -3586 |
| nm0000717 | Kareem Abdul-Jabbar | person | 1 | 1 | 35 |

_111 rows in total, first 20 shown._

### Finalised event-time windows

<!-- RESULTS: finalised_windows -->

**finalised_windows**

| window_start | window_end | matched_edits | entities | article_edits | bot_edits | match_rate_pct |
| --- | --- | --- | --- | --- | --- | --- |
| 2026-11-14 20:40:00 | 2026-11-14 20:45:00 | 9 | 7 | 232 | 17 | 3.88 |
| 2026-11-14 20:45:00 | 2026-11-14 20:50:00 | 13 | 9 | 387 | 31 | 3.36 |
| 2026-11-14 20:50:00 | 2026-11-14 20:55:00 | 21 | 21 | 406 | 88 | 5.17 |
| 2026-11-14 20:55:00 | 2026-11-14 21:00:00 | 27 | 26 | 519 | 163 | 5.20 |

_4 rows in total._

### Streamed windows compared with a batch recount

<!-- RESULTS: window_reconciliation -->

**window_reconciliation**

| window_start | window_end | batch_edits | batch_entities | streamed_edits | emitted_by_stream | missing_in_stream |
| --- | --- | --- | --- | --- | --- | --- |
| 2026-11-14 20:20:00 | 2026-11-14 20:25:00 | 2 | 2 |  | False | 2 |
| 2026-11-14 20:25:00 | 2026-11-14 20:30:00 | 5 | 5 |  | False | 5 |
| 2026-11-14 20:40:00 | 2026-11-14 20:45:00 | 9 | 7 | 9 | True | 0 |
| 2026-11-14 20:45:00 | 2026-11-14 20:50:00 | 13 | 9 | 13 | True | 0 |
| 2026-11-14 20:50:00 | 2026-11-14 20:55:00 | 21 | 21 | 21 | True | 0 |
| 2026-11-14 20:55:00 | 2026-11-14 21:00:00 | 27 | 26 | 27 | True | 0 |
| 2026-11-14 21:00:00 | 2026-11-14 21:05:00 | 30 | 25 |  | False | 30 |
| 2026-11-14 21:05:00 | 2026-11-14 21:10:00 | 22 | 19 |  | False | 22 |
| 2026-11-14 21:10:00 | 2026-11-14 21:15:00 | 10 | 9 |  | False | 10 |

_9 rows in total._

### Events delayed beyond the watermark

<!-- RESULTS: late_events -->

**late_events**

| event_time | kafka_time | ingestion_delay_s | title | imdb_id | match_type |
| --- | --- | --- | --- | --- | --- |
| 2026-11-14 20:24:42 | 2026-11-14 20:54:33.129000 | 1791 | Barry Martin | nm0551951 | imdb_person |
| 2026-11-14 20:24:49 | 2026-11-14 20:54:33.225000 | 1784 | Lorne Balfe | nm1154632 | imdb_person |
| 2026-11-14 20:25:05 | 2026-11-14 20:54:33.349000 | 1768 | Madagascar: Escape 2 Africa | tt0479952 | enriched_article |
| 2026-11-14 20:25:14 | 2026-11-14 20:54:33.430000 | 1759 | Johnny Vegas | nm0891943 | imdb_person |
| 2026-11-14 20:25:33 | 2026-11-14 20:54:33.671000 | 1740 | Gene Roddenberry | nm0734472 | imdb_person |
| 2026-11-14 20:25:35 | 2026-11-14 20:54:33.627000 | 1738 | Little Bear (TV series) | tt0245637 | imdb_title |
| 2026-11-14 20:25:42 | 2026-11-14 20:54:33.696000 | 1731 | Trace Lysette | nm6006903 | imdb_person |

_7 rows in total._

### Matched events

<!-- RESULTS: matched_events -->

**matched_events**

| event_time | title | imdb_id | entity_type | match_type | user | bytes_delta | delayed_beyond_watermark |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 2026-11-14 20:24:42 | Barry Martin | nm0551951 | person | imdb_person | Tassedethe | 95 | True |
| 2026-11-14 20:24:49 | Lorne Balfe | nm1154632 | person | imdb_person | ~2026-60385-34 | 12 | True |
| 2026-11-14 20:25:05 | Madagascar: Escape 2 Africa | tt0479952 | film | enriched_article | Suleeabc2 | -1 | True |
| 2026-11-14 20:25:14 | Johnny Vegas | nm0891943 | person | imdb_person | ~2026-52346-47 | 8 | True |
| 2026-11-14 20:25:33 | Gene Roddenberry | nm0734472 | person | imdb_person | Starst90 | 4 | True |
| 2026-11-14 20:25:35 | Little Bear (TV series) | tt0245637 | series | imdb_title | ~2026-59016-42 | 37 | True |
| 2026-11-14 20:25:42 | Trace Lysette | nm6006903 | person | imdb_person | ~2026-60386-51 | 1 | True |
| 2026-11-14 20:42:18 | Campbell Scott | nm0001714 | person | enriched_article | AnomieBOT | 19 | False |
| 2026-11-14 20:42:26 | Stephnie Weir | nm0918633 | person | imdb_person | Stonecold415 | 19 | False |
| 2026-11-14 20:42:35 | Stephnie Weir | nm0918633 | person | imdb_person | Stonecold415 | 6 | False |
| 2026-11-14 20:42:53 | Sharon Tate | nm0001790 | person | imdb_person | Nonojonyy | 7 | False |
| 2026-11-14 20:43:44 | Queen | nm1277102 | person | imdb_person | Bkonrad | 24 | False |
| 2026-11-14 20:43:57 | Queen | nm1277102 | person | imdb_person | Bkonrad | -1 | False |
| 2026-11-14 20:44:18 | The General's Daughter (film) | tt0144214 | film | imdb_title | ~2026-51475-41 | 7 | False |
| 2026-11-14 20:44:30 | Ice Cube | nm0001084 | person | enriched_article | AquaHeart3 | 11 | False |
| 2026-11-14 20:44:55 | Godzilla Minus Zero | tt34384661 | film | imdb_title | Eiga-Kevin2 | 0 | False |
| 2026-11-14 20:45:21 | Sharon Tate | nm0001790 | person | imdb_person | Celjski Grad | -7 | False |
| 2026-11-14 20:45:31 | Ice Cube | nm0001084 | person | enriched_article | AquaHeart3 | 4 | False |
| 2026-11-14 20:45:44 | Henry | nm11437554 | person | imdb_person | Bkonrad | -7 | False |
| 2026-11-14 20:46:51 | Belén Cuesta | nm3177382 | person | enriched_article | Asqueladd | 2 | False |
| 2026-11-14 20:47:00 | Cecil Kellaway | nm0445523 | person | imdb_person | RustyPeg | 81 | False |
| 2026-11-14 20:47:42 | Eddie George | nm1261984 | person | imdb_person | Erik255 | 0 | False |
| 2026-11-14 20:47:46 | Terry Pratchett | nm0695332 | person | imdb_person | InternetArchiveBot | 142 | False |
| 2026-11-14 20:47:56 | Elaine Hendrix | nm0005006 | person | enriched_article | Anightmareonelmstreet193 | -452 | False |
| 2026-11-14 20:48:00 | Kirk Franklin | nm0004938 | person | imdb_person | Hometown Kid | 41 | False |
| 2026-11-14 20:48:01 | Eddie George | nm1261984 | person | imdb_person | Erik255 | 0 | False |
| 2026-11-14 20:48:57 | Kirk Franklin | nm0004938 | person | imdb_person | Hometown Kid | 112 | False |
| 2026-11-14 20:49:20 | Kirk Franklin | nm0004938 | person | imdb_person | Hometown Kid | 4 | False |
| 2026-11-14 20:49:43 | Kirk Franklin | nm0004938 | person | imdb_person | Hometown Kid | 8 | False |
| 2026-11-14 20:50:16 | Chantal Akerman | nm0001901 | person | enriched_article | JhowieNitnek | 40 | False |

_139 rows in total, first 30 shown._

### Handling of late-arriving data

Our windows use the time of the edit on Wikipedia and not the time Spark
receives it. We used 5-minute windows and a 10-minute watermark, which means
Spark waits 10 minutes before closing a window. Normally events arrive in a
few seconds, so this is enough.

To test it, we sent again 3,000 events from 30 minutes earlier while the job
was running. Seven of them matched IMDb, and since they were too old, Spark
didn't add them to the windows (we can see it in the dropped rows metric).
We still kept them in `matched_events`, so the batch recount at the end finds
them again in the 20:20 and 20:25 windows. The last three windows are missing
for another reason: the job stopped before they could be closed.

### Methodological explanation

We used the Wikimedia `recentchange` feed, which sends every Wikipedia edit
live. A Python producer reads it and puts the events in a Kafka topic, with
Kafka running in Docker. Spark Structured Streaming then reads the topic,
keeps only article edits on English Wikipedia and compares the page title
with a table built from IMDb.

This table contains the article titles from the enrichment, the popular
films and series (5,000+ votes) written like Wikipedia titles ("Title
(film)", "Title (1995 film)"...) and the names of their cast and crew. When a
name could mean several people, we keep the most popular one. The results
go to three Parquet outputs: every matched edit, the edits per IMDb entity
per window, and the total traffic per window. In our 33-minute test, 139
edits matched 111 IMDb entities, so around 3 to 5 % of the edits.

## Open question

### Question, motivation and additional data

Our question is: have the most popular films become more international since
1980? In other words, are the people at the top of the cast more and more
often born outside the United States, and are these films rated or watched
differently?

We chose it because people often say Hollywood is more global now, with more
British or Australian actors and more foreign films getting a big audience,
and we wanted to see if the data agrees. IMDb doesn't say where people were
born, so we used Wikidata to get the birthplace of each person (P19) and its
country (P17). We kept the same films and people as in the enrichment part,
and we found the country for 88 % of them.

### Results

<!-- RESULTS: coverage -->

**coverage**

| scope | principals | known_country | born_abroad | pct_born_abroad | pct_known | no_wikidata_item | no_birth_country | ambiguous_country |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| all | 20431 | 18036 | 8620 | 47.80 | 88.30 | 1804 | 591 | 101 |

_1 rows in total._

<!-- RESULTS: trend_by_period, profiles_by_period -->

**trend_by_period**

| period | principals | known_country | born_abroad | pct_born_abroad | pct_known |
| --- | --- | --- | --- | --- | --- |
| 1980-1984 | 2087 | 1878 | 964 | 51.30 | 90.00 |
| 1985-1989 | 2120 | 1881 | 809 | 43.00 | 88.70 |
| 1990-1994 | 2191 | 1985 | 849 | 42.80 | 90.60 |
| 1995-1999 | 2106 | 1935 | 886 | 45.80 | 91.90 |
| 2000-2004 | 2162 | 1978 | 951 | 48.10 | 91.50 |
| 2005-2009 | 2164 | 1956 | 884 | 45.20 | 90.40 |
| 2010-2014 | 2410 | 2095 | 1063 | 50.70 | 86.90 |
| 2015-2019 | 2357 | 2011 | 1011 | 50.30 | 85.30 |
| 2020-2024 | 2375 | 1937 | 1009 | 52.10 | 81.60 |
| 2025-2025 | 459 | 380 | 194 | 51.10 | 82.80 |

_10 rows in total._

**profiles_by_period**

| period | us_only | mixed | abroad_only |
| --- | --- | --- | --- |
| 1980-1984 | 208 | 185 | 253 |
| 1985-1989 | 245 | 211 | 191 |
| 1990-1994 | 259 | 220 | 201 |
| 1995-1999 | 227 | 230 | 199 |
| 2000-2004 | 206 | 259 | 203 |
| 2005-2009 | 213 | 273 | 168 |
| 2010-2014 | 178 | 312 | 211 |
| 2015-2019 | 175 | 321 | 192 |
| 2020-2024 | 167 | 284 | 213 |
| 2025-2025 | 32 | 59 | 40 |

_10 rows in total._

<!-- RESULTS: by_genre -->

**by_genre**

| genre | known_country | pct_born_abroad | pct_1980s | pct_2016_2025 | change_pts |
| --- | --- | --- | --- | --- | --- |
| Thriller | 1338 | 37.20 | 29.00 | 51.90 | 22.90 |
| Crime | 1357 | 33.00 | 23.10 | 44.70 | 21.60 |
| Sci-Fi | 1330 | 38.10 | 27.80 | 48.90 | 21.10 |
| Comedy | 1358 | 27.80 | 21.20 | 41.90 | 20.70 |
| Drama | 1362 | 36.60 | 29.30 | 47.90 | 18.60 |
| Romance | 1356 | 35.50 | 27.70 | 45.50 | 17.80 |
| Fantasy | 1331 | 46.80 | 39.10 | 55.90 | 16.80 |
| Horror | 1318 | 36.40 | 27.50 | 44.20 | 16.70 |
| Action | 1364 | 40.20 | 32.50 | 48.30 | 15.80 |
| Sport | 1188 | 43.40 | 44.30 | 57.80 | 13.50 |
| War | 1164 | 73.20 | 67.00 | 80.10 | 13.10 |
| Mystery | 1330 | 37.00 | 32.30 | 43.20 | 10.90 |
| Adventure | 1370 | 41.40 | 39.00 | 46.60 | 7.60 |
| Music | 1227 | 45.60 | 43.10 | 48.40 | 5.30 |
| Family | 1310 | 43.00 | 49.10 | 54.30 | 5.20 |
| Biography | 1285 | 47.90 | 49.30 | 51.50 | 2.20 |
| Musical | 1234 | 78.10 | 70.30 | 66.80 | -3.50 |
| Documentary | 784 | 46.70 | 54.80 | 45.20 | -9.60 |
| History | 1233 | 68.90 | 71.80 | 60.10 | -11.70 |
| Western | 914 | 45.30 | 67.00 | 34.20 | -32.80 |
| Animation | 1295 | 49.70 | 72.90 | 36.50 | -36.40 |
| News | 134 | 46.30 | 100.00 | 47.50 | -52.50 |

_22 rows in total._

<!-- RESULTS: top_countries_by_decade -->

**top_countries_by_decade**

| decade | country_iso | country_label | people | rank |
| --- | --- | --- | --- | --- |
| 1980s | GB | United Kingdom | 241 | 1 |
| 1980s | JP | Japan | 113 | 2 |
| 1980s | FR | France | 98 | 3 |
| 1980s | IN | India | 86 | 4 |
| 1980s | IT | Italy | 75 | 5 |
| 1990s | GB | United Kingdom | 230 | 1 |
| 1990s | IN | India | 130 | 2 |
| 1990s | JP | Japan | 103 | 3 |
| 1990s | FR | France | 97 | 4 |
| 1990s | CA | Canada | 74 | 5 |
| 2000s | GB | United Kingdom | 275 | 1 |
| 2000s | IN | India | 122 | 2 |
| 2000s | FR | France | 90 | 3 |
| 2000s | CA | Canada | 74 | 4 |
| 2000s | JP | Japan | 74 | 5 |
| 2010s | GB | United Kingdom | 337 | 1 |
| 2010s | IN | India | 145 | 2 |
| 2010s | CA | Canada | 78 | 3 |
| 2010s | AU | Australia | 73 | 4 |
| 2010s | FR | France | 61 | 5 |
| 2020s | GB | United Kingdom | 259 | 1 |
| 2020s | IN | India | 161 | 2 |
| 2020s | CA | Canada | 56 | 3 |
| 2020s | AU | Australia | 32 | 4 |
| 2020s | DE | Germany | 32 | 5 |

_25 rows in total._

<!-- RESULTS: share_by_role, trend_actors_actresses -->

**share_by_role**

| role | principals | known_country | born_abroad | pct_born_abroad | pct_known |
| --- | --- | --- | --- | --- | --- |
| cast | 20006 | 17815 | 8522 | 47.80 | 89.00 |
| crew | 425 | 221 | 98 | 44.30 | 52.00 |

_2 rows in total._

**trend_actors_actresses**

| period | actors_pct_born_abroad | actresses_pct_born_abroad |
| --- | --- | --- |
| 1980-1984 | 51.70 | 49.90 |
| 1985-1989 | 43.40 | 40.40 |
| 1990-1994 | 41.60 | 43.80 |
| 1995-1999 | 45.20 | 47.00 |
| 2000-2004 | 48.30 | 50.10 |
| 2005-2009 | 45.80 | 44.80 |
| 2010-2014 | 51.40 | 50.20 |
| 2015-2019 | 49.20 | 53.20 |
| 2020-2024 | 54.70 | 49.30 |
| 2025-2025 | 53.80 | 44.40 |

_10 rows in total._

<!-- RESULTS: performance_by_profile -->

**performance_by_profile**

| profile | films | avg_rating | median_votes | rating_vs_year | log10_votes_vs_year |
| --- | --- | --- | --- | --- | --- |
| abroad_only | 1871 | 6.93 | 10233 | 0.28 | -0.44 |
| mixed | 2354 | 6.53 | 87021 | -0.12 | 0.23 |
| us_only | 1910 | 6.53 | 56098 | -0.12 | 0.14 |

_3 rows in total._

### Key takeaways

The answer is not a clear yes. In 1980-1984, 51 % of the people were already
born outside the US. This went down to about 43 % around 1990 and then came
back up to 50-52 % after 2010. What really changed is that films mix more:
films with both US-born and foreign-born people went from 29 % to 43 %, and
films with only Americans dropped from 32 % to 25 %.

The rise is clear in big genres like thriller, crime, sci-fi and comedy (about
+20 points), but animation, western and history went down. The UK is always
the first foreign country, and India is second from the 1990s. Films with
only foreign-born people get better ratings but about three times fewer
votes, while mixed films get the most votes. One limit is that born abroad
doesn't always mean a foreigner in an American film, since the sample also
has Indian or Japanese films. Also, people from recent films are less often
found in Wikidata.

### Methodological explanation

We joined the selected films, their first three people and the countries
from Wikidata in Spark. When a place had several countries (for example a
city in the USSR that is now in Ukraine), we took the current one. A person
is "born abroad" if the country is not the US, and people with no known
country are left out of the percentages.

We then computed the share of people born abroad per 5-year period, per
genre (1980s against 2016-2025), for actors and actresses, and the main
foreign countries per decade. For the ratings part, each film is labelled
US only, mixed or abroad only. Since recent films have more votes and more
foreign actors at the same time, we compared each film to the average of its
own year before comparing the groups.

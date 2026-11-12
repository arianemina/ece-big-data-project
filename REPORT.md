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

TODO (written by the team)

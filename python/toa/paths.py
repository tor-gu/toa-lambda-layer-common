NAMES_UNPROCESSED_PREFIX = "names/unprocessed/"
NAMES_PROCESSED_PREFIX = "names/processed/"
NAMES_CONSOLIDATED_KEY = "names/consolidated/names.parquet"

RESULTS_UNPROCESSED_PREFIX = "results/unprocessed/"
RESULTS_PROCESSED_PREFIX = "results/processed/"
# The redacted view, rebuilt in full on every consolidator run. Downstream steps read
# this one; the unredacted file below is the incrementally-built source of truth.
RESULTS_CONSOLIDATED_KEY = "results/consolidated/results.parquet"
RESULTS_UNREDACTED_KEY = "results/consolidated/unredacted_results.parquet"

REDACTIONS_UNPROCESSED_PREFIX = "redactions/unprocessed/"
REDACTIONS_PROCESSED_PREFIX = "redactions/processed/"
REDACTIONS_CONSOLIDATED_KEY = "redactions/consolidated/redactions.parquet"

SCORES_KEY = "scores/scores.parquet"
ENRICHED_SCORES_KEY = "scores/enriched_scores.parquet"

GLOBAL_STATISTICS_KEY = "statistics/global_statistics.parquet"

VIZ_DATES_KEY = "viz/dates.parquet"
VIZ_ALBUMS_KEY = "viz/albums.parquet"
VIZ_MATCHES_KEY = "viz/matches.parquet"

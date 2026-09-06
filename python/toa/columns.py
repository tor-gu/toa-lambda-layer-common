class NamesCol:
    ID = "id"
    ARTIST = "artist"
    ALBUM = "album"
    SHORT_NAME = "short-name"


class ResultsCol:
    MATCH_ID = "match_id"
    DATE = "date"
    ORDER = "order"


class RedactionsCol:
    ID = "id"
    ARTIST = "artist"
    ALBUM = "album"


class ScoresCol:
    ID = "id"
    SCORE = "score"
    ROBUSTNESS = "robustness"
    DATE = "date"
    RANK = "rank"
    IS_NEW = "is_new"
    SCORE_DELTA = "score_delta"
    RANK_DELTA = "rank_delta"


class VizCol:
    ID = "id"
    DEBUT = "debut"
    SCORES = "scores"
    MATCH_IDS = "match_ids"
    MATCH_ID = "match_id"
    DATE = "date"
    ORDER = "order"


class StatisticsCol:
    EARLIEST_MATCH = "earliest_match"
    LATEST_MATCH = "latest_match"
    MIN_SCORE = "min_score"
    MAX_SCORE = "max_score"
    NUM_ALBUMS = "num_albums"
    NUM_MATCHES = "num_matches"

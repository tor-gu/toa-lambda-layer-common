"""Star ratings derived from scores.

The mapping is fixed by the model's prior distribution, N(0, sd). Ratings run 
from 0 to 5 in half-star steps:

- a score of 0 sits at the midpoint of the 3.5-star bin, and
- 5 stars starts at the prior's 95th percentile, so the top 5% under the prior
  get 5 stars.

Let Z95 be the the 95th percentile of the standard normal distribution. Then
each half-star bin is 0.4 * Z95 * sd wide (about 0.658 * sd).
"""

import math
import os
from statistics import NormalDist

# The 95th percentile of the standard normal, about 1.6449.
Z95 = NormalDist().inv_cdf(0.95)

MIN_STARS = 0.0
MAX_STARS = 5.0

_TRUE = {"true", "1"}
_FALSE = {"false", "0"}


def star_rating(score: float, sd: float, truncate: bool = True) -> float:
    """The half-star rating for `score` under a N(0, `sd`) prior.

    In half-star units the continuous rating is 7.5 + 2.5 * score / (Z95 * sd):
    7.5 is the centre of the 3.5-star bin [7, 8), and score = Z95 * sd lands on
    10, the start of 5 stars. Flooring picks the bin. With `truncate`, the
    result is clamped to [0, 5]; without it, ratings above 5 or below 0 pass
    through in the same half-star steps.
    """
    stars = math.floor(7.5 + 2.5 * float(score) / (Z95 * sd)) / 2
    if truncate:
        stars = min(max(stars, MIN_STARS), MAX_STARS)
    return stars


def stars_config_from_env() -> tuple[float, bool]:
    """(sd, truncate) from the `SD` and `TRUNCATE_STARS` environment variables.

    `SD` is required. `TRUNCATE_STARS` defaults to true and accepts
    true/false/1/0, case-insensitively; anything else raises.
    """
    sd = float(os.environ["SD"])
    raw = os.environ.get("TRUNCATE_STARS", "true").strip().lower()
    if raw in _TRUE:
        return sd, True
    if raw in _FALSE:
        return sd, False
    raise ValueError(f"TRUNCATE_STARS must be true/false/1/0, got {raw!r}")

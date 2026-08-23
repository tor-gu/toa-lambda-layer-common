import pytest
from toa.dynamodb import batch_get_all

TABLE = "scores"


class FakeResource:
    """Stands in for a boto3 DynamoDB service resource.

    Hands back `responses` in order and records every RequestItems it was
    called with, so a test can assert on the chunking as well as the result.
    """

    def __init__(self, responses):
        self.responses = list(responses)
        self.requests = []

    def batch_get_item(self, RequestItems):  # noqa: N803 — boto3's spelling
        self.requests.append(RequestItems)
        return self.responses.pop(0)


def keys(*ids, date="2024-01-01"):
    return [{"id": album_id, "date": date} for album_id in ids]


def response(*ids, unprocessed=(), date="2024-01-01"):
    resp = {
        "Responses": {TABLE: [{"id": album_id, "score": 1.0} for album_id in ids]},
        "UnprocessedKeys": {},
    }
    if unprocessed:
        resp["UnprocessedKeys"] = {TABLE: {"Keys": keys(*unprocessed, date=date)}}
    return resp


@pytest.fixture(autouse=True)
def no_sleep(monkeypatch):
    """The backoff is real time; the tests should not pay for it."""
    monkeypatch.setattr("toa.dynamodb.time.sleep", lambda _seconds: None)


# ── the ordinary path ────────────────────────────────────────────────────────


def test_single_chunk_one_call():
    resource = FakeResource([response("a", "b", "c")])
    items = batch_get_all(resource, TABLE, keys("a", "b", "c"))

    assert [item["id"] for item in items] == ["a", "b", "c"]
    assert len(resource.requests) == 1
    assert resource.requests[0] == {TABLE: {"Keys": keys("a", "b", "c")}}


def test_empty_keys_makes_no_call():
    resource = FakeResource([])
    assert batch_get_all(resource, TABLE, []) == []
    assert resource.requests == []


def test_missing_item_is_simply_absent():
    # DynamoDB does not error on a key with no item; it just returns fewer.
    resource = FakeResource([response("a")])
    items = batch_get_all(resource, TABLE, keys("a", "gone"))
    assert [item["id"] for item in items] == ["a"]


# ── chunking at the 100-key cap ──────────────────────────────────────────────


def test_101_keys_split_into_two_calls():
    ids = [f"album{i:03d}" for i in range(101)]
    resource = FakeResource([response(*ids[:100]), response(*ids[100:])])

    items = batch_get_all(resource, TABLE, keys(*ids))

    assert len(items) == 101
    assert len(resource.requests) == 2
    assert len(resource.requests[0][TABLE]["Keys"]) == 100
    assert len(resource.requests[1][TABLE]["Keys"]) == 1


def test_exactly_100_keys_is_one_call():
    ids = [f"album{i:03d}" for i in range(100)]
    resource = FakeResource([response(*ids)])
    batch_get_all(resource, TABLE, keys(*ids))
    assert len(resource.requests) == 1


# ── UnprocessedKeys ──────────────────────────────────────────────────────────


def test_unprocessed_keys_are_resubmitted():
    resource = FakeResource([response("a", unprocessed=["b"]), response("b")])

    items = batch_get_all(resource, TABLE, keys("a", "b"))

    assert sorted(item["id"] for item in items) == ["a", "b"]
    assert len(resource.requests) == 2
    # The retry asks for the leftovers only, not the whole chunk again.
    assert resource.requests[1] == {TABLE: {"Keys": keys("b")}}


def test_gives_up_after_max_attempts():
    # A throttled table can hand the same keys back forever.
    stubborn = [response(unprocessed=["b"]) for _ in range(3)]
    resource = FakeResource(stubborn)

    with pytest.raises(RuntimeError, match="1 key"):
        batch_get_all(resource, TABLE, keys("a", "b"), max_attempts=3)

    assert len(resource.requests) == 3


def test_partial_results_survive_the_retry():
    resource = FakeResource(
        [
            response("a", unprocessed=["b", "c"]),
            response("b", unprocessed=["c"]),
            response("c"),
        ]
    )
    items = batch_get_all(resource, TABLE, keys("a", "b", "c"))
    assert sorted(item["id"] for item in items) == ["a", "b", "c"]

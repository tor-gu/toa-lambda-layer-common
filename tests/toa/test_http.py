import json
from datetime import date
from decimal import Decimal

import pytest
from toa.http import (
    ATOM_CONTENT_TYPE,
    CORS_HEADERS,
    JSON_CONTENT_TYPE,
    atom_response,
    json_response,
)

FEED_XML = (
    '<?xml version="1.0" encoding="utf-8"?><feed><entry>é &amp; ok</entry></feed>'
)


def make_body():
    return {"matches": [{"match_id": "a1b2c3d4", "date": "2024-03-15"}]}


# ── content types ────────────────────────────────────────────────────────────


def test_json_response_content_type():
    assert json_response(200, make_body())["headers"]["Content-Type"] == (
        JSON_CONTENT_TYPE
    )


def test_atom_response_content_type():
    # The charset matters here: Atom bodies carry non-ASCII album titles.
    headers = atom_response(200, FEED_XML)["headers"]
    assert headers["Content-Type"] == ATOM_CONTENT_TYPE
    assert "charset=utf-8" in headers["Content-Type"]


# ── CORS headers ─────────────────────────────────────────────────────────────


@pytest.mark.parametrize(
    "resp",
    [json_response(200, {"a": 1}), atom_response(200, "<feed/>")],
    ids=["json", "atom"],
)
def test_cors_headers_present(resp):
    assert resp["headers"]["Access-Control-Allow-Origin"] == "*"
    assert resp["headers"]["Access-Control-Allow-Methods"] == "GET,OPTIONS"
    assert resp["headers"]["Access-Control-Allow-Headers"] == "content-type"


def test_both_wrappers_share_one_cors_block():
    json_headers = json_response(200, {})["headers"]
    atom_headers = atom_response(200, "")["headers"]
    assert {
        k: v for k, v in json_headers.items() if k != "Content-Type"
    } == CORS_HEADERS
    assert {
        k: v for k, v in atom_headers.items() if k != "Content-Type"
    } == CORS_HEADERS


# ── bodies ───────────────────────────────────────────────────────────────────


def test_json_response_serializes_body():
    assert json.loads(json_response(200, make_body())["body"]) == make_body()


def test_json_response_falls_back_to_str_for_unserializable():
    # get-results relies on this: Decimals that escape conversion become quoted
    # strings rather than raising at response time.
    body = json.loads(
        json_response(200, {"n": Decimal("0.5"), "d": date(2024, 3, 15)})["body"]
    )
    assert body == {"n": "0.5", "d": "2024-03-15"}


def test_atom_response_passes_body_through_verbatim():
    # Already-rendered XML: no JSON encoding and no second round of escaping.
    assert atom_response(200, FEED_XML)["body"] == FEED_XML


def test_atom_response_does_not_touch_entities():
    assert atom_response(200, "<error>a &amp; b</error>")["body"] == (
        "<error>a &amp; b</error>"
    )


# ── status codes ─────────────────────────────────────────────────────────────


@pytest.mark.parametrize("status_code", [200, 400, 404, 500])
def test_status_code_is_echoed(status_code):
    assert json_response(status_code, {})["statusCode"] == status_code
    assert atom_response(status_code, "")["statusCode"] == status_code


# ── header isolation ─────────────────────────────────────────────────────────


def test_headers_are_not_shared_between_responses():
    # A shared module-level dict would let one handler's mutation leak into
    # every response that followed, for the life of the execution environment.
    first = json_response(200, {})
    first["headers"]["Access-Control-Allow-Origin"] = "https://evil.example"
    assert json_response(200, {})["headers"]["Access-Control-Allow-Origin"] == "*"


def test_mutating_a_response_does_not_touch_the_cors_constant():
    atom_response(200, "")["headers"]["Access-Control-Allow-Methods"] = "DELETE"
    assert CORS_HEADERS["Access-Control-Allow-Methods"] == "GET,OPTIONS"

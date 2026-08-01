import json

CORS_HEADERS = {
    "Access-Control-Allow-Origin": "*",
    "Access-Control-Allow-Methods": "GET,OPTIONS",
    "Access-Control-Allow-Headers": "content-type",
}

JSON_CONTENT_TYPE = "application/json"
ATOM_CONTENT_TYPE = "application/atom+xml; charset=utf-8"


def _response(status_code: int, body: str, content_type: str) -> dict:
    # Fresh headers dict per call, so a caller that mutates one response's
    # headers cannot affect every response that follows.
    return {
        "statusCode": status_code,
        "headers": {"Content-Type": content_type, **CORS_HEADERS},
        "body": body,
    }


def json_response(status_code: int, body: dict) -> dict:
    """API Gateway response with a JSON body and the standard CORS headers."""
    return _response(status_code, json.dumps(body, default=str), JSON_CONTENT_TYPE)


def atom_response(status_code: int, body: str) -> dict:
    """API Gateway response for an already-rendered Atom document."""
    return _response(status_code, body, ATOM_CONTENT_TYPE)

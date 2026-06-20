import json


_HEADERS = {
    "Content-Type": "application/json",
    "Access-Control-Allow-Origin": "*",
    "Access-Control-Allow-Methods": "GET,OPTIONS",
    "Access-Control-Allow-Headers": "content-type",
}


def response(status_code: int, body: dict) -> dict:
    return {
        "statusCode": status_code,
        "headers": _HEADERS,
        "body": json.dumps(body, default=str),
    }

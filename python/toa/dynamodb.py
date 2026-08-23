import time

# BatchGetItem's hard cap on keys per request.
BATCH_GET_MAX_KEYS = 100

# Base for the exponential backoff between UnprocessedKeys retries (in seconds).
BATCH_GET_BACKOFF_BASE = 0.03


def query_all(table, **kwargs):
    items = []
    while True:
        resp = table.query(**kwargs)
        items.extend(resp["Items"])
        if "LastEvaluatedKey" not in resp:
            break
        kwargs["ExclusiveStartKey"] = resp["LastEvaluatedKey"]
    return items


def batch_get_all(dynamodb, table_name, keys, max_attempts=3):
    """Every item in `keys`, fetched from `table_name` by full primary key.

    Results are unordered.

    Implementation note: There are two loops here:
    1. The outer loop is batching, because of BatchGetItems's hard limit
    of 100 keys at a time.
    2. The inner loop is retries-with-backoff, because BatchGetItems can return partial
    results.
    """
    items = []
    # Outer loop -- batching
    for start in range(0, len(keys), BATCH_GET_MAX_KEYS):
        request = {table_name: {"Keys": keys[start : start + BATCH_GET_MAX_KEYS]}}
        # Inner loop -- retry with backoff
        for attempt in range(max_attempts):
            resp = dynamodb.batch_get_item(RequestItems=request)
            items.extend(resp["Responses"].get(table_name, []))
            request = resp.get("UnprocessedKeys")
            if not request:
                break
            time.sleep(2**attempt * BATCH_GET_BACKOFF_BASE)
        else:
            # We weren't able to finish this batch. Raise.
            leftover = len(request[table_name]["Keys"])
            raise RuntimeError(
                f"batch_get_all gave up on {table_name}: {leftover} key(s) still "
                f"unprocessed after {max_attempts} attempts"
            )
    return items

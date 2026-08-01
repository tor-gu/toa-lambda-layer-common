# toa-lambda-layer-common

Shared Python layer for every Lambda in the Tournament of Albums backend — both the
[pipeline](https://github.com/tor-gu/toa-data-pipeline) Lambdas and the
[API](https://github.com/tor-gu/toa-api) Lambdas. `python/` is zipped as-is, so the
modules import as `toa.*`.

## Modules

| Module | Contents |
|---|---|
| `toa.logging` | `get_logger(name=, domain=)` and the `Domain` enum |
| `toa.columns` | column name constants: `NamesCol`, `ResultsCol`, `ScoresCol`, `VizCol`, `StatisticsCol` |
| `toa.paths` | S3 keys and prefixes for every Parquet file |
| `toa.http` | `json_response(status_code, body)` and `atom_response(status_code, body)` — the standard CORS headers plus the matching `Content-Type`. `response` is a deprecated alias for `json_response` |
| `toa.dynamodb` | `query_all(table, **kwargs)` — runs a query to completion across pages |

`atom_response` takes an already-rendered XML string and passes it through untouched;
`json_response` serializes its dict body with `default=str`, so values that aren't natively
JSON-serializable (`Decimal`, `date`) become quoted strings rather than raising.

## Testing

`make test` runs the suite in `tests/`, `make lint` runs black/isort/flake8, and `make check`
runs both — the same targets as `toa-api` and `toa-data-pipeline`. Tests import the layer's
modules as `toa.*` via the `pythonpath` in `pyproject.toml`.

## Building

`make build` rebuilds `common.zip` from `python/`, excluding bytecode caches. The zip is
gitignored rather than checked in. Execute the rebuild step before deploying with terraform.



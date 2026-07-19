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
| `toa.http` | `response(status_code, body)` — JSON body plus the standard CORS headers |
| `toa.dynamodb` | `query_all(table, **kwargs)` — runs a query to completion across pages |

## Building

`make build` rebuilds `common.zip`. The zip is gitignored rather than checked in. Execute the rebuild step before deploying with terraform.



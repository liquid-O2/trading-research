> ## Documentation Index
> Fetch the complete documentation index at: https://docs.skylit.ai/llms.txt
> Use this file to discover all available pages before exploring further.

# Datafeed configuration

> The static UDF `DatafeedConfiguration` — supported resolutions,
exchanges, symbol types, and feature flags. Free.

Also carries **`max_fetch_trading_days`**: the `/v1/history`
request-window cap, keyed by every advertised resolution. Read it once
at startup and size your history pages from it, rather than hardcoding a
window that later drifts — or discovering the limit by being rejected,
which costs a credit each time. This call is free precisely so the limit
is knowable in advance.

The values are served from the same table the server enforces, so they
cannot disagree with it. A charting client can ignore the field: it is
not part of the UDF spec, and TradingView skips config keys it does not
recognise.

⚠ Cached for an hour (`max-age=3600`), so treat a `400` naming a
`max_days` SMALLER than your cached value as authoritative and re-read
this endpoint.




## OpenAPI

````yaml /atlas-openapi.yaml get /v1/config
openapi: 3.1.0
info:
  title: Atlas Public API
  version: 1.0.0
  summary: OHLCV price history as a TradingView-UDF datafeed.
  description: >
    Atlas exposes Skylit's real-time and historical **OHLCV** (open / high / low

    / close / volume) price bars as a versioned public HTTP API that implements

    the TradingView **UDF** (Universal Data Feed) datafeed contract. Point a

    TradingView Charting Library datafeed at `https://atlas-api.skylit.ai/v1`,
    or

    call the endpoints directly.


    **Authentication.** Send your Skylit API key as a bearer token:

        Authorization: Bearer <key>

    (`X-API-Key: <key>` is also accepted.) One Skylit key spans every product —

    the same key and credit balance work for Heatseeker and Flowseeker.


    **Credit metering.** Each chargeable request debits a fixed cost from your

    balance:


    | Endpoint       | Cost |

    |----------------|-----:|

    | `/v1/history`  | 1    |

    | `/v1/search`   | 1    |

    | `/v1/symbols`  | 1    |

    | `/v1/config`   | 0    |

    | `/v1/time`     | 0    |


    New customers are seeded with 5,000 credits. Every chargeable response

    carries `X-Credits-Remaining: <balance>`. Out of credits → `402`

    `insufficient_credits`; an admin-suspended account → `403`

    `account_suspended`. `/v1/config` and `/v1/time` are free metadata calls.


    Note that a charting client fetches `/v1/history` in **pages** (it walks the

    `to` cursor backward to fill the requested range), so a deep history pull

    naturally costs one credit per page — the cost scales with the data you

    actually retrieve.


    **Request-window limit.** One `/v1/history` call may span at most a fixed

    number of **trading days**, set by the bar tier the resolution reads from —

    not by the resolution itself. `240` and `60` share the 1-hour tier and

    therefore share its allowance.


    | Tier   | Resolutions                | Max trading days / request |

    |--------|----------------------------|---------------------------:|

    | 1-min  | `1` `2` `3` `5` `15` `30`  |                         90 |

    | 1-hour | `60` `240` `480`           |                        720 |

    | 1-day  | `D` `W`                    |                      2,600 |


    A window **wider than the cap is rejected with `400`**, carrying the two

    numbers a client needs to react (`requested_days`, `max_days`). It is never

    silently shortened — a short `{ "s": "ok" }` always means the data ends

    there, never that your range was clipped. Page through anything wider in

    windows of `max_days` or fewer.


    A rejected `400` still debits 1 credit, because metering happens before the

    request is inspected. The caps are fixed and published above, so check your

    range before sending it rather than discovering the limit by retrying — a

    client that retries a `400` unchanged burns credits without ever

    succeeding.


    **Rate limits.** A safety ceiling of 600 requests / minute is enforced by

    the Skylit gateway and surfaced via `X-RateLimit-Limit`,

    `X-RateLimit-Remaining`, and `X-RateLimit-Reset`. `429` includes

    `Retry-After`. This is runaway protection, not a quota — credit metering

    does the per-customer accounting.


    **The datafeed flow.** A UDF client calls `/v1/config` once for the feed's

    capabilities, `/v1/symbols` to resolve a ticker (price scale, session,

    supported resolutions), then `/v1/history` for the bars; `/v1/search` powers

    the symbol picker and `/v1/time` the server clock. History follows the UDF

    convention: a `200` with `{ "s": "ok", ... }` on success and `{ "s":

    "no_data" }` when the window has no bars (not a `404`); an over-wide range

    is a `400` with `{ "s": "error", "errmsg": ... }` plus `requested_days` and

    `max_days`. Auth and credit errors, which aren't part of UDF, use the

    envelope `{ "error": { "code": "...", "message": "..." } }`.
servers:
  - url: https://atlas-api.skylit.ai
    description: Production
security:
  - bearerApiKey: []
tags:
  - name: History
    description: OHLCV price bars.
  - name: Symbols
    description: Symbol search and resolution.
  - name: Meta
    description: Datafeed configuration and server time (free).
paths:
  /v1/config:
    get:
      tags:
        - Meta
      summary: Datafeed configuration
      description: |
        The static UDF `DatafeedConfiguration` — supported resolutions,
        exchanges, symbol types, and feature flags. Free.

        Also carries **`max_fetch_trading_days`**: the `/v1/history`
        request-window cap, keyed by every advertised resolution. Read it once
        at startup and size your history pages from it, rather than hardcoding a
        window that later drifts — or discovering the limit by being rejected,
        which costs a credit each time. This call is free precisely so the limit
        is knowable in advance.

        The values are served from the same table the server enforces, so they
        cannot disagree with it. A charting client can ignore the field: it is
        not part of the UDF spec, and TradingView skips config keys it does not
        recognise.

        ⚠ Cached for an hour (`max-age=3600`), so treat a `400` naming a
        `max_days` SMALLER than your cached value as authoritative and re-read
        this endpoint.
      operationId: getConfig
      responses:
        '200':
          description: Datafeed configuration.
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/DatafeedConfig'
              examples:
                config:
                  value:
                    supports_search: true
                    supports_group_request: false
                    supports_marks: false
                    supports_timescale_marks: false
                    supports_time: true
                    supported_resolutions:
                      - '1'
                      - '2'
                      - '3'
                      - '5'
                      - '15'
                      - '30'
                      - '60'
                      - '240'
                      - '480'
                      - D
                      - W
                    max_fetch_trading_days:
                      '1': 90
                      '2': 90
                      '3': 90
                      '5': 90
                      '15': 90
                      '30': 90
                      '60': 720
                      '240': 720
                      '480': 720
                      D: 2600
                      W: 2600
                    intraday_multipliers:
                      - '1'
                      - '60'
                    exchanges:
                      - value: NASDAQ
                        name: NASDAQ
                        desc: NASDAQ
                      - value: NYSE
                        name: NYSE
                        desc: NYSE
                      - value: ARCA
                        name: NYSE ARCA
                        desc: NYSE ARCA
                    symbols_types:
                      - name: stock
                        value: stock
                      - name: fund
                        value: fund
                      - name: dr
                        value: dr
                      - name: index
                        value: index
                      - name: futures
                        value: futures
        '401':
          $ref: '#/components/responses/Unauthorized'
components:
  schemas:
    DatafeedConfig:
      type: object
      properties:
        supports_search:
          type: boolean
        supports_group_request:
          type: boolean
        supports_marks:
          type: boolean
        supports_timescale_marks:
          type: boolean
        supports_time:
          type: boolean
        supported_resolutions:
          type: array
          items:
            type: string
        max_fetch_trading_days:
          type: object
          description: |
            Max trading days one `/v1/history` request may span, keyed by
            resolution. Resolutions sharing a bar tier share a value — `60`,
            `240` and `480` all read hourly bars and all cap at 720.
          additionalProperties:
            type: integer
          example:
            '1': 90
            '60': 720
            '240': 720
            D: 2600
        intraday_multipliers:
          type: array
          items:
            type: string
        exchanges:
          type: array
          items:
            type: object
            properties:
              value:
                type: string
              name:
                type: string
              desc:
                type: string
        symbols_types:
          type: array
          items:
            type: object
            properties:
              name:
                type: string
              value:
                type: string
    Error:
      type: object
      required:
        - error
      properties:
        error:
          type: object
          required:
            - code
            - message
          properties:
            code:
              type: string
              description: Stable machine-readable code.
              example: insufficient_credits
            message:
              type: string
  responses:
    Unauthorized:
      description: Missing or invalid API key.
      content:
        application/json:
          schema:
            $ref: '#/components/schemas/Error'
  securitySchemes:
    bearerApiKey:
      type: http
      scheme: bearer
      description: |
        Skylit API key in the `Authorization` header
        (`Authorization: Bearer <key>`). `X-API-Key` is also accepted. The same
        key works across Atlas, Heatseeker, and Flowseeker.

````
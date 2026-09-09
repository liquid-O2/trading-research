> ## Documentation Index
> Fetch the complete documentation index at: https://docs.skylit.ai/llms.txt
> Use this file to discover all available pages before exploring further.

# OHLCV price bars for a symbol and resolution

> TradingView UDF history bars for one `symbol` at one `resolution`,
covering `[from, to)` (Unix seconds; `to` is exclusive). Returns column arrays (`t`, `o`,
`h`, `l`, `c`, `v`) of equal length, oldest-first. When the window
holds no bars the response is a `200` with `{ "s": "no_data" }` (plus
`nextTime` pointing at the nearest earlier bar when one exists), per the
UDF contract. Equity bars also carry sided-volume columns (`bv`/`sv`/`uv`
= buy / sell / unclassified) where available.

## Request-window limit

One call may span at most a fixed number of **trading days**, set by the
bar tier the resolution reads from — not by the resolution itself. `240`
and `60` share the 1-hour tier and therefore share its allowance.

| Tier   | Resolutions                | Max trading days / request |
|--------|----------------------------|---------------------------:|
| 1-min  | `1` `2` `3` `5` `15` `30`  |                         90 |
| 1-hour | `60` `240` `480`           |                        720 |
| 1-day  | `D` `W`                    |                      2,600 |

A window **wider than the cap is rejected with `400`**, carrying the two
numbers a client needs to react (`requested_days`, `max_days`). It is
never silently shortened — a short `{ "s": "ok" }` always means the data
ends there, never that your range was clipped. Page through anything
wider in windows of `max_days` or fewer.

A rejected `400` **still debits 1 credit**, because metering happens
before the request is inspected. The caps are fixed and published here,
so check your range before sending it rather than discovering the limit
by retrying — a client that retries a `400` unchanged burns credits
without ever succeeding. `/v1/config` is free if you would rather read
the feed's capabilities first.

Cache-Control tracks data freshness: today `max-age=2`, the prior
session `max-age=60`, older complete days `immutable`. A `400` is
`no-store`.




## OpenAPI

````yaml /atlas-openapi.yaml get /v1/history
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
  /v1/history:
    get:
      tags:
        - History
      summary: OHLCV price bars for a symbol and resolution
      description: >
        TradingView UDF history bars for one `symbol` at one `resolution`,

        covering `[from, to)` (Unix seconds; `to` is exclusive). Returns column
        arrays (`t`, `o`,

        `h`, `l`, `c`, `v`) of equal length, oldest-first. When the window

        holds no bars the response is a `200` with `{ "s": "no_data" }` (plus

        `nextTime` pointing at the nearest earlier bar when one exists), per the

        UDF contract. Equity bars also carry sided-volume columns
        (`bv`/`sv`/`uv`

        = buy / sell / unclassified) where available.


        ## Request-window limit


        One call may span at most a fixed number of **trading days**, set by the

        bar tier the resolution reads from — not by the resolution itself. `240`

        and `60` share the 1-hour tier and therefore share its allowance.


        | Tier   | Resolutions                | Max trading days / request |

        |--------|----------------------------|---------------------------:|

        | 1-min  | `1` `2` `3` `5` `15` `30`  |                         90 |

        | 1-hour | `60` `240` `480`           |                        720 |

        | 1-day  | `D` `W`                    |                      2,600 |


        A window **wider than the cap is rejected with `400`**, carrying the two

        numbers a client needs to react (`requested_days`, `max_days`). It is

        never silently shortened — a short `{ "s": "ok" }` always means the data

        ends there, never that your range was clipped. Page through anything

        wider in windows of `max_days` or fewer.


        A rejected `400` **still debits 1 credit**, because metering happens

        before the request is inspected. The caps are fixed and published here,

        so check your range before sending it rather than discovering the limit

        by retrying — a client that retries a `400` unchanged burns credits

        without ever succeeding. `/v1/config` is free if you would rather read

        the feed's capabilities first.


        Cache-Control tracks data freshness: today `max-age=2`, the prior

        session `max-age=60`, older complete days `immutable`. A `400` is

        `no-store`.
      operationId: getHistory
      parameters:
        - $ref: '#/components/parameters/Symbol'
        - name: resolution
          in: query
          required: true
          description: Bar size. Intraday minutes or `D`/`W`.
          schema:
            type: string
            enum:
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
            example: D
        - name: from
          in: query
          required: true
          description: Window start, Unix seconds (UTC).
          schema:
            type: integer
            format: int64
            example: 1748131200
        - name: to
          in: query
          required: true
          description: Window end, Unix seconds (UTC).
          schema:
            type: integer
            format: int64
            example: 1748736000
        - name: countback
          in: query
          required: false
          description: |
            When set, return exactly this many bars ending at `to` (takes
            precedence over `from`, per the UDF spec).
          schema:
            type: integer
            minimum: 1
        - name: extended
          in: query
          required: false
          description: |
            Include extended-hours (pre / post-market) bars. Default is regular
            trading hours only (09:30–16:00 ET).
          schema:
            type: boolean
            default: false
      responses:
        '200':
          description: Bars, or a `no_data` marker — both `200` per UDF.
          headers:
            X-Credits-Remaining:
              $ref: '#/components/headers/CreditsRemaining'
            Cache-Control:
              schema:
                type: string
                example: public, max-age=2
            X-RateLimit-Limit:
              schema:
                type: integer
            X-RateLimit-Remaining:
              schema:
                type: integer
            X-RateLimit-Reset:
              schema:
                type: integer
          content:
            application/json:
              schema:
                oneOf:
                  - $ref: '#/components/schemas/HistoryOk'
                  - $ref: '#/components/schemas/HistoryNoData'
              examples:
                ok:
                  summary: SPY daily (truncated)
                  value:
                    s: ok
                    t:
                      - 1748304000
                      - 1748390400
                      - 1748476800
                    o:
                      - 742.1
                      - 744.02
                      - 733.9
                    h:
                      - 750.18
                      - 745.61
                      - 739.94
                    l:
                      - 741.55
                      - 732.88
                      - 731.2
                    c:
                      - 744.38
                      - 733.68
                      - 733.05
                    v:
                      - 61230400
                      - 74910200
                      - 58120900
                noData:
                  summary: Empty window
                  value:
                    s: no_data
                    nextTime: 1746057600
        '400':
          description: |
            The requested range is wider than the resolution's tier allows.
            Debits 1 credit like any other metered request.
          headers:
            X-Credits-Remaining:
              $ref: '#/components/headers/CreditsRemaining'
            Cache-Control:
              schema:
                type: string
                example: no-store
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/HistoryError'
              examples:
                rangeTooWide:
                  summary: 171 trading days asked of the 90-day 1-minute tier
                  value:
                    s: error
                    errmsg: >-
                      requested range spans 171 trading days; resolution "1"
                      allows at most 90 per request. Narrow the range, or page
                      through it in windows of 90 trading days or fewer.
                    requested_days: 171
                    max_days: 90
        '401':
          $ref: '#/components/responses/Unauthorized'
        '402':
          $ref: '#/components/responses/InsufficientCredits'
        '403':
          $ref: '#/components/responses/AccountSuspended'
        '429':
          $ref: '#/components/responses/RateLimited'
        '503':
          $ref: '#/components/responses/Unavailable'
components:
  parameters:
    Symbol:
      name: symbol
      in: query
      required: true
      description: Ticker (e.g. `SPY`).
      schema:
        type: string
        example: SPY
  headers:
    CreditsRemaining:
      description: Credit balance remaining after this request was debited.
      schema:
        type: integer
        example: 4999
  schemas:
    HistoryOk:
      type: object
      required:
        - s
        - t
        - o
        - h
        - l
        - c
        - v
      properties:
        s:
          type: string
          enum:
            - ok
          description: Status flag.
        t:
          type: array
          description: Bar open times, Unix seconds (UTC), oldest-first.
          items:
            type: integer
            format: int64
        o:
          type: array
          description: Opens.
          items:
            type: number
        h:
          type: array
          description: Highs.
          items:
            type: number
        l:
          type: array
          description: Lows.
          items:
            type: number
        c:
          type: array
          description: Closes.
          items:
            type: number
        v:
          type: array
          description: Volumes.
          items:
            type: number
        bv:
          type: array
          description: Buy (aggressor) volume per bar, equities where available.
          items:
            type: number
        sv:
          type: array
          description: Sell (aggressor) volume per bar.
          items:
            type: number
        uv:
          type: array
          description: Unclassified volume per bar.
          items:
            type: number
    HistoryNoData:
      type: object
      required:
        - s
      properties:
        s:
          type: string
          enum:
            - no_data
        nextTime:
          type: integer
          format: int64
          description: Unix seconds of the nearest earlier bar, when one exists.
    HistoryError:
      type: object
      description: >
        UDF-shaped error body for a rejected `/v1/history` request. `errmsg` is

        the human-readable text a TradingView datafeed surfaces;
        `requested_days`

        and `max_days` are additive fields for programmatic callers, which are

        the ones that have to react — compute your page size from `max_days`

        rather than hardcoding a cap that later drifts.
      required:
        - s
        - errmsg
      properties:
        s:
          type: string
          enum:
            - error
        errmsg:
          type: string
        requested_days:
          type: integer
          description: Trading days the requested window spans.
        max_days:
          type: integer
          description: Trading days one request may span at this resolution's tier.
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
    InsufficientCredits:
      description: Credit balance is below the request cost.
      headers:
        X-Credits-Remaining:
          $ref: '#/components/headers/CreditsRemaining'
      content:
        application/json:
          schema:
            $ref: '#/components/schemas/Error'
          examples:
            outOfCredits:
              value:
                error:
                  code: insufficient_credits
                  message: Out of credits.
    AccountSuspended:
      description: Account is not API-eligible (suspended).
      content:
        application/json:
          schema:
            $ref: '#/components/schemas/Error'
          examples:
            suspended:
              value:
                error:
                  code: account_suspended
                  message: Account suspended.
    RateLimited:
      description: Per-minute rate limit exceeded.
      headers:
        Retry-After:
          schema:
            type: integer
      content:
        application/json:
          schema:
            $ref: '#/components/schemas/Error'
    Unavailable:
      description: The credit ledger or datafeed is temporarily unavailable.
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
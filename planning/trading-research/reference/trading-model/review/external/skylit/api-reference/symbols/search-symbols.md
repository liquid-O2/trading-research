> ## Documentation Index
> Fetch the complete documentation index at: https://docs.skylit.ai/llms.txt
> Use this file to discover all available pages before exploring further.

# Search symbols

> Ranked symbol search for the datafeed's symbol picker (exact ticker >
prefix > substring). Returns up to `limit` matches.




## OpenAPI

````yaml /atlas-openapi.yaml get /v1/search
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
  /v1/search:
    get:
      tags:
        - Symbols
      summary: Search symbols
      description: |
        Ranked symbol search for the datafeed's symbol picker (exact ticker >
        prefix > substring). Returns up to `limit` matches.
      operationId: searchSymbols
      parameters:
        - name: query
          in: query
          required: true
          description: Search text (ticker or name fragment).
          schema:
            type: string
            example: SP
        - name: limit
          in: query
          required: false
          description: Max results.
          schema:
            type: integer
            default: 25
            minimum: 1
            maximum: 500
      responses:
        '200':
          description: Matching symbols.
          headers:
            X-Credits-Remaining:
              $ref: '#/components/headers/CreditsRemaining'
            Cache-Control:
              schema:
                type: string
                example: public, max-age=300, stale-while-revalidate=60
          content:
            application/json:
              schema:
                type: array
                items:
                  $ref: '#/components/schemas/SearchResult'
              examples:
                spy:
                  value:
                    - symbol: SPY
                      ticker: SPY
                      description: SPDR S&P 500 ETF Trust
                      exchange: ARCA
                      type: etf
                    - symbol: SPX
                      ticker: SPX
                      description: S&P 500 Index
                      exchange: NASDAQ
                      type: index
        '401':
          $ref: '#/components/responses/Unauthorized'
        '402':
          $ref: '#/components/responses/InsufficientCredits'
        '403':
          $ref: '#/components/responses/AccountSuspended'
        '429':
          $ref: '#/components/responses/RateLimited'
components:
  headers:
    CreditsRemaining:
      description: Credit balance remaining after this request was debited.
      schema:
        type: integer
        example: 4999
  schemas:
    SearchResult:
      type: object
      required:
        - symbol
        - ticker
        - description
        - exchange
        - type
      properties:
        symbol:
          type: string
          description: >-
            Canonical internal identifier (echo back to /v1/symbols and
            /v1/history).
        ticker:
          type: string
          description: Display ticker shown in the picker.
        description:
          type: string
        exchange:
          type: string
          example: ARCA
        type:
          type: string
          enum:
            - stock
            - etf
            - index
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
  securitySchemes:
    bearerApiKey:
      type: http
      scheme: bearer
      description: |
        Skylit API key in the `Authorization` header
        (`Authorization: Bearer <key>`). `X-API-Key` is also accepted. The same
        key works across Atlas, Heatseeker, and Flowseeker.

````
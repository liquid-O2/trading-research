# Level Atlas

Descriptive census. This document selects nothing.

Levels counted: 77319 (headline QQQ+SPY: 46633; NQ+ES degenerate: 30686). Strategy-alignment rows (headline QQQ+SPY): 370656.

Headline proximity rates are after-availability: a level marks an extreme only if that extreme printed at or after the 10:00 ET availability clock. Unrestricted rates (all extremes) are the diagnostic column `unrestricted high 8`. Rates are day-block bootstrap means with 95 percent intervals (399 resamples, seed 15022026).

Headline tables use QQQ and SPY only. NQ and ES are reported separately under degenerate board (median n_live 2 / 7). NQ and ES rows are not evidence for the futures-option levels thesis until a BBO or MBP schema for those roots is owned. Owned NQ/ES option DBN has no BBO; only ohlcv-1m last-trade midpoints pass the 60 s age rule, so boards collapse to a median of 2 (NQ) and 7 (ES) live contracts.

## Extreme proximity overall (QQQ+SPY, after availability)

| group | n | high 4 | high 8 | high 16 | low 4 | low 8 | low 16 | control high 8 | unrestricted high 8 | high after available | low after available |
| --- | ---: | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| all | 46633 | 0.002 [0.001, 0.003] n=25369 | 0.004 [0.002, 0.005] n=25369 | 0.007 [0.005, 0.008] n=25369 | 0.002 [0.001, 0.004] n=22503 | 0.004 [0.002, 0.005] n=22503 | 0.007 [0.005, 0.009] n=22503 | 0.002 [0.002, 0.003] n=25369 | 0.004 [0.003, 0.005] n=45557 | 0.557 [0.535, 0.582] n=45557 | 0.494 [0.470, 0.516] n=45557 |

## By level kind (QQQ+SPY, after availability)

| group | n | high 4 | high 8 | high 16 | low 4 | low 8 | low 16 | control high 8 | unrestricted high 8 | high after available | low after available |
| --- | ---: | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| call_wall | 3344 | 0.004 [0.001, 0.008] n=1820 | 0.008 [0.004, 0.012] n=1820 | 0.012 [0.006, 0.016] n=1820 | 0.003 [0.001, 0.006] n=1613 | 0.004 [0.002, 0.007] n=1613 | 0.009 [0.004, 0.013] n=1613 | 0.003 [0.001, 0.005] n=1820 | 0.008 [0.005, 0.012] n=3267 | 0.557 [0.534, 0.581] n=3267 | 0.494 [0.470, 0.514] n=3267 |
| gamma_flip | 3159 | 0.000 [0.000, 0.000] n=1707 | 0.000 [0.000, 0.000] n=1707 | 0.000 [0.000, 0.000] n=1707 | 0.001 [0.000, 0.003] n=1532 | 0.003 [0.001, 0.005] n=1532 | 0.003 [0.001, 0.006] n=1532 | 0.000 [0.000, 0.000] n=1707 | 0.000 [0.000, 0.001] n=3084 | 0.554 [0.528, 0.579] n=3084 | 0.497 [0.471, 0.520] n=3084 |
| key_gamma | 3344 | 0.003 [0.001, 0.005] n=1820 | 0.006 [0.003, 0.010] n=1820 | 0.010 [0.007, 0.015] n=1820 | 0.004 [0.001, 0.007] n=1613 | 0.006 [0.003, 0.010] n=1613 | 0.011 [0.007, 0.017] n=1613 | 0.002 [0.000, 0.004] n=1820 | 0.006 [0.004, 0.009] n=3267 | 0.557 [0.534, 0.581] n=3267 | 0.494 [0.470, 0.514] n=3267 |
| max_pain | 3346 | 0.001 [0.000, 0.003] n=1822 | 0.003 [0.001, 0.005] n=1822 | 0.005 [0.002, 0.008] n=1822 | 0.002 [0.000, 0.004] n=1615 | 0.004 [0.001, 0.007] n=1615 | 0.010 [0.005, 0.015] n=1615 | 0.003 [0.001, 0.005] n=1822 | 0.003 [0.002, 0.005] n=3269 | 0.557 [0.536, 0.583] n=3269 | 0.494 [0.470, 0.516] n=3269 |
| put_wall | 3344 | 0.003 [0.001, 0.006] n=1820 | 0.007 [0.003, 0.010] n=1820 | 0.009 [0.005, 0.013] n=1820 | 0.004 [0.001, 0.007] n=1613 | 0.005 [0.002, 0.009] n=1613 | 0.009 [0.005, 0.014] n=1613 | 0.002 [0.000, 0.004] n=1820 | 0.006 [0.004, 0.009] n=3267 | 0.557 [0.534, 0.581] n=3267 | 0.494 [0.470, 0.514] n=3267 |
| top_gamma | 10032 | 0.003 [0.001, 0.005] n=5460 | 0.005 [0.003, 0.007] n=5460 | 0.009 [0.006, 0.011] n=5460 | 0.003 [0.001, 0.005] n=4839 | 0.004 [0.002, 0.006] n=4839 | 0.009 [0.006, 0.012] n=4839 | 0.003 [0.002, 0.004] n=5460 | 0.006 [0.004, 0.007] n=9801 | 0.557 [0.534, 0.581] n=9801 | 0.494 [0.470, 0.514] n=9801 |
| top_vanna | 10032 | 0.001 [0.000, 0.002] n=5460 | 0.001 [0.000, 0.003] n=5460 | 0.003 [0.002, 0.005] n=5460 | 0.001 [0.000, 0.001] n=4839 | 0.001 [0.000, 0.002] n=4839 | 0.002 [0.001, 0.003] n=4839 | 0.003 [0.001, 0.004] n=5460 | 0.002 [0.001, 0.003] n=9801 | 0.557 [0.534, 0.581] n=9801 | 0.494 [0.470, 0.514] n=9801 |
| top_vega | 10032 | 0.002 [0.001, 0.004] n=5460 | 0.003 [0.002, 0.005] n=5460 | 0.007 [0.005, 0.009] n=5460 | 0.003 [0.001, 0.004] n=4839 | 0.004 [0.002, 0.006] n=4839 | 0.007 [0.004, 0.009] n=4839 | 0.002 [0.001, 0.004] n=5460 | 0.003 [0.002, 0.005] n=9801 | 0.557 [0.534, 0.581] n=9801 | 0.494 [0.470, 0.514] n=9801 |

## By root (headline QQQ+SPY, after availability)

| group | n | high 4 | high 8 | high 16 | low 4 | low 8 | low 16 | control high 8 | unrestricted high 8 | high after available | low after available |
| --- | ---: | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| QQQ | 23319 | 0.003 [0.001, 0.005] n=12682 | 0.004 [0.002, 0.007] n=12682 | 0.007 [0.004, 0.010] n=12682 | 0.002 [0.001, 0.004] n=11251 | 0.003 [0.002, 0.005] n=11251 | 0.005 [0.003, 0.007] n=11251 | 0.002 [0.001, 0.003] n=12682 | 0.004 [0.003, 0.006] n=22774 | 0.557 [0.534, 0.580] n=22774 | 0.494 [0.469, 0.520] n=22774 |
| SPY | 23314 | 0.001 [0.000, 0.003] n=12687 | 0.004 [0.002, 0.006] n=12687 | 0.006 [0.004, 0.009] n=12687 | 0.002 [0.001, 0.005] n=11252 | 0.004 [0.002, 0.007] n=11252 | 0.009 [0.005, 0.012] n=11252 | 0.003 [0.002, 0.004] n=12687 | 0.004 [0.003, 0.006] n=22783 | 0.557 [0.534, 0.582] n=22783 | 0.494 [0.469, 0.516] n=22783 |

## By year (QQQ+SPY, after availability)

| group | n | high 4 | high 8 | high 16 | low 4 | low 8 | low 16 | control high 8 | unrestricted high 8 | high after available | low after available |
| --- | ---: | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 2020 | 7024 | 0.003 [0.000, 0.008] n=4013 | 0.004 [0.001, 0.008] n=4013 | 0.008 [0.003, 0.015] n=4013 | 0.002 [0.000, 0.004] n=3013 | 0.002 [0.000, 0.005] n=3013 | 0.006 [0.002, 0.012] n=3013 | 0.003 [0.001, 0.005] n=4013 | 0.003 [0.001, 0.006] n=6884 | 0.583 [0.521, 0.643] n=6884 | 0.438 [0.378, 0.501] n=6884 |
| 2021 | 7029 | 0.001 [0.000, 0.002] n=3907 | 0.003 [0.000, 0.008] n=3907 | 0.005 [0.001, 0.013] n=3907 | 0.003 [0.000, 0.008] n=3489 | 0.004 [0.001, 0.009] n=3489 | 0.006 [0.002, 0.011] n=3489 | 0.002 [0.000, 0.004] n=3907 | 0.005 [0.002, 0.009] n=6917 | 0.565 [0.504, 0.624] n=6917 | 0.504 [0.436, 0.569] n=6917 |
| 2022 | 6993 | 0.000 [0.000, 0.001] n=3508 | 0.003 [0.000, 0.006] n=3508 | 0.004 [0.001, 0.007] n=3508 | 0.003 [0.001, 0.006] n=3762 | 0.005 [0.002, 0.008] n=3762 | 0.011 [0.005, 0.018] n=3762 | 0.002 [0.000, 0.004] n=3508 | 0.003 [0.001, 0.006] n=6881 | 0.510 [0.444, 0.567] n=6881 | 0.547 [0.487, 0.608] n=6881 |
| 2023 | 6963 | 0.004 [0.000, 0.009] n=4039 | 0.004 [0.000, 0.009] n=4039 | 0.007 [0.003, 0.013] n=4039 | 0.002 [0.000, 0.005] n=3619 | 0.004 [0.001, 0.009] n=3619 | 0.006 [0.002, 0.011] n=3619 | 0.004 [0.001, 0.006] n=4039 | 0.006 [0.003, 0.010] n=6851 | 0.590 [0.525, 0.655] n=6851 | 0.528 [0.467, 0.585] n=6851 |
| 2024 | 7026 | 0.001 [0.000, 0.004] n=3927 | 0.005 [0.001, 0.011] n=3927 | 0.006 [0.002, 0.012] n=3927 | 0.001 [0.000, 0.004] n=3406 | 0.002 [0.000, 0.004] n=3406 | 0.003 [0.000, 0.007] n=3406 | 0.003 [0.001, 0.005] n=3927 | 0.003 [0.001, 0.007] n=6916 | 0.568 [0.503, 0.628] n=6916 | 0.492 [0.433, 0.556] n=6916 |
| 2025 | 6985 | 0.003 [0.001, 0.007] n=3854 | 0.005 [0.002, 0.009] n=3854 | 0.007 [0.003, 0.013] n=3854 | 0.003 [0.000, 0.006] n=3298 | 0.005 [0.000, 0.012] n=3298 | 0.008 [0.002, 0.015] n=3298 | 0.002 [0.000, 0.003] n=3854 | 0.005 [0.002, 0.008] n=6817 | 0.565 [0.508, 0.631] n=6817 | 0.484 [0.418, 0.542] n=6817 |
| 2026 | 4613 | 0.001 [0.000, 0.004] n=2121 | 0.001 [0.000, 0.004] n=2121 | 0.008 [0.003, 0.016] n=2121 | 0.001 [0.000, 0.003] n=1916 | 0.002 [0.000, 0.005] n=1916 | 0.006 [0.001, 0.012] n=1916 | 0.001 [0.000, 0.003] n=2121 | 0.003 [0.000, 0.007] n=4291 | 0.494 [0.423, 0.568] n=4291 | 0.447 [0.369, 0.514] n=4291 |

## By expiry bucket (QQQ+SPY, after availability)

| group | n | high 4 | high 8 | high 16 | low 4 | low 8 | low 16 | control high 8 | unrestricted high 8 | high after available | low after available |
| --- | ---: | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 0DTE | 37217 | 0.002 [0.001, 0.003] n=19888 | 0.004 [0.002, 0.005] n=19888 | 0.007 [0.005, 0.009] n=19888 | 0.002 [0.001, 0.004] n=17702 | 0.004 [0.002, 0.005] n=17702 | 0.007 [0.005, 0.009] n=17702 | 0.002 [0.001, 0.003] n=19888 | 0.004 [0.003, 0.005] n=36239 | 0.549 [0.523, 0.576] n=36239 | 0.488 [0.462, 0.514] n=36239 |
| 1-7 | 9416 | 0.002 [0.000, 0.006] n=5481 | 0.005 [0.001, 0.010] n=5481 | 0.006 [0.001, 0.010] n=5481 | 0.003 [0.001, 0.006] n=4801 | 0.004 [0.001, 0.007] n=4801 | 0.006 [0.003, 0.011] n=4801 | 0.003 [0.001, 0.005] n=5481 | 0.004 [0.002, 0.007] n=9318 | 0.588 [0.540, 0.633] n=9318 | 0.515 [0.469, 0.566] n=9318 |

## By session bucket of the account-day high (QQQ+SPY, after availability)

| group | n | high 4 | high 8 | high 16 | low 4 | low 8 | low 16 | control high 8 | unrestricted high 8 | high after available | low after available |
| --- | ---: | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| other | 6056 | 0.001 [0.000, 0.003] n=5916 | 0.003 [0.001, 0.006] n=5916 | 0.005 [0.002, 0.009] n=5916 | 0.001 [0.000, 0.003] n=1145 | 0.001 [0.000, 0.003] n=1145 | 0.004 [0.000, 0.012] n=1145 | 0.003 [0.001, 0.004] n=5916 | 0.003 [0.001, 0.006] n=5916 | 1.000 [1.000, 1.000] n=5916 | 0.194 [0.142, 0.242] n=5916 |
| overnight_or_pre | 16908 | n/a | n/a | n/a | 0.001 [0.000, 0.002] n=13310 | 0.002 [0.001, 0.004] n=13310 | 0.005 [0.003, 0.007] n=13310 | n/a | 0.004 [0.003, 0.006] n=16516 | 0.000 [0.000, 0.000] n=16516 | 0.806 [0.778, 0.836] n=16516 |
| rth | 23669 | 0.002 [0.001, 0.004] n=19453 | 0.004 [0.002, 0.006] n=19453 | 0.007 [0.005, 0.009] n=19453 | 0.005 [0.002, 0.008] n=8048 | 0.006 [0.003, 0.008] n=8048 | 0.010 [0.007, 0.015] n=8048 | 0.002 [0.001, 0.003] n=19453 | 0.004 [0.003, 0.006] n=23125 | 0.841 [0.815, 0.866] n=23125 | 0.348 [0.317, 0.383] n=23125 |

## By session bucket of the account-day low (QQQ+SPY, after availability)

| group | n | high 4 | high 8 | high 16 | low 4 | low 8 | low 16 | control high 8 | unrestricted high 8 | high after available | low after available |
| --- | ---: | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| other | 3809 | 0.003 [0.000, 0.010] n=947 | 0.003 [0.000, 0.010] n=947 | 0.003 [0.000, 0.010] n=947 | 0.003 [0.001, 0.006] n=3697 | 0.005 [0.001, 0.008] n=3697 | 0.006 [0.002, 0.010] n=3697 | 0.001 [0.000, 0.003] n=947 | 0.001 [0.000, 0.004] n=3697 | 0.256 [0.180, 0.331] n=3697 | 1.000 [1.000, 1.000] n=3697 |
| overnight_or_pre | 20144 | 0.002 [0.001, 0.004] n=16575 | 0.005 [0.003, 0.007] n=16575 | 0.008 [0.005, 0.011] n=16575 | n/a | n/a | n/a | 0.003 [0.002, 0.004] n=16575 | 0.005 [0.003, 0.007] n=19585 | 0.846 [0.819, 0.876] n=19585 | 0.000 [0.000, 0.000] n=19585 |
| rth | 22680 | 0.002 [0.001, 0.003] n=7847 | 0.002 [0.001, 0.003] n=7847 | 0.004 [0.002, 0.007] n=7847 | 0.002 [0.001, 0.004] n=18806 | 0.003 [0.002, 0.005] n=18806 | 0.007 [0.005, 0.009] n=18806 | 0.001 [0.000, 0.002] n=7847 | 0.004 [0.003, 0.006] n=22275 | 0.352 [0.319, 0.383] n=22275 | 0.844 [0.819, 0.868] n=22275 |

## By volatility regime (QQQ+SPY, after availability)

| group | n | high 4 | high 8 | high 16 | low 4 | low 8 | low 16 | control high 8 | unrestricted high 8 | high after available | low after available |
| --- | ---: | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| high | 8191 | 0.002 [0.000, 0.005] n=4621 | 0.003 [0.000, 0.007] n=4621 | 0.005 [0.001, 0.009] n=4621 | 0.002 [0.000, 0.004] n=4167 | 0.002 [0.001, 0.004] n=4167 | 0.006 [0.002, 0.012] n=4167 | 0.002 [0.000, 0.004] n=4621 | 0.003 [0.001, 0.006] n=8107 | 0.570 [0.520, 0.616] n=8107 | 0.514 [0.468, 0.563] n=8107 |
| low | 23198 | 0.002 [0.001, 0.003] n=12800 | 0.004 [0.002, 0.006] n=12800 | 0.007 [0.004, 0.009] n=12800 | 0.002 [0.001, 0.004] n=10701 | 0.004 [0.002, 0.006] n=10701 | 0.006 [0.004, 0.009] n=10701 | 0.003 [0.002, 0.004] n=12800 | 0.004 [0.003, 0.006] n=22597 | 0.566 [0.535, 0.600] n=22597 | 0.474 [0.441, 0.509] n=22597 |
| mid | 15242 | 0.002 [0.000, 0.005] n=7946 | 0.004 [0.002, 0.008] n=7946 | 0.007 [0.004, 0.011] n=7946 | 0.003 [0.001, 0.005] n=7633 | 0.004 [0.002, 0.007] n=7633 | 0.007 [0.004, 0.012] n=7633 | 0.002 [0.001, 0.003] n=7946 | 0.005 [0.003, 0.007] n=14851 | 0.535 [0.501, 0.569] n=14851 | 0.514 [0.475, 0.550] n=14851 |
| unknown | 2 | 0.000 [0.000, 0.000] n=2 | 0.000 [0.000, 0.000] n=2 | 0.000 [0.000, 0.000] n=2 | 0.000 [0.000, 0.000] n=2 | 0.000 [0.000, 0.000] n=2 | 0.000 [0.000, 0.000] n=2 | 0.000 [0.000, 0.000] n=2 | 0.000 [0.000, 0.000] n=2 | 1.000 [1.000, 1.000] n=2 | 1.000 [1.000, 1.000] n=2 |

## Root agreement versus single-root (QQQ+SPY)

| group | n | high 4 | high 8 | high 16 | low 4 | low 8 | low 16 | control high 8 | unrestricted high 8 | high after available | low after available |
| --- | ---: | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| agreeing | 13769 | n/a | n/a | n/a | n/a | n/a | n/a | n/a | 0.005 [0.003, 0.006] n=13769 | n/a | n/a |
| single_root | 31788 | n/a | n/a | n/a | n/a | n/a | n/a | n/a | 0.004 [0.003, 0.005] n=31788 | n/a | n/a |

Agreeing levels: 13769. Single-root levels: 31788.

## NQ and ES degenerate board (median n_live 2 / 7)

NQ and ES rows are not evidence for the futures-option levels thesis until a BBO or MBP schema for those roots is owned. Owned NQ/ES option DBN has no BBO; only ohlcv-1m last-trade midpoints pass the 60 s age rule, so boards collapse to a median of 2 (NQ) and 7 (ES) live contracts.

## NQ and ES extreme proximity (degenerate board (median n_live 2 / 7))

| group | n | high 4 | high 8 | high 16 | low 4 | low 8 | low 16 | control high 8 | unrestricted high 8 | high after available | low after available |
| --- | ---: | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| NQ+ES | 30686 | 0.001 [0.000, 0.002] n=16767 | 0.002 [0.001, 0.004] n=16767 | 0.004 [0.002, 0.007] n=16767 | 0.001 [0.000, 0.002] n=15043 | 0.001 [0.000, 0.002] n=15043 | 0.003 [0.002, 0.005] n=15043 | 0.001 [0.001, 0.002] n=16767 | 0.002 [0.001, 0.003] n=30155 | 0.556 [0.532, 0.583] n=30155 | 0.499 [0.474, 0.525] n=30155 |

## NQ and ES by root (degenerate board (median n_live 2 / 7))

| group | n | high 4 | high 8 | high 16 | low 4 | low 8 | low 16 | control high 8 | unrestricted high 8 | high after available | low after available |
| --- | ---: | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| ES (degenerate board (median n_live 2 / 7)) | 20416 | 0.000 [0.000, 0.001] n=11204 | 0.002 [0.001, 0.004] n=11204 | 0.004 [0.002, 0.007] n=11204 | 0.000 [0.000, 0.001] n=9934 | 0.001 [0.000, 0.002] n=9934 | 0.003 [0.001, 0.005] n=9934 | 0.001 [0.001, 0.002] n=11204 | 0.002 [0.001, 0.003] n=20001 | 0.560 [0.539, 0.585] n=20001 | 0.497 [0.471, 0.520] n=20001 |
| NQ (degenerate board (median n_live 2 / 7)) | 10270 | 0.002 [0.000, 0.005] n=5563 | 0.002 [0.000, 0.006] n=5563 | 0.004 [0.001, 0.009] n=5563 | 0.002 [0.000, 0.004] n=5109 | 0.002 [0.000, 0.004] n=5109 | 0.004 [0.000, 0.008] n=5109 | 0.002 [0.001, 0.003] n=5563 | 0.002 [0.000, 0.003] n=10154 | 0.548 [0.517, 0.579] n=10154 | 0.503 [0.472, 0.537] n=10154 |

## NQ and ES by level kind (degenerate board (median n_live 2 / 7))

| group | n | high 4 | high 8 | high 16 | low 4 | low 8 | low 16 | control high 8 | unrestricted high 8 | high after available | low after available |
| --- | ---: | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| call_wall | 2080 | 0.000 [0.000, 0.000] n=1150 | 0.002 [0.000, 0.004] n=1150 | 0.006 [0.003, 0.011] n=1150 | 0.001 [0.000, 0.003] n=1028 | 0.001 [0.000, 0.003] n=1028 | 0.001 [0.000, 0.003] n=1028 | 0.001 [0.000, 0.003] n=1150 | 0.002 [0.000, 0.004] n=2049 | 0.561 [0.531, 0.586] n=2049 | 0.502 [0.477, 0.530] n=2049 |
| gamma_flip | 929 | 0.002 [0.000, 0.008] n=514 | 0.004 [0.000, 0.010] n=514 | 0.006 [0.000, 0.014] n=514 | 0.000 [0.000, 0.000] n=465 | 0.000 [0.000, 0.000] n=465 | 0.002 [0.000, 0.008] n=465 | 0.002 [0.000, 0.006] n=514 | 0.002 [0.000, 0.005] n=917 | 0.561 [0.527, 0.592] n=917 | 0.507 [0.473, 0.544] n=917 |
| key_gamma | 2727 | 0.001 [0.000, 0.002] n=1484 | 0.002 [0.000, 0.005] n=1484 | 0.005 [0.002, 0.009] n=1484 | 0.001 [0.000, 0.002] n=1322 | 0.001 [0.000, 0.002] n=1322 | 0.004 [0.001, 0.007] n=1322 | 0.003 [0.001, 0.005] n=1484 | 0.002 [0.000, 0.004] n=2677 | 0.554 [0.529, 0.577] n=2677 | 0.494 [0.469, 0.518] n=2677 |
| max_pain | 2906 | 0.001 [0.000, 0.003] n=1588 | 0.003 [0.001, 0.006] n=1588 | 0.006 [0.003, 0.011] n=1588 | 0.001 [0.000, 0.003] n=1416 | 0.002 [0.000, 0.005] n=1416 | 0.006 [0.002, 0.011] n=1416 | 0.003 [0.001, 0.005] n=1588 | 0.002 [0.001, 0.004] n=2854 | 0.556 [0.531, 0.582] n=2854 | 0.496 [0.474, 0.522] n=2854 |
| put_wall | 2364 | 0.001 [0.000, 0.003] n=1279 | 0.002 [0.000, 0.005] n=1279 | 0.004 [0.001, 0.008] n=1279 | 0.001 [0.000, 0.003] n=1152 | 0.001 [0.000, 0.003] n=1152 | 0.007 [0.003, 0.012] n=1152 | 0.002 [0.000, 0.005] n=1279 | 0.002 [0.000, 0.003] n=2320 | 0.551 [0.523, 0.577] n=2320 | 0.497 [0.471, 0.519] n=2320 |
| top_gamma | 6560 | 0.001 [0.000, 0.002] n=3584 | 0.002 [0.001, 0.004] n=3584 | 0.004 [0.002, 0.007] n=3584 | 0.001 [0.000, 0.002] n=3220 | 0.001 [0.000, 0.003] n=3220 | 0.003 [0.002, 0.006] n=3220 | 0.001 [0.000, 0.002] n=3584 | 0.002 [0.001, 0.003] n=6446 | 0.556 [0.532, 0.581] n=6446 | 0.500 [0.474, 0.522] n=6446 |
| top_vanna | 6560 | 0.001 [0.000, 0.002] n=3584 | 0.002 [0.001, 0.003] n=3584 | 0.004 [0.002, 0.006] n=3584 | 0.001 [0.000, 0.002] n=3220 | 0.001 [0.000, 0.002] n=3220 | 0.002 [0.001, 0.004] n=3220 | 0.001 [0.000, 0.001] n=3584 | 0.002 [0.001, 0.003] n=6446 | 0.556 [0.532, 0.581] n=6446 | 0.500 [0.474, 0.522] n=6446 |
| top_vega | 6560 | 0.001 [0.000, 0.002] n=3584 | 0.002 [0.001, 0.004] n=3584 | 0.004 [0.002, 0.006] n=3584 | 0.001 [0.000, 0.002] n=3220 | 0.001 [0.000, 0.002] n=3220 | 0.003 [0.001, 0.005] n=3220 | 0.002 [0.001, 0.003] n=3584 | 0.002 [0.001, 0.003] n=6446 | 0.556 [0.532, 0.581] n=6446 | 0.500 [0.474, 0.522] n=6446 |

## Strategy alignment outcomes (QQQ+SPY headline; NQ/ES excluded)

Rows: 370656. result=not_applicable: 17308 (0.04669558836225503).

Unconditional result mix: invalid_geometry=85535, missing_future=30, neither=18378, not_applicable=17308, stop_first=190229, target_first=59176.

| branch | level kind | n | unconditional | bucket | bucket n | conditional |
| --- | --- | ---: | --- | --- | ---: | --- |
| nyam_box | key_gamma | 4341 | invalid_geometry:0.001, neither:0.073, stop_first:0.732, target_first:0.194 | beyond | 1452 | invalid_geometry:0.001, neither:0.075, stop_first:0.738, target_first:0.185 |
|  |  |  |  | within_0.1 | 397 | invalid_geometry:0.003, neither:0.073, stop_first:0.698, target_first:0.227 |
|  |  |  |  | within_0.25 | 606 | neither:0.048, stop_first:0.756, target_first:0.196 |
|  |  |  |  | within_0.5 | 796 | invalid_geometry:0.003, neither:0.075, stop_first:0.727, target_first:0.195 |
|  |  |  |  | within_1.0 | 1090 | invalid_geometry:0.001, neither:0.082, stop_first:0.726, target_first:0.192 |
| nyam_box | call_wall | 4341 | invalid_geometry:0.001, neither:0.073, stop_first:0.732, target_first:0.194 | beyond | 1517 | invalid_geometry:0.001, neither:0.082, stop_first:0.750, target_first:0.168 |
|  |  |  |  | within_0.1 | 371 | invalid_geometry:0.003, neither:0.070, stop_first:0.690, target_first:0.237 |
|  |  |  |  | within_0.25 | 569 | neither:0.058, stop_first:0.708, target_first:0.234 |
|  |  |  |  | within_0.5 | 760 | invalid_geometry:0.001, neither:0.082, stop_first:0.720, target_first:0.197 |
|  |  |  |  | within_1.0 | 1124 | invalid_geometry:0.003, neither:0.063, stop_first:0.742, target_first:0.192 |
| nyam_box | put_wall | 4341 | invalid_geometry:0.001, neither:0.073, stop_first:0.732, target_first:0.194 | beyond | 1597 | invalid_geometry:0.001, neither:0.073, stop_first:0.729, target_first:0.197 |
|  |  |  |  | within_0.1 | 379 | invalid_geometry:0.003, neither:0.087, stop_first:0.704, target_first:0.206 |
|  |  |  |  | within_0.25 | 525 | invalid_geometry:0.002, neither:0.050, stop_first:0.766, target_first:0.183 |
|  |  |  |  | within_0.5 | 763 | invalid_geometry:0.003, neither:0.075, stop_first:0.739, target_first:0.183 |
|  |  |  |  | within_1.0 | 1077 | neither:0.078, stop_first:0.723, target_first:0.199 |
| nyam_box | gamma_flip | 4107 | invalid_geometry:0.001, neither:0.071, stop_first:0.735, target_first:0.193 | beyond | 3828 | invalid_geometry:0.001, neither:0.071, stop_first:0.734, target_first:0.194 |
|  |  |  |  | within_0.1 | 27 | neither:0.111, stop_first:0.741, target_first:0.148 |
|  |  |  |  | within_0.25 | 51 | neither:0.059, stop_first:0.765, target_first:0.176 |
|  |  |  |  | within_0.5 | 65 | neither:0.108, stop_first:0.692, target_first:0.200 |
|  |  |  |  | within_1.0 | 136 | invalid_geometry:0.007, neither:0.051, stop_first:0.750, target_first:0.191 |
| nyam_box | max_pain | 4345 | invalid_geometry:0.001, neither:0.073, stop_first:0.732, target_first:0.194 | beyond | 1842 | invalid_geometry:0.001, neither:0.072, stop_first:0.730, target_first:0.198 |
|  |  |  |  | within_0.1 | 302 | invalid_geometry:0.007, neither:0.066, stop_first:0.738, target_first:0.189 |
|  |  |  |  | within_0.25 | 456 | neither:0.066, stop_first:0.752, target_first:0.182 |
|  |  |  |  | within_0.5 | 704 | invalid_geometry:0.001, neither:0.082, stop_first:0.717, target_first:0.199 |
|  |  |  |  | within_1.0 | 1041 | invalid_geometry:0.001, neither:0.073, stop_first:0.734, target_first:0.192 |
| previous_hour | key_gamma | 18544 | invalid_geometry:0.003, missing_future:0.000, neither:0.054, stop_first:0.777, target_first:0.166 | beyond | 6800 | invalid_geometry:0.004, missing_future:0.000, neither:0.056, stop_first:0.781, target_first:0.159 |
|  |  |  |  | within_0.1 | 1462 | invalid_geometry:0.003, neither:0.053, stop_first:0.781, target_first:0.163 |
|  |  |  |  | within_0.25 | 2245 | invalid_geometry:0.002, neither:0.053, stop_first:0.773, target_first:0.171 |
|  |  |  |  | within_0.5 | 3445 | invalid_geometry:0.002, neither:0.050, stop_first:0.780, target_first:0.168 |
|  |  |  |  | within_1.0 | 4592 | invalid_geometry:0.002, missing_future:0.000, neither:0.056, stop_first:0.770, target_first:0.172 |
| previous_hour | call_wall | 18544 | invalid_geometry:0.003, missing_future:0.000, neither:0.054, stop_first:0.777, target_first:0.166 | beyond | 7161 | invalid_geometry:0.003, missing_future:0.000, neither:0.056, stop_first:0.784, target_first:0.157 |
|  |  |  |  | within_0.1 | 1426 | invalid_geometry:0.003, neither:0.051, stop_first:0.774, target_first:0.172 |
|  |  |  |  | within_0.25 | 2198 | invalid_geometry:0.002, neither:0.052, stop_first:0.758, target_first:0.187 |
|  |  |  |  | within_0.5 | 3170 | invalid_geometry:0.003, neither:0.058, stop_first:0.775, target_first:0.165 |
|  |  |  |  | within_1.0 | 4589 | invalid_geometry:0.003, missing_future:0.000, neither:0.050, stop_first:0.779, target_first:0.168 |
| previous_hour | put_wall | 18544 | invalid_geometry:0.003, missing_future:0.000, neither:0.054, stop_first:0.777, target_first:0.166 | beyond | 7387 | invalid_geometry:0.004, neither:0.055, stop_first:0.782, target_first:0.160 |
|  |  |  |  | within_0.1 | 1464 | invalid_geometry:0.003, neither:0.056, stop_first:0.769, target_first:0.171 |
|  |  |  |  | within_0.25 | 2030 | invalid_geometry:0.002, neither:0.054, stop_first:0.785, target_first:0.159 |
|  |  |  |  | within_0.5 | 3174 | invalid_geometry:0.002, missing_future:0.000, neither:0.048, stop_first:0.782, target_first:0.168 |
|  |  |  |  | within_1.0 | 4489 | invalid_geometry:0.002, missing_future:0.000, neither:0.057, stop_first:0.765, target_first:0.176 |
| previous_hour | gamma_flip | 17538 | invalid_geometry:0.003, missing_future:0.000, neither:0.054, stop_first:0.778, target_first:0.165 | beyond | 16329 | invalid_geometry:0.003, missing_future:0.000, neither:0.054, stop_first:0.777, target_first:0.167 |
|  |  |  |  | within_0.1 | 130 | neither:0.038, stop_first:0.815, target_first:0.146 |
|  |  |  |  | within_0.25 | 210 | invalid_geometry:0.005, neither:0.048, stop_first:0.833, target_first:0.114 |
|  |  |  |  | within_0.5 | 304 | neither:0.062, stop_first:0.770, target_first:0.168 |
|  |  |  |  | within_1.0 | 565 | invalid_geometry:0.002, neither:0.055, stop_first:0.786, target_first:0.158 |
| previous_hour | max_pain | 18556 | invalid_geometry:0.003, missing_future:0.000, neither:0.054, stop_first:0.777, target_first:0.166 | beyond | 8374 | invalid_geometry:0.003, neither:0.054, stop_first:0.778, target_first:0.165 |
|  |  |  |  | within_0.1 | 1225 | invalid_geometry:0.004, missing_future:0.001, neither:0.062, stop_first:0.763, target_first:0.170 |
|  |  |  |  | within_0.25 | 1707 | invalid_geometry:0.003, neither:0.057, stop_first:0.773, target_first:0.167 |
|  |  |  |  | within_0.5 | 2822 | invalid_geometry:0.002, missing_future:0.000, neither:0.056, stop_first:0.774, target_first:0.167 |
|  |  |  |  | within_1.0 | 4428 | invalid_geometry:0.002, neither:0.049, stop_first:0.782, target_first:0.166 |
| other_session | key_gamma | 13728 | invalid_geometry:0.269, missing_future:0.000, neither:0.020, stop_first:0.562, target_first:0.149 | beyond | 4961 | invalid_geometry:0.269, missing_future:0.000, neither:0.024, stop_first:0.563, target_first:0.144 |
|  |  |  |  | within_0.1 | 1124 | invalid_geometry:0.254, neither:0.015, stop_first:0.568, target_first:0.163 |
|  |  |  |  | within_0.25 | 1674 | invalid_geometry:0.271, neither:0.023, stop_first:0.550, target_first:0.157 |
|  |  |  |  | within_0.5 | 2499 | invalid_geometry:0.269, missing_future:0.000, neither:0.013, stop_first:0.567, target_first:0.150 |
|  |  |  |  | within_1.0 | 3470 | invalid_geometry:0.271, neither:0.018, stop_first:0.563, target_first:0.148 |
| other_session | call_wall | 13728 | invalid_geometry:0.269, missing_future:0.000, neither:0.020, stop_first:0.562, target_first:0.149 | beyond | 5234 | invalid_geometry:0.268, missing_future:0.000, neither:0.022, stop_first:0.564, target_first:0.146 |
|  |  |  |  | within_0.1 | 1100 | invalid_geometry:0.257, neither:0.016, stop_first:0.567, target_first:0.159 |
|  |  |  |  | within_0.25 | 1587 | invalid_geometry:0.264, neither:0.023, stop_first:0.551, target_first:0.161 |
|  |  |  |  | within_0.5 | 2373 | invalid_geometry:0.273, missing_future:0.000, neither:0.016, stop_first:0.560, target_first:0.151 |
|  |  |  |  | within_1.0 | 3434 | invalid_geometry:0.272, neither:0.018, stop_first:0.565, target_first:0.145 |
| other_session | put_wall | 13728 | invalid_geometry:0.269, missing_future:0.000, neither:0.020, stop_first:0.562, target_first:0.149 | beyond | 5426 | invalid_geometry:0.274, missing_future:0.000, neither:0.023, stop_first:0.558, target_first:0.145 |
|  |  |  |  | within_0.1 | 1055 | invalid_geometry:0.245, neither:0.020, stop_first:0.568, target_first:0.167 |
|  |  |  |  | within_0.25 | 1580 | invalid_geometry:0.270, neither:0.019, stop_first:0.557, target_first:0.154 |
|  |  |  |  | within_0.5 | 2317 | invalid_geometry:0.268, neither:0.016, stop_first:0.570, target_first:0.147 |
|  |  |  |  | within_1.0 | 3350 | invalid_geometry:0.267, missing_future:0.000, neither:0.017, stop_first:0.565, target_first:0.150 |
| other_session | gamma_flip | 12983 | invalid_geometry:0.267, missing_future:0.000, neither:0.019, stop_first:0.564, target_first:0.150 | beyond | 12100 | invalid_geometry:0.268, missing_future:0.000, neither:0.019, stop_first:0.562, target_first:0.152 |
|  |  |  |  | within_0.1 | 86 | invalid_geometry:0.326, neither:0.035, stop_first:0.547, target_first:0.093 |
|  |  |  |  | within_0.25 | 155 | invalid_geometry:0.277, neither:0.013, stop_first:0.548, target_first:0.161 |
|  |  |  |  | within_0.5 | 225 | invalid_geometry:0.262, neither:0.009, stop_first:0.613, target_first:0.116 |
|  |  |  |  | within_1.0 | 417 | invalid_geometry:0.242, neither:0.043, stop_first:0.602, target_first:0.113 |
| other_session | max_pain | 13736 | invalid_geometry:0.269, missing_future:0.000, neither:0.020, stop_first:0.562, target_first:0.149 | beyond | 6144 | invalid_geometry:0.276, neither:0.022, stop_first:0.552, target_first:0.150 |
|  |  |  |  | within_0.1 | 936 | invalid_geometry:0.237, missing_future:0.002, neither:0.016, stop_first:0.591, target_first:0.154 |
|  |  |  |  | within_0.25 | 1287 | invalid_geometry:0.254, neither:0.017, stop_first:0.578, target_first:0.151 |
|  |  |  |  | within_0.5 | 2043 | invalid_geometry:0.256, neither:0.016, stop_first:0.575, target_first:0.153 |
|  |  |  |  | within_1.0 | 3326 | invalid_geometry:0.278, neither:0.020, stop_first:0.560, target_first:0.143 |
| resistance_short | key_gamma | 97 | stop_first:0.546, target_first:0.454 | beyond | 31 | stop_first:0.452, target_first:0.548 |
|  |  |  |  | within_0.1 | 4 | stop_first:0.500, target_first:0.500 |
|  |  |  |  | within_0.25 | 11 | stop_first:0.636, target_first:0.364 |
|  |  |  |  | within_0.5 | 22 | stop_first:0.591, target_first:0.409 |
|  |  |  |  | within_1.0 | 29 | stop_first:0.586, target_first:0.414 |
| resistance_short | call_wall | 97 | stop_first:0.546, target_first:0.454 | beyond | 34 | stop_first:0.559, target_first:0.441 |
|  |  |  |  | within_0.1 | 4 | stop_first:0.500, target_first:0.500 |
|  |  |  |  | within_0.25 | 11 | stop_first:0.545, target_first:0.455 |
|  |  |  |  | within_0.5 | 21 | stop_first:0.429, target_first:0.571 |
|  |  |  |  | within_1.0 | 27 | stop_first:0.630, target_first:0.370 |
| resistance_short | put_wall | 97 | stop_first:0.546, target_first:0.454 | beyond | 33 | stop_first:0.424, target_first:0.576 |
|  |  |  |  | within_0.1 | 8 | stop_first:0.500, target_first:0.500 |
|  |  |  |  | within_0.25 | 9 | stop_first:0.778, target_first:0.222 |
|  |  |  |  | within_0.5 | 21 | stop_first:0.667, target_first:0.333 |
|  |  |  |  | within_1.0 | 26 | stop_first:0.538, target_first:0.462 |
| resistance_short | gamma_flip | 94 | stop_first:0.553, target_first:0.447 | beyond | 94 | stop_first:0.553, target_first:0.447 |
| resistance_short | max_pain | 97 | stop_first:0.546, target_first:0.454 | beyond | 46 | stop_first:0.500, target_first:0.500 |
|  |  |  |  | within_0.1 | 4 | stop_first:0.500, target_first:0.500 |
|  |  |  |  | within_0.25 | 11 | stop_first:0.818, target_first:0.182 |
|  |  |  |  | within_0.5 | 14 | stop_first:0.643, target_first:0.357 |
|  |  |  |  | within_1.0 | 22 | stop_first:0.455, target_first:0.545 |
| defended_band_continuation | key_gamma | 702 | invalid_geometry:0.387, stop_first:0.487, target_first:0.125 | beyond | 223 | invalid_geometry:0.422, stop_first:0.475, target_first:0.103 |
|  |  |  |  | within_0.1 | 65 | invalid_geometry:0.338, stop_first:0.492, target_first:0.169 |
|  |  |  |  | within_0.25 | 86 | invalid_geometry:0.430, stop_first:0.453, target_first:0.116 |
|  |  |  |  | within_0.5 | 150 | invalid_geometry:0.360, stop_first:0.507, target_first:0.133 |
|  |  |  |  | within_1.0 | 178 | invalid_geometry:0.365, stop_first:0.500, target_first:0.135 |
| defended_band_continuation | call_wall | 702 | invalid_geometry:0.387, stop_first:0.487, target_first:0.125 | beyond | 243 | invalid_geometry:0.383, stop_first:0.486, target_first:0.132 |
|  |  |  |  | within_0.1 | 50 | invalid_geometry:0.360, stop_first:0.480, target_first:0.160 |
|  |  |  |  | within_0.25 | 94 | invalid_geometry:0.404, stop_first:0.468, target_first:0.128 |
|  |  |  |  | within_0.5 | 124 | invalid_geometry:0.379, stop_first:0.508, target_first:0.113 |
|  |  |  |  | within_1.0 | 191 | invalid_geometry:0.398, stop_first:0.487, target_first:0.115 |
| defended_band_continuation | put_wall | 702 | invalid_geometry:0.387, stop_first:0.487, target_first:0.125 | beyond | 258 | invalid_geometry:0.422, stop_first:0.453, target_first:0.124 |
|  |  |  |  | within_0.1 | 66 | invalid_geometry:0.364, stop_first:0.500, target_first:0.136 |
|  |  |  |  | within_0.25 | 77 | invalid_geometry:0.390, stop_first:0.506, target_first:0.104 |
|  |  |  |  | within_0.5 | 132 | invalid_geometry:0.348, stop_first:0.515, target_first:0.136 |
|  |  |  |  | within_1.0 | 169 | invalid_geometry:0.373, stop_first:0.503, target_first:0.124 |
| defended_band_continuation | gamma_flip | 660 | invalid_geometry:0.386, stop_first:0.489, target_first:0.124 | beyond | 617 | invalid_geometry:0.381, stop_first:0.498, target_first:0.122 |
|  |  |  |  | within_0.1 | 6 | invalid_geometry:0.833, stop_first:0.167 |
|  |  |  |  | within_0.25 | 5 | invalid_geometry:0.200, stop_first:0.600, target_first:0.200 |
|  |  |  |  | within_0.5 | 12 | invalid_geometry:0.583, stop_first:0.333, target_first:0.083 |
|  |  |  |  | within_1.0 | 20 | invalid_geometry:0.350, stop_first:0.400, target_first:0.250 |
| defended_band_continuation | max_pain | 706 | invalid_geometry:0.388, stop_first:0.487, target_first:0.125 | beyond | 307 | invalid_geometry:0.404, stop_first:0.485, target_first:0.111 |
|  |  |  |  | within_0.1 | 56 | invalid_geometry:0.357, stop_first:0.429, target_first:0.214 |
|  |  |  |  | within_0.25 | 75 | invalid_geometry:0.493, stop_first:0.373, target_first:0.133 |
|  |  |  |  | within_0.5 | 86 | invalid_geometry:0.360, stop_first:0.512, target_first:0.128 |
|  |  |  |  | within_1.0 | 182 | invalid_geometry:0.341, stop_first:0.544, target_first:0.115 |
| microbalance_break | key_gamma | 4141 | invalid_geometry:0.496, neither:0.107, stop_first:0.180, target_first:0.217 | beyond | 1431 | invalid_geometry:0.515, neither:0.098, stop_first:0.172, target_first:0.215 |
|  |  |  |  | within_0.1 | 345 | invalid_geometry:0.441, neither:0.113, stop_first:0.194, target_first:0.252 |
|  |  |  |  | within_0.25 | 516 | invalid_geometry:0.465, neither:0.114, stop_first:0.209, target_first:0.211 |
|  |  |  |  | within_0.5 | 815 | invalid_geometry:0.475, neither:0.130, stop_first:0.188, target_first:0.207 |
|  |  |  |  | within_1.0 | 1034 | invalid_geometry:0.520, neither:0.095, stop_first:0.166, target_first:0.219 |
| microbalance_break | call_wall | 4141 | invalid_geometry:0.496, neither:0.107, stop_first:0.180, target_first:0.217 | beyond | 1522 | invalid_geometry:0.543, neither:0.087, stop_first:0.172, target_first:0.198 |
|  |  |  |  | within_0.1 | 333 | invalid_geometry:0.432, neither:0.126, stop_first:0.192, target_first:0.249 |
|  |  |  |  | within_0.25 | 499 | invalid_geometry:0.431, neither:0.144, stop_first:0.194, target_first:0.230 |
|  |  |  |  | within_0.5 | 765 | invalid_geometry:0.467, neither:0.124, stop_first:0.191, target_first:0.218 |
|  |  |  |  | within_1.0 | 1022 | invalid_geometry:0.500, neither:0.099, stop_first:0.173, target_first:0.228 |
| microbalance_break | put_wall | 4141 | invalid_geometry:0.496, neither:0.107, stop_first:0.180, target_first:0.217 | beyond | 1623 | invalid_geometry:0.512, neither:0.096, stop_first:0.168, target_first:0.224 |
|  |  |  |  | within_0.1 | 321 | invalid_geometry:0.421, neither:0.131, stop_first:0.206, target_first:0.243 |
|  |  |  |  | within_0.25 | 472 | invalid_geometry:0.468, neither:0.106, stop_first:0.212, target_first:0.214 |
|  |  |  |  | within_0.5 | 733 | invalid_geometry:0.503, neither:0.119, stop_first:0.179, target_first:0.199 |
|  |  |  |  | within_1.0 | 992 | invalid_geometry:0.502, neither:0.108, stop_first:0.177, target_first:0.213 |
| microbalance_break | gamma_flip | 3913 | invalid_geometry:0.498, neither:0.107, stop_first:0.179, target_first:0.216 | beyond | 3636 | invalid_geometry:0.502, neither:0.105, stop_first:0.178, target_first:0.215 |
|  |  |  |  | within_0.1 | 29 | invalid_geometry:0.414, neither:0.069, stop_first:0.207, target_first:0.310 |
|  |  |  |  | within_0.25 | 44 | invalid_geometry:0.409, neither:0.227, stop_first:0.159, target_first:0.205 |
|  |  |  |  | within_0.5 | 78 | invalid_geometry:0.474, neither:0.115, stop_first:0.154, target_first:0.256 |
|  |  |  |  | within_1.0 | 126 | invalid_geometry:0.452, neither:0.127, stop_first:0.222, target_first:0.198 |
| microbalance_break | max_pain | 4143 | invalid_geometry:0.496, neither:0.107, stop_first:0.180, target_first:0.217 | beyond | 1845 | invalid_geometry:0.529, neither:0.100, stop_first:0.167, target_first:0.204 |
|  |  |  |  | within_0.1 | 256 | invalid_geometry:0.410, neither:0.133, stop_first:0.211, target_first:0.246 |
|  |  |  |  | within_0.25 | 399 | invalid_geometry:0.406, neither:0.123, stop_first:0.218, target_first:0.253 |
|  |  |  |  | within_0.5 | 631 | invalid_geometry:0.464, neither:0.103, stop_first:0.185, target_first:0.247 |
|  |  |  |  | within_1.0 | 1012 | invalid_geometry:0.514, neither:0.108, stop_first:0.178, target_first:0.201 |
| vwap_deviation_fade | key_gamma | 1531 | invalid_geometry:0.423, stop_first:0.462, target_first:0.114 | beyond | 523 | invalid_geometry:0.440, stop_first:0.451, target_first:0.109 |
|  |  |  |  | within_0.1 | 145 | invalid_geometry:0.441, stop_first:0.462, target_first:0.097 |
|  |  |  |  | within_0.25 | 193 | invalid_geometry:0.383, stop_first:0.466, target_first:0.150 |
|  |  |  |  | within_0.5 | 299 | invalid_geometry:0.438, stop_first:0.452, target_first:0.110 |
|  |  |  |  | within_1.0 | 371 | invalid_geometry:0.402, stop_first:0.485, target_first:0.113 |
| vwap_deviation_fade | call_wall | 1531 | invalid_geometry:0.423, stop_first:0.462, target_first:0.114 | beyond | 530 | invalid_geometry:0.432, stop_first:0.447, target_first:0.121 |
|  |  |  |  | within_0.1 | 142 | invalid_geometry:0.437, stop_first:0.493, target_first:0.070 |
|  |  |  |  | within_0.25 | 191 | invalid_geometry:0.366, stop_first:0.471, target_first:0.162 |
|  |  |  |  | within_0.5 | 272 | invalid_geometry:0.449, stop_first:0.434, target_first:0.118 |
|  |  |  |  | within_1.0 | 396 | invalid_geometry:0.417, stop_first:0.487, target_first:0.096 |
| vwap_deviation_fade | put_wall | 1531 | invalid_geometry:0.423, stop_first:0.462, target_first:0.114 | beyond | 587 | invalid_geometry:0.429, stop_first:0.465, target_first:0.106 |
|  |  |  |  | within_0.1 | 111 | invalid_geometry:0.477, stop_first:0.414, target_first:0.108 |
|  |  |  |  | within_0.25 | 198 | invalid_geometry:0.404, stop_first:0.444, target_first:0.152 |
|  |  |  |  | within_0.5 | 265 | invalid_geometry:0.411, stop_first:0.487, target_first:0.102 |
|  |  |  |  | within_1.0 | 370 | invalid_geometry:0.416, stop_first:0.465, target_first:0.119 |
| vwap_deviation_fade | gamma_flip | 1438 | invalid_geometry:0.424, stop_first:0.465, target_first:0.112 | beyond | 1331 | invalid_geometry:0.426, stop_first:0.458, target_first:0.116 |
|  |  |  |  | within_0.1 | 11 | invalid_geometry:0.273, stop_first:0.636, target_first:0.091 |
|  |  |  |  | within_0.25 | 20 | invalid_geometry:0.450, stop_first:0.550 |
|  |  |  |  | within_0.5 | 21 | invalid_geometry:0.381, stop_first:0.619 |
|  |  |  |  | within_1.0 | 55 | invalid_geometry:0.400, stop_first:0.491, target_first:0.109 |
| vwap_deviation_fade | max_pain | 1533 | invalid_geometry:0.423, stop_first:0.463, target_first:0.114 | beyond | 643 | invalid_geometry:0.397, stop_first:0.468, target_first:0.135 |
|  |  |  |  | within_0.1 | 127 | invalid_geometry:0.465, stop_first:0.457, target_first:0.079 |
|  |  |  |  | within_0.25 | 162 | invalid_geometry:0.438, stop_first:0.444, target_first:0.117 |
|  |  |  |  | within_0.5 | 240 | invalid_geometry:0.454, stop_first:0.450, target_first:0.096 |
|  |  |  |  | within_1.0 | 361 | invalid_geometry:0.427, stop_first:0.474, target_first:0.100 |
| asia_tdo_case | key_gamma | 2202 | invalid_geometry:0.026, neither:0.110, stop_first:0.407, target_first:0.456 | beyond | 781 | invalid_geometry:0.029, neither:0.111, stop_first:0.407, target_first:0.452 |
|  |  |  |  | within_0.1 | 202 | invalid_geometry:0.015, neither:0.124, stop_first:0.406, target_first:0.455 |
|  |  |  |  | within_0.25 | 323 | invalid_geometry:0.022, neither:0.090, stop_first:0.378, target_first:0.511 |
|  |  |  |  | within_0.5 | 389 | invalid_geometry:0.026, neither:0.111, stop_first:0.445, target_first:0.419 |
|  |  |  |  | within_1.0 | 507 | invalid_geometry:0.030, neither:0.114, stop_first:0.398, target_first:0.458 |
| asia_tdo_case | call_wall | 2202 | invalid_geometry:0.026, neither:0.110, stop_first:0.407, target_first:0.456 | beyond | 821 | invalid_geometry:0.030, neither:0.112, stop_first:0.425, target_first:0.432 |
|  |  |  |  | within_0.1 | 183 | invalid_geometry:0.022, neither:0.131, stop_first:0.388, target_first:0.459 |
|  |  |  |  | within_0.25 | 288 | invalid_geometry:0.017, neither:0.108, stop_first:0.382, target_first:0.493 |
|  |  |  |  | within_0.5 | 384 | invalid_geometry:0.021, neither:0.117, stop_first:0.414, target_first:0.448 |
|  |  |  |  | within_1.0 | 526 | invalid_geometry:0.030, neither:0.095, stop_first:0.395, target_first:0.479 |
| asia_tdo_case | put_wall | 2202 | invalid_geometry:0.026, neither:0.110, stop_first:0.407, target_first:0.456 | beyond | 863 | invalid_geometry:0.030, neither:0.111, stop_first:0.411, target_first:0.447 |
|  |  |  |  | within_0.1 | 185 | invalid_geometry:0.011, neither:0.135, stop_first:0.438, target_first:0.416 |
|  |  |  |  | within_0.25 | 287 | invalid_geometry:0.021, neither:0.084, stop_first:0.418, target_first:0.477 |
|  |  |  |  | within_0.5 | 360 | invalid_geometry:0.031, neither:0.097, stop_first:0.403, target_first:0.469 |
|  |  |  |  | within_1.0 | 507 | invalid_geometry:0.026, neither:0.122, stop_first:0.387, target_first:0.465 |
| asia_tdo_case | gamma_flip | 2063 | invalid_geometry:0.025, neither:0.111, stop_first:0.412, target_first:0.452 | beyond | 1900 | invalid_geometry:0.025, neither:0.114, stop_first:0.411, target_first:0.451 |
|  |  |  |  | within_0.1 | 16 | stop_first:0.562, target_first:0.438 |
|  |  |  |  | within_0.25 | 28 | neither:0.071, stop_first:0.286, target_first:0.643 |
|  |  |  |  | within_0.5 | 60 | invalid_geometry:0.050, neither:0.067, stop_first:0.450, target_first:0.433 |
|  |  |  |  | within_1.0 | 59 | invalid_geometry:0.034, neither:0.102, stop_first:0.441, target_first:0.424 |
| asia_tdo_case | max_pain | 2204 | invalid_geometry:0.026, neither:0.110, stop_first:0.408, target_first:0.456 | beyond | 926 | invalid_geometry:0.031, neither:0.104, stop_first:0.402, target_first:0.463 |
|  |  |  |  | within_0.1 | 171 | invalid_geometry:0.006, neither:0.129, stop_first:0.456, target_first:0.409 |
|  |  |  |  | within_0.25 | 232 | invalid_geometry:0.013, neither:0.116, stop_first:0.435, target_first:0.435 |
|  |  |  |  | within_0.5 | 342 | invalid_geometry:0.020, neither:0.117, stop_first:0.368, target_first:0.494 |
|  |  |  |  | within_1.0 | 533 | invalid_geometry:0.034, neither:0.107, stop_first:0.417, target_first:0.443 |
| prior_day_level | key_gamma | 1627 | invalid_geometry:0.002, neither:0.312, stop_first:0.594, target_first:0.091 | beyond | 618 | invalid_geometry:0.003, neither:0.275, stop_first:0.621, target_first:0.100 |
|  |  |  |  | within_0.1 | 130 | invalid_geometry:0.008, neither:0.338, stop_first:0.569, target_first:0.085 |
|  |  |  |  | within_0.25 | 196 | neither:0.378, stop_first:0.536, target_first:0.087 |
|  |  |  |  | within_0.5 | 299 | neither:0.318, stop_first:0.589, target_first:0.094 |
|  |  |  |  | within_1.0 | 384 | invalid_geometry:0.003, neither:0.326, stop_first:0.594, target_first:0.078 |
| prior_day_level | call_wall | 1627 | invalid_geometry:0.002, neither:0.312, stop_first:0.594, target_first:0.091 | beyond | 658 | invalid_geometry:0.003, neither:0.290, stop_first:0.606, target_first:0.100 |
|  |  |  |  | within_0.1 | 129 | neither:0.326, stop_first:0.550, target_first:0.124 |
|  |  |  |  | within_0.25 | 173 | neither:0.370, stop_first:0.572, target_first:0.058 |
|  |  |  |  | within_0.5 | 291 | invalid_geometry:0.003, neither:0.302, stop_first:0.581, target_first:0.113 |
|  |  |  |  | within_1.0 | 376 | invalid_geometry:0.003, neither:0.327, stop_first:0.609, target_first:0.061 |
| prior_day_level | put_wall | 1627 | invalid_geometry:0.002, neither:0.312, stop_first:0.594, target_first:0.091 | beyond | 648 | invalid_geometry:0.003, neither:0.290, stop_first:0.606, target_first:0.100 |
|  |  |  |  | within_0.1 | 123 | invalid_geometry:0.008, neither:0.333, stop_first:0.561, target_first:0.098 |
|  |  |  |  | within_0.25 | 183 | neither:0.361, stop_first:0.546, target_first:0.093 |
|  |  |  |  | within_0.5 | 269 | neither:0.331, stop_first:0.580, target_first:0.089 |
|  |  |  |  | within_1.0 | 404 | invalid_geometry:0.002, neither:0.307, stop_first:0.616, target_first:0.074 |
| prior_day_level | gamma_flip | 1528 | invalid_geometry:0.003, neither:0.315, stop_first:0.594, target_first:0.088 | beyond | 1420 | invalid_geometry:0.003, neither:0.317, stop_first:0.589, target_first:0.091 |
|  |  |  |  | within_0.1 | 18 | neither:0.278, stop_first:0.667, target_first:0.056 |
|  |  |  |  | within_0.25 | 18 | neither:0.389, stop_first:0.556, target_first:0.056 |
|  |  |  |  | within_0.5 | 31 | neither:0.194, stop_first:0.710, target_first:0.097 |
|  |  |  |  | within_1.0 | 41 | neither:0.341, stop_first:0.634, target_first:0.024 |
| prior_day_level | max_pain | 1627 | invalid_geometry:0.002, neither:0.312, stop_first:0.594, target_first:0.091 | beyond | 713 | invalid_geometry:0.003, neither:0.300, stop_first:0.590, target_first:0.107 |
|  |  |  |  | within_0.1 | 109 | neither:0.330, stop_first:0.569, target_first:0.101 |
|  |  |  |  | within_0.25 | 157 | neither:0.401, stop_first:0.541, target_first:0.057 |
|  |  |  |  | within_0.5 | 250 | invalid_geometry:0.004, neither:0.344, stop_first:0.584, target_first:0.068 |
|  |  |  |  | within_1.0 | 398 | invalid_geometry:0.003, neither:0.274, stop_first:0.636, target_first:0.088 |
| prior_month_level | key_gamma | 412 | neither:0.432, stop_first:0.568 | beyond | 164 | neither:0.439, stop_first:0.561 |
|  |  |  |  | within_0.1 | 33 | neither:0.606, stop_first:0.394 |
|  |  |  |  | within_0.25 | 58 | neither:0.397, stop_first:0.603 |
|  |  |  |  | within_0.5 | 56 | neither:0.375, stop_first:0.625 |
|  |  |  |  | within_1.0 | 101 | neither:0.416, stop_first:0.584 |
| prior_month_level | call_wall | 412 | neither:0.432, stop_first:0.568 | beyond | 161 | neither:0.503, stop_first:0.497 |
|  |  |  |  | within_0.1 | 33 | neither:0.455, stop_first:0.545 |
|  |  |  |  | within_0.25 | 44 | neither:0.364, stop_first:0.636 |
|  |  |  |  | within_0.5 | 66 | neither:0.364, stop_first:0.636 |
|  |  |  |  | within_1.0 | 108 | neither:0.389, stop_first:0.611 |
| prior_month_level | put_wall | 412 | neither:0.432, stop_first:0.568 | beyond | 184 | neither:0.429, stop_first:0.571 |
|  |  |  |  | within_0.1 | 37 | neither:0.649, stop_first:0.351 |
|  |  |  |  | within_0.25 | 42 | neither:0.452, stop_first:0.548 |
|  |  |  |  | within_0.5 | 54 | neither:0.278, stop_first:0.722 |
|  |  |  |  | within_1.0 | 95 | neither:0.432, stop_first:0.568 |
| prior_month_level | gamma_flip | 390 | neither:0.428, stop_first:0.572 | beyond | 366 | neither:0.418, stop_first:0.582 |
|  |  |  |  | within_0.1 | 3 | neither:0.667, stop_first:0.333 |
|  |  |  |  | within_0.25 | 7 | neither:0.571, stop_first:0.429 |
|  |  |  |  | within_0.5 | 4 | neither:0.250, stop_first:0.750 |
|  |  |  |  | within_1.0 | 10 | neither:0.700, stop_first:0.300 |
| prior_month_level | max_pain | 412 | neither:0.432, stop_first:0.568 | beyond | 190 | neither:0.400, stop_first:0.600 |
|  |  |  |  | within_0.1 | 27 | neither:0.667, stop_first:0.333 |
|  |  |  |  | within_0.25 | 45 | neither:0.333, stop_first:0.667 |
|  |  |  |  | within_0.5 | 54 | neither:0.481, stop_first:0.519 |
|  |  |  |  | within_1.0 | 96 | neither:0.448, stop_first:0.552 |
| timed_pzone_reversal | key_gamma | 4048 | invalid_geometry:0.286, missing_future:0.000, neither:0.050, stop_first:0.604, target_first:0.059 | beyond | 1662 | invalid_geometry:0.290, missing_future:0.001, neither:0.049, stop_first:0.606, target_first:0.054 |
|  |  |  |  | within_0.1 | 280 | invalid_geometry:0.289, neither:0.043, stop_first:0.621, target_first:0.046 |
|  |  |  |  | within_0.25 | 420 | invalid_geometry:0.245, neither:0.040, stop_first:0.638, target_first:0.076 |
|  |  |  |  | within_0.5 | 669 | invalid_geometry:0.299, neither:0.054, stop_first:0.577, target_first:0.070 |
|  |  |  |  | within_1.0 | 1017 | invalid_geometry:0.287, missing_future:0.001, neither:0.055, stop_first:0.602, target_first:0.055 |
| timed_pzone_reversal | call_wall | 4048 | invalid_geometry:0.286, missing_future:0.000, neither:0.050, stop_first:0.604, target_first:0.059 | beyond | 1739 | invalid_geometry:0.293, missing_future:0.001, neither:0.047, stop_first:0.603, target_first:0.057 |
|  |  |  |  | within_0.1 | 278 | invalid_geometry:0.281, neither:0.054, stop_first:0.619, target_first:0.047 |
|  |  |  |  | within_0.25 | 402 | invalid_geometry:0.281, neither:0.067, stop_first:0.585, target_first:0.067 |
|  |  |  |  | within_0.5 | 633 | invalid_geometry:0.280, neither:0.041, stop_first:0.610, target_first:0.070 |
|  |  |  |  | within_1.0 | 996 | invalid_geometry:0.281, missing_future:0.001, neither:0.054, stop_first:0.608, target_first:0.055 |
| timed_pzone_reversal | put_wall | 4048 | invalid_geometry:0.286, missing_future:0.000, neither:0.050, stop_first:0.604, target_first:0.059 | beyond | 1817 | invalid_geometry:0.289, neither:0.052, stop_first:0.603, target_first:0.055 |
|  |  |  |  | within_0.1 | 250 | invalid_geometry:0.304, neither:0.036, stop_first:0.588, target_first:0.072 |
|  |  |  |  | within_0.25 | 406 | invalid_geometry:0.254, neither:0.037, stop_first:0.645, target_first:0.064 |
|  |  |  |  | within_0.5 | 615 | invalid_geometry:0.286, missing_future:0.002, neither:0.068, stop_first:0.585, target_first:0.059 |
|  |  |  |  | within_1.0 | 960 | invalid_geometry:0.289, missing_future:0.001, neither:0.044, stop_first:0.606, target_first:0.060 |
| timed_pzone_reversal | gamma_flip | 3833 | invalid_geometry:0.284, missing_future:0.001, neither:0.051, stop_first:0.606, target_first:0.059 | beyond | 3558 | invalid_geometry:0.284, missing_future:0.001, neither:0.050, stop_first:0.607, target_first:0.059 |
|  |  |  |  | within_0.1 | 26 | invalid_geometry:0.423, stop_first:0.462, target_first:0.115 |
|  |  |  |  | within_0.25 | 41 | invalid_geometry:0.268, neither:0.049, stop_first:0.610, target_first:0.073 |
|  |  |  |  | within_0.5 | 75 | invalid_geometry:0.293, neither:0.080, stop_first:0.547, target_first:0.080 |
|  |  |  |  | within_1.0 | 133 | invalid_geometry:0.271, neither:0.060, stop_first:0.639, target_first:0.030 |
| timed_pzone_reversal | max_pain | 4052 | invalid_geometry:0.286, missing_future:0.000, neither:0.050, stop_first:0.605, target_first:0.059 | beyond | 1957 | invalid_geometry:0.295, neither:0.048, stop_first:0.603, target_first:0.055 |
|  |  |  |  | within_0.1 | 212 | invalid_geometry:0.297, missing_future:0.005, neither:0.075, stop_first:0.590, target_first:0.033 |
|  |  |  |  | within_0.25 | 333 | invalid_geometry:0.252, neither:0.063, stop_first:0.637, target_first:0.048 |
|  |  |  |  | within_0.5 | 552 | invalid_geometry:0.255, missing_future:0.002, neither:0.053, stop_first:0.605, target_first:0.085 |
|  |  |  |  | within_1.0 | 998 | invalid_geometry:0.294, neither:0.044, stop_first:0.601, target_first:0.061 |
| continuation_retest | key_gamma | 1547 | invalid_geometry:0.646, neither:0.005, stop_first:0.222, target_first:0.127 | beyond | 517 | invalid_geometry:0.673, stop_first:0.201, target_first:0.126 |
|  |  |  |  | within_0.1 | 136 | invalid_geometry:0.632, neither:0.022, stop_first:0.243, target_first:0.103 |
|  |  |  |  | within_0.25 | 207 | invalid_geometry:0.609, neither:0.005, stop_first:0.266, target_first:0.121 |
|  |  |  |  | within_0.5 | 318 | invalid_geometry:0.660, neither:0.003, stop_first:0.220, target_first:0.116 |
|  |  |  |  | within_1.0 | 369 | invalid_geometry:0.623, neither:0.008, stop_first:0.220, target_first:0.149 |
| continuation_retest | call_wall | 1547 | invalid_geometry:0.646, neither:0.005, stop_first:0.222, target_first:0.127 | beyond | 543 | invalid_geometry:0.637, neither:0.002, stop_first:0.234, target_first:0.127 |
|  |  |  |  | within_0.1 | 122 | invalid_geometry:0.664, neither:0.016, stop_first:0.213, target_first:0.107 |
|  |  |  |  | within_0.25 | 181 | invalid_geometry:0.613, neither:0.006, stop_first:0.265, target_first:0.116 |
|  |  |  |  | within_0.5 | 308 | invalid_geometry:0.669, neither:0.006, stop_first:0.192, target_first:0.133 |
|  |  |  |  | within_1.0 | 393 | invalid_geometry:0.651, neither:0.005, stop_first:0.211, target_first:0.132 |
| continuation_retest | put_wall | 1547 | invalid_geometry:0.646, neither:0.005, stop_first:0.222, target_first:0.127 | beyond | 579 | invalid_geometry:0.660, stop_first:0.225, target_first:0.116 |
|  |  |  |  | within_0.1 | 133 | invalid_geometry:0.654, neither:0.008, stop_first:0.226, target_first:0.113 |
|  |  |  |  | within_0.25 | 194 | invalid_geometry:0.588, neither:0.005, stop_first:0.247, target_first:0.160 |
|  |  |  |  | within_0.5 | 290 | invalid_geometry:0.645, neither:0.007, stop_first:0.224, target_first:0.124 |
|  |  |  |  | within_1.0 | 351 | invalid_geometry:0.655, neither:0.011, stop_first:0.199, target_first:0.134 |
| continuation_retest | gamma_flip | 1459 | invalid_geometry:0.649, neither:0.005, stop_first:0.221, target_first:0.125 | beyond | 1336 | invalid_geometry:0.653, neither:0.005, stop_first:0.219, target_first:0.123 |
|  |  |  |  | within_0.1 | 11 | invalid_geometry:0.636, stop_first:0.182, target_first:0.182 |
|  |  |  |  | within_0.25 | 25 | invalid_geometry:0.520, stop_first:0.240, target_first:0.240 |
|  |  |  |  | within_0.5 | 31 | invalid_geometry:0.710, stop_first:0.226, target_first:0.065 |
|  |  |  |  | within_1.0 | 56 | invalid_geometry:0.589, stop_first:0.250, target_first:0.161 |
| continuation_retest | max_pain | 1549 | invalid_geometry:0.646, neither:0.005, stop_first:0.221, target_first:0.128 | beyond | 633 | invalid_geometry:0.659, neither:0.005, stop_first:0.215, target_first:0.122 |
|  |  |  |  | within_0.1 | 122 | invalid_geometry:0.631, stop_first:0.238, target_first:0.131 |
|  |  |  |  | within_0.25 | 161 | invalid_geometry:0.609, neither:0.012, stop_first:0.230, target_first:0.149 |
|  |  |  |  | within_0.5 | 233 | invalid_geometry:0.665, neither:0.004, stop_first:0.227, target_first:0.103 |
|  |  |  |  | within_1.0 | 400 | invalid_geometry:0.632, neither:0.005, stop_first:0.220, target_first:0.142 |
| trapped_buyers_retest | key_gamma | 777 | invalid_geometry:0.598, neither:0.005, stop_first:0.250, target_first:0.147 | beyond | 269 | invalid_geometry:0.639, stop_first:0.204, target_first:0.156 |
|  |  |  |  | within_0.1 | 67 | invalid_geometry:0.493, neither:0.030, stop_first:0.328, target_first:0.149 |
|  |  |  |  | within_0.25 | 93 | invalid_geometry:0.527, stop_first:0.344, target_first:0.129 |
|  |  |  |  | within_0.5 | 165 | invalid_geometry:0.606, neither:0.006, stop_first:0.267, target_first:0.121 |
|  |  |  |  | within_1.0 | 183 | invalid_geometry:0.607, neither:0.005, stop_first:0.224, target_first:0.164 |
| trapped_buyers_retest | call_wall | 777 | invalid_geometry:0.598, neither:0.005, stop_first:0.250, target_first:0.147 | beyond | 278 | invalid_geometry:0.612, stop_first:0.241, target_first:0.147 |
|  |  |  |  | within_0.1 | 61 | invalid_geometry:0.607, neither:0.033, stop_first:0.262, target_first:0.098 |
|  |  |  |  | within_0.25 | 87 | invalid_geometry:0.517, stop_first:0.333, target_first:0.149 |
|  |  |  |  | within_0.5 | 150 | invalid_geometry:0.607, neither:0.007, stop_first:0.253, target_first:0.133 |
|  |  |  |  | within_1.0 | 201 | invalid_geometry:0.607, neither:0.005, stop_first:0.219, target_first:0.169 |
| trapped_buyers_retest | put_wall | 777 | invalid_geometry:0.598, neither:0.005, stop_first:0.250, target_first:0.147 | beyond | 300 | invalid_geometry:0.603, stop_first:0.257, target_first:0.140 |
|  |  |  |  | within_0.1 | 65 | invalid_geometry:0.554, stop_first:0.292, target_first:0.154 |
|  |  |  |  | within_0.25 | 92 | invalid_geometry:0.587, stop_first:0.250, target_first:0.163 |
|  |  |  |  | within_0.5 | 152 | invalid_geometry:0.586, neither:0.013, stop_first:0.270, target_first:0.132 |
|  |  |  |  | within_1.0 | 168 | invalid_geometry:0.625, neither:0.012, stop_first:0.202, target_first:0.161 |
| trapped_buyers_retest | gamma_flip | 731 | invalid_geometry:0.599, neither:0.004, stop_first:0.249, target_first:0.148 | beyond | 668 | invalid_geometry:0.600, neither:0.004, stop_first:0.249, target_first:0.147 |
|  |  |  |  | within_0.1 | 4 | invalid_geometry:0.750, target_first:0.250 |
|  |  |  |  | within_0.25 | 18 | invalid_geometry:0.500, stop_first:0.222, target_first:0.278 |
|  |  |  |  | within_0.5 | 13 | invalid_geometry:0.692, stop_first:0.308 |
|  |  |  |  | within_1.0 | 28 | invalid_geometry:0.571, stop_first:0.286, target_first:0.143 |
| trapped_buyers_retest | max_pain | 779 | invalid_geometry:0.597, neither:0.005, stop_first:0.249, target_first:0.149 | beyond | 323 | invalid_geometry:0.604, neither:0.009, stop_first:0.245, target_first:0.142 |
|  |  |  |  | within_0.1 | 61 | invalid_geometry:0.541, stop_first:0.279, target_first:0.180 |
|  |  |  |  | within_0.25 | 78 | invalid_geometry:0.628, stop_first:0.231, target_first:0.141 |
|  |  |  |  | within_0.5 | 115 | invalid_geometry:0.626, stop_first:0.261, target_first:0.113 |
|  |  |  |  | within_1.0 | 202 | invalid_geometry:0.574, neither:0.005, stop_first:0.248, target_first:0.173 |
| kg1_retest | key_gamma | 1610 | invalid_geometry:0.424, neither:0.027, stop_first:0.527, target_first:0.021 | beyond | 603 | invalid_geometry:0.418, neither:0.032, stop_first:0.529, target_first:0.022 |
|  |  |  |  | within_0.1 | 146 | invalid_geometry:0.432, neither:0.027, stop_first:0.534, target_first:0.007 |
|  |  |  |  | within_0.25 | 182 | invalid_geometry:0.429, neither:0.016, stop_first:0.522, target_first:0.033 |
|  |  |  |  | within_0.5 | 268 | invalid_geometry:0.414, neither:0.022, stop_first:0.537, target_first:0.026 |
|  |  |  |  | within_1.0 | 411 | invalid_geometry:0.436, neither:0.029, stop_first:0.518, target_first:0.017 |
| kg1_retest | call_wall | 1610 | invalid_geometry:0.424, neither:0.027, stop_first:0.527, target_first:0.021 | beyond | 607 | invalid_geometry:0.417, neither:0.033, stop_first:0.532, target_first:0.018 |
|  |  |  |  | within_0.1 | 137 | invalid_geometry:0.460, neither:0.022, stop_first:0.474, target_first:0.044 |
|  |  |  |  | within_0.25 | 164 | invalid_geometry:0.421, neither:0.024, stop_first:0.543, target_first:0.012 |
|  |  |  |  | within_0.5 | 273 | invalid_geometry:0.425, neither:0.011, stop_first:0.546, target_first:0.018 |
|  |  |  |  | within_1.0 | 429 | invalid_geometry:0.424, neither:0.033, stop_first:0.520, target_first:0.023 |
| kg1_retest | put_wall | 1610 | invalid_geometry:0.424, neither:0.027, stop_first:0.527, target_first:0.021 | beyond | 675 | invalid_geometry:0.421, neither:0.027, stop_first:0.533, target_first:0.019 |
|  |  |  |  | within_0.1 | 137 | invalid_geometry:0.416, neither:0.036, stop_first:0.533, target_first:0.015 |
|  |  |  |  | within_0.25 | 158 | invalid_geometry:0.443, neither:0.013, stop_first:0.500, target_first:0.044 |
|  |  |  |  | within_0.5 | 282 | invalid_geometry:0.429, neither:0.021, stop_first:0.518, target_first:0.032 |
|  |  |  |  | within_1.0 | 358 | invalid_geometry:0.422, neither:0.036, stop_first:0.534, target_first:0.008 |
| kg1_retest | gamma_flip | 1536 | invalid_geometry:0.427, neither:0.027, stop_first:0.525, target_first:0.021 | beyond | 1415 | invalid_geometry:0.429, neither:0.028, stop_first:0.524, target_first:0.020 |
|  |  |  |  | within_0.1 | 14 | invalid_geometry:0.357, stop_first:0.643 |
|  |  |  |  | within_0.25 | 19 | invalid_geometry:0.421, neither:0.105, stop_first:0.474 |
|  |  |  |  | within_0.5 | 23 | invalid_geometry:0.435, stop_first:0.565 |
|  |  |  |  | within_1.0 | 65 | invalid_geometry:0.400, neither:0.015, stop_first:0.523, target_first:0.062 |
| kg1_retest | max_pain | 1610 | invalid_geometry:0.424, neither:0.027, stop_first:0.527, target_first:0.021 | beyond | 710 | invalid_geometry:0.417, neither:0.035, stop_first:0.530, target_first:0.018 |
|  |  |  |  | within_0.1 | 114 | invalid_geometry:0.456, neither:0.009, stop_first:0.482, target_first:0.053 |
|  |  |  |  | within_0.25 | 168 | invalid_geometry:0.452, neither:0.018, stop_first:0.518, target_first:0.012 |
|  |  |  |  | within_0.5 | 227 | invalid_geometry:0.410, neither:0.031, stop_first:0.537, target_first:0.022 |
|  |  |  |  | within_1.0 | 391 | invalid_geometry:0.425, neither:0.020, stop_first:0.535, target_first:0.020 |
| failed_auction_return | key_gamma | 1676 | invalid_geometry:0.425, neither:0.005, stop_first:0.249, target_first:0.321 | beyond | 544 | invalid_geometry:0.458, neither:0.011, stop_first:0.233, target_first:0.298 |
|  |  |  |  | within_0.1 | 170 | invalid_geometry:0.318, stop_first:0.306, target_first:0.376 |
|  |  |  |  | within_0.25 | 229 | invalid_geometry:0.476, stop_first:0.205, target_first:0.319 |
|  |  |  |  | within_0.5 | 338 | invalid_geometry:0.388, stop_first:0.266, target_first:0.346 |
|  |  |  |  | within_1.0 | 395 | invalid_geometry:0.428, neither:0.005, stop_first:0.258, target_first:0.309 |
| failed_auction_return | call_wall | 1676 | invalid_geometry:0.425, neither:0.005, stop_first:0.249, target_first:0.321 | beyond | 576 | invalid_geometry:0.434, neither:0.010, stop_first:0.224, target_first:0.332 |
|  |  |  |  | within_0.1 | 150 | invalid_geometry:0.413, stop_first:0.260, target_first:0.327 |
|  |  |  |  | within_0.25 | 209 | invalid_geometry:0.426, stop_first:0.239, target_first:0.335 |
|  |  |  |  | within_0.5 | 319 | invalid_geometry:0.408, stop_first:0.276, target_first:0.317 |
|  |  |  |  | within_1.0 | 422 | invalid_geometry:0.429, neither:0.005, stop_first:0.265, target_first:0.301 |
| failed_auction_return | put_wall | 1676 | invalid_geometry:0.425, neither:0.005, stop_first:0.249, target_first:0.321 | beyond | 609 | invalid_geometry:0.447, neither:0.010, stop_first:0.245, target_first:0.299 |
|  |  |  |  | within_0.1 | 151 | invalid_geometry:0.358, stop_first:0.291, target_first:0.351 |
|  |  |  |  | within_0.25 | 221 | invalid_geometry:0.425, stop_first:0.226, target_first:0.348 |
|  |  |  |  | within_0.5 | 308 | invalid_geometry:0.403, neither:0.003, stop_first:0.260, target_first:0.334 |
|  |  |  |  | within_1.0 | 387 | invalid_geometry:0.434, neither:0.003, stop_first:0.245, target_first:0.318 |
| failed_auction_return | gamma_flip | 1578 | invalid_geometry:0.424, neither:0.005, stop_first:0.251, target_first:0.320 | beyond | 1449 | invalid_geometry:0.422, neither:0.006, stop_first:0.255, target_first:0.317 |
|  |  |  |  | within_0.1 | 16 | invalid_geometry:0.500, stop_first:0.250, target_first:0.250 |
|  |  |  |  | within_0.25 | 24 | invalid_geometry:0.458, stop_first:0.250, target_first:0.292 |
|  |  |  |  | within_0.5 | 32 | invalid_geometry:0.375, stop_first:0.219, target_first:0.406 |
|  |  |  |  | within_1.0 | 57 | invalid_geometry:0.456, stop_first:0.158, target_first:0.386 |
| failed_auction_return | max_pain | 1678 | invalid_geometry:0.426, neither:0.005, stop_first:0.249, target_first:0.321 | beyond | 673 | invalid_geometry:0.447, neither:0.009, stop_first:0.238, target_first:0.306 |
|  |  |  |  | within_0.1 | 132 | invalid_geometry:0.386, stop_first:0.258, target_first:0.356 |
|  |  |  |  | within_0.25 | 170 | invalid_geometry:0.424, stop_first:0.259, target_first:0.318 |
|  |  |  |  | within_0.5 | 277 | invalid_geometry:0.419, neither:0.004, stop_first:0.245, target_first:0.332 |
|  |  |  |  | within_1.0 | 426 | invalid_geometry:0.408, neither:0.002, stop_first:0.263, target_first:0.326 |
| poc_traversal | key_gamma | 1431 | invalid_geometry:0.498, neither:0.008, stop_first:0.165, target_first:0.329 | beyond | 464 | invalid_geometry:0.502, neither:0.011, stop_first:0.155, target_first:0.332 |
|  |  |  |  | within_0.1 | 159 | invalid_geometry:0.465, neither:0.019, stop_first:0.189, target_first:0.327 |
|  |  |  |  | within_0.25 | 190 | invalid_geometry:0.511, stop_first:0.163, target_first:0.326 |
|  |  |  |  | within_0.5 | 291 | invalid_geometry:0.478, neither:0.007, stop_first:0.179, target_first:0.337 |
|  |  |  |  | within_1.0 | 327 | invalid_geometry:0.517, neither:0.006, stop_first:0.156, target_first:0.321 |
| poc_traversal | call_wall | 1431 | invalid_geometry:0.498, neither:0.008, stop_first:0.165, target_first:0.329 | beyond | 483 | invalid_geometry:0.499, neither:0.010, stop_first:0.161, target_first:0.329 |
|  |  |  |  | within_0.1 | 144 | invalid_geometry:0.507, neither:0.007, stop_first:0.174, target_first:0.312 |
|  |  |  |  | within_0.25 | 175 | invalid_geometry:0.520, stop_first:0.137, target_first:0.343 |
|  |  |  |  | within_0.5 | 275 | invalid_geometry:0.476, neither:0.007, stop_first:0.178, target_first:0.338 |
|  |  |  |  | within_1.0 | 354 | invalid_geometry:0.497, neither:0.011, stop_first:0.169, target_first:0.322 |
| poc_traversal | put_wall | 1431 | invalid_geometry:0.498, neither:0.008, stop_first:0.165, target_first:0.329 | beyond | 521 | invalid_geometry:0.499, neither:0.012, stop_first:0.157, target_first:0.332 |
|  |  |  |  | within_0.1 | 135 | invalid_geometry:0.526, neither:0.022, stop_first:0.141, target_first:0.311 |
|  |  |  |  | within_0.25 | 182 | invalid_geometry:0.489, stop_first:0.181, target_first:0.330 |
|  |  |  |  | within_0.5 | 260 | invalid_geometry:0.504, neither:0.004, stop_first:0.165, target_first:0.327 |
|  |  |  |  | within_1.0 | 333 | invalid_geometry:0.483, neither:0.006, stop_first:0.177, target_first:0.333 |
| poc_traversal | gamma_flip | 1353 | invalid_geometry:0.497, neither:0.009, stop_first:0.167, target_first:0.327 | beyond | 1249 | invalid_geometry:0.492, neither:0.009, stop_first:0.170, target_first:0.329 |
|  |  |  |  | within_0.1 | 11 | invalid_geometry:0.545, stop_first:0.182, target_first:0.273 |
|  |  |  |  | within_0.25 | 18 | invalid_geometry:0.556, stop_first:0.111, target_first:0.333 |
|  |  |  |  | within_0.5 | 27 | invalid_geometry:0.556, neither:0.037, stop_first:0.148, target_first:0.259 |
|  |  |  |  | within_1.0 | 48 | invalid_geometry:0.562, stop_first:0.125, target_first:0.312 |
| poc_traversal | max_pain | 1431 | invalid_geometry:0.498, neither:0.008, stop_first:0.165, target_first:0.329 | beyond | 590 | invalid_geometry:0.517, neither:0.010, stop_first:0.151, target_first:0.322 |
|  |  |  |  | within_0.1 | 111 | invalid_geometry:0.423, stop_first:0.189, target_first:0.387 |
|  |  |  |  | within_0.25 | 155 | invalid_geometry:0.548, stop_first:0.148, target_first:0.303 |
|  |  |  |  | within_0.5 | 226 | invalid_geometry:0.469, neither:0.013, stop_first:0.186, target_first:0.332 |
|  |  |  |  | within_1.0 | 349 | invalid_geometry:0.484, neither:0.009, stop_first:0.175, target_first:0.332 |
| absorption_reward_retest | key_gamma | 1420 | invalid_geometry:0.542, stop_first:0.318, target_first:0.141 | beyond | 478 | invalid_geometry:0.567, stop_first:0.308, target_first:0.126 |
|  |  |  |  | within_0.1 | 125 | invalid_geometry:0.504, stop_first:0.336, target_first:0.160 |
|  |  |  |  | within_0.25 | 190 | invalid_geometry:0.542, stop_first:0.316, target_first:0.142 |
|  |  |  |  | within_0.5 | 282 | invalid_geometry:0.528, stop_first:0.348, target_first:0.124 |
|  |  |  |  | within_1.0 | 345 | invalid_geometry:0.530, stop_first:0.301, target_first:0.168 |
| absorption_reward_retest | call_wall | 1420 | invalid_geometry:0.542, stop_first:0.318, target_first:0.141 | beyond | 510 | invalid_geometry:0.582, stop_first:0.310, target_first:0.108 |
|  |  |  |  | within_0.1 | 115 | invalid_geometry:0.504, stop_first:0.278, target_first:0.217 |
|  |  |  |  | within_0.25 | 166 | invalid_geometry:0.506, stop_first:0.337, target_first:0.157 |
|  |  |  |  | within_0.5 | 268 | invalid_geometry:0.552, stop_first:0.325, target_first:0.123 |
|  |  |  |  | within_1.0 | 361 | invalid_geometry:0.504, stop_first:0.327, target_first:0.169 |
| absorption_reward_retest | put_wall | 1420 | invalid_geometry:0.542, stop_first:0.318, target_first:0.141 | beyond | 516 | invalid_geometry:0.554, stop_first:0.306, target_first:0.140 |
|  |  |  |  | within_0.1 | 107 | invalid_geometry:0.542, stop_first:0.327, target_first:0.131 |
|  |  |  |  | within_0.25 | 197 | invalid_geometry:0.543, stop_first:0.315, target_first:0.142 |
|  |  |  |  | within_0.5 | 260 | invalid_geometry:0.492, stop_first:0.365, target_first:0.142 |
|  |  |  |  | within_1.0 | 340 | invalid_geometry:0.559, stop_first:0.297, target_first:0.144 |
| absorption_reward_retest | gamma_flip | 1333 | invalid_geometry:0.549, stop_first:0.314, target_first:0.137 | beyond | 1220 | invalid_geometry:0.543, stop_first:0.319, target_first:0.139 |
|  |  |  |  | within_0.1 | 4 | invalid_geometry:1.000 |
|  |  |  |  | within_0.25 | 20 | invalid_geometry:0.500, stop_first:0.300, target_first:0.200 |
|  |  |  |  | within_0.5 | 31 | invalid_geometry:0.710, stop_first:0.226, target_first:0.065 |
|  |  |  |  | within_1.0 | 58 | invalid_geometry:0.586, stop_first:0.276, target_first:0.138 |
| absorption_reward_retest | max_pain | 1424 | invalid_geometry:0.540, stop_first:0.320, target_first:0.140 | beyond | 566 | invalid_geometry:0.583, stop_first:0.283, target_first:0.134 |
|  |  |  |  | within_0.1 | 120 | invalid_geometry:0.467, stop_first:0.333, target_first:0.200 |
|  |  |  |  | within_0.25 | 127 | invalid_geometry:0.567, stop_first:0.362, target_first:0.071 |
|  |  |  |  | within_0.5 | 238 | invalid_geometry:0.504, stop_first:0.345, target_first:0.151 |
|  |  |  |  | within_1.0 | 373 | invalid_geometry:0.512, stop_first:0.340, target_first:0.147 |
| balance_failure_fade | key_gamma | 1420 | invalid_geometry:0.537, stop_first:0.322, target_first:0.141 | beyond | 479 | invalid_geometry:0.557, stop_first:0.317, target_first:0.125 |
|  |  |  |  | within_0.1 | 124 | invalid_geometry:0.484, stop_first:0.355, target_first:0.161 |
|  |  |  |  | within_0.25 | 192 | invalid_geometry:0.542, stop_first:0.318, target_first:0.141 |
|  |  |  |  | within_0.5 | 281 | invalid_geometry:0.520, stop_first:0.356, target_first:0.125 |
|  |  |  |  | within_1.0 | 344 | invalid_geometry:0.541, stop_first:0.291, target_first:0.169 |
| balance_failure_fade | call_wall | 1420 | invalid_geometry:0.537, stop_first:0.322, target_first:0.141 | beyond | 511 | invalid_geometry:0.571, stop_first:0.321, target_first:0.108 |
|  |  |  |  | within_0.1 | 115 | invalid_geometry:0.487, stop_first:0.296, target_first:0.217 |
|  |  |  |  | within_0.25 | 166 | invalid_geometry:0.512, stop_first:0.331, target_first:0.157 |
|  |  |  |  | within_0.5 | 267 | invalid_geometry:0.547, stop_first:0.330, target_first:0.124 |
|  |  |  |  | within_1.0 | 361 | invalid_geometry:0.510, stop_first:0.321, target_first:0.169 |
| balance_failure_fade | put_wall | 1420 | invalid_geometry:0.537, stop_first:0.322, target_first:0.141 | beyond | 516 | invalid_geometry:0.550, stop_first:0.310, target_first:0.140 |
|  |  |  |  | within_0.1 | 106 | invalid_geometry:0.538, stop_first:0.330, target_first:0.132 |
|  |  |  |  | within_0.25 | 199 | invalid_geometry:0.538, stop_first:0.322, target_first:0.141 |
|  |  |  |  | within_0.5 | 259 | invalid_geometry:0.483, stop_first:0.375, target_first:0.143 |
|  |  |  |  | within_1.0 | 340 | invalid_geometry:0.559, stop_first:0.297, target_first:0.144 |
| balance_failure_fade | gamma_flip | 1333 | invalid_geometry:0.545, stop_first:0.317, target_first:0.137 | beyond | 1220 | invalid_geometry:0.539, stop_first:0.322, target_first:0.139 |
|  |  |  |  | within_0.1 | 4 | invalid_geometry:1.000 |
|  |  |  |  | within_0.25 | 20 | invalid_geometry:0.500, stop_first:0.300, target_first:0.200 |
|  |  |  |  | within_0.5 | 33 | invalid_geometry:0.667, stop_first:0.273, target_first:0.061 |
|  |  |  |  | within_1.0 | 56 | invalid_geometry:0.589, stop_first:0.268, target_first:0.143 |
| balance_failure_fade | max_pain | 1424 | invalid_geometry:0.536, stop_first:0.324, target_first:0.140 | beyond | 565 | invalid_geometry:0.581, stop_first:0.285, target_first:0.135 |
|  |  |  |  | within_0.1 | 120 | invalid_geometry:0.450, stop_first:0.350, target_first:0.200 |
|  |  |  |  | within_0.25 | 127 | invalid_geometry:0.575, stop_first:0.354, target_first:0.071 |
|  |  |  |  | within_0.5 | 237 | invalid_geometry:0.498, stop_first:0.350, target_first:0.152 |
|  |  |  |  | within_1.0 | 375 | invalid_geometry:0.507, stop_first:0.347, target_first:0.147 |
| clean_squeeze | key_gamma | 1420 | invalid_geometry:0.546, stop_first:0.312, target_first:0.142 | beyond | 478 | invalid_geometry:0.569, stop_first:0.303, target_first:0.128 |
|  |  |  |  | within_0.1 | 124 | invalid_geometry:0.524, stop_first:0.315, target_first:0.161 |
|  |  |  |  | within_0.25 | 192 | invalid_geometry:0.542, stop_first:0.312, target_first:0.146 |
|  |  |  |  | within_0.5 | 281 | invalid_geometry:0.527, stop_first:0.345, target_first:0.128 |
|  |  |  |  | within_1.0 | 345 | invalid_geometry:0.539, stop_first:0.296, target_first:0.165 |
| clean_squeeze | call_wall | 1420 | invalid_geometry:0.546, stop_first:0.312, target_first:0.142 | beyond | 510 | invalid_geometry:0.584, stop_first:0.304, target_first:0.112 |
|  |  |  |  | within_0.1 | 115 | invalid_geometry:0.522, stop_first:0.261, target_first:0.217 |
|  |  |  |  | within_0.25 | 165 | invalid_geometry:0.521, stop_first:0.327, target_first:0.152 |
|  |  |  |  | within_0.5 | 268 | invalid_geometry:0.552, stop_first:0.325, target_first:0.123 |
|  |  |  |  | within_1.0 | 362 | invalid_geometry:0.506, stop_first:0.323, target_first:0.171 |
| clean_squeeze | put_wall | 1420 | invalid_geometry:0.546, stop_first:0.312, target_first:0.142 | beyond | 516 | invalid_geometry:0.560, stop_first:0.300, target_first:0.140 |
|  |  |  |  | within_0.1 | 106 | invalid_geometry:0.547, stop_first:0.321, target_first:0.132 |
|  |  |  |  | within_0.25 | 199 | invalid_geometry:0.543, stop_first:0.307, target_first:0.151 |
|  |  |  |  | within_0.5 | 259 | invalid_geometry:0.490, stop_first:0.363, target_first:0.147 |
|  |  |  |  | within_1.0 | 340 | invalid_geometry:0.568, stop_first:0.291, target_first:0.141 |
| clean_squeeze | gamma_flip | 1333 | invalid_geometry:0.554, stop_first:0.308, target_first:0.139 | beyond | 1220 | invalid_geometry:0.548, stop_first:0.311, target_first:0.140 |
|  |  |  |  | within_0.1 | 4 | invalid_geometry:1.000 |
|  |  |  |  | within_0.25 | 20 | invalid_geometry:0.450, stop_first:0.350, target_first:0.200 |
|  |  |  |  | within_0.5 | 31 | invalid_geometry:0.710, stop_first:0.226, target_first:0.065 |
|  |  |  |  | within_1.0 | 58 | invalid_geometry:0.586, stop_first:0.276, target_first:0.138 |
| clean_squeeze | max_pain | 1424 | invalid_geometry:0.544, stop_first:0.314, target_first:0.142 | beyond | 566 | invalid_geometry:0.587, stop_first:0.279, target_first:0.134 |
|  |  |  |  | within_0.1 | 120 | invalid_geometry:0.475, stop_first:0.317, target_first:0.208 |
|  |  |  |  | within_0.25 | 127 | invalid_geometry:0.575, stop_first:0.346, target_first:0.079 |
|  |  |  |  | within_0.5 | 238 | invalid_geometry:0.508, stop_first:0.340, target_first:0.151 |
|  |  |  |  | within_1.0 | 373 | invalid_geometry:0.515, stop_first:0.338, target_first:0.147 |
| dom_rejection | key_gamma | 1420 | invalid_geometry:0.489, stop_first:0.377, target_first:0.134 | beyond | 478 | invalid_geometry:0.527, stop_first:0.356, target_first:0.117 |
|  |  |  |  | within_0.1 | 124 | invalid_geometry:0.476, stop_first:0.363, target_first:0.161 |
|  |  |  |  | within_0.25 | 193 | invalid_geometry:0.466, stop_first:0.404, target_first:0.130 |
|  |  |  |  | within_0.5 | 276 | invalid_geometry:0.471, stop_first:0.406, target_first:0.123 |
|  |  |  |  | within_1.0 | 349 | invalid_geometry:0.470, stop_first:0.372, target_first:0.158 |
| dom_rejection | call_wall | 1420 | invalid_geometry:0.489, stop_first:0.377, target_first:0.134 | beyond | 510 | invalid_geometry:0.529, stop_first:0.363, target_first:0.108 |
|  |  |  |  | within_0.1 | 113 | invalid_geometry:0.469, stop_first:0.319, target_first:0.212 |
|  |  |  |  | within_0.25 | 169 | invalid_geometry:0.444, stop_first:0.420, target_first:0.136 |
|  |  |  |  | within_0.5 | 267 | invalid_geometry:0.498, stop_first:0.382, target_first:0.120 |
|  |  |  |  | within_1.0 | 361 | invalid_geometry:0.454, stop_first:0.391, target_first:0.155 |
| dom_rejection | put_wall | 1420 | invalid_geometry:0.489, stop_first:0.377, target_first:0.134 | beyond | 515 | invalid_geometry:0.517, stop_first:0.359, target_first:0.124 |
|  |  |  |  | within_0.1 | 107 | invalid_geometry:0.523, stop_first:0.346, target_first:0.131 |
|  |  |  |  | within_0.25 | 200 | invalid_geometry:0.495, stop_first:0.365, target_first:0.140 |
|  |  |  |  | within_0.5 | 254 | invalid_geometry:0.433, stop_first:0.429, target_first:0.138 |
|  |  |  |  | within_1.0 | 344 | invalid_geometry:0.477, stop_first:0.381, target_first:0.142 |
| dom_rejection | gamma_flip | 1333 | invalid_geometry:0.495, stop_first:0.374, target_first:0.131 | beyond | 1220 | invalid_geometry:0.492, stop_first:0.377, target_first:0.131 |
|  |  |  |  | within_0.1 | 4 | invalid_geometry:0.750, stop_first:0.250 |
|  |  |  |  | within_0.25 | 21 | invalid_geometry:0.429, stop_first:0.381, target_first:0.190 |
|  |  |  |  | within_0.5 | 31 | invalid_geometry:0.581, stop_first:0.355, target_first:0.065 |
|  |  |  |  | within_1.0 | 57 | invalid_geometry:0.526, stop_first:0.316, target_first:0.158 |
| dom_rejection | max_pain | 1424 | invalid_geometry:0.488, stop_first:0.379, target_first:0.133 | beyond | 563 | invalid_geometry:0.531, stop_first:0.345, target_first:0.124 |
|  |  |  |  | within_0.1 | 119 | invalid_geometry:0.395, stop_first:0.420, target_first:0.185 |
|  |  |  |  | within_0.25 | 128 | invalid_geometry:0.492, stop_first:0.438, target_first:0.070 |
|  |  |  |  | within_0.5 | 235 | invalid_geometry:0.464, stop_first:0.400, target_first:0.136 |
|  |  |  |  | within_1.0 | 379 | invalid_geometry:0.467, stop_first:0.383, target_first:0.150 |
| footprint_confirmed_reaction | key_gamma | 1420 | invalid_geometry:0.489, stop_first:0.375, target_first:0.135 | beyond | 478 | invalid_geometry:0.527, stop_first:0.356, target_first:0.117 |
|  |  |  |  | within_0.1 | 124 | invalid_geometry:0.476, stop_first:0.363, target_first:0.161 |
|  |  |  |  | within_0.25 | 193 | invalid_geometry:0.466, stop_first:0.399, target_first:0.135 |
|  |  |  |  | within_0.5 | 276 | invalid_geometry:0.471, stop_first:0.406, target_first:0.123 |
|  |  |  |  | within_1.0 | 349 | invalid_geometry:0.470, stop_first:0.370, target_first:0.160 |
| footprint_confirmed_reaction | call_wall | 1420 | invalid_geometry:0.489, stop_first:0.375, target_first:0.135 | beyond | 510 | invalid_geometry:0.529, stop_first:0.363, target_first:0.108 |
|  |  |  |  | within_0.1 | 113 | invalid_geometry:0.469, stop_first:0.319, target_first:0.212 |
|  |  |  |  | within_0.25 | 169 | invalid_geometry:0.444, stop_first:0.414, target_first:0.142 |
|  |  |  |  | within_0.5 | 267 | invalid_geometry:0.498, stop_first:0.382, target_first:0.120 |
|  |  |  |  | within_1.0 | 361 | invalid_geometry:0.454, stop_first:0.388, target_first:0.158 |
| footprint_confirmed_reaction | put_wall | 1420 | invalid_geometry:0.489, stop_first:0.375, target_first:0.135 | beyond | 515 | invalid_geometry:0.517, stop_first:0.357, target_first:0.126 |
|  |  |  |  | within_0.1 | 107 | invalid_geometry:0.523, stop_first:0.346, target_first:0.131 |
|  |  |  |  | within_0.25 | 200 | invalid_geometry:0.495, stop_first:0.365, target_first:0.140 |
|  |  |  |  | within_0.5 | 254 | invalid_geometry:0.433, stop_first:0.429, target_first:0.138 |
|  |  |  |  | within_1.0 | 344 | invalid_geometry:0.477, stop_first:0.378, target_first:0.145 |
| footprint_confirmed_reaction | gamma_flip | 1333 | invalid_geometry:0.495, stop_first:0.372, target_first:0.133 | beyond | 1220 | invalid_geometry:0.492, stop_first:0.375, target_first:0.133 |
|  |  |  |  | within_0.1 | 4 | invalid_geometry:0.750, stop_first:0.250 |
|  |  |  |  | within_0.25 | 21 | invalid_geometry:0.429, stop_first:0.381, target_first:0.190 |
|  |  |  |  | within_0.5 | 31 | invalid_geometry:0.581, stop_first:0.355, target_first:0.065 |
|  |  |  |  | within_1.0 | 57 | invalid_geometry:0.526, stop_first:0.316, target_first:0.158 |
| footprint_confirmed_reaction | max_pain | 1424 | invalid_geometry:0.488, stop_first:0.377, target_first:0.135 | beyond | 563 | invalid_geometry:0.531, stop_first:0.343, target_first:0.126 |
|  |  |  |  | within_0.1 | 119 | invalid_geometry:0.395, stop_first:0.412, target_first:0.193 |
|  |  |  |  | within_0.25 | 128 | invalid_geometry:0.492, stop_first:0.438, target_first:0.070 |
|  |  |  |  | within_0.5 | 235 | invalid_geometry:0.464, stop_first:0.400, target_first:0.136 |
|  |  |  |  | within_1.0 | 379 | invalid_geometry:0.467, stop_first:0.383, target_first:0.150 |
| ofm_aggressive | key_gamma | 1420 | invalid_geometry:0.553, stop_first:0.305, target_first:0.142 | beyond | 478 | invalid_geometry:0.573, stop_first:0.297, target_first:0.130 |
|  |  |  |  | within_0.1 | 124 | invalid_geometry:0.524, stop_first:0.315, target_first:0.161 |
|  |  |  |  | within_0.25 | 191 | invalid_geometry:0.560, stop_first:0.298, target_first:0.141 |
|  |  |  |  | within_0.5 | 282 | invalid_geometry:0.535, stop_first:0.337, target_first:0.128 |
|  |  |  |  | within_1.0 | 345 | invalid_geometry:0.545, stop_first:0.290, target_first:0.165 |
| ofm_aggressive | call_wall | 1420 | invalid_geometry:0.553, stop_first:0.305, target_first:0.142 | beyond | 510 | invalid_geometry:0.590, stop_first:0.298, target_first:0.112 |
|  |  |  |  | within_0.1 | 115 | invalid_geometry:0.522, stop_first:0.261, target_first:0.217 |
|  |  |  |  | within_0.25 | 166 | invalid_geometry:0.536, stop_first:0.313, target_first:0.151 |
|  |  |  |  | within_0.5 | 267 | invalid_geometry:0.558, stop_first:0.315, target_first:0.127 |
|  |  |  |  | within_1.0 | 362 | invalid_geometry:0.514, stop_first:0.318, target_first:0.169 |
| ofm_aggressive | put_wall | 1420 | invalid_geometry:0.553, stop_first:0.305, target_first:0.142 | beyond | 517 | invalid_geometry:0.567, stop_first:0.292, target_first:0.141 |
|  |  |  |  | within_0.1 | 107 | invalid_geometry:0.542, stop_first:0.327, target_first:0.131 |
|  |  |  |  | within_0.25 | 197 | invalid_geometry:0.553, stop_first:0.299, target_first:0.147 |
|  |  |  |  | within_0.5 | 260 | invalid_geometry:0.500, stop_first:0.354, target_first:0.146 |
|  |  |  |  | within_1.0 | 339 | invalid_geometry:0.575, stop_first:0.283, target_first:0.142 |
| ofm_aggressive | gamma_flip | 1333 | invalid_geometry:0.561, stop_first:0.300, target_first:0.139 | beyond | 1220 | invalid_geometry:0.556, stop_first:0.304, target_first:0.140 |
|  |  |  |  | within_0.1 | 4 | invalid_geometry:1.000 |
|  |  |  |  | within_0.25 | 20 | invalid_geometry:0.500, stop_first:0.300, target_first:0.200 |
|  |  |  |  | within_0.5 | 31 | invalid_geometry:0.710, stop_first:0.226, target_first:0.065 |
|  |  |  |  | within_1.0 | 58 | invalid_geometry:0.586, stop_first:0.276, target_first:0.138 |
| ofm_aggressive | max_pain | 1424 | invalid_geometry:0.551, stop_first:0.307, target_first:0.142 | beyond | 566 | invalid_geometry:0.592, stop_first:0.270, target_first:0.138 |
|  |  |  |  | within_0.1 | 120 | invalid_geometry:0.483, stop_first:0.317, target_first:0.200 |
|  |  |  |  | within_0.25 | 127 | invalid_geometry:0.583, stop_first:0.339, target_first:0.079 |
|  |  |  |  | within_0.5 | 237 | invalid_geometry:0.515, stop_first:0.333, target_first:0.152 |
|  |  |  |  | within_1.0 | 374 | invalid_geometry:0.524, stop_first:0.332, target_first:0.144 |
| stop_four_stage | key_gamma | 1420 | invalid_geometry:0.542, stop_first:0.316, target_first:0.142 | beyond | 479 | invalid_geometry:0.553, stop_first:0.317, target_first:0.129 |
|  |  |  |  | within_0.1 | 124 | invalid_geometry:0.508, stop_first:0.331, target_first:0.161 |
|  |  |  |  | within_0.25 | 190 | invalid_geometry:0.558, stop_first:0.300, target_first:0.142 |
|  |  |  |  | within_0.5 | 283 | invalid_geometry:0.527, stop_first:0.346, target_first:0.127 |
|  |  |  |  | within_1.0 | 344 | invalid_geometry:0.541, stop_first:0.294, target_first:0.166 |
| stop_four_stage | call_wall | 1420 | invalid_geometry:0.542, stop_first:0.316, target_first:0.142 | beyond | 511 | invalid_geometry:0.569, stop_first:0.319, target_first:0.112 |
|  |  |  |  | within_0.1 | 115 | invalid_geometry:0.513, stop_first:0.270, target_first:0.217 |
|  |  |  |  | within_0.25 | 165 | invalid_geometry:0.533, stop_first:0.315, target_first:0.152 |
|  |  |  |  | within_0.5 | 269 | invalid_geometry:0.546, stop_first:0.327, target_first:0.126 |
|  |  |  |  | within_1.0 | 360 | invalid_geometry:0.511, stop_first:0.319, target_first:0.169 |
| stop_four_stage | put_wall | 1420 | invalid_geometry:0.542, stop_first:0.316, target_first:0.142 | beyond | 517 | invalid_geometry:0.549, stop_first:0.309, target_first:0.141 |
|  |  |  |  | within_0.1 | 107 | invalid_geometry:0.533, stop_first:0.336, target_first:0.131 |
|  |  |  |  | within_0.25 | 198 | invalid_geometry:0.545, stop_first:0.303, target_first:0.152 |
|  |  |  |  | within_0.5 | 259 | invalid_geometry:0.490, stop_first:0.367, target_first:0.143 |
|  |  |  |  | within_1.0 | 339 | invalid_geometry:0.569, stop_first:0.289, target_first:0.142 |
| stop_four_stage | gamma_flip | 1333 | invalid_geometry:0.549, stop_first:0.312, target_first:0.139 | beyond | 1220 | invalid_geometry:0.544, stop_first:0.316, target_first:0.140 |
|  |  |  |  | within_0.1 | 4 | invalid_geometry:1.000 |
|  |  |  |  | within_0.25 | 20 | invalid_geometry:0.500, stop_first:0.300, target_first:0.200 |
|  |  |  |  | within_0.5 | 32 | invalid_geometry:0.656, stop_first:0.281, target_first:0.062 |
|  |  |  |  | within_1.0 | 57 | invalid_geometry:0.579, stop_first:0.281, target_first:0.140 |
| stop_four_stage | max_pain | 1424 | invalid_geometry:0.540, stop_first:0.318, target_first:0.142 | beyond | 565 | invalid_geometry:0.579, stop_first:0.283, target_first:0.138 |
|  |  |  |  | within_0.1 | 120 | invalid_geometry:0.475, stop_first:0.325, target_first:0.200 |
|  |  |  |  | within_0.25 | 127 | invalid_geometry:0.575, stop_first:0.346, target_first:0.079 |
|  |  |  |  | within_0.5 | 237 | invalid_geometry:0.502, stop_first:0.346, target_first:0.152 |
|  |  |  |  | within_1.0 | 375 | invalid_geometry:0.515, stop_first:0.341, target_first:0.144 |
| prior_week_level | key_gamma | 810 | neither:0.475, stop_first:0.520, target_first:0.005 | beyond | 313 | neither:0.457, stop_first:0.530, target_first:0.013 |
|  |  |  |  | within_0.1 | 53 | neither:0.528, stop_first:0.472 |
|  |  |  |  | within_0.25 | 105 | neither:0.476, stop_first:0.524 |
|  |  |  |  | within_0.5 | 144 | neither:0.479, stop_first:0.521 |
|  |  |  |  | within_1.0 | 195 | neither:0.487, stop_first:0.513 |
| prior_week_level | call_wall | 810 | neither:0.475, stop_first:0.520, target_first:0.005 | beyond | 338 | neither:0.420, stop_first:0.571, target_first:0.009 |
|  |  |  |  | within_0.1 | 49 | neither:0.531, stop_first:0.469 |
|  |  |  |  | within_0.25 | 83 | neither:0.446, stop_first:0.554 |
|  |  |  |  | within_0.5 | 163 | neither:0.521, stop_first:0.479 |
|  |  |  |  | within_1.0 | 177 | neither:0.537, stop_first:0.458, target_first:0.006 |
| prior_week_level | put_wall | 810 | neither:0.475, stop_first:0.520, target_first:0.005 | beyond | 335 | neither:0.481, stop_first:0.513, target_first:0.006 |
|  |  |  |  | within_0.1 | 60 | neither:0.450, stop_first:0.550 |
|  |  |  |  | within_0.25 | 93 | neither:0.505, stop_first:0.495 |
|  |  |  |  | within_0.5 | 119 | neither:0.496, stop_first:0.496, target_first:0.008 |
|  |  |  |  | within_1.0 | 203 | neither:0.448, stop_first:0.547, target_first:0.005 |
| prior_week_level | gamma_flip | 766 | neither:0.477, stop_first:0.518, target_first:0.005 | beyond | 702 | neither:0.477, stop_first:0.519, target_first:0.004 |
|  |  |  |  | within_0.1 | 6 | neither:0.167, stop_first:0.833 |
|  |  |  |  | within_0.25 | 13 | neither:0.692, stop_first:0.308 |
|  |  |  |  | within_0.5 | 20 | neither:0.500, stop_first:0.450, target_first:0.050 |
|  |  |  |  | within_1.0 | 25 | neither:0.400, stop_first:0.600 |
| prior_week_level | max_pain | 812 | neither:0.477, stop_first:0.518, target_first:0.005 | beyond | 383 | neither:0.467, stop_first:0.525, target_first:0.008 |
|  |  |  |  | within_0.1 | 50 | neither:0.420, stop_first:0.580 |
|  |  |  |  | within_0.25 | 80 | neither:0.562, stop_first:0.438 |
|  |  |  |  | within_0.5 | 128 | neither:0.461, stop_first:0.531, target_first:0.008 |
|  |  |  |  | within_1.0 | 171 | neither:0.485, stop_first:0.515 |
| ofm_passive | key_gamma | 698 | invalid_geometry:0.536, stop_first:0.315, target_first:0.149 | beyond | 253 | invalid_geometry:0.522, stop_first:0.340, target_first:0.138 |
|  |  |  |  | within_0.1 | 60 | invalid_geometry:0.483, stop_first:0.317, target_first:0.200 |
|  |  |  |  | within_0.25 | 84 | invalid_geometry:0.512, stop_first:0.333, target_first:0.155 |
|  |  |  |  | within_0.5 | 140 | invalid_geometry:0.564, stop_first:0.321, target_first:0.114 |
|  |  |  |  | within_1.0 | 161 | invalid_geometry:0.565, stop_first:0.261, target_first:0.174 |
| ofm_passive | call_wall | 698 | invalid_geometry:0.536, stop_first:0.315, target_first:0.149 | beyond | 263 | invalid_geometry:0.548, stop_first:0.342, target_first:0.110 |
|  |  |  |  | within_0.1 | 53 | invalid_geometry:0.453, stop_first:0.302, target_first:0.245 |
|  |  |  |  | within_0.25 | 77 | invalid_geometry:0.455, stop_first:0.377, target_first:0.169 |
|  |  |  |  | within_0.5 | 132 | invalid_geometry:0.576, stop_first:0.288, target_first:0.136 |
|  |  |  |  | within_1.0 | 173 | invalid_geometry:0.549, stop_first:0.272, target_first:0.179 |
| ofm_passive | put_wall | 698 | invalid_geometry:0.536, stop_first:0.315, target_first:0.149 | beyond | 257 | invalid_geometry:0.537, stop_first:0.315, target_first:0.148 |
|  |  |  |  | within_0.1 | 53 | invalid_geometry:0.528, stop_first:0.283, target_first:0.189 |
|  |  |  |  | within_0.25 | 92 | invalid_geometry:0.576, stop_first:0.239, target_first:0.185 |
|  |  |  |  | within_0.5 | 128 | invalid_geometry:0.445, stop_first:0.414, target_first:0.141 |
|  |  |  |  | within_1.0 | 168 | invalid_geometry:0.583, stop_first:0.292, target_first:0.125 |
| ofm_passive | gamma_flip | 653 | invalid_geometry:0.544, stop_first:0.309, target_first:0.147 | beyond | 596 | invalid_geometry:0.542, stop_first:0.310, target_first:0.148 |
|  |  |  |  | within_0.1 | 2 | invalid_geometry:1.000 |
|  |  |  |  | within_0.25 | 8 | invalid_geometry:0.500, stop_first:0.250, target_first:0.250 |
|  |  |  |  | within_0.5 | 19 | invalid_geometry:0.579, stop_first:0.368, target_first:0.053 |
|  |  |  |  | within_1.0 | 28 | invalid_geometry:0.536, stop_first:0.286, target_first:0.179 |
| ofm_passive | max_pain | 700 | invalid_geometry:0.534, stop_first:0.317, target_first:0.149 | beyond | 275 | invalid_geometry:0.596, stop_first:0.276, target_first:0.127 |
|  |  |  |  | within_0.1 | 60 | invalid_geometry:0.367, stop_first:0.417, target_first:0.217 |
|  |  |  |  | within_0.25 | 63 | invalid_geometry:0.619, stop_first:0.286, target_first:0.095 |
|  |  |  |  | within_0.5 | 117 | invalid_geometry:0.513, stop_first:0.342, target_first:0.145 |
|  |  |  |  | within_1.0 | 185 | invalid_geometry:0.481, stop_first:0.341, target_first:0.178 |
| cash_open_reclaim_case | key_gamma | 731 | invalid_geometry:0.153, neither:0.127, stop_first:0.172, target_first:0.547 | beyond | 258 | invalid_geometry:0.151, neither:0.128, stop_first:0.225, target_first:0.496 |
|  |  |  |  | within_0.1 | 61 | invalid_geometry:0.180, neither:0.115, stop_first:0.148, target_first:0.557 |
|  |  |  |  | within_0.25 | 107 | invalid_geometry:0.131, neither:0.131, stop_first:0.121, target_first:0.617 |
|  |  |  |  | within_0.5 | 130 | invalid_geometry:0.146, neither:0.100, stop_first:0.138, target_first:0.615 |
|  |  |  |  | within_1.0 | 175 | invalid_geometry:0.166, neither:0.149, stop_first:0.160, target_first:0.526 |
| cash_open_reclaim_case | call_wall | 731 | invalid_geometry:0.153, neither:0.127, stop_first:0.172, target_first:0.547 | beyond | 248 | invalid_geometry:0.173, neither:0.133, stop_first:0.210, target_first:0.484 |
|  |  |  |  | within_0.1 | 55 | invalid_geometry:0.109, neither:0.127, stop_first:0.218, target_first:0.545 |
|  |  |  |  | within_0.25 | 107 | invalid_geometry:0.168, neither:0.168, stop_first:0.121, target_first:0.542 |
|  |  |  |  | within_0.5 | 114 | invalid_geometry:0.123, neither:0.105, stop_first:0.140, target_first:0.632 |
|  |  |  |  | within_1.0 | 207 | invalid_geometry:0.150, neither:0.111, stop_first:0.159, target_first:0.580 |
| cash_open_reclaim_case | put_wall | 731 | invalid_geometry:0.153, neither:0.127, stop_first:0.172, target_first:0.547 | beyond | 276 | invalid_geometry:0.152, neither:0.116, stop_first:0.167, target_first:0.565 |
|  |  |  |  | within_0.1 | 63 | invalid_geometry:0.206, neither:0.175, stop_first:0.111, target_first:0.508 |
|  |  |  |  | within_0.25 | 87 | invalid_geometry:0.103, neither:0.115, stop_first:0.149, target_first:0.632 |
|  |  |  |  | within_0.5 | 136 | invalid_geometry:0.154, neither:0.110, stop_first:0.169, target_first:0.566 |
|  |  |  |  | within_1.0 | 169 | invalid_geometry:0.160, neither:0.148, stop_first:0.219, target_first:0.473 |
| cash_open_reclaim_case | gamma_flip | 694 | invalid_geometry:0.151, neither:0.127, stop_first:0.173, target_first:0.549 | beyond | 663 | invalid_geometry:0.151, neither:0.133, stop_first:0.170, target_first:0.546 |
|  |  |  |  | within_0.1 | 3 | stop_first:0.333, target_first:0.667 |
|  |  |  |  | within_0.25 | 6 | stop_first:0.500, target_first:0.500 |
|  |  |  |  | within_0.5 | 9 | invalid_geometry:0.111, stop_first:0.111, target_first:0.778 |
|  |  |  |  | within_1.0 | 13 | invalid_geometry:0.308, stop_first:0.154, target_first:0.538 |
| cash_open_reclaim_case | max_pain | 733 | invalid_geometry:0.153, neither:0.127, stop_first:0.175, target_first:0.546 | beyond | 304 | invalid_geometry:0.155, neither:0.112, stop_first:0.191, target_first:0.543 |
|  |  |  |  | within_0.1 | 62 | invalid_geometry:0.194, neither:0.129, stop_first:0.145, target_first:0.532 |
|  |  |  |  | within_0.25 | 85 | invalid_geometry:0.141, neither:0.118, stop_first:0.118, target_first:0.624 |
|  |  |  |  | within_0.5 | 113 | invalid_geometry:0.142, neither:0.142, stop_first:0.159, target_first:0.558 |
|  |  |  |  | within_1.0 | 169 | invalid_geometry:0.148, neither:0.148, stop_first:0.195, target_first:0.509 |
| planned_return_long | key_gamma | 281 | stop_first:0.580, target_first:0.420 | beyond | 111 | stop_first:0.550, target_first:0.450 |
|  |  |  |  | within_0.1 | 20 | stop_first:0.600, target_first:0.400 |
|  |  |  |  | within_0.25 | 35 | stop_first:0.543, target_first:0.457 |
|  |  |  |  | within_0.5 | 53 | stop_first:0.698, target_first:0.302 |
|  |  |  |  | within_1.0 | 62 | stop_first:0.548, target_first:0.452 |
| planned_return_long | call_wall | 281 | stop_first:0.580, target_first:0.420 | beyond | 117 | stop_first:0.573, target_first:0.427 |
|  |  |  |  | within_0.1 | 25 | stop_first:0.520, target_first:0.480 |
|  |  |  |  | within_0.25 | 26 | stop_first:0.500, target_first:0.500 |
|  |  |  |  | within_0.5 | 53 | stop_first:0.698, target_first:0.302 |
|  |  |  |  | within_1.0 | 60 | stop_first:0.550, target_first:0.450 |
| planned_return_long | put_wall | 281 | stop_first:0.580, target_first:0.420 | beyond | 119 | stop_first:0.571, target_first:0.429 |
|  |  |  |  | within_0.1 | 20 | stop_first:0.550, target_first:0.450 |
|  |  |  |  | within_0.25 | 32 | stop_first:0.688, target_first:0.312 |
|  |  |  |  | within_0.5 | 54 | stop_first:0.593, target_first:0.407 |
|  |  |  |  | within_1.0 | 56 | stop_first:0.536, target_first:0.464 |
| planned_return_long | gamma_flip | 263 | stop_first:0.570, target_first:0.430 | beyond | 250 | stop_first:0.576, target_first:0.424 |
|  |  |  |  | within_0.1 | 2 | target_first:1.000 |
|  |  |  |  | within_0.25 | 2 | stop_first:0.500, target_first:0.500 |
|  |  |  |  | within_0.5 | 2 | stop_first:0.500, target_first:0.500 |
|  |  |  |  | within_1.0 | 7 | stop_first:0.571, target_first:0.429 |
| planned_return_long | max_pain | 281 | stop_first:0.580, target_first:0.420 | beyond | 127 | stop_first:0.543, target_first:0.457 |
|  |  |  |  | within_0.1 | 18 | stop_first:0.444, target_first:0.556 |
|  |  |  |  | within_0.25 | 24 | stop_first:0.667, target_first:0.333 |
|  |  |  |  | within_0.5 | 34 | stop_first:0.647, target_first:0.353 |
|  |  |  |  | within_1.0 | 78 | stop_first:0.615, target_first:0.385 |
| source_long | key_gamma | 903 | invalid_geometry:0.011, neither:0.002, not_applicable:0.564, stop_first:0.403, target_first:0.020 | beyond | 285 | invalid_geometry:0.011, not_applicable:0.575, stop_first:0.389, target_first:0.025 |
|  |  |  |  | within_0.1 | 98 | invalid_geometry:0.010, neither:0.010, not_applicable:0.582, stop_first:0.388, target_first:0.010 |
|  |  |  |  | within_0.25 | 116 | invalid_geometry:0.009, not_applicable:0.491, stop_first:0.483, target_first:0.017 |
|  |  |  |  | within_0.5 | 181 | invalid_geometry:0.017, neither:0.006, not_applicable:0.586, stop_first:0.381, target_first:0.011 |
|  |  |  |  | within_1.0 | 223 | invalid_geometry:0.009, not_applicable:0.561, stop_first:0.404, target_first:0.027 |
| source_long | call_wall | 903 | invalid_geometry:0.011, neither:0.002, not_applicable:0.564, stop_first:0.403, target_first:0.020 | beyond | 315 | invalid_geometry:0.016, neither:0.003, not_applicable:0.562, stop_first:0.390, target_first:0.029 |
|  |  |  |  | within_0.1 | 87 | not_applicable:0.621, stop_first:0.368, target_first:0.011 |
|  |  |  |  | within_0.25 | 112 | not_applicable:0.491, stop_first:0.500, target_first:0.009 |
|  |  |  |  | within_0.5 | 175 | invalid_geometry:0.023, neither:0.006, not_applicable:0.571, stop_first:0.389, target_first:0.011 |
|  |  |  |  | within_1.0 | 214 | invalid_geometry:0.005, not_applicable:0.575, stop_first:0.397, target_first:0.023 |
| source_long | put_wall | 903 | invalid_geometry:0.011, neither:0.002, not_applicable:0.564, stop_first:0.403, target_first:0.020 | beyond | 303 | invalid_geometry:0.010, not_applicable:0.551, stop_first:0.413, target_first:0.026 |
|  |  |  |  | within_0.1 | 84 | invalid_geometry:0.012, neither:0.012, not_applicable:0.679, stop_first:0.286, target_first:0.012 |
|  |  |  |  | within_0.25 | 110 | invalid_geometry:0.009, not_applicable:0.482, stop_first:0.500, target_first:0.009 |
|  |  |  |  | within_0.5 | 161 | invalid_geometry:0.012, neither:0.006, not_applicable:0.615, stop_first:0.360, target_first:0.006 |
|  |  |  |  | within_1.0 | 245 | invalid_geometry:0.012, not_applicable:0.543, stop_first:0.416, target_first:0.029 |
| source_long | gamma_flip | 847 | invalid_geometry:0.012, neither:0.002, not_applicable:0.564, stop_first:0.400, target_first:0.021 | beyond | 792 | invalid_geometry:0.011, neither:0.001, not_applicable:0.562, stop_first:0.404, target_first:0.021 |
|  |  |  |  | within_0.1 | 7 | neither:0.143, not_applicable:0.571, stop_first:0.286 |
|  |  |  |  | within_0.25 | 11 | not_applicable:0.545, stop_first:0.455 |
|  |  |  |  | within_0.5 | 7 | not_applicable:0.857, stop_first:0.143 |
|  |  |  |  | within_1.0 | 30 | invalid_geometry:0.033, not_applicable:0.567, stop_first:0.367, target_first:0.033 |
| source_long | max_pain | 903 | invalid_geometry:0.011, neither:0.002, not_applicable:0.564, stop_first:0.403, target_first:0.020 | beyond | 379 | invalid_geometry:0.013, neither:0.003, not_applicable:0.530, stop_first:0.441, target_first:0.013 |
|  |  |  |  | within_0.1 | 70 | not_applicable:0.657, stop_first:0.314, target_first:0.029 |
|  |  |  |  | within_0.25 | 105 | invalid_geometry:0.010, not_applicable:0.562, stop_first:0.410, target_first:0.019 |
|  |  |  |  | within_0.5 | 128 | invalid_geometry:0.008, not_applicable:0.586, stop_first:0.375, target_first:0.031 |
|  |  |  |  | within_1.0 | 221 | invalid_geometry:0.014, neither:0.005, not_applicable:0.579, stop_first:0.380, target_first:0.023 |
| extension_reaction | key_gamma | 99 | invalid_geometry:0.232, neither:0.020, stop_first:0.646, target_first:0.101 | beyond | 31 | invalid_geometry:0.194, neither:0.032, stop_first:0.613, target_first:0.161 |
|  |  |  |  | within_0.1 | 8 | invalid_geometry:0.250, stop_first:0.625, target_first:0.125 |
|  |  |  |  | within_0.25 | 14 | invalid_geometry:0.357, stop_first:0.643 |
|  |  |  |  | within_0.5 | 27 | invalid_geometry:0.185, stop_first:0.667, target_first:0.148 |
|  |  |  |  | within_1.0 | 19 | invalid_geometry:0.263, neither:0.053, stop_first:0.684 |
| extension_reaction | call_wall | 99 | invalid_geometry:0.232, neither:0.020, stop_first:0.646, target_first:0.101 | beyond | 35 | invalid_geometry:0.257, neither:0.029, stop_first:0.543, target_first:0.171 |
|  |  |  |  | within_0.1 | 10 | invalid_geometry:0.200, stop_first:0.700, target_first:0.100 |
|  |  |  |  | within_0.25 | 10 | invalid_geometry:0.100, stop_first:0.800, target_first:0.100 |
|  |  |  |  | within_0.5 | 19 | invalid_geometry:0.211, stop_first:0.737, target_first:0.053 |
|  |  |  |  | within_1.0 | 25 | invalid_geometry:0.280, neither:0.040, stop_first:0.640, target_first:0.040 |
| extension_reaction | put_wall | 99 | invalid_geometry:0.232, neither:0.020, stop_first:0.646, target_first:0.101 | beyond | 30 | invalid_geometry:0.167, neither:0.033, stop_first:0.633, target_first:0.167 |
|  |  |  |  | within_0.1 | 6 | invalid_geometry:0.500, stop_first:0.333, target_first:0.167 |
|  |  |  |  | within_0.25 | 17 | invalid_geometry:0.353, stop_first:0.647 |
|  |  |  |  | within_0.5 | 20 | invalid_geometry:0.200, stop_first:0.650, target_first:0.150 |
|  |  |  |  | within_1.0 | 26 | invalid_geometry:0.192, neither:0.038, stop_first:0.731, target_first:0.038 |
| extension_reaction | gamma_flip | 90 | invalid_geometry:0.244, neither:0.022, stop_first:0.633, target_first:0.100 | beyond | 83 | invalid_geometry:0.241, neither:0.024, stop_first:0.627, target_first:0.108 |
|  |  |  |  | within_0.1 | 1 | stop_first:1.000 |
|  |  |  |  | within_0.25 | 2 | invalid_geometry:0.500, stop_first:0.500 |
|  |  |  |  | within_0.5 | 1 | stop_first:1.000 |
|  |  |  |  | within_1.0 | 3 | invalid_geometry:0.333, stop_first:0.667 |
| extension_reaction | max_pain | 99 | invalid_geometry:0.232, neither:0.020, stop_first:0.646, target_first:0.101 | beyond | 57 | invalid_geometry:0.246, neither:0.035, stop_first:0.614, target_first:0.105 |
|  |  |  |  | within_0.1 | 5 | invalid_geometry:0.400, stop_first:0.400, target_first:0.200 |
|  |  |  |  | within_0.25 | 10 | invalid_geometry:0.200, stop_first:0.800 |
|  |  |  |  | within_0.5 | 7 | invalid_geometry:0.143, stop_first:0.857 |
|  |  |  |  | within_1.0 | 20 | invalid_geometry:0.200, stop_first:0.650, target_first:0.150 |
| internal_rotation | key_gamma | 44 | invalid_geometry:0.136, stop_first:0.636, target_first:0.227 | beyond | 18 | invalid_geometry:0.222, stop_first:0.556, target_first:0.222 |
|  |  |  |  | within_0.1 | 6 | stop_first:0.833, target_first:0.167 |
|  |  |  |  | within_0.25 | 8 | stop_first:1.000 |
|  |  |  |  | within_0.5 | 4 | stop_first:0.750, target_first:0.250 |
|  |  |  |  | within_1.0 | 8 | invalid_geometry:0.250, stop_first:0.250, target_first:0.500 |
| internal_rotation | call_wall | 44 | invalid_geometry:0.136, stop_first:0.636, target_first:0.227 | beyond | 18 | invalid_geometry:0.167, stop_first:0.611, target_first:0.222 |
|  |  |  |  | within_0.1 | 6 | stop_first:0.833, target_first:0.167 |
|  |  |  |  | within_0.25 | 4 | stop_first:1.000 |
|  |  |  |  | within_0.5 | 8 | invalid_geometry:0.125, stop_first:0.500, target_first:0.375 |
|  |  |  |  | within_1.0 | 8 | invalid_geometry:0.250, stop_first:0.500, target_first:0.250 |
| internal_rotation | put_wall | 44 | invalid_geometry:0.136, stop_first:0.636, target_first:0.227 | beyond | 26 | invalid_geometry:0.192, stop_first:0.538, target_first:0.269 |
|  |  |  |  | within_0.1 | 4 | stop_first:1.000 |
|  |  |  |  | within_0.25 | 4 | stop_first:1.000 |
|  |  |  |  | within_0.5 | 4 | stop_first:1.000 |
|  |  |  |  | within_1.0 | 6 | invalid_geometry:0.167, stop_first:0.333, target_first:0.500 |
| internal_rotation | gamma_flip | 40 | invalid_geometry:0.125, stop_first:0.650, target_first:0.225 | beyond | 38 | invalid_geometry:0.105, stop_first:0.684, target_first:0.211 |
|  |  |  |  | within_1.0 | 2 | invalid_geometry:0.500, target_first:0.500 |
| internal_rotation | max_pain | 44 | invalid_geometry:0.136, stop_first:0.636, target_first:0.227 | beyond | 18 | invalid_geometry:0.167, stop_first:0.611, target_first:0.222 |
|  |  |  |  | within_0.1 | 6 | stop_first:0.833, target_first:0.167 |
|  |  |  |  | within_0.25 | 6 | invalid_geometry:0.167, stop_first:0.500, target_first:0.333 |
|  |  |  |  | within_0.5 | 6 | invalid_geometry:0.333, stop_first:0.167, target_first:0.500 |
|  |  |  |  | within_1.0 | 8 | stop_first:1.000 |
| single_extended | key_gamma | 22 | invalid_geometry:0.091, stop_first:0.636, target_first:0.273 | beyond | 9 | stop_first:0.556, target_first:0.444 |
|  |  |  |  | within_0.1 | 3 | stop_first:1.000 |
|  |  |  |  | within_0.25 | 4 | stop_first:1.000 |
|  |  |  |  | within_0.5 | 2 | stop_first:0.500, target_first:0.500 |
|  |  |  |  | within_1.0 | 4 | invalid_geometry:0.500, stop_first:0.250, target_first:0.250 |
| single_extended | call_wall | 22 | invalid_geometry:0.091, stop_first:0.636, target_first:0.273 | beyond | 9 | stop_first:0.556, target_first:0.444 |
|  |  |  |  | within_0.1 | 3 | stop_first:1.000 |
|  |  |  |  | within_0.25 | 2 | stop_first:1.000 |
|  |  |  |  | within_0.5 | 4 | invalid_geometry:0.250, stop_first:0.500, target_first:0.250 |
|  |  |  |  | within_1.0 | 4 | invalid_geometry:0.250, stop_first:0.500, target_first:0.250 |
| single_extended | put_wall | 22 | invalid_geometry:0.091, stop_first:0.636, target_first:0.273 | beyond | 13 | invalid_geometry:0.077, stop_first:0.538, target_first:0.385 |
|  |  |  |  | within_0.1 | 2 | stop_first:1.000 |
|  |  |  |  | within_0.25 | 2 | stop_first:1.000 |
|  |  |  |  | within_0.5 | 2 | stop_first:1.000 |
|  |  |  |  | within_1.0 | 3 | invalid_geometry:0.333, stop_first:0.333, target_first:0.333 |
| single_extended | gamma_flip | 20 | invalid_geometry:0.050, stop_first:0.650, target_first:0.300 | beyond | 19 | stop_first:0.684, target_first:0.316 |
|  |  |  |  | within_1.0 | 1 | invalid_geometry:1.000 |
| single_extended | max_pain | 22 | invalid_geometry:0.091, stop_first:0.636, target_first:0.273 | beyond | 9 | stop_first:0.667, target_first:0.333 |
|  |  |  |  | within_0.1 | 3 | stop_first:1.000 |
|  |  |  |  | within_0.25 | 3 | stop_first:0.333, target_first:0.667 |
|  |  |  |  | within_0.5 | 3 | invalid_geometry:0.667, target_first:0.333 |
|  |  |  |  | within_1.0 | 4 | stop_first:1.000 |
| single_purged | key_gamma | 22 | invalid_geometry:0.091, stop_first:0.636, target_first:0.273 | beyond | 9 | stop_first:0.556, target_first:0.444 |
|  |  |  |  | within_0.1 | 3 | stop_first:1.000 |
|  |  |  |  | within_0.25 | 4 | stop_first:1.000 |
|  |  |  |  | within_0.5 | 2 | stop_first:0.500, target_first:0.500 |
|  |  |  |  | within_1.0 | 4 | invalid_geometry:0.500, stop_first:0.250, target_first:0.250 |
| single_purged | call_wall | 22 | invalid_geometry:0.091, stop_first:0.636, target_first:0.273 | beyond | 9 | stop_first:0.556, target_first:0.444 |
|  |  |  |  | within_0.1 | 3 | stop_first:1.000 |
|  |  |  |  | within_0.25 | 2 | stop_first:1.000 |
|  |  |  |  | within_0.5 | 4 | invalid_geometry:0.250, stop_first:0.500, target_first:0.250 |
|  |  |  |  | within_1.0 | 4 | invalid_geometry:0.250, stop_first:0.500, target_first:0.250 |
| single_purged | put_wall | 22 | invalid_geometry:0.091, stop_first:0.636, target_first:0.273 | beyond | 13 | invalid_geometry:0.077, stop_first:0.538, target_first:0.385 |
|  |  |  |  | within_0.1 | 2 | stop_first:1.000 |
|  |  |  |  | within_0.25 | 2 | stop_first:1.000 |
|  |  |  |  | within_0.5 | 2 | stop_first:1.000 |
|  |  |  |  | within_1.0 | 3 | invalid_geometry:0.333, stop_first:0.333, target_first:0.333 |
| single_purged | gamma_flip | 20 | invalid_geometry:0.050, stop_first:0.650, target_first:0.300 | beyond | 19 | stop_first:0.684, target_first:0.316 |
|  |  |  |  | within_1.0 | 1 | invalid_geometry:1.000 |
| single_purged | max_pain | 22 | invalid_geometry:0.091, stop_first:0.636, target_first:0.273 | beyond | 9 | stop_first:0.667, target_first:0.333 |
|  |  |  |  | within_0.1 | 3 | stop_first:1.000 |
|  |  |  |  | within_0.25 | 3 | stop_first:0.333, target_first:0.667 |
|  |  |  |  | within_0.5 | 3 | invalid_geometry:0.667, target_first:0.333 |
|  |  |  |  | within_1.0 | 4 | stop_first:1.000 |
| touch_record | key_gamma | 2962 | not_applicable:1.000 | beyond | 974 | not_applicable:1.000 |
|  |  |  |  | within_0.1 | 215 | not_applicable:1.000 |
|  |  |  |  | within_0.25 | 432 | not_applicable:1.000 |
|  |  |  |  | within_0.5 | 498 | not_applicable:1.000 |
|  |  |  |  | within_1.0 | 843 | not_applicable:1.000 |
| touch_record | call_wall | 2962 | not_applicable:1.000 | beyond | 1322 | not_applicable:1.000 |
|  |  |  |  | within_0.1 | 211 | not_applicable:1.000 |
|  |  |  |  | within_0.25 | 262 | not_applicable:1.000 |
|  |  |  |  | within_0.5 | 412 | not_applicable:1.000 |
|  |  |  |  | within_1.0 | 755 | not_applicable:1.000 |
| touch_record | put_wall | 2962 | not_applicable:1.000 | beyond | 1141 | not_applicable:1.000 |
|  |  |  |  | within_0.1 | 272 | not_applicable:1.000 |
|  |  |  |  | within_0.25 | 327 | not_applicable:1.000 |
|  |  |  |  | within_0.5 | 386 | not_applicable:1.000 |
|  |  |  |  | within_1.0 | 836 | not_applicable:1.000 |
| touch_record | gamma_flip | 2946 | not_applicable:1.000 | beyond | 2743 | not_applicable:1.000 |
|  |  |  |  | within_1.0 | 203 | not_applicable:1.000 |
| touch_record | max_pain | 2962 | not_applicable:1.000 | beyond | 1452 | not_applicable:1.000 |
|  |  |  |  | within_0.1 | 399 | not_applicable:1.000 |
|  |  |  |  | within_0.25 | 113 | not_applicable:1.000 |
|  |  |  |  | within_0.5 | 788 | not_applicable:1.000 |
|  |  |  |  | within_1.0 | 210 | not_applicable:1.000 |

## Strategy alignment outcomes for NQ and ES (degenerate board (median n_live 2 / 7))

Not evidence for the futures-option levels thesis until a BBO or MBP schema is owned.

Rows: 250677. result=not_applicable: 11316 (0.04514175612441508).

Unconditional result mix: invalid_geometry=57767, missing_future=48, neither=12712, not_applicable=11316, stop_first=129112, target_first=39722.

| branch | level kind | n | unconditional | bucket | bucket n | conditional |
| --- | --- | ---: | --- | --- | ---: | --- |
| asia_tdo_case | key_gamma | 1800 | invalid_geometry:0.027, neither:0.119, stop_first:0.413, target_first:0.442 | beyond | 1273 | invalid_geometry:0.026, neither:0.134, stop_first:0.400, target_first:0.440 |
|  |  |  |  | within_0.1 | 71 | invalid_geometry:0.042, neither:0.070, stop_first:0.408, target_first:0.479 |
|  |  |  |  | within_0.25 | 105 | invalid_geometry:0.029, neither:0.067, stop_first:0.467, target_first:0.438 |
|  |  |  |  | within_0.5 | 139 | invalid_geometry:0.036, neither:0.115, stop_first:0.446, target_first:0.403 |
|  |  |  |  | within_1.0 | 212 | invalid_geometry:0.019, neither:0.071, stop_first:0.443, target_first:0.467 |
| asia_tdo_case | put_wall | 1557 | invalid_geometry:0.029, neither:0.115, stop_first:0.409, target_first:0.447 | beyond | 1149 | invalid_geometry:0.030, neither:0.127, stop_first:0.397, target_first:0.446 |
|  |  |  |  | within_0.1 | 54 | neither:0.056, stop_first:0.352, target_first:0.593 |
|  |  |  |  | within_0.25 | 80 | invalid_geometry:0.025, neither:0.075, stop_first:0.487, target_first:0.412 |
|  |  |  |  | within_0.5 | 102 | invalid_geometry:0.049, neither:0.098, stop_first:0.441, target_first:0.412 |
|  |  |  |  | within_1.0 | 172 | invalid_geometry:0.017, neither:0.081, stop_first:0.453, target_first:0.448 |
| asia_tdo_case | max_pain | 1926 | invalid_geometry:0.026, neither:0.114, stop_first:0.414, target_first:0.446 | beyond | 1246 | invalid_geometry:0.029, neither:0.121, stop_first:0.413, target_first:0.437 |
|  |  |  |  | within_0.1 | 111 | invalid_geometry:0.009, neither:0.054, stop_first:0.342, target_first:0.595 |
|  |  |  |  | within_0.25 | 129 | invalid_geometry:0.031, neither:0.101, stop_first:0.450, target_first:0.419 |
|  |  |  |  | within_0.5 | 196 | invalid_geometry:0.041, neither:0.138, stop_first:0.408, target_first:0.413 |
|  |  |  |  | within_1.0 | 244 | invalid_geometry:0.004, neither:0.094, stop_first:0.434, target_first:0.467 |
| nyam_box | key_gamma | 3590 | invalid_geometry:0.001, neither:0.075, stop_first:0.730, target_first:0.194 | beyond | 2458 | invalid_geometry:0.001, neither:0.078, stop_first:0.730, target_first:0.191 |
|  |  |  |  | within_0.1 | 157 | invalid_geometry:0.006, neither:0.045, stop_first:0.752, target_first:0.197 |
|  |  |  |  | within_0.25 | 203 | neither:0.079, stop_first:0.744, target_first:0.177 |
|  |  |  |  | within_0.5 | 324 | neither:0.059, stop_first:0.716, target_first:0.225 |
|  |  |  |  | within_1.0 | 448 | invalid_geometry:0.002, neither:0.076, stop_first:0.725, target_first:0.196 |
| nyam_box | put_wall | 3104 | invalid_geometry:0.001, neither:0.075, stop_first:0.732, target_first:0.192 | beyond | 2291 | invalid_geometry:0.001, neither:0.076, stop_first:0.731, target_first:0.192 |
|  |  |  |  | within_0.1 | 102 | invalid_geometry:0.010, neither:0.078, stop_first:0.725, target_first:0.186 |
|  |  |  |  | within_0.25 | 146 | neither:0.082, stop_first:0.753, target_first:0.164 |
|  |  |  |  | within_0.5 | 242 | invalid_geometry:0.004, neither:0.062, stop_first:0.723, target_first:0.211 |
|  |  |  |  | within_1.0 | 323 | neither:0.071, stop_first:0.737, target_first:0.192 |
| nyam_box | max_pain | 3832 | invalid_geometry:0.001, neither:0.074, stop_first:0.730, target_first:0.195 | beyond | 2513 | invalid_geometry:0.002, neither:0.074, stop_first:0.733, target_first:0.191 |
|  |  |  |  | within_0.1 | 190 | neither:0.063, stop_first:0.758, target_first:0.179 |
|  |  |  |  | within_0.25 | 266 | neither:0.075, stop_first:0.707, target_first:0.218 |
|  |  |  |  | within_0.5 | 379 | invalid_geometry:0.003, neither:0.066, stop_first:0.710, target_first:0.222 |
|  |  |  |  | within_1.0 | 484 | neither:0.081, stop_first:0.731, target_first:0.188 |
| previous_hour | key_gamma | 15338 | invalid_geometry:0.002, missing_future:0.000, neither:0.056, stop_first:0.776, target_first:0.166 | beyond | 10779 | invalid_geometry:0.002, missing_future:0.000, neither:0.059, stop_first:0.778, target_first:0.161 |
|  |  |  |  | within_0.1 | 536 | invalid_geometry:0.006, neither:0.041, stop_first:0.791, target_first:0.162 |
|  |  |  |  | within_0.25 | 823 | invalid_geometry:0.002, neither:0.053, stop_first:0.759, target_first:0.185 |
|  |  |  |  | within_0.5 | 1244 | invalid_geometry:0.002, missing_future:0.001, neither:0.058, stop_first:0.758, target_first:0.182 |
|  |  |  |  | within_1.0 | 1956 | invalid_geometry:0.003, missing_future:0.001, neither:0.043, stop_first:0.778, target_first:0.175 |
| previous_hour | put_wall | 13306 | invalid_geometry:0.003, missing_future:0.001, neither:0.057, stop_first:0.776, target_first:0.164 | beyond | 10024 | invalid_geometry:0.003, missing_future:0.000, neither:0.058, stop_first:0.776, target_first:0.163 |
|  |  |  |  | within_0.1 | 386 | invalid_geometry:0.005, neither:0.057, stop_first:0.780, target_first:0.158 |
|  |  |  |  | within_0.25 | 609 | invalid_geometry:0.003, missing_future:0.002, neither:0.054, stop_first:0.767, target_first:0.174 |
|  |  |  |  | within_0.5 | 905 | invalid_geometry:0.002, missing_future:0.001, neither:0.060, stop_first:0.771, target_first:0.166 |
|  |  |  |  | within_1.0 | 1382 | invalid_geometry:0.001, missing_future:0.001, neither:0.045, stop_first:0.783, target_first:0.170 |
| previous_hour | max_pain | 16379 | invalid_geometry:0.003, missing_future:0.000, neither:0.056, stop_first:0.776, target_first:0.166 | beyond | 10955 | invalid_geometry:0.002, missing_future:0.000, neither:0.053, stop_first:0.783, target_first:0.161 |
|  |  |  |  | within_0.1 | 708 | invalid_geometry:0.006, neither:0.056, stop_first:0.761, target_first:0.177 |
|  |  |  |  | within_0.25 | 1010 | invalid_geometry:0.002, missing_future:0.001, neither:0.058, stop_first:0.742, target_first:0.197 |
|  |  |  |  | within_0.5 | 1489 | invalid_geometry:0.003, missing_future:0.001, neither:0.067, stop_first:0.754, target_first:0.175 |
|  |  |  |  | within_1.0 | 2217 | invalid_geometry:0.002, missing_future:0.001, neither:0.058, stop_first:0.774, target_first:0.165 |
| prior_day_level | key_gamma | 1344 | invalid_geometry:0.002, neither:0.316, stop_first:0.592, target_first:0.089 | beyond | 963 | invalid_geometry:0.003, neither:0.325, stop_first:0.585, target_first:0.087 |
|  |  |  |  | within_0.1 | 48 | neither:0.188, stop_first:0.750, target_first:0.062 |
|  |  |  |  | within_0.25 | 52 | neither:0.288, stop_first:0.596, target_first:0.115 |
|  |  |  |  | within_0.5 | 100 | neither:0.270, stop_first:0.620, target_first:0.110 |
|  |  |  |  | within_1.0 | 181 | neither:0.337, stop_first:0.575, target_first:0.088 |
| prior_day_level | put_wall | 1158 | invalid_geometry:0.003, neither:0.317, stop_first:0.589, target_first:0.092 | beyond | 872 | invalid_geometry:0.002, neither:0.326, stop_first:0.581, target_first:0.091 |
|  |  |  |  | within_0.1 | 32 | invalid_geometry:0.031, neither:0.219, stop_first:0.719, target_first:0.031 |
|  |  |  |  | within_0.25 | 53 | neither:0.396, stop_first:0.528, target_first:0.075 |
|  |  |  |  | within_0.5 | 79 | neither:0.291, stop_first:0.608, target_first:0.101 |
|  |  |  |  | within_1.0 | 122 | neither:0.262, stop_first:0.623, target_first:0.115 |
| prior_day_level | max_pain | 1432 | invalid_geometry:0.002, neither:0.314, stop_first:0.593, target_first:0.091 | beyond | 958 | invalid_geometry:0.002, neither:0.315, stop_first:0.586, target_first:0.097 |
|  |  |  |  | within_0.1 | 64 | invalid_geometry:0.016, neither:0.297, stop_first:0.672, target_first:0.016 |
|  |  |  |  | within_0.25 | 80 | neither:0.400, stop_first:0.487, target_first:0.113 |
|  |  |  |  | within_0.5 | 141 | neither:0.298, stop_first:0.603, target_first:0.099 |
|  |  |  |  | within_1.0 | 189 | neither:0.286, stop_first:0.640, target_first:0.074 |
| prior_month_level | key_gamma | 353 | neither:0.439, stop_first:0.561 | beyond | 249 | neither:0.450, stop_first:0.550 |
|  |  |  |  | within_0.1 | 9 | neither:0.333, stop_first:0.667 |
|  |  |  |  | within_0.25 | 16 | neither:0.562, stop_first:0.438 |
|  |  |  |  | within_0.5 | 23 | neither:0.435, stop_first:0.565 |
|  |  |  |  | within_1.0 | 56 | neither:0.375, stop_first:0.625 |
| prior_month_level | put_wall | 304 | neither:0.428, stop_first:0.572 | beyond | 230 | neither:0.417, stop_first:0.583 |
|  |  |  |  | within_0.1 | 6 | neither:0.333, stop_first:0.667 |
|  |  |  |  | within_0.25 | 14 | neither:0.571, stop_first:0.429 |
|  |  |  |  | within_0.5 | 24 | neither:0.500, stop_first:0.500 |
|  |  |  |  | within_1.0 | 30 | neither:0.400, stop_first:0.600 |
| prior_month_level | max_pain | 378 | neither:0.434, stop_first:0.566 | beyond | 243 | neither:0.428, stop_first:0.572 |
|  |  |  |  | within_0.1 | 11 | neither:0.545, stop_first:0.455 |
|  |  |  |  | within_0.25 | 22 | neither:0.409, stop_first:0.591 |
|  |  |  |  | within_0.5 | 41 | neither:0.439, stop_first:0.561 |
|  |  |  |  | within_1.0 | 61 | neither:0.443, stop_first:0.557 |
| other_session | key_gamma | 11399 | invalid_geometry:0.269, missing_future:0.000, neither:0.019, stop_first:0.562, target_first:0.150 | beyond | 8018 | invalid_geometry:0.269, missing_future:0.000, neither:0.020, stop_first:0.563, target_first:0.147 |
|  |  |  |  | within_0.1 | 394 | invalid_geometry:0.284, neither:0.005, stop_first:0.566, target_first:0.145 |
|  |  |  |  | within_0.25 | 615 | invalid_geometry:0.241, neither:0.021, stop_first:0.553, target_first:0.185 |
|  |  |  |  | within_0.5 | 934 | invalid_geometry:0.259, missing_future:0.001, neither:0.013, stop_first:0.560, target_first:0.167 |
|  |  |  |  | within_1.0 | 1438 | invalid_geometry:0.277, neither:0.022, stop_first:0.559, target_first:0.141 |
| other_session | put_wall | 9873 | invalid_geometry:0.271, missing_future:0.000, neither:0.019, stop_first:0.561, target_first:0.149 | beyond | 7418 | invalid_geometry:0.268, missing_future:0.000, neither:0.020, stop_first:0.561, target_first:0.150 |
|  |  |  |  | within_0.1 | 295 | invalid_geometry:0.312, neither:0.007, stop_first:0.508, target_first:0.173 |
|  |  |  |  | within_0.25 | 437 | invalid_geometry:0.231, neither:0.023, stop_first:0.588, target_first:0.158 |
|  |  |  |  | within_0.5 | 690 | invalid_geometry:0.267, missing_future:0.001, neither:0.012, stop_first:0.568, target_first:0.152 |
|  |  |  |  | within_1.0 | 1033 | invalid_geometry:0.303, neither:0.016, stop_first:0.557, target_first:0.124 |
| other_session | max_pain | 12156 | invalid_geometry:0.268, missing_future:0.000, neither:0.019, stop_first:0.563, target_first:0.150 | beyond | 8142 | invalid_geometry:0.265, missing_future:0.000, neither:0.019, stop_first:0.566, target_first:0.149 |
|  |  |  |  | within_0.1 | 517 | invalid_geometry:0.257, neither:0.015, stop_first:0.596, target_first:0.132 |
|  |  |  |  | within_0.25 | 755 | invalid_geometry:0.268, neither:0.021, stop_first:0.538, target_first:0.174 |
|  |  |  |  | within_0.5 | 1133 | invalid_geometry:0.258, missing_future:0.001, neither:0.014, stop_first:0.557, target_first:0.170 |
|  |  |  |  | within_1.0 | 1609 | invalid_geometry:0.290, neither:0.024, stop_first:0.553, target_first:0.133 |
| timed_pzone_reversal | key_gamma | 3274 | invalid_geometry:0.280, missing_future:0.001, neither:0.048, stop_first:0.613, target_first:0.058 | beyond | 2356 | invalid_geometry:0.274, missing_future:0.000, neither:0.048, stop_first:0.626, target_first:0.052 |
|  |  |  |  | within_0.1 | 110 | invalid_geometry:0.236, neither:0.055, stop_first:0.591, target_first:0.118 |
|  |  |  |  | within_0.25 | 139 | invalid_geometry:0.266, neither:0.043, stop_first:0.604, target_first:0.086 |
|  |  |  |  | within_0.5 | 234 | invalid_geometry:0.303, neither:0.060, stop_first:0.577, target_first:0.060 |
|  |  |  |  | within_1.0 | 435 | invalid_geometry:0.317, missing_future:0.002, neither:0.046, stop_first:0.568, target_first:0.067 |
| timed_pzone_reversal | put_wall | 2840 | invalid_geometry:0.280, missing_future:0.001, neither:0.048, stop_first:0.612, target_first:0.059 | beyond | 2206 | invalid_geometry:0.264, missing_future:0.000, neither:0.049, stop_first:0.631, target_first:0.055 |
|  |  |  |  | within_0.1 | 68 | invalid_geometry:0.338, neither:0.015, stop_first:0.544, target_first:0.103 |
|  |  |  |  | within_0.25 | 97 | invalid_geometry:0.340, neither:0.041, stop_first:0.546, target_first:0.072 |
|  |  |  |  | within_0.5 | 164 | invalid_geometry:0.287, neither:0.061, stop_first:0.585, target_first:0.067 |
|  |  |  |  | within_1.0 | 305 | invalid_geometry:0.361, missing_future:0.003, neither:0.043, stop_first:0.528, target_first:0.066 |
| timed_pzone_reversal | max_pain | 3507 | invalid_geometry:0.279, missing_future:0.001, neither:0.050, stop_first:0.614, target_first:0.057 | beyond | 2452 | invalid_geometry:0.274, neither:0.051, stop_first:0.628, target_first:0.047 |
|  |  |  |  | within_0.1 | 111 | invalid_geometry:0.279, neither:0.072, stop_first:0.541, target_first:0.108 |
|  |  |  |  | within_0.25 | 171 | invalid_geometry:0.304, neither:0.041, stop_first:0.556, target_first:0.099 |
|  |  |  |  | within_0.5 | 285 | invalid_geometry:0.298, neither:0.039, stop_first:0.579, target_first:0.084 |
|  |  |  |  | within_1.0 | 488 | invalid_geometry:0.283, missing_future:0.004, neither:0.049, stop_first:0.600, target_first:0.064 |
| continuation_retest | key_gamma | 1322 | invalid_geometry:0.635, neither:0.005, stop_first:0.230, target_first:0.130 | beyond | 910 | invalid_geometry:0.622, neither:0.005, stop_first:0.237, target_first:0.135 |
|  |  |  |  | within_0.1 | 50 | invalid_geometry:0.620, stop_first:0.260, target_first:0.120 |
|  |  |  |  | within_0.25 | 90 | invalid_geometry:0.633, stop_first:0.222, target_first:0.144 |
|  |  |  |  | within_0.5 | 108 | invalid_geometry:0.731, stop_first:0.176, target_first:0.093 |
|  |  |  |  | within_1.0 | 164 | invalid_geometry:0.652, neither:0.006, stop_first:0.220, target_first:0.122 |
| continuation_retest | put_wall | 1141 | invalid_geometry:0.637, neither:0.004, stop_first:0.225, target_first:0.134 | beyond | 858 | invalid_geometry:0.636, neither:0.005, stop_first:0.227, target_first:0.132 |
|  |  |  |  | within_0.1 | 28 | invalid_geometry:0.643, stop_first:0.250, target_first:0.107 |
|  |  |  |  | within_0.25 | 60 | invalid_geometry:0.567, stop_first:0.283, target_first:0.150 |
|  |  |  |  | within_0.5 | 71 | invalid_geometry:0.718, stop_first:0.169, target_first:0.113 |
|  |  |  |  | within_1.0 | 124 | invalid_geometry:0.629, stop_first:0.210, target_first:0.161 |
| continuation_retest | max_pain | 1412 | invalid_geometry:0.635, neither:0.004, stop_first:0.230, target_first:0.130 | beyond | 945 | invalid_geometry:0.632, neither:0.005, stop_first:0.239, target_first:0.124 |
|  |  |  |  | within_0.1 | 64 | invalid_geometry:0.625, stop_first:0.219, target_first:0.156 |
|  |  |  |  | within_0.25 | 91 | invalid_geometry:0.582, stop_first:0.308, target_first:0.110 |
|  |  |  |  | within_0.5 | 125 | invalid_geometry:0.696, neither:0.008, stop_first:0.144, target_first:0.152 |
|  |  |  |  | within_1.0 | 187 | invalid_geometry:0.642, stop_first:0.209, target_first:0.150 |
| trapped_buyers_retest | key_gamma | 665 | invalid_geometry:0.588, neither:0.003, stop_first:0.260, target_first:0.149 | beyond | 462 | invalid_geometry:0.597, neither:0.002, stop_first:0.253, target_first:0.147 |
|  |  |  |  | within_0.1 | 28 | invalid_geometry:0.571, stop_first:0.321, target_first:0.107 |
|  |  |  |  | within_0.25 | 42 | invalid_geometry:0.524, stop_first:0.262, target_first:0.214 |
|  |  |  |  | within_0.5 | 61 | invalid_geometry:0.607, stop_first:0.279, target_first:0.115 |
|  |  |  |  | within_1.0 | 72 | invalid_geometry:0.556, neither:0.014, stop_first:0.264, target_first:0.167 |
| trapped_buyers_retest | put_wall | 573 | invalid_geometry:0.590, neither:0.003, stop_first:0.251, target_first:0.155 | beyond | 433 | invalid_geometry:0.605, neither:0.005, stop_first:0.247, target_first:0.143 |
|  |  |  |  | within_0.1 | 14 | invalid_geometry:0.500, stop_first:0.286, target_first:0.214 |
|  |  |  |  | within_0.25 | 33 | invalid_geometry:0.515, stop_first:0.242, target_first:0.242 |
|  |  |  |  | within_0.5 | 40 | invalid_geometry:0.575, stop_first:0.275, target_first:0.150 |
|  |  |  |  | within_1.0 | 53 | invalid_geometry:0.547, stop_first:0.264, target_first:0.189 |
| trapped_buyers_retest | max_pain | 711 | invalid_geometry:0.589, neither:0.003, stop_first:0.259, target_first:0.149 | beyond | 471 | invalid_geometry:0.603, neither:0.002, stop_first:0.268, target_first:0.127 |
|  |  |  |  | within_0.1 | 36 | invalid_geometry:0.500, stop_first:0.278, target_first:0.222 |
|  |  |  |  | within_0.25 | 42 | invalid_geometry:0.452, stop_first:0.381, target_first:0.167 |
|  |  |  |  | within_0.5 | 67 | invalid_geometry:0.627, neither:0.015, stop_first:0.194, target_first:0.164 |
|  |  |  |  | within_1.0 | 95 | invalid_geometry:0.589, stop_first:0.200, target_first:0.211 |
| kg1_retest | key_gamma | 1302 | invalid_geometry:0.423, neither:0.028, stop_first:0.525, target_first:0.024 | beyond | 942 | invalid_geometry:0.426, neither:0.030, stop_first:0.515, target_first:0.030 |
|  |  |  |  | within_0.1 | 32 | invalid_geometry:0.469, neither:0.031, stop_first:0.500 |
|  |  |  |  | within_0.25 | 50 | invalid_geometry:0.460, neither:0.040, stop_first:0.500 |
|  |  |  |  | within_0.5 | 105 | invalid_geometry:0.381, neither:0.029, stop_first:0.571, target_first:0.019 |
|  |  |  |  | within_1.0 | 173 | invalid_geometry:0.416, neither:0.012, stop_first:0.566, target_first:0.006 |
| kg1_retest | put_wall | 1146 | invalid_geometry:0.425, neither:0.028, stop_first:0.525, target_first:0.022 | beyond | 885 | invalid_geometry:0.421, neither:0.028, stop_first:0.523, target_first:0.027 |
|  |  |  |  | within_0.1 | 22 | invalid_geometry:0.500, stop_first:0.500 |
|  |  |  |  | within_0.25 | 34 | invalid_geometry:0.471, neither:0.029, stop_first:0.500 |
|  |  |  |  | within_0.5 | 86 | invalid_geometry:0.430, neither:0.023, stop_first:0.535, target_first:0.012 |
|  |  |  |  | within_1.0 | 119 | invalid_geometry:0.420, neither:0.034, stop_first:0.546 |
| kg1_retest | max_pain | 1410 | invalid_geometry:0.423, neither:0.028, stop_first:0.526, target_first:0.023 | beyond | 972 | invalid_geometry:0.420, neither:0.027, stop_first:0.527, target_first:0.027 |
|  |  |  |  | within_0.1 | 56 | invalid_geometry:0.464, neither:0.036, stop_first:0.482, target_first:0.018 |
|  |  |  |  | within_0.25 | 65 | invalid_geometry:0.415, neither:0.031, stop_first:0.554 |
|  |  |  |  | within_0.5 | 132 | invalid_geometry:0.424, neither:0.023, stop_first:0.530, target_first:0.023 |
|  |  |  |  | within_1.0 | 185 | invalid_geometry:0.427, neither:0.032, stop_first:0.524, target_first:0.016 |
| microbalance_break | key_gamma | 3387 | invalid_geometry:0.493, neither:0.111, stop_first:0.183, target_first:0.213 | beyond | 2428 | invalid_geometry:0.495, neither:0.111, stop_first:0.178, target_first:0.216 |
|  |  |  |  | within_0.1 | 98 | invalid_geometry:0.541, neither:0.112, stop_first:0.173, target_first:0.173 |
|  |  |  |  | within_0.25 | 187 | invalid_geometry:0.385, neither:0.107, stop_first:0.251, target_first:0.257 |
|  |  |  |  | within_0.5 | 274 | invalid_geometry:0.485, neither:0.117, stop_first:0.197, target_first:0.201 |
|  |  |  |  | within_1.0 | 400 | invalid_geometry:0.520, neither:0.113, stop_first:0.175, target_first:0.193 |
| microbalance_break | put_wall | 2906 | invalid_geometry:0.496, neither:0.110, stop_first:0.180, target_first:0.214 | beyond | 2233 | invalid_geometry:0.498, neither:0.111, stop_first:0.181, target_first:0.210 |
|  |  |  |  | within_0.1 | 70 | invalid_geometry:0.529, neither:0.071, stop_first:0.100, target_first:0.300 |
|  |  |  |  | within_0.25 | 130 | invalid_geometry:0.362, neither:0.092, stop_first:0.262, target_first:0.285 |
|  |  |  |  | within_0.5 | 170 | invalid_geometry:0.459, neither:0.124, stop_first:0.176, target_first:0.241 |
|  |  |  |  | within_1.0 | 303 | invalid_geometry:0.548, neither:0.119, stop_first:0.155, target_first:0.178 |
| microbalance_break | max_pain | 3627 | invalid_geometry:0.493, neither:0.111, stop_first:0.182, target_first:0.214 | beyond | 2446 | invalid_geometry:0.491, neither:0.111, stop_first:0.185, target_first:0.213 |
|  |  |  |  | within_0.1 | 151 | invalid_geometry:0.477, neither:0.113, stop_first:0.179, target_first:0.232 |
|  |  |  |  | within_0.25 | 212 | invalid_geometry:0.458, neither:0.104, stop_first:0.189, target_first:0.250 |
|  |  |  |  | within_0.5 | 314 | invalid_geometry:0.497, neither:0.118, stop_first:0.172, target_first:0.213 |
|  |  |  |  | within_1.0 | 504 | invalid_geometry:0.522, neither:0.109, stop_first:0.173, target_first:0.196 |
| asia_tdo_case | call_wall | 1378 | invalid_geometry:0.025, neither:0.124, stop_first:0.410, target_first:0.440 | beyond | 926 | invalid_geometry:0.024, neither:0.139, stop_first:0.401, target_first:0.436 |
|  |  |  |  | within_0.1 | 68 | invalid_geometry:0.059, neither:0.088, stop_first:0.397, target_first:0.456 |
|  |  |  |  | within_0.25 | 80 | invalid_geometry:0.050, neither:0.062, stop_first:0.463, target_first:0.425 |
|  |  |  |  | within_0.5 | 114 | invalid_geometry:0.018, neither:0.132, stop_first:0.386, target_first:0.465 |
|  |  |  |  | within_1.0 | 190 | invalid_geometry:0.016, neither:0.084, stop_first:0.453, target_first:0.447 |
| asia_tdo_case | gamma_flip | 615 | invalid_geometry:0.024, neither:0.127, stop_first:0.377, target_first:0.472 | beyond | 382 | invalid_geometry:0.013, neither:0.139, stop_first:0.369, target_first:0.479 |
|  |  |  |  | within_0.1 | 30 | invalid_geometry:0.067, neither:0.033, stop_first:0.467, target_first:0.433 |
|  |  |  |  | within_0.25 | 46 | neither:0.022, stop_first:0.304, target_first:0.674 |
|  |  |  |  | within_0.5 | 56 | invalid_geometry:0.054, neither:0.125, stop_first:0.500, target_first:0.321 |
|  |  |  |  | within_1.0 | 101 | invalid_geometry:0.050, neither:0.158, stop_first:0.347, target_first:0.446 |
| nyam_box | call_wall | 2771 | invalid_geometry:0.001, neither:0.074, stop_first:0.730, target_first:0.196 | beyond | 1778 | invalid_geometry:0.001, neither:0.075, stop_first:0.726, target_first:0.199 |
|  |  |  |  | within_0.1 | 141 | neither:0.035, stop_first:0.752, target_first:0.213 |
|  |  |  |  | within_0.25 | 173 | neither:0.069, stop_first:0.734, target_first:0.197 |
|  |  |  |  | within_0.5 | 263 | neither:0.076, stop_first:0.730, target_first:0.194 |
|  |  |  |  | within_1.0 | 416 | invalid_geometry:0.002, neither:0.082, stop_first:0.738, target_first:0.178 |
| nyam_box | gamma_flip | 1247 | invalid_geometry:0.002, neither:0.082, stop_first:0.720, target_first:0.196 | beyond | 778 | invalid_geometry:0.001, neither:0.086, stop_first:0.713, target_first:0.199 |
|  |  |  |  | within_0.1 | 51 | neither:0.118, stop_first:0.745, target_first:0.137 |
|  |  |  |  | within_0.25 | 75 | neither:0.027, stop_first:0.773, target_first:0.200 |
|  |  |  |  | within_0.5 | 125 | invalid_geometry:0.008, neither:0.080, stop_first:0.744, target_first:0.168 |
|  |  |  |  | within_1.0 | 218 | neither:0.078, stop_first:0.706, target_first:0.216 |
| previous_hour | call_wall | 11760 | invalid_geometry:0.002, missing_future:0.000, neither:0.055, stop_first:0.777, target_first:0.165 | beyond | 7743 | invalid_geometry:0.002, missing_future:0.000, neither:0.056, stop_first:0.781, target_first:0.161 |
|  |  |  |  | within_0.1 | 487 | invalid_geometry:0.004, neither:0.049, stop_first:0.766, target_first:0.181 |
|  |  |  |  | within_0.25 | 691 | invalid_geometry:0.001, neither:0.058, stop_first:0.735, target_first:0.205 |
|  |  |  |  | within_0.5 | 1051 | invalid_geometry:0.002, neither:0.056, stop_first:0.755, target_first:0.187 |
|  |  |  |  | within_1.0 | 1788 | invalid_geometry:0.003, neither:0.050, stop_first:0.793, target_first:0.154 |
| previous_hour | gamma_flip | 5262 | invalid_geometry:0.002, missing_future:0.000, neither:0.056, stop_first:0.777, target_first:0.165 | beyond | 3323 | invalid_geometry:0.002, missing_future:0.000, neither:0.054, stop_first:0.782, target_first:0.162 |
|  |  |  |  | within_0.1 | 209 | neither:0.048, stop_first:0.794, target_first:0.158 |
|  |  |  |  | within_0.25 | 307 | missing_future:0.003, neither:0.052, stop_first:0.749, target_first:0.195 |
|  |  |  |  | within_0.5 | 520 | invalid_geometry:0.002, neither:0.060, stop_first:0.773, target_first:0.165 |
|  |  |  |  | within_1.0 | 903 | invalid_geometry:0.002, neither:0.064, stop_first:0.763, target_first:0.171 |
| prior_day_level | call_wall | 1036 | invalid_geometry:0.001, neither:0.305, stop_first:0.601, target_first:0.093 | beyond | 684 | invalid_geometry:0.001, neither:0.298, stop_first:0.610, target_first:0.091 |
|  |  |  |  | within_0.1 | 47 | neither:0.277, stop_first:0.638, target_first:0.085 |
|  |  |  |  | within_0.25 | 43 | neither:0.279, stop_first:0.535, target_first:0.186 |
|  |  |  |  | within_0.5 | 90 | neither:0.278, stop_first:0.656, target_first:0.067 |
|  |  |  |  | within_1.0 | 172 | neither:0.360, stop_first:0.547, target_first:0.093 |
| prior_day_level | gamma_flip | 470 | invalid_geometry:0.002, neither:0.315, stop_first:0.589, target_first:0.094 | beyond | 276 | invalid_geometry:0.004, neither:0.312, stop_first:0.591, target_first:0.094 |
|  |  |  |  | within_0.1 | 17 | neither:0.235, stop_first:0.647, target_first:0.118 |
|  |  |  |  | within_0.25 | 31 | neither:0.290, stop_first:0.581, target_first:0.129 |
|  |  |  |  | within_0.5 | 60 | neither:0.333, stop_first:0.600, target_first:0.067 |
|  |  |  |  | within_1.0 | 86 | neither:0.337, stop_first:0.570, target_first:0.093 |
| prior_month_level | call_wall | 274 | neither:0.434, stop_first:0.566 | beyond | 186 | neither:0.452, stop_first:0.548 |
|  |  |  |  | within_0.1 | 8 | neither:0.500, stop_first:0.500 |
|  |  |  |  | within_0.25 | 11 | neither:0.545, stop_first:0.455 |
|  |  |  |  | within_0.5 | 15 | neither:0.267, stop_first:0.733 |
|  |  |  |  | within_1.0 | 54 | neither:0.389, stop_first:0.611 |
| prior_month_level | gamma_flip | 116 | neither:0.388, stop_first:0.612 | beyond | 78 | neither:0.423, stop_first:0.577 |
|  |  |  |  | within_0.1 | 2 | stop_first:1.000 |
|  |  |  |  | within_0.25 | 4 | stop_first:1.000 |
|  |  |  |  | within_0.5 | 10 | neither:0.200, stop_first:0.800 |
|  |  |  |  | within_1.0 | 22 | neither:0.455, stop_first:0.545 |
| other_session | call_wall | 8764 | invalid_geometry:0.266, missing_future:0.000, neither:0.019, stop_first:0.564, target_first:0.151 | beyond | 5771 | invalid_geometry:0.269, missing_future:0.000, neither:0.018, stop_first:0.569, target_first:0.144 |
|  |  |  |  | within_0.1 | 352 | invalid_geometry:0.227, neither:0.014, stop_first:0.614, target_first:0.145 |
|  |  |  |  | within_0.25 | 544 | invalid_geometry:0.268, neither:0.018, stop_first:0.504, target_first:0.210 |
|  |  |  |  | within_0.5 | 758 | invalid_geometry:0.261, missing_future:0.001, neither:0.015, stop_first:0.566, target_first:0.157 |
|  |  |  |  | within_1.0 | 1339 | invalid_geometry:0.266, neither:0.024, stop_first:0.555, target_first:0.155 |
| other_session | gamma_flip | 3916 | invalid_geometry:0.268, missing_future:0.000, neither:0.019, stop_first:0.561, target_first:0.152 | beyond | 2458 | invalid_geometry:0.271, neither:0.019, stop_first:0.561, target_first:0.149 |
|  |  |  |  | within_0.1 | 152 | invalid_geometry:0.263, neither:0.039, stop_first:0.572, target_first:0.125 |
|  |  |  |  | within_0.25 | 229 | invalid_geometry:0.297, neither:0.017, stop_first:0.555, target_first:0.131 |
|  |  |  |  | within_0.5 | 415 | invalid_geometry:0.236, neither:0.007, stop_first:0.593, target_first:0.164 |
|  |  |  |  | within_1.0 | 662 | invalid_geometry:0.266, missing_future:0.002, neither:0.021, stop_first:0.542, target_first:0.169 |
| timed_pzone_reversal | call_wall | 2520 | invalid_geometry:0.280, missing_future:0.000, neither:0.046, stop_first:0.614, target_first:0.060 | beyond | 1664 | invalid_geometry:0.278, missing_future:0.001, neither:0.043, stop_first:0.620, target_first:0.058 |
|  |  |  |  | within_0.1 | 103 | invalid_geometry:0.175, neither:0.058, stop_first:0.660, target_first:0.107 |
|  |  |  |  | within_0.25 | 113 | invalid_geometry:0.274, neither:0.080, stop_first:0.558, target_first:0.088 |
|  |  |  |  | within_0.5 | 214 | invalid_geometry:0.318, neither:0.051, stop_first:0.598, target_first:0.033 |
|  |  |  |  | within_1.0 | 426 | invalid_geometry:0.293, neither:0.042, stop_first:0.601, target_first:0.063 |
| timed_pzone_reversal | gamma_flip | 1140 | invalid_geometry:0.274, missing_future:0.001, neither:0.048, stop_first:0.618, target_first:0.060 | beyond | 726 | invalid_geometry:0.288, neither:0.048, stop_first:0.606, target_first:0.058 |
|  |  |  |  | within_0.1 | 38 | invalid_geometry:0.184, neither:0.053, stop_first:0.658, target_first:0.105 |
|  |  |  |  | within_0.25 | 70 | invalid_geometry:0.329, missing_future:0.014, neither:0.071, stop_first:0.514, target_first:0.071 |
|  |  |  |  | within_0.5 | 98 | invalid_geometry:0.276, neither:0.041, stop_first:0.612, target_first:0.071 |
|  |  |  |  | within_1.0 | 208 | invalid_geometry:0.221, neither:0.043, stop_first:0.688, target_first:0.048 |
| continuation_retest | call_wall | 1005 | invalid_geometry:0.642, neither:0.005, stop_first:0.226, target_first:0.127 | beyond | 634 | invalid_geometry:0.632, neither:0.006, stop_first:0.222, target_first:0.139 |
|  |  |  |  | within_0.1 | 41 | invalid_geometry:0.610, stop_first:0.293, target_first:0.098 |
|  |  |  |  | within_0.25 | 78 | invalid_geometry:0.615, stop_first:0.256, target_first:0.128 |
|  |  |  |  | within_0.5 | 100 | invalid_geometry:0.710, stop_first:0.200, target_first:0.090 |
|  |  |  |  | within_1.0 | 152 | invalid_geometry:0.658, neither:0.007, stop_first:0.224, target_first:0.112 |
| continuation_retest | gamma_flip | 427 | invalid_geometry:0.667, neither:0.007, stop_first:0.199, target_first:0.126 | beyond | 278 | invalid_geometry:0.655, neither:0.011, stop_first:0.216, target_first:0.119 |
|  |  |  |  | within_0.1 | 16 | invalid_geometry:0.688, stop_first:0.312 |
|  |  |  |  | within_0.25 | 20 | invalid_geometry:0.650, stop_first:0.200, target_first:0.150 |
|  |  |  |  | within_0.5 | 53 | invalid_geometry:0.736, stop_first:0.151, target_first:0.113 |
|  |  |  |  | within_1.0 | 60 | invalid_geometry:0.667, stop_first:0.133, target_first:0.200 |
| trapped_buyers_retest | call_wall | 519 | invalid_geometry:0.595, neither:0.002, stop_first:0.256, target_first:0.146 | beyond | 337 | invalid_geometry:0.605, stop_first:0.234, target_first:0.160 |
|  |  |  |  | within_0.1 | 25 | invalid_geometry:0.600, stop_first:0.360, target_first:0.040 |
|  |  |  |  | within_0.25 | 35 | invalid_geometry:0.514, stop_first:0.343, target_first:0.143 |
|  |  |  |  | within_0.5 | 55 | invalid_geometry:0.600, stop_first:0.309, target_first:0.091 |
|  |  |  |  | within_1.0 | 67 | invalid_geometry:0.582, neither:0.015, stop_first:0.239, target_first:0.164 |
| trapped_buyers_retest | gamma_flip | 221 | invalid_geometry:0.629, neither:0.005, stop_first:0.226, target_first:0.140 | beyond | 143 | invalid_geometry:0.629, neither:0.007, stop_first:0.238, target_first:0.126 |
|  |  |  |  | within_0.1 | 9 | invalid_geometry:0.556, stop_first:0.444 |
|  |  |  |  | within_0.25 | 11 | invalid_geometry:0.636, stop_first:0.273, target_first:0.091 |
|  |  |  |  | within_0.5 | 28 | invalid_geometry:0.643, stop_first:0.214, target_first:0.143 |
|  |  |  |  | within_1.0 | 30 | invalid_geometry:0.633, stop_first:0.100, target_first:0.267 |
| kg1_retest | call_wall | 980 | invalid_geometry:0.430, neither:0.027, stop_first:0.518, target_first:0.026 | beyond | 659 | invalid_geometry:0.437, neither:0.029, stop_first:0.504, target_first:0.030 |
|  |  |  |  | within_0.1 | 41 | invalid_geometry:0.439, neither:0.024, stop_first:0.537 |
|  |  |  |  | within_0.25 | 59 | invalid_geometry:0.424, neither:0.034, stop_first:0.508, target_first:0.034 |
|  |  |  |  | within_0.5 | 85 | invalid_geometry:0.376, neither:0.035, stop_first:0.565, target_first:0.024 |
|  |  |  |  | within_1.0 | 136 | invalid_geometry:0.426, neither:0.007, stop_first:0.559, target_first:0.007 |
| kg1_retest | gamma_flip | 444 | invalid_geometry:0.432, neither:0.029, stop_first:0.516, target_first:0.023 | beyond | 297 | invalid_geometry:0.438, neither:0.020, stop_first:0.519, target_first:0.024 |
|  |  |  |  | within_0.1 | 9 | invalid_geometry:0.444, stop_first:0.556 |
|  |  |  |  | within_0.25 | 23 | invalid_geometry:0.391, neither:0.043, stop_first:0.565 |
|  |  |  |  | within_0.5 | 34 | invalid_geometry:0.441, neither:0.059, stop_first:0.471, target_first:0.029 |
|  |  |  |  | within_1.0 | 81 | invalid_geometry:0.420, neither:0.049, stop_first:0.506, target_first:0.025 |
| microbalance_break | call_wall | 2608 | invalid_geometry:0.498, neither:0.110, stop_first:0.189, target_first:0.203 | beyond | 1700 | invalid_geometry:0.505, neither:0.109, stop_first:0.180, target_first:0.206 |
|  |  |  |  | within_0.1 | 94 | invalid_geometry:0.479, neither:0.096, stop_first:0.255, target_first:0.170 |
|  |  |  |  | within_0.25 | 163 | invalid_geometry:0.460, neither:0.092, stop_first:0.221, target_first:0.227 |
|  |  |  |  | within_0.5 | 266 | invalid_geometry:0.474, neither:0.128, stop_first:0.229, target_first:0.169 |
|  |  |  |  | within_1.0 | 385 | invalid_geometry:0.506, neither:0.112, stop_first:0.171, target_first:0.210 |
| microbalance_break | gamma_flip | 1168 | invalid_geometry:0.500, neither:0.117, stop_first:0.185, target_first:0.198 | beyond | 779 | invalid_geometry:0.522, neither:0.105, stop_first:0.181, target_first:0.191 |
|  |  |  |  | within_0.1 | 41 | invalid_geometry:0.244, neither:0.146, stop_first:0.268, target_first:0.341 |
|  |  |  |  | within_0.25 | 72 | invalid_geometry:0.444, neither:0.111, stop_first:0.125, target_first:0.319 |
|  |  |  |  | within_0.5 | 109 | invalid_geometry:0.514, neither:0.110, stop_first:0.220, target_first:0.156 |
|  |  |  |  | within_1.0 | 167 | invalid_geometry:0.473, neither:0.174, stop_first:0.186, target_first:0.168 |
| failed_auction_return | key_gamma | 1388 | invalid_geometry:0.420, neither:0.007, stop_first:0.252, target_first:0.321 | beyond | 942 | invalid_geometry:0.420, neither:0.011, stop_first:0.260, target_first:0.309 |
|  |  |  |  | within_0.1 | 49 | invalid_geometry:0.449, stop_first:0.265, target_first:0.286 |
|  |  |  |  | within_0.25 | 87 | invalid_geometry:0.368, stop_first:0.310, target_first:0.322 |
|  |  |  |  | within_0.5 | 122 | invalid_geometry:0.418, stop_first:0.189, target_first:0.393 |
|  |  |  |  | within_1.0 | 188 | invalid_geometry:0.436, stop_first:0.223, target_first:0.340 |
| failed_auction_return | call_wall | 1056 | invalid_geometry:0.420, neither:0.006, stop_first:0.248, target_first:0.327 | beyond | 675 | invalid_geometry:0.419, neither:0.007, stop_first:0.261, target_first:0.313 |
|  |  |  |  | within_0.1 | 42 | invalid_geometry:0.429, stop_first:0.238, target_first:0.333 |
|  |  |  |  | within_0.25 | 72 | invalid_geometry:0.347, stop_first:0.292, target_first:0.361 |
|  |  |  |  | within_0.5 | 103 | invalid_geometry:0.408, stop_first:0.204, target_first:0.388 |
|  |  |  |  | within_1.0 | 164 | invalid_geometry:0.457, neither:0.006, stop_first:0.207, target_first:0.329 |
| failed_auction_return | put_wall | 1203 | invalid_geometry:0.420, neither:0.006, stop_first:0.259, target_first:0.315 | beyond | 883 | invalid_geometry:0.429, neither:0.008, stop_first:0.259, target_first:0.304 |
|  |  |  |  | within_0.1 | 38 | invalid_geometry:0.421, stop_first:0.211, target_first:0.368 |
|  |  |  |  | within_0.25 | 64 | invalid_geometry:0.359, stop_first:0.328, target_first:0.312 |
|  |  |  |  | within_0.5 | 89 | invalid_geometry:0.404, stop_first:0.213, target_first:0.382 |
|  |  |  |  | within_1.0 | 129 | invalid_geometry:0.395, stop_first:0.271, target_first:0.333 |
| failed_auction_return | gamma_flip | 480 | invalid_geometry:0.419, neither:0.004, stop_first:0.254, target_first:0.323 | beyond | 287 | invalid_geometry:0.418, neither:0.007, stop_first:0.258, target_first:0.317 |
|  |  |  |  | within_0.1 | 17 | invalid_geometry:0.294, stop_first:0.176, target_first:0.529 |
|  |  |  |  | within_0.25 | 39 | invalid_geometry:0.359, stop_first:0.282, target_first:0.359 |
|  |  |  |  | within_0.5 | 57 | invalid_geometry:0.456, stop_first:0.298, target_first:0.246 |
|  |  |  |  | within_1.0 | 80 | invalid_geometry:0.450, stop_first:0.212, target_first:0.338 |
| failed_auction_return | max_pain | 1488 | invalid_geometry:0.421, neither:0.007, stop_first:0.252, target_first:0.319 | beyond | 935 | invalid_geometry:0.419, neither:0.009, stop_first:0.266, target_first:0.306 |
|  |  |  |  | within_0.1 | 73 | invalid_geometry:0.479, neither:0.014, stop_first:0.151, target_first:0.356 |
|  |  |  |  | within_0.25 | 106 | invalid_geometry:0.377, stop_first:0.264, target_first:0.358 |
|  |  |  |  | within_0.5 | 162 | invalid_geometry:0.420, neither:0.006, stop_first:0.247, target_first:0.327 |
|  |  |  |  | within_1.0 | 212 | invalid_geometry:0.434, neither:0.005, stop_first:0.222, target_first:0.340 |
| poc_traversal | key_gamma | 1184 | invalid_geometry:0.494, neither:0.009, stop_first:0.167, target_first:0.329 | beyond | 769 | invalid_geometry:0.477, neither:0.013, stop_first:0.173, target_first:0.337 |
|  |  |  |  | within_0.1 | 48 | invalid_geometry:0.521, stop_first:0.167, target_first:0.312 |
|  |  |  |  | within_0.25 | 84 | invalid_geometry:0.524, stop_first:0.190, target_first:0.286 |
|  |  |  |  | within_0.5 | 117 | invalid_geometry:0.556, stop_first:0.120, target_first:0.325 |
|  |  |  |  | within_1.0 | 166 | invalid_geometry:0.506, neither:0.006, stop_first:0.163, target_first:0.325 |
| poc_traversal | call_wall | 910 | invalid_geometry:0.511, neither:0.008, stop_first:0.169, target_first:0.312 | beyond | 560 | invalid_geometry:0.498, neither:0.011, stop_first:0.175, target_first:0.316 |
|  |  |  |  | within_0.1 | 37 | invalid_geometry:0.541, stop_first:0.081, target_first:0.378 |
|  |  |  |  | within_0.25 | 78 | invalid_geometry:0.513, stop_first:0.231, target_first:0.256 |
|  |  |  |  | within_0.5 | 91 | invalid_geometry:0.538, stop_first:0.132, target_first:0.330 |
|  |  |  |  | within_1.0 | 144 | invalid_geometry:0.535, neither:0.007, stop_first:0.160, target_first:0.299 |
| poc_traversal | put_wall | 1028 | invalid_geometry:0.483, neither:0.007, stop_first:0.171, target_first:0.339 | beyond | 725 | invalid_geometry:0.463, neither:0.008, stop_first:0.186, target_first:0.342 |
|  |  |  |  | within_0.1 | 40 | invalid_geometry:0.375, stop_first:0.250, target_first:0.375 |
|  |  |  |  | within_0.25 | 50 | invalid_geometry:0.620, stop_first:0.060, target_first:0.320 |
|  |  |  |  | within_0.5 | 89 | invalid_geometry:0.573, stop_first:0.101, target_first:0.326 |
|  |  |  |  | within_1.0 | 124 | invalid_geometry:0.516, neither:0.008, stop_first:0.153, target_first:0.323 |
| poc_traversal | gamma_flip | 416 | invalid_geometry:0.502, neither:0.005, stop_first:0.178, target_first:0.315 | beyond | 252 | invalid_geometry:0.500, neither:0.008, stop_first:0.187, target_first:0.306 |
|  |  |  |  | within_0.1 | 21 | invalid_geometry:0.524, stop_first:0.190, target_first:0.286 |
|  |  |  |  | within_0.25 | 28 | invalid_geometry:0.500, stop_first:0.107, target_first:0.393 |
|  |  |  |  | within_0.5 | 46 | invalid_geometry:0.543, stop_first:0.152, target_first:0.304 |
|  |  |  |  | within_1.0 | 69 | invalid_geometry:0.478, stop_first:0.188, target_first:0.333 |
| poc_traversal | max_pain | 1264 | invalid_geometry:0.494, neither:0.009, stop_first:0.167, target_first:0.329 | beyond | 780 | invalid_geometry:0.472, neither:0.012, stop_first:0.182, target_first:0.335 |
|  |  |  |  | within_0.1 | 79 | invalid_geometry:0.506, neither:0.013, stop_first:0.177, target_first:0.304 |
|  |  |  |  | within_0.25 | 89 | invalid_geometry:0.528, neither:0.011, stop_first:0.135, target_first:0.326 |
|  |  |  |  | within_0.5 | 136 | invalid_geometry:0.544, stop_first:0.125, target_first:0.331 |
|  |  |  |  | within_1.0 | 180 | invalid_geometry:0.533, neither:0.006, stop_first:0.144, target_first:0.317 |
| absorption_reward_retest | key_gamma | 1191 | invalid_geometry:0.538, neither:0.001, stop_first:0.328, target_first:0.133 | beyond | 820 | invalid_geometry:0.545, neither:0.001, stop_first:0.323, target_first:0.130 |
|  |  |  |  | within_0.1 | 45 | invalid_geometry:0.556, stop_first:0.311, target_first:0.133 |
|  |  |  |  | within_0.25 | 73 | invalid_geometry:0.507, stop_first:0.288, target_first:0.205 |
|  |  |  |  | within_0.5 | 97 | invalid_geometry:0.598, stop_first:0.320, target_first:0.082 |
|  |  |  |  | within_1.0 | 156 | invalid_geometry:0.474, stop_first:0.385, target_first:0.141 |
| absorption_reward_retest | call_wall | 920 | invalid_geometry:0.550, neither:0.001, stop_first:0.314, target_first:0.135 | beyond | 598 | invalid_geometry:0.574, neither:0.002, stop_first:0.288, target_first:0.137 |
|  |  |  |  | within_0.1 | 32 | invalid_geometry:0.531, stop_first:0.375, target_first:0.094 |
|  |  |  |  | within_0.25 | 76 | invalid_geometry:0.487, stop_first:0.316, target_first:0.197 |
|  |  |  |  | within_0.5 | 84 | invalid_geometry:0.595, stop_first:0.333, target_first:0.071 |
|  |  |  |  | within_1.0 | 130 | invalid_geometry:0.454, stop_first:0.408, target_first:0.138 |
| absorption_reward_retest | put_wall | 1015 | invalid_geometry:0.530, stop_first:0.338, target_first:0.132 | beyond | 729 | invalid_geometry:0.529, stop_first:0.343, target_first:0.128 |
|  |  |  |  | within_0.1 | 37 | invalid_geometry:0.541, stop_first:0.297, target_first:0.162 |
|  |  |  |  | within_0.25 | 45 | invalid_geometry:0.533, stop_first:0.244, target_first:0.222 |
|  |  |  |  | within_0.5 | 68 | invalid_geometry:0.574, stop_first:0.338, target_first:0.088 |
|  |  |  |  | within_1.0 | 136 | invalid_geometry:0.507, stop_first:0.353, target_first:0.140 |
| absorption_reward_retest | gamma_flip | 394 | invalid_geometry:0.548, stop_first:0.325, target_first:0.127 | beyond | 232 | invalid_geometry:0.534, stop_first:0.345, target_first:0.121 |
|  |  |  |  | within_0.1 | 16 | invalid_geometry:0.750, stop_first:0.188, target_first:0.062 |
|  |  |  |  | within_0.25 | 31 | invalid_geometry:0.710, stop_first:0.226, target_first:0.065 |
|  |  |  |  | within_0.5 | 49 | invalid_geometry:0.490, stop_first:0.388, target_first:0.122 |
|  |  |  |  | within_1.0 | 66 | invalid_geometry:0.515, stop_first:0.288, target_first:0.197 |
| absorption_reward_retest | max_pain | 1268 | invalid_geometry:0.535, neither:0.001, stop_first:0.324, target_first:0.140 | beyond | 810 | invalid_geometry:0.538, neither:0.001, stop_first:0.314, target_first:0.147 |
|  |  |  |  | within_0.1 | 73 | invalid_geometry:0.575, stop_first:0.288, target_first:0.137 |
|  |  |  |  | within_0.25 | 79 | invalid_geometry:0.557, stop_first:0.316, target_first:0.127 |
|  |  |  |  | within_0.5 | 123 | invalid_geometry:0.569, stop_first:0.341, target_first:0.089 |
|  |  |  |  | within_1.0 | 183 | invalid_geometry:0.470, stop_first:0.377, target_first:0.153 |
| balance_failure_fade | key_gamma | 1191 | invalid_geometry:0.534, neither:0.001, stop_first:0.332, target_first:0.133 | beyond | 820 | invalid_geometry:0.539, neither:0.001, stop_first:0.329, target_first:0.130 |
|  |  |  |  | within_0.1 | 45 | invalid_geometry:0.556, stop_first:0.311, target_first:0.133 |
|  |  |  |  | within_0.25 | 73 | invalid_geometry:0.479, stop_first:0.315, target_first:0.205 |
|  |  |  |  | within_0.5 | 97 | invalid_geometry:0.608, stop_first:0.309, target_first:0.082 |
|  |  |  |  | within_1.0 | 156 | invalid_geometry:0.481, stop_first:0.378, target_first:0.141 |
| balance_failure_fade | call_wall | 920 | invalid_geometry:0.547, neither:0.001, stop_first:0.317, target_first:0.135 | beyond | 598 | invalid_geometry:0.574, neither:0.002, stop_first:0.288, target_first:0.137 |
|  |  |  |  | within_0.1 | 32 | invalid_geometry:0.531, stop_first:0.375, target_first:0.094 |
|  |  |  |  | within_0.25 | 77 | invalid_geometry:0.455, stop_first:0.351, target_first:0.195 |
|  |  |  |  | within_0.5 | 84 | invalid_geometry:0.607, stop_first:0.321, target_first:0.071 |
|  |  |  |  | within_1.0 | 129 | invalid_geometry:0.442, stop_first:0.419, target_first:0.140 |
| balance_failure_fade | put_wall | 1015 | invalid_geometry:0.525, stop_first:0.343, target_first:0.132 | beyond | 729 | invalid_geometry:0.521, stop_first:0.351, target_first:0.128 |
|  |  |  |  | within_0.1 | 37 | invalid_geometry:0.541, stop_first:0.297, target_first:0.162 |
|  |  |  |  | within_0.25 | 45 | invalid_geometry:0.511, stop_first:0.267, target_first:0.222 |
|  |  |  |  | within_0.5 | 68 | invalid_geometry:0.588, stop_first:0.324, target_first:0.088 |
|  |  |  |  | within_1.0 | 136 | invalid_geometry:0.515, stop_first:0.346, target_first:0.140 |
| balance_failure_fade | gamma_flip | 394 | invalid_geometry:0.546, stop_first:0.327, target_first:0.127 | beyond | 232 | invalid_geometry:0.530, stop_first:0.349, target_first:0.121 |
|  |  |  |  | within_0.1 | 15 | invalid_geometry:0.800, stop_first:0.133, target_first:0.067 |
|  |  |  |  | within_0.25 | 32 | invalid_geometry:0.719, stop_first:0.219, target_first:0.062 |
|  |  |  |  | within_0.5 | 49 | invalid_geometry:0.490, stop_first:0.388, target_first:0.122 |
|  |  |  |  | within_1.0 | 66 | invalid_geometry:0.500, stop_first:0.303, target_first:0.197 |
| balance_failure_fade | max_pain | 1268 | invalid_geometry:0.531, neither:0.001, stop_first:0.328, target_first:0.140 | beyond | 810 | invalid_geometry:0.533, neither:0.001, stop_first:0.319, target_first:0.147 |
|  |  |  |  | within_0.1 | 73 | invalid_geometry:0.589, stop_first:0.274, target_first:0.137 |
|  |  |  |  | within_0.25 | 79 | invalid_geometry:0.544, stop_first:0.329, target_first:0.127 |
|  |  |  |  | within_0.5 | 123 | invalid_geometry:0.569, stop_first:0.341, target_first:0.089 |
|  |  |  |  | within_1.0 | 183 | invalid_geometry:0.464, stop_first:0.383, target_first:0.153 |
| clean_squeeze | key_gamma | 1191 | invalid_geometry:0.542, neither:0.001, stop_first:0.322, target_first:0.135 | beyond | 820 | invalid_geometry:0.546, neither:0.001, stop_first:0.320, target_first:0.133 |
|  |  |  |  | within_0.1 | 45 | invalid_geometry:0.556, stop_first:0.311, target_first:0.133 |
|  |  |  |  | within_0.25 | 73 | invalid_geometry:0.521, stop_first:0.274, target_first:0.205 |
|  |  |  |  | within_0.5 | 97 | invalid_geometry:0.608, stop_first:0.309, target_first:0.082 |
|  |  |  |  | within_1.0 | 156 | invalid_geometry:0.487, stop_first:0.365, target_first:0.147 |
| clean_squeeze | call_wall | 920 | invalid_geometry:0.557, neither:0.001, stop_first:0.307, target_first:0.136 | beyond | 598 | invalid_geometry:0.579, neither:0.002, stop_first:0.283, target_first:0.137 |
|  |  |  |  | within_0.1 | 32 | invalid_geometry:0.531, stop_first:0.375, target_first:0.094 |
|  |  |  |  | within_0.25 | 76 | invalid_geometry:0.500, stop_first:0.303, target_first:0.197 |
|  |  |  |  | within_0.5 | 85 | invalid_geometry:0.612, stop_first:0.318, target_first:0.071 |
|  |  |  |  | within_1.0 | 129 | invalid_geometry:0.457, stop_first:0.395, target_first:0.147 |
| clean_squeeze | put_wall | 1015 | invalid_geometry:0.534, stop_first:0.331, target_first:0.135 | beyond | 729 | invalid_geometry:0.529, stop_first:0.337, target_first:0.133 |
|  |  |  |  | within_0.1 | 37 | invalid_geometry:0.514, stop_first:0.324, target_first:0.162 |
|  |  |  |  | within_0.25 | 45 | invalid_geometry:0.533, stop_first:0.244, target_first:0.222 |
|  |  |  |  | within_0.5 | 68 | invalid_geometry:0.588, stop_first:0.324, target_first:0.088 |
|  |  |  |  | within_1.0 | 136 | invalid_geometry:0.537, stop_first:0.331, target_first:0.132 |
| clean_squeeze | gamma_flip | 394 | invalid_geometry:0.558, stop_first:0.315, target_first:0.127 | beyond | 232 | invalid_geometry:0.543, stop_first:0.341, target_first:0.116 |
|  |  |  |  | within_0.1 | 15 | invalid_geometry:0.800, stop_first:0.133, target_first:0.067 |
|  |  |  |  | within_0.25 | 32 | invalid_geometry:0.688, stop_first:0.250, target_first:0.062 |
|  |  |  |  | within_0.5 | 49 | invalid_geometry:0.490, stop_first:0.388, target_first:0.122 |
|  |  |  |  | within_1.0 | 66 | invalid_geometry:0.545, stop_first:0.242, target_first:0.212 |
| clean_squeeze | max_pain | 1268 | invalid_geometry:0.539, neither:0.001, stop_first:0.317, target_first:0.143 | beyond | 810 | invalid_geometry:0.541, neither:0.001, stop_first:0.307, target_first:0.151 |
|  |  |  |  | within_0.1 | 73 | invalid_geometry:0.575, stop_first:0.288, target_first:0.137 |
|  |  |  |  | within_0.25 | 79 | invalid_geometry:0.557, stop_first:0.316, target_first:0.127 |
|  |  |  |  | within_0.5 | 123 | invalid_geometry:0.577, stop_first:0.333, target_first:0.089 |
|  |  |  |  | within_1.0 | 183 | invalid_geometry:0.486, stop_first:0.361, target_first:0.153 |
| dom_rejection | key_gamma | 1191 | invalid_geometry:0.487, neither:0.001, stop_first:0.385, target_first:0.127 | beyond | 819 | invalid_geometry:0.493, neither:0.001, stop_first:0.383, target_first:0.122 |
|  |  |  |  | within_0.1 | 45 | invalid_geometry:0.511, stop_first:0.333, target_first:0.156 |
|  |  |  |  | within_0.25 | 74 | invalid_geometry:0.432, stop_first:0.365, target_first:0.203 |
|  |  |  |  | within_0.5 | 97 | invalid_geometry:0.557, stop_first:0.371, target_first:0.072 |
|  |  |  |  | within_1.0 | 156 | invalid_geometry:0.429, stop_first:0.429, target_first:0.141 |
| dom_rejection | call_wall | 920 | invalid_geometry:0.499, neither:0.001, stop_first:0.374, target_first:0.126 | beyond | 597 | invalid_geometry:0.521, neither:0.002, stop_first:0.353, target_first:0.124 |
|  |  |  |  | within_0.1 | 32 | invalid_geometry:0.469, stop_first:0.406, target_first:0.125 |
|  |  |  |  | within_0.25 | 78 | invalid_geometry:0.423, stop_first:0.385, target_first:0.192 |
|  |  |  |  | within_0.5 | 83 | invalid_geometry:0.554, stop_first:0.386, target_first:0.060 |
|  |  |  |  | within_1.0 | 130 | invalid_geometry:0.415, stop_first:0.446, target_first:0.138 |
| dom_rejection | put_wall | 1015 | invalid_geometry:0.476, stop_first:0.395, target_first:0.129 | beyond | 729 | invalid_geometry:0.473, stop_first:0.402, target_first:0.125 |
|  |  |  |  | within_0.1 | 37 | invalid_geometry:0.514, stop_first:0.324, target_first:0.162 |
|  |  |  |  | within_0.25 | 45 | invalid_geometry:0.467, stop_first:0.311, target_first:0.222 |
|  |  |  |  | within_0.5 | 68 | invalid_geometry:0.544, stop_first:0.368, target_first:0.088 |
|  |  |  |  | within_1.0 | 136 | invalid_geometry:0.449, stop_first:0.419, target_first:0.132 |
| dom_rejection | gamma_flip | 394 | invalid_geometry:0.487, stop_first:0.393, target_first:0.119 | beyond | 232 | invalid_geometry:0.483, stop_first:0.401, target_first:0.116 |
|  |  |  |  | within_0.1 | 15 | invalid_geometry:0.600, stop_first:0.333, target_first:0.067 |
|  |  |  |  | within_0.25 | 32 | invalid_geometry:0.562, stop_first:0.406, target_first:0.031 |
|  |  |  |  | within_0.5 | 48 | invalid_geometry:0.479, stop_first:0.417, target_first:0.104 |
|  |  |  |  | within_1.0 | 67 | invalid_geometry:0.448, stop_first:0.358, target_first:0.194 |
| dom_rejection | max_pain | 1268 | invalid_geometry:0.483, neither:0.001, stop_first:0.382, target_first:0.134 | beyond | 810 | invalid_geometry:0.481, neither:0.001, stop_first:0.379, target_first:0.138 |
|  |  |  |  | within_0.1 | 72 | invalid_geometry:0.542, stop_first:0.319, target_first:0.139 |
|  |  |  |  | within_0.25 | 81 | invalid_geometry:0.494, stop_first:0.395, target_first:0.111 |
|  |  |  |  | within_0.5 | 123 | invalid_geometry:0.545, stop_first:0.366, target_first:0.089 |
|  |  |  |  | within_1.0 | 182 | invalid_geometry:0.423, stop_first:0.423, target_first:0.154 |
| footprint_confirmed_reaction | key_gamma | 1191 | invalid_geometry:0.487, neither:0.001, stop_first:0.385, target_first:0.128 | beyond | 819 | invalid_geometry:0.493, neither:0.001, stop_first:0.383, target_first:0.122 |
|  |  |  |  | within_0.1 | 45 | invalid_geometry:0.511, stop_first:0.333, target_first:0.156 |
|  |  |  |  | within_0.25 | 74 | invalid_geometry:0.432, stop_first:0.365, target_first:0.203 |
|  |  |  |  | within_0.5 | 97 | invalid_geometry:0.557, stop_first:0.361, target_first:0.082 |
|  |  |  |  | within_1.0 | 156 | invalid_geometry:0.429, stop_first:0.429, target_first:0.141 |
| footprint_confirmed_reaction | call_wall | 920 | invalid_geometry:0.499, neither:0.001, stop_first:0.373, target_first:0.127 | beyond | 597 | invalid_geometry:0.521, neither:0.002, stop_first:0.353, target_first:0.124 |
|  |  |  |  | within_0.1 | 32 | invalid_geometry:0.469, stop_first:0.406, target_first:0.125 |
|  |  |  |  | within_0.25 | 78 | invalid_geometry:0.423, stop_first:0.385, target_first:0.192 |
|  |  |  |  | within_0.5 | 83 | invalid_geometry:0.554, stop_first:0.373, target_first:0.072 |
|  |  |  |  | within_1.0 | 130 | invalid_geometry:0.415, stop_first:0.446, target_first:0.138 |
| footprint_confirmed_reaction | put_wall | 1015 | invalid_geometry:0.476, stop_first:0.394, target_first:0.130 | beyond | 729 | invalid_geometry:0.473, stop_first:0.401, target_first:0.126 |
|  |  |  |  | within_0.1 | 37 | invalid_geometry:0.514, stop_first:0.324, target_first:0.162 |
|  |  |  |  | within_0.25 | 45 | invalid_geometry:0.467, stop_first:0.311, target_first:0.222 |
|  |  |  |  | within_0.5 | 68 | invalid_geometry:0.544, stop_first:0.368, target_first:0.088 |
|  |  |  |  | within_1.0 | 136 | invalid_geometry:0.449, stop_first:0.419, target_first:0.132 |
| footprint_confirmed_reaction | gamma_flip | 394 | invalid_geometry:0.487, stop_first:0.391, target_first:0.122 | beyond | 232 | invalid_geometry:0.483, stop_first:0.401, target_first:0.116 |
|  |  |  |  | within_0.1 | 15 | invalid_geometry:0.600, stop_first:0.333, target_first:0.067 |
|  |  |  |  | within_0.25 | 32 | invalid_geometry:0.562, stop_first:0.375, target_first:0.062 |
|  |  |  |  | within_0.5 | 48 | invalid_geometry:0.479, stop_first:0.417, target_first:0.104 |
|  |  |  |  | within_1.0 | 67 | invalid_geometry:0.448, stop_first:0.358, target_first:0.194 |
| footprint_confirmed_reaction | max_pain | 1268 | invalid_geometry:0.483, neither:0.001, stop_first:0.381, target_first:0.135 | beyond | 810 | invalid_geometry:0.481, neither:0.001, stop_first:0.379, target_first:0.138 |
|  |  |  |  | within_0.1 | 72 | invalid_geometry:0.542, stop_first:0.319, target_first:0.139 |
|  |  |  |  | within_0.25 | 81 | invalid_geometry:0.494, stop_first:0.383, target_first:0.123 |
|  |  |  |  | within_0.5 | 123 | invalid_geometry:0.545, stop_first:0.366, target_first:0.089 |
|  |  |  |  | within_1.0 | 182 | invalid_geometry:0.423, stop_first:0.423, target_first:0.154 |
| ofm_aggressive | key_gamma | 1191 | invalid_geometry:0.549, neither:0.001, stop_first:0.316, target_first:0.134 | beyond | 820 | invalid_geometry:0.552, neither:0.001, stop_first:0.315, target_first:0.132 |
|  |  |  |  | within_0.1 | 45 | invalid_geometry:0.556, stop_first:0.311, target_first:0.133 |
|  |  |  |  | within_0.25 | 73 | invalid_geometry:0.521, stop_first:0.274, target_first:0.205 |
|  |  |  |  | within_0.5 | 97 | invalid_geometry:0.619, stop_first:0.299, target_first:0.082 |
|  |  |  |  | within_1.0 | 156 | invalid_geometry:0.500, stop_first:0.353, target_first:0.147 |
| ofm_aggressive | call_wall | 920 | invalid_geometry:0.562, neither:0.001, stop_first:0.301, target_first:0.136 | beyond | 598 | invalid_geometry:0.585, neither:0.002, stop_first:0.276, target_first:0.137 |
|  |  |  |  | within_0.1 | 32 | invalid_geometry:0.531, stop_first:0.375, target_first:0.094 |
|  |  |  |  | within_0.25 | 76 | invalid_geometry:0.500, stop_first:0.303, target_first:0.197 |
|  |  |  |  | within_0.5 | 85 | invalid_geometry:0.624, stop_first:0.306, target_first:0.071 |
|  |  |  |  | within_1.0 | 129 | invalid_geometry:0.457, stop_first:0.395, target_first:0.147 |
| ofm_aggressive | put_wall | 1015 | invalid_geometry:0.542, stop_first:0.324, target_first:0.134 | beyond | 729 | invalid_geometry:0.535, stop_first:0.333, target_first:0.132 |
|  |  |  |  | within_0.1 | 37 | invalid_geometry:0.541, stop_first:0.297, target_first:0.162 |
|  |  |  |  | within_0.25 | 45 | invalid_geometry:0.533, stop_first:0.244, target_first:0.222 |
|  |  |  |  | within_0.5 | 68 | invalid_geometry:0.588, stop_first:0.324, target_first:0.088 |
|  |  |  |  | within_1.0 | 136 | invalid_geometry:0.559, stop_first:0.309, target_first:0.132 |
| ofm_aggressive | gamma_flip | 394 | invalid_geometry:0.569, stop_first:0.305, target_first:0.127 | beyond | 232 | invalid_geometry:0.556, stop_first:0.328, target_first:0.116 |
|  |  |  |  | within_0.1 | 15 | invalid_geometry:0.800, stop_first:0.133, target_first:0.067 |
|  |  |  |  | within_0.25 | 33 | invalid_geometry:0.697, stop_first:0.242, target_first:0.061 |
|  |  |  |  | within_0.5 | 48 | invalid_geometry:0.500, stop_first:0.375, target_first:0.125 |
|  |  |  |  | within_1.0 | 66 | invalid_geometry:0.545, stop_first:0.242, target_first:0.212 |
| ofm_aggressive | max_pain | 1268 | invalid_geometry:0.546, neither:0.001, stop_first:0.312, target_first:0.142 | beyond | 810 | invalid_geometry:0.546, neither:0.001, stop_first:0.304, target_first:0.149 |
|  |  |  |  | within_0.1 | 73 | invalid_geometry:0.589, stop_first:0.274, target_first:0.137 |
|  |  |  |  | within_0.25 | 79 | invalid_geometry:0.570, stop_first:0.304, target_first:0.127 |
|  |  |  |  | within_0.5 | 123 | invalid_geometry:0.577, stop_first:0.333, target_first:0.089 |
|  |  |  |  | within_1.0 | 183 | invalid_geometry:0.497, stop_first:0.350, target_first:0.153 |
| stop_four_stage | key_gamma | 1191 | invalid_geometry:0.538, neither:0.001, stop_first:0.327, target_first:0.134 | beyond | 820 | invalid_geometry:0.540, neither:0.001, stop_first:0.327, target_first:0.132 |
|  |  |  |  | within_0.1 | 45 | invalid_geometry:0.556, stop_first:0.311, target_first:0.133 |
|  |  |  |  | within_0.25 | 73 | invalid_geometry:0.507, stop_first:0.288, target_first:0.205 |
|  |  |  |  | within_0.5 | 98 | invalid_geometry:0.612, stop_first:0.296, target_first:0.092 |
|  |  |  |  | within_1.0 | 155 | invalid_geometry:0.490, stop_first:0.368, target_first:0.142 |
| stop_four_stage | call_wall | 920 | invalid_geometry:0.551, neither:0.001, stop_first:0.312, target_first:0.136 | beyond | 598 | invalid_geometry:0.572, neither:0.002, stop_first:0.289, target_first:0.137 |
|  |  |  |  | within_0.1 | 32 | invalid_geometry:0.531, stop_first:0.375, target_first:0.094 |
|  |  |  |  | within_0.25 | 76 | invalid_geometry:0.487, stop_first:0.316, target_first:0.197 |
|  |  |  |  | within_0.5 | 86 | invalid_geometry:0.616, stop_first:0.302, target_first:0.081 |
|  |  |  |  | within_1.0 | 128 | invalid_geometry:0.453, stop_first:0.406, target_first:0.141 |
| stop_four_stage | put_wall | 1015 | invalid_geometry:0.531, stop_first:0.335, target_first:0.134 | beyond | 729 | invalid_geometry:0.523, stop_first:0.346, target_first:0.132 |
|  |  |  |  | within_0.1 | 37 | invalid_geometry:0.541, stop_first:0.297, target_first:0.162 |
|  |  |  |  | within_0.25 | 45 | invalid_geometry:0.533, stop_first:0.244, target_first:0.222 |
|  |  |  |  | within_0.5 | 68 | invalid_geometry:0.588, stop_first:0.324, target_first:0.088 |
|  |  |  |  | within_1.0 | 136 | invalid_geometry:0.544, stop_first:0.324, target_first:0.132 |
| stop_four_stage | gamma_flip | 394 | invalid_geometry:0.553, stop_first:0.320, target_first:0.127 | beyond | 232 | invalid_geometry:0.534, stop_first:0.349, target_first:0.116 |
|  |  |  |  | within_0.1 | 14 | invalid_geometry:0.786, stop_first:0.143, target_first:0.071 |
|  |  |  |  | within_0.25 | 34 | invalid_geometry:0.676, stop_first:0.265, target_first:0.059 |
|  |  |  |  | within_0.5 | 48 | invalid_geometry:0.500, stop_first:0.375, target_first:0.125 |
|  |  |  |  | within_1.0 | 66 | invalid_geometry:0.545, stop_first:0.242, target_first:0.212 |
| stop_four_stage | max_pain | 1268 | invalid_geometry:0.534, neither:0.001, stop_first:0.323, target_first:0.142 | beyond | 810 | invalid_geometry:0.532, neither:0.001, stop_first:0.317, target_first:0.149 |
|  |  |  |  | within_0.1 | 73 | invalid_geometry:0.589, stop_first:0.274, target_first:0.137 |
|  |  |  |  | within_0.25 | 79 | invalid_geometry:0.544, stop_first:0.329, target_first:0.127 |
|  |  |  |  | within_0.5 | 123 | invalid_geometry:0.577, stop_first:0.333, target_first:0.089 |
|  |  |  |  | within_1.0 | 183 | invalid_geometry:0.486, stop_first:0.361, target_first:0.153 |
| vwap_deviation_fade | key_gamma | 1270 | invalid_geometry:0.417, neither:0.001, stop_first:0.467, target_first:0.116 | beyond | 899 | invalid_geometry:0.404, neither:0.001, stop_first:0.475, target_first:0.120 |
|  |  |  |  | within_0.1 | 45 | invalid_geometry:0.378, stop_first:0.422, target_first:0.200 |
|  |  |  |  | within_0.25 | 80 | invalid_geometry:0.425, stop_first:0.525, target_first:0.050 |
|  |  |  |  | within_0.5 | 91 | invalid_geometry:0.451, stop_first:0.440, target_first:0.110 |
|  |  |  |  | within_1.0 | 155 | invalid_geometry:0.477, stop_first:0.419, target_first:0.103 |
| vwap_deviation_fade | call_wall | 983 | invalid_geometry:0.434, stop_first:0.452, target_first:0.114 | beyond | 648 | invalid_geometry:0.446, stop_first:0.438, target_first:0.116 |
|  |  |  |  | within_0.1 | 38 | invalid_geometry:0.421, stop_first:0.421, target_first:0.158 |
|  |  |  |  | within_0.25 | 74 | invalid_geometry:0.432, stop_first:0.500, target_first:0.068 |
|  |  |  |  | within_0.5 | 88 | invalid_geometry:0.386, stop_first:0.489, target_first:0.125 |
|  |  |  |  | within_1.0 | 135 | invalid_geometry:0.415, stop_first:0.474, target_first:0.111 |
| vwap_deviation_fade | put_wall | 1101 | invalid_geometry:0.414, neither:0.001, stop_first:0.467, target_first:0.118 | beyond | 817 | invalid_geometry:0.398, neither:0.001, stop_first:0.480, target_first:0.121 |
|  |  |  |  | within_0.1 | 37 | invalid_geometry:0.432, stop_first:0.405, target_first:0.162 |
|  |  |  |  | within_0.25 | 47 | invalid_geometry:0.511, stop_first:0.468, target_first:0.021 |
|  |  |  |  | within_0.5 | 68 | invalid_geometry:0.456, stop_first:0.471, target_first:0.074 |
|  |  |  |  | within_1.0 | 132 | invalid_geometry:0.455, stop_first:0.402, target_first:0.144 |
| vwap_deviation_fade | gamma_flip | 443 | invalid_geometry:0.415, stop_first:0.472, target_first:0.113 | beyond | 271 | invalid_geometry:0.406, stop_first:0.472, target_first:0.122 |
|  |  |  |  | within_0.1 | 23 | invalid_geometry:0.435, stop_first:0.435, target_first:0.130 |
|  |  |  |  | within_0.25 | 29 | invalid_geometry:0.379, stop_first:0.552, target_first:0.069 |
|  |  |  |  | within_0.5 | 54 | invalid_geometry:0.444, stop_first:0.481, target_first:0.074 |
|  |  |  |  | within_1.0 | 66 | invalid_geometry:0.439, stop_first:0.439, target_first:0.121 |
| vwap_deviation_fade | max_pain | 1350 | invalid_geometry:0.416, neither:0.001, stop_first:0.467, target_first:0.116 | beyond | 870 | invalid_geometry:0.406, neither:0.001, stop_first:0.476, target_first:0.117 |
|  |  |  |  | within_0.1 | 69 | invalid_geometry:0.377, stop_first:0.464, target_first:0.159 |
|  |  |  |  | within_0.25 | 93 | invalid_geometry:0.452, stop_first:0.484, target_first:0.065 |
|  |  |  |  | within_0.5 | 127 | invalid_geometry:0.480, stop_first:0.425, target_first:0.094 |
|  |  |  |  | within_1.0 | 191 | invalid_geometry:0.419, stop_first:0.445, target_first:0.136 |
| prior_week_level | key_gamma | 682 | neither:0.479, stop_first:0.515, target_first:0.006 | beyond | 495 | neither:0.489, stop_first:0.503, target_first:0.008 |
|  |  |  |  | within_0.1 | 19 | neither:0.526, stop_first:0.474 |
|  |  |  |  | within_0.25 | 34 | neither:0.412, stop_first:0.588 |
|  |  |  |  | within_0.5 | 44 | neither:0.341, stop_first:0.659 |
|  |  |  |  | within_1.0 | 90 | neither:0.511, stop_first:0.489 |
| prior_week_level | put_wall | 599 | neither:0.476, stop_first:0.518, target_first:0.007 | beyond | 450 | neither:0.482, stop_first:0.509, target_first:0.009 |
|  |  |  |  | within_0.1 | 16 | neither:0.375, stop_first:0.625 |
|  |  |  |  | within_0.25 | 25 | neither:0.360, stop_first:0.640 |
|  |  |  |  | within_0.5 | 34 | neither:0.353, stop_first:0.647 |
|  |  |  |  | within_1.0 | 74 | neither:0.554, stop_first:0.446 |
| prior_week_level | max_pain | 726 | neither:0.483, stop_first:0.511, target_first:0.006 | beyond | 484 | neither:0.492, stop_first:0.500, target_first:0.008 |
|  |  |  |  | within_0.1 | 44 | neither:0.523, stop_first:0.477 |
|  |  |  |  | within_0.25 | 38 | neither:0.474, stop_first:0.526 |
|  |  |  |  | within_0.5 | 56 | neither:0.464, stop_first:0.536 |
|  |  |  |  | within_1.0 | 104 | neither:0.442, stop_first:0.558 |
| defended_band_continuation | key_gamma | 601 | invalid_geometry:0.384, stop_first:0.488, target_first:0.128 | beyond | 422 | invalid_geometry:0.382, stop_first:0.509, target_first:0.109 |
|  |  |  |  | within_0.1 | 22 | invalid_geometry:0.409, stop_first:0.364, target_first:0.227 |
|  |  |  |  | within_0.25 | 43 | invalid_geometry:0.349, stop_first:0.465, target_first:0.186 |
|  |  |  |  | within_0.5 | 47 | invalid_geometry:0.447, stop_first:0.404, target_first:0.149 |
|  |  |  |  | within_1.0 | 67 | invalid_geometry:0.373, stop_first:0.463, target_first:0.164 |
| defended_band_continuation | put_wall | 514 | invalid_geometry:0.395, stop_first:0.488, target_first:0.117 | beyond | 401 | invalid_geometry:0.401, stop_first:0.499, target_first:0.100 |
|  |  |  |  | within_0.1 | 17 | invalid_geometry:0.529, stop_first:0.353, target_first:0.118 |
|  |  |  |  | within_0.25 | 25 | invalid_geometry:0.400, stop_first:0.320, target_first:0.280 |
|  |  |  |  | within_0.5 | 25 | invalid_geometry:0.480, stop_first:0.400, target_first:0.120 |
|  |  |  |  | within_1.0 | 46 | invalid_geometry:0.239, stop_first:0.587, target_first:0.174 |
| defended_band_continuation | max_pain | 637 | invalid_geometry:0.388, stop_first:0.490, target_first:0.122 | beyond | 429 | invalid_geometry:0.392, stop_first:0.508, target_first:0.100 |
|  |  |  |  | within_0.1 | 29 | invalid_geometry:0.483, stop_first:0.345, target_first:0.172 |
|  |  |  |  | within_0.25 | 46 | invalid_geometry:0.457, stop_first:0.413, target_first:0.130 |
|  |  |  |  | within_0.5 | 54 | invalid_geometry:0.370, stop_first:0.407, target_first:0.222 |
|  |  |  |  | within_1.0 | 79 | invalid_geometry:0.304, stop_first:0.544, target_first:0.152 |
| prior_week_level | call_wall | 513 | neither:0.466, stop_first:0.528, target_first:0.006 | beyond | 350 | neither:0.457, stop_first:0.534, target_first:0.009 |
|  |  |  |  | within_0.1 | 18 | neither:0.556, stop_first:0.444 |
|  |  |  |  | within_0.25 | 22 | neither:0.409, stop_first:0.591 |
|  |  |  |  | within_0.5 | 42 | neither:0.452, stop_first:0.548 |
|  |  |  |  | within_1.0 | 81 | neither:0.506, stop_first:0.494 |
| prior_week_level | gamma_flip | 236 | neither:0.424, stop_first:0.564, target_first:0.013 | beyond | 158 | neither:0.392, stop_first:0.601, target_first:0.006 |
|  |  |  |  | within_0.1 | 11 | neither:0.364, stop_first:0.636 |
|  |  |  |  | within_0.25 | 8 | neither:0.375, stop_first:0.625 |
|  |  |  |  | within_0.5 | 22 | neither:0.636, stop_first:0.364 |
|  |  |  |  | within_1.0 | 37 | neither:0.459, stop_first:0.486, target_first:0.054 |
| defended_band_continuation | call_wall | 459 | invalid_geometry:0.386, stop_first:0.475, target_first:0.139 | beyond | 298 | invalid_geometry:0.369, stop_first:0.513, target_first:0.117 |
|  |  |  |  | within_0.1 | 19 | invalid_geometry:0.421, stop_first:0.316, target_first:0.263 |
|  |  |  |  | within_0.25 | 32 | invalid_geometry:0.344, stop_first:0.531, target_first:0.125 |
|  |  |  |  | within_0.5 | 44 | invalid_geometry:0.455, stop_first:0.409, target_first:0.136 |
|  |  |  |  | within_1.0 | 66 | invalid_geometry:0.424, stop_first:0.364, target_first:0.212 |
| defended_band_continuation | gamma_flip | 222 | invalid_geometry:0.360, stop_first:0.518, target_first:0.122 | beyond | 133 | invalid_geometry:0.293, stop_first:0.594, target_first:0.113 |
|  |  |  |  | within_0.1 | 5 | invalid_geometry:0.600, stop_first:0.200, target_first:0.200 |
|  |  |  |  | within_0.25 | 23 | invalid_geometry:0.522, stop_first:0.348, target_first:0.130 |
|  |  |  |  | within_0.5 | 21 | invalid_geometry:0.476, stop_first:0.381, target_first:0.143 |
|  |  |  |  | within_1.0 | 40 | invalid_geometry:0.400, stop_first:0.475, target_first:0.125 |
| ofm_passive | key_gamma | 580 | invalid_geometry:0.547, neither:0.002, stop_first:0.314, target_first:0.138 | beyond | 402 | invalid_geometry:0.542, neither:0.002, stop_first:0.311, target_first:0.144 |
|  |  |  |  | within_0.1 | 14 | invalid_geometry:0.643, stop_first:0.214, target_first:0.143 |
|  |  |  |  | within_0.25 | 35 | invalid_geometry:0.514, stop_first:0.314, target_first:0.171 |
|  |  |  |  | within_0.5 | 50 | invalid_geometry:0.640, stop_first:0.260, target_first:0.100 |
|  |  |  |  | within_1.0 | 79 | invalid_geometry:0.506, stop_first:0.380, target_first:0.114 |
| ofm_passive | call_wall | 453 | invalid_geometry:0.570, neither:0.002, stop_first:0.300, target_first:0.128 | beyond | 303 | invalid_geometry:0.564, neither:0.003, stop_first:0.290, target_first:0.142 |
|  |  |  |  | within_0.1 | 10 | invalid_geometry:0.600, stop_first:0.300, target_first:0.100 |
|  |  |  |  | within_0.25 | 37 | invalid_geometry:0.486, stop_first:0.324, target_first:0.189 |
|  |  |  |  | within_0.5 | 42 | invalid_geometry:0.714, stop_first:0.262, target_first:0.024 |
|  |  |  |  | within_1.0 | 61 | invalid_geometry:0.541, stop_first:0.361, target_first:0.098 |
| ofm_passive | max_pain | 619 | invalid_geometry:0.541, neither:0.002, stop_first:0.307, target_first:0.150 | beyond | 394 | invalid_geometry:0.533, neither:0.003, stop_first:0.302, target_first:0.162 |
|  |  |  |  | within_0.1 | 34 | invalid_geometry:0.618, stop_first:0.324, target_first:0.059 |
|  |  |  |  | within_0.25 | 40 | invalid_geometry:0.625, stop_first:0.275, target_first:0.100 |
|  |  |  |  | within_0.5 | 63 | invalid_geometry:0.603, stop_first:0.286, target_first:0.111 |
|  |  |  |  | within_1.0 | 88 | invalid_geometry:0.466, stop_first:0.352, target_first:0.182 |
| ofm_passive | put_wall | 491 | invalid_geometry:0.532, stop_first:0.328, target_first:0.141 | beyond | 351 | invalid_geometry:0.533, stop_first:0.328, target_first:0.140 |
|  |  |  |  | within_0.1 | 14 | invalid_geometry:0.500, stop_first:0.429, target_first:0.071 |
|  |  |  |  | within_0.25 | 23 | invalid_geometry:0.565, stop_first:0.261, target_first:0.174 |
|  |  |  |  | within_0.5 | 37 | invalid_geometry:0.568, stop_first:0.270, target_first:0.162 |
|  |  |  |  | within_1.0 | 66 | invalid_geometry:0.500, stop_first:0.364, target_first:0.136 |
| ofm_passive | gamma_flip | 188 | invalid_geometry:0.574, stop_first:0.314, target_first:0.112 | beyond | 111 | invalid_geometry:0.559, stop_first:0.333, target_first:0.108 |
|  |  |  |  | within_0.1 | 7 | invalid_geometry:0.857, stop_first:0.143 |
|  |  |  |  | within_0.25 | 16 | invalid_geometry:0.750, stop_first:0.250 |
|  |  |  |  | within_0.5 | 23 | invalid_geometry:0.565, stop_first:0.304, target_first:0.130 |
|  |  |  |  | within_1.0 | 31 | invalid_geometry:0.484, stop_first:0.323, target_first:0.194 |
| cash_open_reclaim_case | max_pain | 663 | invalid_geometry:0.157, neither:0.131, stop_first:0.178, target_first:0.534 | beyond | 434 | invalid_geometry:0.171, neither:0.127, stop_first:0.159, target_first:0.544 |
|  |  |  |  | within_0.1 | 23 | invalid_geometry:0.043, neither:0.087, stop_first:0.217, target_first:0.652 |
|  |  |  |  | within_0.25 | 53 | invalid_geometry:0.113, neither:0.170, stop_first:0.226, target_first:0.491 |
|  |  |  |  | within_0.5 | 60 | invalid_geometry:0.133, neither:0.150, stop_first:0.183, target_first:0.533 |
|  |  |  |  | within_1.0 | 93 | invalid_geometry:0.161, neither:0.129, stop_first:0.226, target_first:0.484 |
| planned_return_long | max_pain | 235 | stop_first:0.557, target_first:0.443 | beyond | 158 | stop_first:0.557, target_first:0.443 |
|  |  |  |  | within_0.1 | 8 | stop_first:0.500, target_first:0.500 |
|  |  |  |  | within_0.25 | 10 | stop_first:0.500, target_first:0.500 |
|  |  |  |  | within_0.5 | 26 | stop_first:0.538, target_first:0.462 |
|  |  |  |  | within_1.0 | 33 | stop_first:0.606, target_first:0.394 |
| cash_open_reclaim_case | key_gamma | 619 | invalid_geometry:0.157, neither:0.134, stop_first:0.181, target_first:0.528 | beyond | 421 | invalid_geometry:0.176, neither:0.145, stop_first:0.166, target_first:0.513 |
|  |  |  |  | within_0.1 | 28 | invalid_geometry:0.071, neither:0.107, stop_first:0.250, target_first:0.571 |
|  |  |  |  | within_0.25 | 40 | invalid_geometry:0.125, neither:0.050, stop_first:0.200, target_first:0.625 |
|  |  |  |  | within_0.5 | 57 | invalid_geometry:0.105, neither:0.175, stop_first:0.193, target_first:0.526 |
|  |  |  |  | within_1.0 | 73 | invalid_geometry:0.137, neither:0.096, stop_first:0.219, target_first:0.548 |
| cash_open_reclaim_case | put_wall | 536 | invalid_geometry:0.162, neither:0.131, stop_first:0.183, target_first:0.524 | beyond | 399 | invalid_geometry:0.175, neither:0.130, stop_first:0.168, target_first:0.526 |
|  |  |  |  | within_0.1 | 14 | neither:0.143, stop_first:0.143, target_first:0.714 |
|  |  |  |  | within_0.25 | 30 | invalid_geometry:0.133, neither:0.200, stop_first:0.300, target_first:0.367 |
|  |  |  |  | within_0.5 | 39 | invalid_geometry:0.154, neither:0.154, stop_first:0.205, target_first:0.487 |
|  |  |  |  | within_1.0 | 54 | invalid_geometry:0.130, neither:0.074, stop_first:0.222, target_first:0.574 |
| planned_return_long | key_gamma | 221 | stop_first:0.548, target_first:0.452 | beyond | 162 | stop_first:0.537, target_first:0.463 |
|  |  |  |  | within_0.1 | 4 | stop_first:0.250, target_first:0.750 |
|  |  |  |  | within_0.25 | 10 | stop_first:0.700, target_first:0.300 |
|  |  |  |  | within_0.5 | 22 | stop_first:0.591, target_first:0.409 |
|  |  |  |  | within_1.0 | 23 | stop_first:0.565, target_first:0.435 |
| planned_return_long | put_wall | 182 | stop_first:0.571, target_first:0.429 | beyond | 131 | stop_first:0.542, target_first:0.458 |
|  |  |  |  | within_0.1 | 4 | stop_first:0.250, target_first:0.750 |
|  |  |  |  | within_0.25 | 7 | stop_first:0.571, target_first:0.429 |
|  |  |  |  | within_0.5 | 15 | stop_first:0.667, target_first:0.333 |
|  |  |  |  | within_1.0 | 25 | stop_first:0.720, target_first:0.280 |
| source_long | key_gamma | 744 | invalid_geometry:0.009, neither:0.003, not_applicable:0.569, stop_first:0.402, target_first:0.017 | beyond | 524 | invalid_geometry:0.010, neither:0.004, not_applicable:0.584, stop_first:0.385, target_first:0.017 |
|  |  |  |  | within_0.1 | 34 | not_applicable:0.706, stop_first:0.294 |
|  |  |  |  | within_0.25 | 30 | not_applicable:0.400, stop_first:0.567, target_first:0.033 |
|  |  |  |  | within_0.5 | 69 | not_applicable:0.507, stop_first:0.464, target_first:0.029 |
|  |  |  |  | within_1.0 | 87 | invalid_geometry:0.023, not_applicable:0.529, stop_first:0.437, target_first:0.011 |
| source_long | call_wall | 542 | invalid_geometry:0.007, neither:0.002, not_applicable:0.559, stop_first:0.410, target_first:0.022 | beyond | 357 | invalid_geometry:0.006, neither:0.003, not_applicable:0.566, stop_first:0.398, target_first:0.028 |
|  |  |  |  | within_0.1 | 29 | not_applicable:0.621, stop_first:0.379 |
|  |  |  |  | within_0.25 | 29 | not_applicable:0.448, stop_first:0.552 |
|  |  |  |  | within_0.5 | 56 | not_applicable:0.500, stop_first:0.482, target_first:0.018 |
|  |  |  |  | within_1.0 | 71 | invalid_geometry:0.028, not_applicable:0.592, stop_first:0.366, target_first:0.014 |
| source_long | put_wall | 635 | invalid_geometry:0.011, neither:0.003, not_applicable:0.567, stop_first:0.403, target_first:0.016 | beyond | 482 | invalid_geometry:0.015, neither:0.002, not_applicable:0.568, stop_first:0.398, target_first:0.017 |
|  |  |  |  | within_0.1 | 20 | not_applicable:0.850, stop_first:0.150 |
|  |  |  |  | within_0.25 | 24 | not_applicable:0.458, stop_first:0.500, target_first:0.042 |
|  |  |  |  | within_0.5 | 41 | not_applicable:0.537, stop_first:0.439, target_first:0.024 |
|  |  |  |  | within_1.0 | 68 | neither:0.015, not_applicable:0.529, stop_first:0.456 |
| source_long | gamma_flip | 235 | invalid_geometry:0.009, neither:0.004, not_applicable:0.528, stop_first:0.438, target_first:0.021 | beyond | 150 | invalid_geometry:0.013, neither:0.007, not_applicable:0.513, stop_first:0.433, target_first:0.033 |
|  |  |  |  | within_0.1 | 10 | not_applicable:0.700, stop_first:0.300 |
|  |  |  |  | within_0.25 | 13 | not_applicable:0.615, stop_first:0.385 |
|  |  |  |  | within_0.5 | 29 | not_applicable:0.448, stop_first:0.552 |
|  |  |  |  | within_1.0 | 33 | not_applicable:0.576, stop_first:0.424 |
| source_long | max_pain | 794 | invalid_geometry:0.010, neither:0.003, not_applicable:0.571, stop_first:0.399, target_first:0.018 | beyond | 533 | invalid_geometry:0.013, neither:0.002, not_applicable:0.572, stop_first:0.392, target_first:0.021 |
|  |  |  |  | within_0.1 | 41 | invalid_geometry:0.024, not_applicable:0.732, stop_first:0.244 |
|  |  |  |  | within_0.25 | 48 | not_applicable:0.542, stop_first:0.458 |
|  |  |  |  | within_0.5 | 70 | not_applicable:0.557, stop_first:0.429, target_first:0.014 |
|  |  |  |  | within_1.0 | 102 | neither:0.010, not_applicable:0.520, stop_first:0.451, target_first:0.020 |
| cash_open_reclaim_case | call_wall | 467 | invalid_geometry:0.143, neither:0.137, stop_first:0.184, target_first:0.535 | beyond | 291 | invalid_geometry:0.168, neither:0.155, stop_first:0.192, target_first:0.485 |
|  |  |  |  | within_0.1 | 29 | invalid_geometry:0.172, neither:0.069, stop_first:0.241, target_first:0.517 |
|  |  |  |  | within_0.25 | 35 | invalid_geometry:0.086, stop_first:0.114, target_first:0.800 |
|  |  |  |  | within_0.5 | 46 | invalid_geometry:0.065, neither:0.174, stop_first:0.174, target_first:0.587 |
|  |  |  |  | within_1.0 | 66 | invalid_geometry:0.106, neither:0.136, stop_first:0.167, target_first:0.591 |
| cash_open_reclaim_case | gamma_flip | 213 | invalid_geometry:0.131, neither:0.146, stop_first:0.174, target_first:0.549 | beyond | 133 | invalid_geometry:0.150, neither:0.158, stop_first:0.158, target_first:0.534 |
|  |  |  |  | within_0.1 | 14 | invalid_geometry:0.071, neither:0.143, stop_first:0.214, target_first:0.571 |
|  |  |  |  | within_0.25 | 9 | invalid_geometry:0.111, neither:0.222, stop_first:0.222, target_first:0.444 |
|  |  |  |  | within_0.5 | 24 | invalid_geometry:0.042, neither:0.042, stop_first:0.208, target_first:0.708 |
|  |  |  |  | within_1.0 | 33 | invalid_geometry:0.152, neither:0.152, stop_first:0.182, target_first:0.515 |
| planned_return_long | call_wall | 167 | stop_first:0.539, target_first:0.461 | beyond | 123 | stop_first:0.528, target_first:0.472 |
|  |  |  |  | within_0.1 | 3 | stop_first:0.333, target_first:0.667 |
|  |  |  |  | within_0.25 | 6 | stop_first:0.833, target_first:0.167 |
|  |  |  |  | within_0.5 | 17 | stop_first:0.588, target_first:0.412 |
|  |  |  |  | within_1.0 | 18 | stop_first:0.500, target_first:0.500 |
| resistance_short | key_gamma | 77 | stop_first:0.571, target_first:0.429 | beyond | 54 | stop_first:0.519, target_first:0.481 |
|  |  |  |  | within_0.1 | 1 | stop_first:1.000 |
|  |  |  |  | within_0.25 | 3 | stop_first:1.000 |
|  |  |  |  | within_0.5 | 9 | stop_first:0.556, target_first:0.444 |
|  |  |  |  | within_1.0 | 10 | stop_first:0.700, target_first:0.300 |
| resistance_short | put_wall | 67 | stop_first:0.567, target_first:0.433 | beyond | 52 | stop_first:0.538, target_first:0.462 |
|  |  |  |  | within_0.1 | 1 | target_first:1.000 |
|  |  |  |  | within_0.25 | 2 | stop_first:1.000 |
|  |  |  |  | within_0.5 | 3 | stop_first:1.000 |
|  |  |  |  | within_1.0 | 9 | stop_first:0.556, target_first:0.444 |
| resistance_short | max_pain | 81 | stop_first:0.556, target_first:0.444 | beyond | 59 | stop_first:0.508, target_first:0.492 |
|  |  |  |  | within_0.1 | 3 | stop_first:0.667, target_first:0.333 |
|  |  |  |  | within_0.25 | 2 | stop_first:1.000 |
|  |  |  |  | within_0.5 | 7 | stop_first:0.714, target_first:0.286 |
|  |  |  |  | within_1.0 | 10 | stop_first:0.600, target_first:0.400 |
| resistance_short | call_wall | 62 | stop_first:0.597, target_first:0.403 | beyond | 41 | stop_first:0.634, target_first:0.366 |
|  |  |  |  | within_0.1 | 2 | stop_first:0.500, target_first:0.500 |
|  |  |  |  | within_0.25 | 3 | stop_first:0.333, target_first:0.667 |
|  |  |  |  | within_0.5 | 7 | stop_first:0.429, target_first:0.571 |
|  |  |  |  | within_1.0 | 9 | stop_first:0.667, target_first:0.333 |
| resistance_short | gamma_flip | 28 | stop_first:0.536, target_first:0.464 | beyond | 16 | stop_first:0.438, target_first:0.562 |
|  |  |  |  | within_0.1 | 1 | stop_first:1.000 |
|  |  |  |  | within_0.25 | 3 | stop_first:0.333, target_first:0.667 |
|  |  |  |  | within_0.5 | 4 | stop_first:0.750, target_first:0.250 |
|  |  |  |  | within_1.0 | 4 | stop_first:0.750, target_first:0.250 |
| extension_reaction | key_gamma | 83 | invalid_geometry:0.265, neither:0.024, stop_first:0.663, target_first:0.048 | beyond | 54 | invalid_geometry:0.315, neither:0.019, stop_first:0.611, target_first:0.056 |
|  |  |  |  | within_0.1 | 5 | invalid_geometry:0.200, stop_first:0.800 |
|  |  |  |  | within_0.25 | 4 | invalid_geometry:0.250, stop_first:0.500, target_first:0.250 |
|  |  |  |  | within_0.5 | 9 | invalid_geometry:0.222, neither:0.111, stop_first:0.667 |
|  |  |  |  | within_1.0 | 11 | invalid_geometry:0.091, stop_first:0.909 |
| extension_reaction | call_wall | 65 | invalid_geometry:0.292, neither:0.031, stop_first:0.615, target_first:0.062 | beyond | 45 | invalid_geometry:0.289, neither:0.022, stop_first:0.600, target_first:0.089 |
|  |  |  |  | within_0.1 | 3 | invalid_geometry:0.333, stop_first:0.667 |
|  |  |  |  | within_0.25 | 5 | invalid_geometry:0.400, stop_first:0.600 |
|  |  |  |  | within_0.5 | 6 | invalid_geometry:0.333, neither:0.167, stop_first:0.500 |
|  |  |  |  | within_1.0 | 6 | invalid_geometry:0.167, stop_first:0.833 |
| extension_reaction | max_pain | 90 | invalid_geometry:0.244, neither:0.022, stop_first:0.656, target_first:0.078 | beyond | 55 | invalid_geometry:0.291, neither:0.018, stop_first:0.582, target_first:0.109 |
|  |  |  |  | within_0.1 | 7 | invalid_geometry:0.286, stop_first:0.714 |
|  |  |  |  | within_0.25 | 6 | invalid_geometry:0.333, stop_first:0.500, target_first:0.167 |
|  |  |  |  | within_0.5 | 10 | invalid_geometry:0.100, neither:0.100, stop_first:0.800 |
|  |  |  |  | within_1.0 | 12 | invalid_geometry:0.083, stop_first:0.917 |
| extension_reaction | put_wall | 72 | invalid_geometry:0.264, neither:0.014, stop_first:0.667, target_first:0.056 | beyond | 47 | invalid_geometry:0.298, neither:0.021, stop_first:0.638, target_first:0.043 |
|  |  |  |  | within_0.1 | 3 | stop_first:1.000 |
|  |  |  |  | within_0.25 | 5 | invalid_geometry:0.400, stop_first:0.400, target_first:0.200 |
|  |  |  |  | within_0.5 | 8 | invalid_geometry:0.250, stop_first:0.750 |
|  |  |  |  | within_1.0 | 9 | invalid_geometry:0.111, stop_first:0.778, target_first:0.111 |
| extension_reaction | gamma_flip | 33 | invalid_geometry:0.273, neither:0.030, stop_first:0.636, target_first:0.061 | beyond | 22 | invalid_geometry:0.364, neither:0.045, stop_first:0.500, target_first:0.091 |
|  |  |  |  | within_0.1 | 3 | stop_first:1.000 |
|  |  |  |  | within_0.25 | 2 | stop_first:1.000 |
|  |  |  |  | within_0.5 | 2 | stop_first:1.000 |
|  |  |  |  | within_1.0 | 4 | invalid_geometry:0.250, stop_first:0.750 |
| internal_rotation | key_gamma | 44 | invalid_geometry:0.182, stop_first:0.545, target_first:0.273 | beyond | 28 | invalid_geometry:0.143, stop_first:0.607, target_first:0.250 |
|  |  |  |  | within_0.1 | 4 | invalid_geometry:0.250, stop_first:0.500, target_first:0.250 |
|  |  |  |  | within_0.25 | 2 | invalid_geometry:0.500, target_first:0.500 |
|  |  |  |  | within_0.5 | 6 | invalid_geometry:0.167, stop_first:0.667, target_first:0.167 |
|  |  |  |  | within_1.0 | 4 | invalid_geometry:0.250, stop_first:0.250, target_first:0.500 |
| internal_rotation | put_wall | 36 | invalid_geometry:0.167, stop_first:0.556, target_first:0.278 | beyond | 24 | invalid_geometry:0.125, stop_first:0.583, target_first:0.292 |
|  |  |  |  | within_0.1 | 2 | stop_first:1.000 |
|  |  |  |  | within_0.25 | 2 | invalid_geometry:0.500, target_first:0.500 |
|  |  |  |  | within_0.5 | 4 | stop_first:1.000 |
|  |  |  |  | within_1.0 | 4 | invalid_geometry:0.500, target_first:0.500 |
| internal_rotation | max_pain | 44 | invalid_geometry:0.182, stop_first:0.545, target_first:0.273 | beyond | 22 | invalid_geometry:0.182, stop_first:0.455, target_first:0.364 |
|  |  |  |  | within_0.1 | 4 | invalid_geometry:0.250, stop_first:0.500, target_first:0.250 |
|  |  |  |  | within_0.25 | 4 | invalid_geometry:0.250, stop_first:0.500, target_first:0.250 |
|  |  |  |  | within_0.5 | 10 | invalid_geometry:0.100, stop_first:0.800, target_first:0.100 |
|  |  |  |  | within_1.0 | 4 | invalid_geometry:0.250, stop_first:0.500, target_first:0.250 |
| single_extended | key_gamma | 22 | invalid_geometry:0.182, stop_first:0.545, target_first:0.273 | beyond | 14 | invalid_geometry:0.071, stop_first:0.571, target_first:0.357 |
|  |  |  |  | within_0.1 | 2 | invalid_geometry:0.500, stop_first:0.500 |
|  |  |  |  | within_0.25 | 1 | invalid_geometry:1.000 |
|  |  |  |  | within_0.5 | 3 | invalid_geometry:0.333, stop_first:0.667 |
|  |  |  |  | within_1.0 | 2 | stop_first:0.500, target_first:0.500 |
| single_extended | put_wall | 18 | invalid_geometry:0.167, stop_first:0.556, target_first:0.278 | beyond | 12 | invalid_geometry:0.083, stop_first:0.583, target_first:0.333 |
|  |  |  |  | within_0.1 | 1 | stop_first:1.000 |
|  |  |  |  | within_0.25 | 1 | invalid_geometry:1.000 |
|  |  |  |  | within_0.5 | 2 | stop_first:1.000 |
|  |  |  |  | within_1.0 | 2 | invalid_geometry:0.500, target_first:0.500 |
| single_extended | max_pain | 22 | invalid_geometry:0.182, stop_first:0.545, target_first:0.273 | beyond | 11 | invalid_geometry:0.091, stop_first:0.455, target_first:0.455 |
|  |  |  |  | within_0.1 | 2 | invalid_geometry:0.500, stop_first:0.500 |
|  |  |  |  | within_0.25 | 2 | invalid_geometry:0.500, stop_first:0.500 |
|  |  |  |  | within_0.5 | 5 | invalid_geometry:0.200, stop_first:0.800 |
|  |  |  |  | within_1.0 | 2 | stop_first:0.500, target_first:0.500 |
| single_purged | key_gamma | 22 | invalid_geometry:0.182, stop_first:0.545, target_first:0.273 | beyond | 14 | invalid_geometry:0.071, stop_first:0.571, target_first:0.357 |
|  |  |  |  | within_0.1 | 2 | invalid_geometry:0.500, stop_first:0.500 |
|  |  |  |  | within_0.25 | 1 | invalid_geometry:1.000 |
|  |  |  |  | within_0.5 | 3 | invalid_geometry:0.333, stop_first:0.667 |
|  |  |  |  | within_1.0 | 2 | stop_first:0.500, target_first:0.500 |
| single_purged | put_wall | 18 | invalid_geometry:0.167, stop_first:0.556, target_first:0.278 | beyond | 12 | invalid_geometry:0.083, stop_first:0.583, target_first:0.333 |
|  |  |  |  | within_0.1 | 1 | stop_first:1.000 |
|  |  |  |  | within_0.25 | 1 | invalid_geometry:1.000 |
|  |  |  |  | within_0.5 | 2 | stop_first:1.000 |
|  |  |  |  | within_1.0 | 2 | invalid_geometry:0.500, target_first:0.500 |
| single_purged | max_pain | 22 | invalid_geometry:0.182, stop_first:0.545, target_first:0.273 | beyond | 11 | invalid_geometry:0.091, stop_first:0.455, target_first:0.455 |
|  |  |  |  | within_0.1 | 2 | invalid_geometry:0.500, stop_first:0.500 |
|  |  |  |  | within_0.25 | 2 | invalid_geometry:0.500, stop_first:0.500 |
|  |  |  |  | within_0.5 | 5 | invalid_geometry:0.200, stop_first:0.800 |
|  |  |  |  | within_1.0 | 2 | stop_first:0.500, target_first:0.500 |
| internal_rotation | call_wall | 36 | invalid_geometry:0.194, stop_first:0.556, target_first:0.250 | beyond | 18 | invalid_geometry:0.167, stop_first:0.611, target_first:0.222 |
|  |  |  |  | within_0.1 | 4 | invalid_geometry:0.500, target_first:0.500 |
|  |  |  |  | within_0.25 | 2 | stop_first:1.000 |
|  |  |  |  | within_0.5 | 8 | invalid_geometry:0.250, stop_first:0.500, target_first:0.250 |
|  |  |  |  | within_1.0 | 4 | stop_first:0.750, target_first:0.250 |
| single_extended | call_wall | 18 | invalid_geometry:0.222, stop_first:0.556, target_first:0.222 | beyond | 9 | invalid_geometry:0.111, stop_first:0.556, target_first:0.333 |
|  |  |  |  | within_0.1 | 2 | invalid_geometry:0.500, target_first:0.500 |
|  |  |  |  | within_0.25 | 1 | stop_first:1.000 |
|  |  |  |  | within_0.5 | 4 | invalid_geometry:0.500, stop_first:0.500 |
|  |  |  |  | within_1.0 | 2 | stop_first:1.000 |
| single_purged | call_wall | 18 | invalid_geometry:0.222, stop_first:0.556, target_first:0.222 | beyond | 9 | invalid_geometry:0.111, stop_first:0.556, target_first:0.333 |
|  |  |  |  | within_0.1 | 2 | invalid_geometry:0.500, target_first:0.500 |
|  |  |  |  | within_0.25 | 1 | stop_first:1.000 |
|  |  |  |  | within_0.5 | 4 | invalid_geometry:0.500, stop_first:0.500 |
|  |  |  |  | within_1.0 | 2 | stop_first:1.000 |
| planned_return_long | gamma_flip | 72 | stop_first:0.514, target_first:0.486 | beyond | 48 | stop_first:0.542, target_first:0.458 |
|  |  |  |  | within_0.1 | 4 | stop_first:0.500, target_first:0.500 |
|  |  |  |  | within_0.25 | 6 | stop_first:0.500, target_first:0.500 |
|  |  |  |  | within_0.5 | 6 | stop_first:0.500, target_first:0.500 |
|  |  |  |  | within_1.0 | 8 | stop_first:0.375, target_first:0.625 |
| internal_rotation | gamma_flip | 14 | invalid_geometry:0.143, stop_first:0.643, target_first:0.214 | beyond | 10 | invalid_geometry:0.100, stop_first:0.700, target_first:0.200 |
|  |  |  |  | within_0.5 | 4 | invalid_geometry:0.250, stop_first:0.500, target_first:0.250 |
| single_extended | gamma_flip | 7 | invalid_geometry:0.143, stop_first:0.714, target_first:0.143 | beyond | 5 | stop_first:0.800, target_first:0.200 |
|  |  |  |  | within_0.5 | 2 | invalid_geometry:0.500, stop_first:0.500 |
| single_purged | gamma_flip | 7 | invalid_geometry:0.143, stop_first:0.714, target_first:0.143 | beyond | 5 | stop_first:0.800, target_first:0.200 |
|  |  |  |  | within_0.5 | 2 | invalid_geometry:0.500, stop_first:0.500 |
| touch_record | key_gamma | 2545 | not_applicable:1.000 | beyond | 1961 | not_applicable:1.000 |
|  |  |  |  | within_0.25 | 220 | not_applicable:1.000 |
|  |  |  |  | within_0.5 | 147 | not_applicable:1.000 |
|  |  |  |  | within_1.0 | 217 | not_applicable:1.000 |
| touch_record | put_wall | 2331 | not_applicable:1.000 | beyond | 1707 | not_applicable:1.000 |
|  |  |  |  | within_0.25 | 220 | not_applicable:1.000 |
|  |  |  |  | within_0.5 | 181 | not_applicable:1.000 |
|  |  |  |  | within_1.0 | 223 | not_applicable:1.000 |
| touch_record | max_pain | 2835 | not_applicable:1.000 | beyond | 2208 | not_applicable:1.000 |
|  |  |  |  | within_0.1 | 114 | not_applicable:1.000 |
|  |  |  |  | within_0.25 | 106 | not_applicable:1.000 |
|  |  |  |  | within_0.5 | 111 | not_applicable:1.000 |
|  |  |  |  | within_1.0 | 296 | not_applicable:1.000 |
| touch_record | call_wall | 1394 | not_applicable:1.000 | beyond | 1071 | not_applicable:1.000 |
|  |  |  |  | within_0.5 | 217 | not_applicable:1.000 |
|  |  |  |  | within_1.0 | 106 | not_applicable:1.000 |
| touch_record | gamma_flip | 548 | not_applicable:1.000 | beyond | 439 | not_applicable:1.000 |
|  |  |  |  | within_0.1 | 15 | not_applicable:1.000 |
|  |  |  |  | within_0.25 | 32 | not_applicable:1.000 |
|  |  |  |  | within_1.0 | 62 | not_applicable:1.000 |

## Change features

One-day matched level rows: 29323. Intraday gamma/volume rate: unavailable_single_10et_snapshot.

## Deviations from LEVEL_ATLAS.md

- B0.1 / P15-03: B0.1 job geometry.entry/decision_at with P15-03 first-passage labels on market-view trades
- Extremes source: P15-02 NativeMarketView trade prints (trades-only load_span_arrow)
- Census reconciliation: 1711 row-days + 31 listed missing = 1742 census dates; identity=True.
- Missing slice dates (31):
  - 2020-01-01: P15-02 market-view trades absent: NQSessionPolicy state=unverified_holiday reason=new_year
  - 2020-01-20: P15-02 market-view trades absent: NQSessionPolicy state=unverified_holiday reason=mlk
  - 2020-04-10: P15-02 market-view trades absent: NQSessionPolicy state=unverified_holiday reason=good_friday
  - 2020-07-03: P15-02 market-view trades absent: NQSessionPolicy state=unverified_holiday reason=independence_eve
  - 2020-12-25: P15-02 market-view trades absent: NQSessionPolicy state=unverified_holiday reason=christmas
  - 2021-01-01: P15-02 market-view trades absent: NQSessionPolicy state=unverified_holiday reason=new_year
  - 2021-04-02: P15-02 market-view trades absent: NQSessionPolicy state=unverified_holiday reason=good_friday
  - 2021-07-05: P15-02 market-view trades absent: NQSessionPolicy state=unverified_holiday reason=independence
  - 2021-12-24: P15-02 market-view trades absent: NQSessionPolicy state=unverified_holiday reason=christmas_eve
  - 2022-04-15: P15-02 market-view trades absent: NQSessionPolicy state=unverified_holiday reason=good_friday
  - 2022-07-04: P15-02 market-view trades absent: NQSessionPolicy state=unverified_holiday reason=independence
  - 2022-11-24: P15-02 market-view trades absent: NQSessionPolicy state=unverified_holiday reason=thanksgiving
  - 2022-12-26: P15-02 market-view trades absent: NQSessionPolicy state=unverified_holiday reason=christmas
  - 2023-01-02: P15-02 market-view trades absent: NQSessionPolicy state=unverified_holiday reason=new_year
  - 2023-04-07: P15-02 market-view trades absent: NQSessionPolicy state=unverified_holiday reason=good_friday
  - 2023-06-19: P15-02 market-view trades absent: NQSessionPolicy state=unverified_holiday reason=juneteenth
  - 2023-07-04: P15-02 market-view trades absent: NQSessionPolicy state=unverified_holiday reason=independence
  - 2023-12-25: NQSessionPolicy closed_rth: None
  - 2024-01-01: NQSessionPolicy closed_rth: None
  - 2024-03-29: P15-02 market-view trades absent: NQSessionPolicy state=unverified_holiday reason=good_friday
  - 2024-07-04: P15-02 market-view trades absent: NQSessionPolicy state=unverified_holiday reason=independence
  - 2024-12-25: P15-02 market-view trades absent: NQSessionPolicy state=unverified_holiday reason=christmas
  - 2025-01-01: P15-02 market-view trades absent: NQSessionPolicy state=unverified_holiday reason=new_year
  - 2025-01-09: no 10:00 exposure board for QQQ/SPY/NQ/ES and no atlas rows
  - 2025-04-18: P15-02 market-view trades absent: NQSessionPolicy state=unverified_holiday reason=good_friday
  - 2025-09-01: P15-02 market-view trades absent: NQSessionPolicy state=unverified_holiday reason=labor
  - 2025-12-25: P15-02 market-view trades absent: NQSessionPolicy state=unverified_holiday reason=christmas
  - 2026-01-01: P15-02 market-view trades absent: NQSessionPolicy state=unverified_holiday reason=new_year
  - 2026-04-03: P15-02 market-view trades absent: NQSessionPolicy state=unverified_holiday reason=good_friday
  - 2026-06-19: P15-02 market-view trades absent: NQSessionPolicy state=unverified_holiday reason=juneteenth
  - 2026-09-03: partial_session_2026-09-03; P15-02 complete account-day tape and 10:00 boards absent

## Limitations

- The atlas is descriptive. It selects nothing.
- Inventory-sign assumption: call-positive/put-negative labelled scenario, not known dealer inventory.
- Strategy references come from the B0.1 corrected-baseline job files when present; otherwise run-1.0.1 evaluation jobs.
- P15-03 outcomes are ordered first-passage labels on P15-02 market-view trade prints from decision_at through the last trade of the loaded account day. Coverage gaps are not re-injected into that scan.
- Account-day and RTH extremes are max/min P15-02 market-view trade prints, not 1-minute OHLC and not BBO midpoints.
- Profile-family atlas cells are specified and deferred to Phase 3. They are not produced in this attempt.
- Intraday rate-of-change of aggregate gamma and executed volume is unavailable. This atlas freezes one 10:00 ET board per day.
- OPRA quotes are scoped DTE/strike feeds, not full chain. NQ/ES quotes are owned DBN ohlcv-1m last-trade mids, not BBO.
- Continuous NQ/ES 1-minute series is the underlier proxy for futures-option boards; the option definition underlying_id is preserved separately.
- Headline proximity cells are after-availability rates: a level can only mark an extreme it was known before. Unrestricted rates (all extremes, ignoring the availability clock) are the superseded diagnostic column.
- degenerate board (median n_live 2 / 7). NQ and ES rows are not evidence for the futures-option levels thesis until a BBO or MBP schema for those roots is owned. Owned NQ/ES option DBN has no BBO; only ohlcv-1m last-trade midpoints pass the 60 s age rule, so boards collapse to a median of 2 (NQ) and 7 (ES) live contracts.
- Alignment headline tables exclude NQ and ES; those rows are reported separately under the degenerate-board label.
- Board depth QQQ: n_boards=1672 n_live median=1127.0 p10=291.0 p90=1510.0 min=0.0 max=1786.0.
- Board depth SPY: n_boards=1674 n_live median=1213.0 p10=839.0 p90=1708.0 min=0.0 max=3580.0.
- Board depth NQ: n_boards=1251 n_live median=2.0 p10=0.0 p90=4.0 min=0.0 max=18.0.
- Board depth ES: n_boards=1656 n_live median=7.0 p10=2.0 p90=19.0 min=0.0 max=75.0.
- Superseded diagnostic (unrestricted high-within-8 over headline roots): 0.004 [0.003, 0.005] n=45557.
- Chain coverage per root and year over the full B0.1 census (days with an OI vintage, days with quotes, days with a fresh 10:00 quote under the 60 s age rule, days with a board):
- ES all-years: oi_vintage=1679 quotes=1733 fresh_quote=1686 board=1656
- ES 2020: oi_vintage=253 quotes=260 fresh_quote=254 board=249
- ES 2021: oi_vintage=253 quotes=259 fresh_quote=255 board=251
- ES 2022: oi_vintage=251 quotes=259 fresh_quote=256 board=252
- ES 2023: oi_vintage=251 quotes=260 fresh_quote=251 board=247
- ES 2024: oi_vintage=251 quotes=261 fresh_quote=250 board=246
- ES 2025: oi_vintage=252 quotes=260 fresh_quote=250 board=245
- ES 2026: oi_vintage=168 quotes=174 fresh_quote=170 board=166
- NDX all-years: oi_vintage=2682 quotes=777 fresh_quote=0 board=0
- NDX 2020: oi_vintage=253 quotes=116 fresh_quote=0 board=0
- NDX 2021: oi_vintage=252 quotes=115 fresh_quote=0 board=0
- NDX 2022: oi_vintage=251 quotes=118 fresh_quote=0 board=0
- NDX 2023: oi_vintage=250 quotes=117 fresh_quote=0 board=0
- NDX 2024: oi_vintage=252 quotes=118 fresh_quote=0 board=0
- NDX 2025: oi_vintage=250 quotes=116 fresh_quote=0 board=0
- NDX 2026: oi_vintage=168 quotes=77 fresh_quote=0 board=0
- NDXP all-years: oi_vintage=2176 quotes=1677 fresh_quote=0 board=0
- NDXP 2020: oi_vintage=253 quotes=253 fresh_quote=0 board=0
- NDXP 2021: oi_vintage=252 quotes=252 fresh_quote=0 board=0
- NDXP 2022: oi_vintage=251 quotes=251 fresh_quote=0 board=0
- NDXP 2023: oi_vintage=250 quotes=250 fresh_quote=0 board=0
- NDXP 2024: oi_vintage=252 quotes=252 fresh_quote=0 board=0
- NDXP 2025: oi_vintage=250 quotes=250 fresh_quote=0 board=0
- NDXP 2026: oi_vintage=168 quotes=169 fresh_quote=0 board=0
- NQ all-years: oi_vintage=1679 quotes=1733 fresh_quote=1273 board=1251
- NQ 2020: oi_vintage=253 quotes=260 fresh_quote=178 board=176
- NQ 2021: oi_vintage=253 quotes=259 fresh_quote=182 board=179
- NQ 2022: oi_vintage=251 quotes=259 fresh_quote=190 board=187
- NQ 2023: oi_vintage=251 quotes=260 fresh_quote=182 board=181
- NQ 2024: oi_vintage=251 quotes=261 fresh_quote=191 board=188
- NQ 2025: oi_vintage=252 quotes=260 fresh_quote=197 board=195
- NQ 2026: oi_vintage=168 quotes=174 fresh_quote=153 board=145
- QQQ all-years: oi_vintage=2682 quotes=1677 fresh_quote=1672 board=1672
- QQQ 2020: oi_vintage=253 quotes=253 fresh_quote=253 board=253
- QQQ 2021: oi_vintage=252 quotes=252 fresh_quote=252 board=252
- QQQ 2022: oi_vintage=251 quotes=251 fresh_quote=251 board=251
- QQQ 2023: oi_vintage=250 quotes=250 fresh_quote=250 board=250
- QQQ 2024: oi_vintage=252 quotes=252 fresh_quote=252 board=252
- QQQ 2025: oi_vintage=250 quotes=250 fresh_quote=250 board=250
- QQQ 2026: oi_vintage=168 quotes=169 fresh_quote=164 board=164
- SPX all-years: oi_vintage=2682 quotes=778 fresh_quote=0 board=0
- SPX 2020: oi_vintage=253 quotes=116 fresh_quote=0 board=0
- SPX 2021: oi_vintage=252 quotes=115 fresh_quote=0 board=0
- SPX 2022: oi_vintage=251 quotes=118 fresh_quote=0 board=0
- SPX 2023: oi_vintage=250 quotes=117 fresh_quote=0 board=0
- SPX 2024: oi_vintage=252 quotes=118 fresh_quote=0 board=0
- SPX 2025: oi_vintage=250 quotes=116 fresh_quote=0 board=0
- SPX 2026: oi_vintage=168 quotes=78 fresh_quote=0 board=0
- SPXW all-years: oi_vintage=2682 quotes=1677 fresh_quote=0 board=0
- SPXW 2020: oi_vintage=253 quotes=253 fresh_quote=0 board=0
- SPXW 2021: oi_vintage=252 quotes=252 fresh_quote=0 board=0
- SPXW 2022: oi_vintage=251 quotes=251 fresh_quote=0 board=0
- SPXW 2023: oi_vintage=250 quotes=250 fresh_quote=0 board=0
- SPXW 2024: oi_vintage=252 quotes=252 fresh_quote=0 board=0
- SPXW 2025: oi_vintage=250 quotes=250 fresh_quote=0 board=0
- SPXW 2026: oi_vintage=168 quotes=169 fresh_quote=0 board=0
- SPY all-years: oi_vintage=2682 quotes=1677 fresh_quote=1674 board=1674
- SPY 2020: oi_vintage=253 quotes=253 fresh_quote=253 board=253
- SPY 2021: oi_vintage=252 quotes=252 fresh_quote=252 board=252
- SPY 2022: oi_vintage=251 quotes=251 fresh_quote=251 board=251
- SPY 2023: oi_vintage=250 quotes=250 fresh_quote=250 board=250
- SPY 2024: oi_vintage=252 quotes=252 fresh_quote=252 board=252
- SPY 2025: oi_vintage=250 quotes=250 fresh_quote=250 board=250
- SPY 2026: oi_vintage=168 quotes=169 fresh_quote=166 board=166
- OI vintage = unique OI session dates. Quotes = unique quote-file or decoded-quote dates. Fresh quote = 10:00 snapshot under the 60 s age rule (OPRA: days that produced a board snapshot; NQ/ES: 09:59 ohlcv-1m bar or a board snapshot). Board = ATLAS_BOARDS entry.
- 20-date OPTIONS_AVAILABILITY slice (superseded as the coverage table; retained as the producing-slice disposition log):
- ES 2020: n=5 complete_observed_scope=5 partial=0 unsupported_owned_input=0
- ES 2021: n=3 complete_observed_scope=3 partial=0 unsupported_owned_input=0
- ES 2022: n=3 complete_observed_scope=3 partial=0 unsupported_owned_input=0
- ES 2023: n=3 complete_observed_scope=3 partial=0 unsupported_owned_input=0
- ES 2024: n=2 complete_observed_scope=2 partial=0 unsupported_owned_input=0
- ES 2025: n=2 complete_observed_scope=2 partial=0 unsupported_owned_input=0
- ES 2026: n=2 complete_observed_scope=1 partial=1 unsupported_owned_input=0
- NDX 2020: n=5 complete_observed_scope=5 partial=0 unsupported_owned_input=0
- NDX 2021: n=3 complete_observed_scope=3 partial=0 unsupported_owned_input=0
- NDX 2022: n=3 complete_observed_scope=3 partial=0 unsupported_owned_input=0
- NDX 2023: n=3 complete_observed_scope=3 partial=0 unsupported_owned_input=0
- NDX 2024: n=2 complete_observed_scope=2 partial=0 unsupported_owned_input=0
- NDX 2025: n=2 complete_observed_scope=2 partial=0 unsupported_owned_input=0
- NDX 2026: n=2 complete_observed_scope=1 partial=1 unsupported_owned_input=0
- NDXP 2020: n=5 complete_observed_scope=5 partial=0 unsupported_owned_input=0
- NDXP 2021: n=3 complete_observed_scope=3 partial=0 unsupported_owned_input=0
- NDXP 2022: n=3 complete_observed_scope=3 partial=0 unsupported_owned_input=0
- NDXP 2023: n=3 complete_observed_scope=3 partial=0 unsupported_owned_input=0
- NDXP 2024: n=2 complete_observed_scope=2 partial=0 unsupported_owned_input=0
- NDXP 2025: n=2 complete_observed_scope=2 partial=0 unsupported_owned_input=0
- NDXP 2026: n=2 complete_observed_scope=1 partial=1 unsupported_owned_input=0
- NQ 2020: n=5 complete_observed_scope=5 partial=0 unsupported_owned_input=0
- NQ 2021: n=3 complete_observed_scope=3 partial=0 unsupported_owned_input=0
- NQ 2022: n=3 complete_observed_scope=3 partial=0 unsupported_owned_input=0
- NQ 2023: n=3 complete_observed_scope=3 partial=0 unsupported_owned_input=0
- NQ 2024: n=2 complete_observed_scope=2 partial=0 unsupported_owned_input=0
- NQ 2025: n=2 complete_observed_scope=2 partial=0 unsupported_owned_input=0
- NQ 2026: n=2 complete_observed_scope=1 partial=1 unsupported_owned_input=0
- QQQ 2020: n=5 complete_observed_scope=5 partial=0 unsupported_owned_input=0
- QQQ 2021: n=3 complete_observed_scope=3 partial=0 unsupported_owned_input=0
- QQQ 2022: n=3 complete_observed_scope=3 partial=0 unsupported_owned_input=0
- QQQ 2023: n=3 complete_observed_scope=3 partial=0 unsupported_owned_input=0
- QQQ 2024: n=2 complete_observed_scope=2 partial=0 unsupported_owned_input=0
- QQQ 2025: n=2 complete_observed_scope=2 partial=0 unsupported_owned_input=0
- QQQ 2026: n=2 complete_observed_scope=1 partial=1 unsupported_owned_input=0
- SPX 2020: n=5 complete_observed_scope=5 partial=0 unsupported_owned_input=0
- SPX 2021: n=3 complete_observed_scope=3 partial=0 unsupported_owned_input=0
- SPX 2022: n=3 complete_observed_scope=3 partial=0 unsupported_owned_input=0
- SPX 2023: n=3 complete_observed_scope=3 partial=0 unsupported_owned_input=0
- SPX 2024: n=2 complete_observed_scope=2 partial=0 unsupported_owned_input=0
- SPX 2025: n=2 complete_observed_scope=2 partial=0 unsupported_owned_input=0
- SPX 2026: n=2 complete_observed_scope=1 partial=1 unsupported_owned_input=0
- SPXW 2020: n=5 complete_observed_scope=5 partial=0 unsupported_owned_input=0
- SPXW 2021: n=3 complete_observed_scope=3 partial=0 unsupported_owned_input=0
- SPXW 2022: n=3 complete_observed_scope=3 partial=0 unsupported_owned_input=0
- SPXW 2023: n=3 complete_observed_scope=3 partial=0 unsupported_owned_input=0
- SPXW 2024: n=2 complete_observed_scope=2 partial=0 unsupported_owned_input=0
- SPXW 2025: n=2 complete_observed_scope=2 partial=0 unsupported_owned_input=0
- SPXW 2026: n=2 complete_observed_scope=1 partial=1 unsupported_owned_input=0
- SPY 2020: n=5 complete_observed_scope=5 partial=0 unsupported_owned_input=0
- SPY 2021: n=3 complete_observed_scope=3 partial=0 unsupported_owned_input=0
- SPY 2022: n=3 complete_observed_scope=3 partial=0 unsupported_owned_input=0
- SPY 2023: n=3 complete_observed_scope=3 partial=0 unsupported_owned_input=0
- SPY 2024: n=2 complete_observed_scope=2 partial=0 unsupported_owned_input=0
- SPY 2025: n=2 complete_observed_scope=2 partial=0 unsupported_owned_input=0
- SPY 2026: n=2 complete_observed_scope=1 partial=1 unsupported_owned_input=0

Every numeric cell points at LEVEL_ATLAS.json rows, `extremes_sha256`, or EXPOSURE_BOARDS.json.


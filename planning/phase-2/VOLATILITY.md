# Joint intraday volatility and movement forecasts

Owners `P2-03` feature/target arithmetic, `P2-04` joint fit and validation. Proposed modules `experts/features/volatility.py`, `experts/labels/volatility.py`, `experts/volatility.py`. Use the [shared fitting recipe](/workspace/planning/research-program/MODEL_FITTING.md), not separate fitted GK/YZ/HAR experts.

## Historical inputs and units

For a complete same-contract OHLC interval with positive prices define `u=ln(H/O)`, `d=ln(L/O)`, `c=ln(C/O)`. The registered simplified Garman–Klass input is `GK=.5*ln(H/L)^2-(2*ln(2)-1)*c^2`. Store interval log-return variance; reject inconsistent OHLC. Values between -1e-12 and 0 may round to0 with a numerical flag; larger negatives fail validation. This is the conventional simplified no-opening-jump version, not every estimator in the [original Garman–Klass paper](https://www.cmegroup.com/trading/fx/files/a_estimation_of_security_price.pdf).

For n=20 complete account days, `o_i=ln(O_i/C_(i-1))`, `c_i=ln(C_i/O_i)`, `v_o=sum((o_i-mean(o))^2)/(n-1)`, `v_c=sum((c_i-mean(c))^2)/(n-1)`, `v_RS=mean(u_i*(u_i-c_i)+d_i*(d_i-c_i))`, `k=.34/(1.34+(n+1)/(n-1))`, and `YZ=v_o+k*v_c+(1-k)*v_RS`. Require n>1 and the preceding same-contract close. Account-day and RTH estimators are separately named. These equations follow the multiple-period construction in [Yang and Zhang](https://www.atmif.com/papers/range.pdf); rolling length20 and the application to our windows are research choices.

Realized variance `RV_[a,b]=sum_j ln(P_j/P_(j-1))^2` uses one-minute sampling, including a final shorter interval if the horizon is not a whole minute. P_j is the last valid native BBO midpoint available at or before the sampling boundary, age<=5 seconds; a missing boundary makes the target incomplete. At t use a midpoint already available at t. Do not bridge contract changes, unscheduled feed gaps or closed markets with a continuous return. Scheduled closure jumps are a separately named return feature/target component; the matching-interval RV excludes them. For account-day targets report matching RV and reopen jump variance separately rather than silently blending definitions.

HAR inputs are prior complete account-day RV, mean of prior 5, mean of prior 22, each `log(RV+1e-12)`, plus same-session versions where complete. The multiscale structure comes from [Corsi's HAR-RV model](https://academic.oup.com/jfec/article-abstract/7/2/174/856522); this pack's intraday multihead and IV extension are our hypotheses. Add recent1/5/15/60-minute RV, GK for completed 15/60-minute windows and prior day, rolling 20-day GK mean/YZ, elapsed matching minutes, remaining minutes, session bucket, prior 20-session same-bucket RV fractions and current range/volume intensity.

IV inputs come from the native option surface contract: ATM IV,25-delta risk reversal/butterfly, term slopes, 0DTE/1–7/8–30/31–90 boards and changes over 5/30 minutes for NDX/NDXP, SPX/SPXW, QQQ, SPY, NQ, ES. Include owned VIX/VX/VVIX/VXN-family series using their actual instrument metadata and known clocks. Different index horizon conventions stay named; do not claim VIX is a next-hour NQ forecast. Preserve spot/option basis, publication/quote age, exercise-model and missing masks. Optional groups absent in training are shown as unconsumed; the native-coverage ledger still requires a disposition for every requested group.

## Targets and forecast times

Use the shared quarter-hour/source-opportunity snapshot grid. Heads are matching-interval RV over next 15,30,60,120 minutes; remaining current analysis bucket; next analysis bucket within the same account day; remaining RTH when t<its close; and remaining account day. Each head stores actual start/end/duration and coverage. Next-bucket target starts at that bucket's open and does not include the intervening interval; identify it explicitly. No fixed-horizon head crosses the account-day/contract boundary. Unsupported heads are masked, not zero. The fitted coefficient matrix has all eight named heads, with per-head support.

Also output `sigma_log=sqrt(predicted_RV)` and conventional points scale `current_spot*sigma_log`. This scale is a volatility conversion, not a guaranteed high/low or a location band. Directional extrema are fitted separately by the range-path expert. The model may predict further movement after a large already-consumed range; there is no fixed daily allowance to subtract mechanically.

## Fits, ablations and acceptance

One `JointVolatilityExpert.fit` consumes all feature groups and produces one multihead artifact. Compare the shared linear ridge and hinge-ridge recipes. Hinge products, exactly six: HAR1×ATM_NQ, HAR22×ATM_NDX, recent15mRV×minutes_remaining, GK60m×ATM_QQQ, YZ20×term_slope_NDX, current_range/S×IV_change5m_NDX. Missing groups retain masks and an unsupported interaction flag.

Ablations: A0 past same-bucket mean variance; A1 HAR-only; A2 GK+YZ+realized-price features; A3 IV-only plus clocks; A4 all historical features without IV; A5 joint all groups. The production architecture is A5 when supported; if A5 fails contribution gates, retain the best supported simpler baseline with an explicit negative joint-input result, never invent improvement. Report each head's QLIKE, log-MAE, calibrated80% coverage/width, support, year/session performance and native-input contribution. Retain failed models and all tuned configurations in the shared trial ledger.

Fixtures: O=100,H=110,L=90,C=100 gives GK=`.5*ln(110/90)^2`; flat OHLC gives0. For n=3 with all o_i=.01, c_i=.02, u_i=.03,d_i=-.01, sample opening/closing variances are0, RS=.0006 and YZ=(1-k)*.0006. RV prices100,101,100 gives `2*ln(1.01)^2`. Annualized IV.2 over one calendar day gives variance`.04/365` only for the explicitly labelled IV scaling feature, never as a realized target.

Future perturbation replaces all prices/IV/OI after issue time and must leave snapshot and forecast bytes unchanged; it must change at least one future target in a positive control. Native charts show predicted versus realized variance and interval width for one high, low, missing-IV and large-error case per supported head. Verify exact numerical expectations independently with hand calculations or scalar math, not by calling the production function twice.

## Source context baselines (added 2026-09-16)

The authors' own context reads, implemented deterministically from the wiki predicates and measured on the full population by [P2-02A](/workspace/planning/phase-2/tasks/P2-02A.md), are the comparison baseline for every fitted expert in this document. Each expert reports the paired comparison against the applicable source read, beside the constant, session-frequency and price-only baselines, and is an upgrade only under the promotion gates; otherwise the source read is retained and nothing is discarded. Forward-volatility, gamma and IV forecasts are upgrades on top of the authors' reads, not replacements for them.

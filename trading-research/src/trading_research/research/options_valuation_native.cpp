/* American spot Black–Scholes obstacle engine (q=0, discrete cash dividends).

   Root build (do not compile on Python import):
     /usr/bin/g++ -O3 -std=c++17 -pipe -shared -fPIC -fno-fast-math -ffp-contract=off
       options_valuation_native.cpp -o liboptions_valuation_native.so

   C ABI (no threads; exceptions are caught at the export boundary):
     int american_price_batch(
         int64_t n_rows,
         const double* S, const double* K, const double* T,
         const double* sigma, const double* r, const int32_t* right,
         const int64_t* div_off, int64_t n_div,
         const double* div_time, const double* div_amount,
         int32_t n_space, int32_t n_time,
         const double* domain_low, const double* domain_high,
         double* price, double* price_error, double* residual,
         int32_t* status, int32_t* iterations);
     int american_iv_batch(
         int64_t n_rows,
         const double* target_price,
         const double* S, const double* K, const double* T, const double* r,
         const int32_t* right,
         const int64_t* div_off, int64_t n_div,
         const double* div_time, const double* div_amount,
         int32_t n_space, int32_t n_time,
         const double* domain_low, const double* domain_high,
         double* iv, double* residual,
         double* bracket_low, double* bracket_high,
         int32_t* status, int32_t* iterations);

   Return 0 if the batch contract is accepted (per-row status lives in status[]).
   Nonzero: 1 n_rows, 2 CSR, 3 grid, 4 null pointer, 5 unexpected exception.
   Dividend times are years from valuation in (0, T]; amounts are cash, >=0.
   right is +1 call / -1 put. domain_low[i] < domain_high[i] fixes the S-grid
   (NaN/unordered => auto domain). Status integers match the Python module.
*/
#include <algorithm>
#include <cmath>
#include <cstdint>
#include <cstdlib>
#include <cstring>
#include <limits>
#include <vector>

namespace {

constexpr int32_t ST_CONVERGED = 0;
constexpr int32_t ST_ENDPOINT_LOWER = 1;
constexpr int32_t ST_ENDPOINT_UPPER = 2;
constexpr int32_t ST_FAILED_BRACKET = 3;
constexpr int32_t ST_ZERO_T = 4;
constexpr int32_t ST_INVALID_INPUT = 5;
constexpr int32_t ST_NONCONVERGED = 6;
constexpr int32_t ST_DOMAIN_ERROR = 10;
constexpr int32_t ST_SIGMA0 = 11;
constexpr int32_t ST_GRID_INCONSISTENT = 13;
constexpr int32_t FLAG_WEAK_VEGA = 1 << 8;
constexpr int32_t FLAG_GRID_ERROR = 1 << 10;

constexpr int32_t STATUS_MASK = 0xFF;
constexpr double SIGMA_HI = 10.0;
constexpr int MAX_SPACE = 2048;
constexpr int MIN_SPACE = 32;
constexpr int MAX_TIME = 8192;
constexpr int MAX_TIMES = 8704;
constexpr int64_t MAX_ROWS = 65536;
constexpr int IV_ITERS = 80;
constexpr int POLICY_ITERS = 20;
constexpr int PSOR_ITERS = 400;

inline double nan_v() { return std::numeric_limits<double>::quiet_NaN(); }

inline double dmax(double a, double b) { return a > b ? a : b; }
inline double dmin(double a, double b) { return a < b ? a : b; }

inline int32_t with_flag(int32_t st, int32_t flag) { return st | flag; }

inline double intrinsic(int right, double S, double K) {
    const double x = static_cast<double>(right) * (S - K);
    return x > 0.0 ? x : 0.0;
}

inline double pv_divs(double t, double r, const double* td, const double* am, int n) {
    double s = 0.0;
    for (int i = 0; i < n; ++i) {
        if (td[i] > t) s += am[i] * std::exp(-r * (td[i] - t));
    }
    return s;
}

inline double bc_low(int right, double K, double r, double tau) {
    if (right > 0) return 0.0;
    const double disc = K * std::exp(-r * tau);
    return dmax(K, disc);
}

inline double bc_high(int right, double S, double K, double r, double tau, double pv) {
    if (right < 0) return 0.0;
    double euro = S - pv - K * std::exp(-r * tau);
    double exer = S - K;
    if (euro < 0.0) euro = 0.0;
    if (exer < 0.0) exer = 0.0;
    return dmax(euro, exer);
}

void auto_domain(double S0, double K, double T, double sigma, double r,
                 const double* amt, int ndiv, double* slo, double* shi) {
    double sumD = 0.0;
    for (int i = 0; i < ndiv; ++i) {
        if (amt[i] > 0.0) sumD += amt[i];
    }
    const double st = (sigma > 0.0 && T > 0.0) ? sigma * std::sqrt(T) : 0.0;
    // Strike-centered nested grids put the terminal payoff kink at a node.
    // Seven diffusion standard deviations plus drift and cash-jump extent.
    const double margin = dmax(7.0 * st, 1e-4);
    const double span = margin + std::fabs(r - 0.5 * sigma * sigma) * T
        + dmax(std::fabs(std::log(S0 / K)), std::log1p(sumD / dmin(S0, K)));
    *shi = K * std::exp(dmin(span, 690.0));
    *slo = K * std::exp(-dmin(span, 690.0));
}

int build_times(double T, int n_time, const double* div_t, int n_div, double* times) {
    int m = 0;
    times[m++] = 0.0;
    times[m++] = T;
    if (T > 0.0 && n_time > 1) {
        for (int i = 1; i < n_time; ++i) {
            times[m++] = T * (static_cast<double>(i) / static_cast<double>(n_time));
        }
    }
    for (int j = 0; j < n_div; ++j) {
        if (div_t[j] > 0.0 && div_t[j] <= T) times[m++] = div_t[j];
    }
    std::sort(times, times + m);
    const double eps = 1e-16 * (1.0 + T);
    int w = 1;
    for (int i = 1; i < m; ++i) {
        if (times[i] - times[w - 1] > eps) times[w++] = times[i];
    }
    return w;
}

double cash_at(double t, double T, const double* td, const double* am, int n) {
    const double eps = 1e-16 * (1.0 + T);
    double D = 0.0;
    for (int j = 0; j < n; ++j) {
        if (td[j] > 0.0 && td[j] <= T && std::fabs(td[j] - t) <= eps) D += am[j];
    }
    return D;
}

double interp_S(const double* S, const double* V, int n, double Sq, double blo, double bhi) {
    if (!(Sq > 0.0) || !std::isfinite(Sq)) return blo;
    if (Sq <= S[0]) return blo;
    if (Sq >= S[n - 1]) return bhi;
    int lo = 0, hi = n - 1;
    while (hi - lo > 1) {
        const int mid = (lo + hi) / 2;
        if (S[mid] <= Sq) lo = mid;
        else hi = mid;
    }
    const double den = S[hi] - S[lo];
    const double w = den > 0.0 ? (Sq - S[lo]) / den : 0.0;
    return (1.0 - w) * V[lo] + w * V[hi];
}

double interp_price(const double* S, const double* V, int n, double Sq,
                    double blo, double bhi) {
    if (Sq <= S[1] || Sq >= S[n - 2]) return interp_S(S, V, n, Sq, blo, bhi);
    int lo = static_cast<int>(std::upper_bound(S, S + n, Sq) - S) - 1;
    lo = std::max(1, std::min(n - 3, lo));
    double value = 0.0;
    for (int j = lo - 1; j <= lo + 2; ++j) {
        double weight = 1.0;
        for (int k = lo - 1; k <= lo + 2; ++k)
            if (j != k) weight *= (Sq - S[k]) / (S[j] - S[k]);
        value += weight * V[j];
    }
    return value;
}

void apply_dividend(double* V, const double* S, int n, double D, int right, double K,
                    double blo) {
    std::vector<double> after(V, V + n);
    for (int i = 0; i < n; ++i) {
        const double Sp = dmax(S[i] - D, 0.0);
        const double cont = interp_S(S, after.data(), n, Sp, blo, after[n - 1]);
        V[i] = dmax(intrinsic(right, S[i], K), cont);
    }
}

bool thomas(int n, double* A, double* B, double* C, double* rhs, double* V) {
    for (int i = 1; i < n; ++i) {
        if (!(std::fabs(B[i - 1]) > 0.0)) return false;
        const double w = A[i] / B[i - 1];
        B[i] -= w * C[i - 1];
        rhs[i] -= w * rhs[i - 1];
    }
    if (!(std::fabs(B[n - 1]) > 0.0)) return false;
    V[n - 1] = rhs[n - 1] / B[n - 1];
    for (int i = n - 2; i >= 0; --i) {
        V[i] = (rhs[i] - C[i] * V[i + 1]) / B[i];
    }
    return std::isfinite(V[0]) && std::isfinite(V[n - 1]);
}

struct StepScratch {
    std::vector<double> A, B, C, rhs, Ac, Bc, Cc, rhsc, H, old;
    std::vector<char> ex;
    explicit StepScratch(int n)
        : A(n), B(n), C(n), rhs(n), Ac(n), Bc(n), Cc(n), rhsc(n), H(n), old(n), ex(n, 0) {}
};

double step_residual(int n, const double* A, const double* B, const double* C,
                     const double* rhs, const double* V, const double* H) {
    double e = 0.0;
    for (int i = 0; i < n; ++i) {
        if (!std::isfinite(V[i])) return std::numeric_limits<double>::infinity();
        const double gap = V[i] - H[i];
        double continuation = B[i] * V[i] - rhs[i];
        if (i > 0) continuation += A[i] * V[i - 1];
        if (i + 1 < n) continuation += C[i] * V[i + 1];
        if (i == 0 || i == n - 1) e = dmax(e, std::fabs(continuation));
        else e = dmax(e, dmax(dmax(-gap, -continuation), std::fabs(dmin(gap, continuation))));
    }
    return e;
}

int american_cn_step(int n, double* V, const double* S, double dx, double dt,
                     double theta, double sigma, double r, int right, double K,
                     double tau_new, double pv_new, StepScratch& sc, double* residual) {
    const double nu = 0.5 * sigma * sigma;
    const double mu = r - 0.5 * sigma * sigma;
    const double invdx2 = 1.0 / (dx * dx);
    const double inv2dx = 0.5 / dx;
    double a = nu * invdx2 - mu * inv2dx;
    double c = nu * invdx2 + mu * inv2dx;
    if (a < 0.0 || c < 0.0) {
        a = nu * invdx2 + dmax(-mu, 0.0) / dx;
        c = nu * invdx2 + dmax(mu, 0.0) / dx;
    }
    const double b = -a - c - r;
    const double blo = bc_low(right, K, r, tau_new);
    const double bhi = bc_high(right, S[n - 1], K, r, tau_new, pv_new);
    std::copy(V, V + n, sc.old.begin());
    const auto& Vold = sc.old;
    for (int i = 0; i < n; ++i) {
        sc.H[i] = intrinsic(right, S[i], K);
        sc.ex[i] = 0;
        sc.A[i] = 0.0;
        sc.C[i] = 0.0;
        sc.B[i] = 1.0;
        sc.rhs[i] = Vold[i];
    }
    sc.rhs[0] = blo;
    sc.rhs[n - 1] = bhi;
    sc.H[0] = blo;
    sc.H[n - 1] = bhi;
    for (int i = 1; i < n - 1; ++i) {
        sc.A[i] = -theta * dt * a;
        sc.B[i] = 1.0 - theta * dt * b;
        sc.C[i] = -theta * dt * c;
        sc.rhs[i] = Vold[i] + (1.0 - theta) * dt * (a * Vold[i - 1] + b * Vold[i] + c * Vold[i + 1]);
    }
    const double scale = dmax(1.0, dmax(K, S[n / 2]));
    int used = 0;
    bool ok = false;
    for (int it = 0; it < POLICY_ITERS; ++it) {
        sc.Ac = sc.A;
        sc.Bc = sc.B;
        sc.Cc = sc.C;
        sc.rhsc = sc.rhs;
        for (int i = 1; i < n - 1; ++i) {
            const double gap = V[i] - sc.H[i];
            const double continuation = sc.A[i] * V[i - 1] + sc.B[i] * V[i]
                + sc.C[i] * V[i + 1] - sc.rhs[i];
            if (gap <= continuation) {
                sc.Ac[i] = 0.0;
                sc.Bc[i] = 1.0;
                sc.Cc[i] = 0.0;
                sc.rhsc[i] = sc.H[i];
            }
        }
        if (!thomas(n, sc.Ac.data(), sc.Bc.data(), sc.Cc.data(), sc.rhsc.data(), V)) break;
        V[0] = blo;
        V[n - 1] = bhi;
        used = it + 1;
        *residual = step_residual(n, sc.A.data(), sc.B.data(), sc.C.data(), sc.rhs.data(), V, sc.H.data());
        if (*residual <= 1e-10 * scale + 1e-12) return used;
    }
    const double omega = 1.4;
    for (int it = 0; it < PSOR_ITERS; ++it) {
        double maxe = 0.0;
        V[0] = blo;
        V[n - 1] = bhi;
        for (int i = 1; i < n - 1; ++i) {
            double y = (sc.rhs[i] - sc.A[i] * V[i - 1] - sc.C[i] * V[i + 1]) / sc.B[i];
            y = V[i] + omega * (y - V[i]);
            if (y < sc.H[i]) y = sc.H[i];
            maxe = dmax(maxe, std::fabs(y - V[i]));
            V[i] = y;
        }
        used += 1;
        if (maxe < 1e-10 * scale + 1e-14) break;
    }
    *residual = step_residual(n, sc.A.data(), sc.B.data(), sc.C.data(), sc.rhs.data(), V, sc.H.data());
    ok = *residual <= 1e-10 * scale + 1e-12;
    return ok ? used : -used;
}

struct SolveOut {
    double price;
    double residual;
    int iterations;
    int32_t status;
};

void fill_grid(double* S, int ns, double slo, double shi) {
    const double x0 = std::log(slo);
    const double dx = (std::log(shi) - x0) / static_cast<double>(ns - 1);
    for (int i = 0; i < ns; ++i) S[i] = std::exp(x0 + dx * static_cast<double>(i));
}

SolveOut solve_one(double S0, double K, double T, double sigma, double r, int right,
                   const double* div_t, const double* div_a, int n_div,
                   int n_space, int n_time, double domain_lo, double domain_hi) {
    SolveOut o{nan_v(), nan_v(), 0, ST_INVALID_INPUT};
    if (!std::isfinite(S0) || !std::isfinite(K) || !std::isfinite(T) || !std::isfinite(sigma)
        || !std::isfinite(r) || !(S0 > 0.0) || !(K > 0.0) || T < 0.0 || sigma < 0.0
        || (right != 1 && right != -1)) {
        return o;
    }
    if (sigma > SIGMA_HI) return o;
    for (int j = 0; j < n_div; ++j) {
        if (!std::isfinite(div_t[j]) || !std::isfinite(div_a[j]) || div_a[j] < 0.0
            || div_t[j] <= 0.0 || div_t[j] > T
            || (j > 0 && div_t[j] < div_t[j - 1])) return o;
    }
    if (!(T > 0.0)) {
        o.price = intrinsic(right, S0, K);
        o.residual = 0.0;
        o.status = ST_ZERO_T;
        return o;
    }
    if (sigma == 0.0) {
        double t = 0.0, spot = S0, best = intrinsic(right, spot, K);
        for (int j = 0; j < n_div;) {
            const double next = div_t[j];
            spot *= std::exp(r * (next - t));
            const double disc = std::exp(-r * next);
            best = dmax(best, disc * intrinsic(right, spot, K));
            double cash = 0.0;
            do { cash += div_a[j++]; } while (j < n_div && div_t[j] == next);
            spot = dmax(spot - cash, 0.0);
            best = dmax(best, disc * intrinsic(right, spot, K));
            t = next;
        }
        spot *= std::exp(r * (T - t));
        best = dmax(best, std::exp(-r * T) * intrinsic(right, spot, K));
        return SolveOut{best, 0.0, 0, ST_SIGMA0};
    }
    double slo = domain_lo, shi = domain_hi;
    if (!(shi > slo) || !std::isfinite(slo) || !std::isfinite(shi) || !(slo > 0.0)) {
        auto_domain(S0, K, T, sigma, r, div_a, n_div, &slo, &shi);
    }
    if (!(slo < S0 && S0 < shi && slo < K && K < shi && slo > 0.0)) {
        o.status = ST_DOMAIN_ERROR;
        return o;
    }
    int ns = n_space, nt = n_time;
    if (ns < MIN_SPACE || ns > MAX_SPACE || nt < 1 || nt > MAX_TIME) {
        o.status = ST_DOMAIN_ERROR;
        return o;
    }
    if (n_div + nt + 2 > MAX_TIMES) {
        o.status = ST_DOMAIN_ERROR;
        return o;
    }
    ++ns; // n_space counts intervals; all supported nested grids include K.

    std::vector<double> S(static_cast<size_t>(ns)), V(static_cast<size_t>(ns));
    std::vector<double> times(static_cast<size_t>(MAX_TIMES));
    fill_grid(S.data(), ns, slo, shi);
    const int ntimes = build_times(T, nt, div_t, n_div, times.data());
    const double dx = (std::log(shi) - std::log(slo)) / static_cast<double>(ns - 1);

    for (int i = 0; i < ns; ++i) V[i] = intrinsic(right, S[i], K);
    const double DT = cash_at(T, T, div_t, div_a, n_div);
    if (DT > 0.0) {
        const double blo = bc_low(right, K, r, 0.0);
        apply_dividend(V.data(), S.data(), ns, DT, right, K, blo);
        for (int i = 0; i < ns; ++i) V[i] = dmax(V[i], intrinsic(right, S[i], K));
    }

    int it_acc = 0;
    double last_res = 0.0;
    bool failed = false;

    StepScratch sc(ns);
    bool just_event = true;
    for (int k = ntimes - 2; k >= 0; --k) {
        const double dt = times[k + 1] - times[k];
        if (!(dt > 0.0)) continue;
        const double tau_new = T - times[k];
        auto run = [&](double h, double theta, double clock) {
            const double pv = pv_divs(clock, r, div_t, div_a, n_div);
            double res = 0.0;
            const int u = american_cn_step(ns, V.data(), S.data(), dx, h, theta, sigma, r,
                                           right, K, T - clock, pv, sc, &res);
            last_res = dmax(last_res, res);
            it_acc += std::abs(u);
            if (u < 0) failed = true;
        };
        if (just_event) {
            run(0.5 * dt, 1.0, times[k] + 0.5 * dt);
            run(0.5 * dt, 1.0, times[k]);
            just_event = false;
        } else {
            run(dt, 0.5, times[k]);
        }
        const double D = cash_at(times[k], T, div_t, div_a, n_div);
        if (D > 0.0) {
            apply_dividend(V.data(), S.data(), ns, D, right, K, bc_low(right, K, r, tau_new));
            just_event = true;
        }
    }

    const double tau0 = T;
    o.price = interp_price(S.data(), V.data(), ns, S0,
                       bc_low(right, K, r, tau0),
                       bc_high(right, S[ns - 1], K, r, tau0, pv_divs(0.0, r, div_t, div_a, n_div)));
    o.price = dmax(intrinsic(right, S0, K), o.price);
    o.residual = last_res;
    o.iterations = it_acc;
    if (!std::isfinite(o.price)) {
        o.status = ST_NONCONVERGED;
        return o;
    }
    o.status = failed ? ST_NONCONVERGED : ST_CONVERGED;
    return o;
}

double grid_tol(double S) { return dmax(0.005, 1e-5 * S); }

bool certified(const SolveOut& p) {
    const int st = p.status & STATUS_MASK;
    return std::isfinite(p.price) && std::isfinite(p.residual)
        && (st == ST_CONVERGED || st == ST_SIGMA0 || st == ST_ZERO_T);
}

SolveOut solve_refined(double S0, double K, double T, double sigma, double r, int right,
                       const double* div_t, const double* div_a, int n_div,
                       int n_space, int n_time, double domain_lo, double domain_hi,
                       double* price_error) {
    const int ns = n_space > 0 ? n_space : 128;
    const int nt = n_time > 0 ? n_time : ns;
    SolveOut prior = solve_one(S0, K, T, sigma, r, right, div_t, div_a, n_div,
                               ns, nt, domain_lo, domain_hi);
    *price_error = nan_v();
    if (!certified(prior)) return prior;
    if (T == 0.0 || sigma == 0.0) { *price_error = 0.0; return prior; }
    if (ns * 2 > MAX_SPACE) { prior.status = ST_GRID_INCONSISTENT | FLAG_GRID_ERROR; return prior; }
    const int final_grid = ns == 128 ? 512 : ns * 2;
    for (int grid = ns * 2; grid <= final_grid; grid *= 2) {
        SolveOut next = solve_one(S0, K, T, sigma, r, right, div_t, div_a, n_div,
                                  grid, std::min(MAX_TIME, nt * (grid / ns)), domain_lo, domain_hi);
        next.iterations += prior.iterations;
        next.residual = dmax(next.residual, prior.residual);
        if (!certified(next)) return next;
        *price_error = std::fabs(next.price - prior.price);
        prior = next;
    }
    if (!std::isfinite(*price_error) || *price_error > grid_tol(S0))
        prior.status = ST_GRID_INCONSISTENT | FLAG_GRID_ERROR;
    return prior;
}

int check_batch(int64_t n_rows, int64_t n_div, int32_t n_space, int32_t n_time,
                const int64_t* div_off, const void* required_core) {
    if (n_rows < 0 || n_rows > MAX_ROWS) return 1;
    if (n_div < 0) return 2;
    if (n_space != 0 && (n_space < MIN_SPACE || n_space > MAX_SPACE)) return 3;
    if (n_time != 0 && (n_time < 1 || n_time > MAX_TIME)) return 3;
    if (required_core == nullptr) return 4;
    if (div_off == nullptr) return 4;
    if (div_off[0] != 0 || div_off[n_rows] != n_div) return 2;
    for (int64_t i = 0; i < n_rows; ++i) {
        if (div_off[i] < 0 || div_off[i + 1] < div_off[i] || div_off[i + 1] > n_div
            || div_off[i + 1] - div_off[i] > MAX_TIMES - 3) return 2;
    }
    return 0;
}

void row_div(const int64_t* off, const double* t, const double* a, int64_t i,
             const double** td, const double** ad, int* nd) {
    const int64_t a0 = off[i];
    const int64_t a1 = off[i + 1];
    *nd = static_cast<int>(a1 - a0);
    *td = (*nd > 0) ? t + a0 : t;
    *ad = (*nd > 0) ? a + a0 : a;
}

int price_batch_impl(
    int64_t n_rows,
    const double* S, const double* K, const double* T,
    const double* sigma, const double* r, const int32_t* right,
    const int64_t* div_off, int64_t n_div,
    const double* div_time, const double* div_amount,
    int32_t n_space, int32_t n_time,
    const double* domain_low, const double* domain_high,
    double* price, double* price_error, double* residual,
    int32_t* status, int32_t* iterations, bool single_grid = false) {
    const int chk = check_batch(n_rows, n_div, n_space, n_time, div_off, S);
    if (chk) return chk;
    if (K == nullptr || T == nullptr || sigma == nullptr || r == nullptr || right == nullptr)
        return 4;
    if (n_div > 0 && (div_time == nullptr || div_amount == nullptr)) return 4;
    if (price == nullptr || price_error == nullptr || residual == nullptr
        || status == nullptr || iterations == nullptr) return 4;
    for (int64_t i = 0; i < n_rows; ++i) {
        price[i] = nan_v();
        price_error[i] = nan_v();
        residual[i] = nan_v();
        status[i] = ST_INVALID_INPUT;
        iterations[i] = 0;
    }
    for (int64_t i = 0; i < n_rows; ++i) {
        try {
            const double* td = nullptr;
            const double* ad = nullptr;
            int nd = 0;
            row_div(div_off, div_time, div_amount, i, &td, &ad, &nd);
            const double lo = domain_low ? domain_low[i] : nan_v();
            const double hi = domain_high ? domain_high[i] : nan_v();
            double err = nan_v();
            const SolveOut o = single_grid
                ? solve_one(S[i], K[i], T[i], sigma[i], r[i], static_cast<int>(right[i]),
                    td, ad, nd, n_space, n_time > 0 ? n_time : n_space, lo, hi)
                : solve_refined(S[i], K[i], T[i], sigma[i], r[i], static_cast<int>(right[i]),
                    td, ad, nd, n_space, n_time, lo, hi, &err);
            price[i] = o.price;
            price_error[i] = err;
            residual[i] = o.residual;
            status[i] = o.status;
            iterations[i] = o.iterations;
        } catch (...) {
            price[i] = nan_v();
            price_error[i] = nan_v();
            residual[i] = nan_v();
            status[i] = ST_NONCONVERGED;
            iterations[i] = 0;
        }
    }
    return 0;
}

SolveOut iv_one(double target, double S0, double K, double T, double r, int right,
                const double* div_t, const double* div_a, int n_div,
                int n_space, int n_time, double domain_lo, double domain_hi,
                double* lo_out, double* hi_out) {
    SolveOut out{nan_v(), nan_v(), 0, ST_INVALID_INPUT};
    *lo_out = 0.0; *hi_out = SIGMA_HI;
    if (!std::isfinite(target) || target < 0.0) return out;
    const double tol = dmax(1e-6, 1e-8 * dmax(1.0, target));
    auto price = [&](double sigma) {
        double error = nan_v();
        SolveOut p = solve_refined(S0, K, T, sigma, r, right, div_t, div_a, n_div,
                                   n_space, n_time, domain_lo, domain_hi, &error);
        return p;
    };
    const SolveOut lower = price(0.0);
    if (!certified(lower)) { out.status = lower.status; return out; }
    out.residual = lower.price - target;
    if (T == 0.0) { out.status = ST_ZERO_T; return out; }
    const double cap = right > 0 ? S0 : K * dmax(1.0, std::exp(-r * T));
    if (target < lower.price - tol || target > cap + tol) {
        out.status = ST_FAILED_BRACKET; return out;
    }
    if (std::fabs(out.residual) <= tol) {
        out.price = 0.0; out.status = ST_ENDPOINT_LOWER | FLAG_WEAK_VEGA;
        return out;
    }
    double lo = 0.0, hi = 0.25;
    SolveOut upper;
    for (;;) {
        upper = price(hi); ++out.iterations;
        if (!certified(upper)) { out.status = upper.status; return out; }
        if (upper.price >= target - tol || hi == SIGMA_HI) break;
        lo = hi;
        hi = dmin(SIGMA_HI, 2.0 * hi);
    }
    *lo_out = lo; *hi_out = hi;
    if (upper.price < target - tol) {
        out.residual = upper.price - target; out.status = ST_FAILED_BRACKET; return out;
    }
    if (std::fabs(upper.price - target) <= tol) {
        out.price = hi; out.residual = upper.price - target;
        out.status = hi == SIGMA_HI ? ST_ENDPOINT_UPPER : ST_CONVERGED;
        return out;
    }
    for (int k = 0; k < IV_ITERS; ++k) {
        const double mid = 0.5 * (lo + hi);
        const SolveOut p = price(mid); ++out.iterations;
        if (!certified(p)) { out.status = p.status; return out; }
        out.residual = p.price - target;
        if (std::fabs(out.residual) <= tol) {
            out.price = mid; out.status = ST_CONVERGED; return out;
        }
        if (out.residual > 0.0) hi = mid; else lo = mid;
        *lo_out = lo; *hi_out = hi;
        if (hi - lo < 1e-12) break;
    }
    out.status = ST_NONCONVERGED;
    return out;
}

int iv_batch_impl(
    int64_t n_rows,
    const double* target_price,
    const double* S, const double* K, const double* T, const double* r,
    const int32_t* right,
    const int64_t* div_off, int64_t n_div,
    const double* div_time, const double* div_amount,
    int32_t n_space, int32_t n_time,
    const double* domain_low, const double* domain_high,
    double* iv, double* residual,
    double* bracket_low, double* bracket_high,
    int32_t* status, int32_t* iterations) {
    const int chk = check_batch(n_rows, n_div, n_space, n_time, div_off, S);
    if (chk) return chk;
    if (target_price == nullptr || K == nullptr || T == nullptr || r == nullptr || right == nullptr)
        return 4;
    if (n_div > 0 && (div_time == nullptr || div_amount == nullptr)) return 4;
    if (iv == nullptr || residual == nullptr || bracket_low == nullptr || bracket_high == nullptr
        || status == nullptr || iterations == nullptr) return 4;
    for (int64_t i = 0; i < n_rows; ++i) {
        iv[i] = nan_v();
        residual[i] = nan_v();
        bracket_low[i] = 0.0;
        bracket_high[i] = SIGMA_HI;
        status[i] = ST_INVALID_INPUT;
        iterations[i] = 0;
    }
    for (int64_t i = 0; i < n_rows; ++i) {
        try {
            const double* td = nullptr;
            const double* ad = nullptr;
            int nd = 0;
            row_div(div_off, div_time, div_amount, i, &td, &ad, &nd);
            const double lo_d = domain_low ? domain_low[i] : nan_v();
            const double hi_d = domain_high ? domain_high[i] : nan_v();
            double blo = 0.0, bhi = SIGMA_HI;
            const SolveOut o = iv_one(
                target_price[i], S[i], K[i], T[i], r[i], static_cast<int>(right[i]),
                td, ad, nd, n_space, n_time, lo_d, hi_d, &blo, &bhi);
            iv[i] = o.price;
            residual[i] = o.residual;
            bracket_low[i] = blo;
            bracket_high[i] = bhi;
            status[i] = o.status;
            iterations[i] = o.iterations;
        } catch (...) {
            iv[i] = nan_v();
            residual[i] = nan_v();
            status[i] = ST_NONCONVERGED;
            iterations[i] = 0;
        }
    }
    return 0;
}

}  // namespace

extern "C" int american_price_batch(
    int64_t n_rows,
    const double* S, const double* K, const double* T,
    const double* sigma, const double* r, const int32_t* right,
    const int64_t* div_off, int64_t n_div,
    const double* div_time, const double* div_amount,
    int32_t n_space, int32_t n_time,
    const double* domain_low, const double* domain_high,
    double* price, double* price_error, double* residual,
    int32_t* status, int32_t* iterations) {
    try {
        return price_batch_impl(
            n_rows, S, K, T, sigma, r, right, div_off, n_div, div_time, div_amount,
            n_space, n_time, domain_low, domain_high,
            price, price_error, residual, status, iterations);
    } catch (...) {
        return 5;
    }
}

extern "C" int american_price_single_grid_batch(
    int64_t n_rows,
    const double* S, const double* K, const double* T,
    const double* sigma, const double* r, const int32_t* right,
    const int64_t* div_off, int64_t n_div,
    const double* div_time, const double* div_amount,
    int32_t n_space, int32_t n_time,
    const double* domain_low, const double* domain_high,
    double* price, double* price_error, double* residual,
    int32_t* status, int32_t* iterations) {
    try {
        return price_batch_impl(
            n_rows, S, K, T, sigma, r, right, div_off, n_div, div_time, div_amount,
            n_space, n_time, domain_low, domain_high,
            price, price_error, residual, status, iterations, true);
    } catch (...) {
        return 5;
    }
}

extern "C" int american_iv_batch(
    int64_t n_rows,
    const double* target_price,
    const double* S, const double* K, const double* T, const double* r,
    const int32_t* right,
    const int64_t* div_off, int64_t n_div,
    const double* div_time, const double* div_amount,
    int32_t n_space, int32_t n_time,
    const double* domain_low, const double* domain_high,
    double* iv, double* residual,
    double* bracket_low, double* bracket_high,
    int32_t* status, int32_t* iterations) {
    try {
        return iv_batch_impl(
            n_rows, target_price, S, K, T, r, right, div_off, n_div, div_time, div_amount,
            n_space, n_time, domain_low, domain_high,
            iv, residual, bracket_low, bracket_high, status, iterations);
    } catch (...) {
        return 5;
    }
}

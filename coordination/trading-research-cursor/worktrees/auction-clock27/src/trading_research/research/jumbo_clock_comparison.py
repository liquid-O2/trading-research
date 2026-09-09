"""Causal common-clock feature/target adapter over an immutable prepared matrix.

Known feature references and observed future references are deliberately selected
in separate passes. A missing clock remains an intended row with shared controls.
"""
import numpy as np
from trading_research.errors import ContractError, IntegrityError
from trading_research.operations.artifacts import digest
from trading_research.research.jumbo_matrix import PreparedPaths, PATH_CLASSES, feature_names
from trading_research.research.jumbo_tables import FEATURES

VERSION = "jumbo-common-clock-comparison-v1"
HORIZON = "common_1001_to_actual_cash_close"
COMMON_FEATURES = (
    "last_close_age_minutes", "weekday", "month", "cut_ny_minutes", "early_close",
    "prior_width_ticks", "prior_age_minutes", "prior_5_mean_width_ticks", "prior_20_mean_width_ticks",
    "last_close_in_prior_position", "prior_last_close_displacement_ticks", "observed_cash_open_gap_ticks",
)
COMMON_TARGETS = ("common_high_priorW", "common_low_priorW", "common_terminal_priorW")


def _exact_field(matrix, name):
    value = np.asarray(matrix.fields[name])
    if value.dtype != np.int64 or value.shape != (matrix.size,):
        raise ContractError(f"{name} requires an aligned exact int64 vector")
    return value


def prepare_common_clock_comparison(matrix, *, plan):
    """Return a PreparedPaths clone with shared causal controls and three targets.

    Every source common-horizon row for each declared clock/date is retained;
    absent physical rows violate the frozen intended population. No future
    completion, class, extreme, or maturity determines any feature mask.
    """
    spec = plan.get("matched_clock_comparison", {})
    clocks = tuple(spec.get("clocks", ()))
    if not clocks or any(type(c) is not str or not c for c in clocks) or len(set(clocks)) != len(clocks):
        raise ContractError("unique declared common-comparison clocks required")
    if spec.get("origin_local", "10:01") != "10:01":
        raise ContractError("adapter requires the declared 10:01 common origin")
    names = feature_names(matrix)
    if matrix.features.shape != (matrix.size,len(names)) or matrix.features.dtype.kind != "f":
        raise ContractError("prepared FEATURES matrix required")
    try:
        clock_codes = np.asarray([matrix.categories["clock"].index(c) for c in clocks],dtype=np.int64)
        horizon_code = matrix.categories["horizon"].index(HORIZON)
    except ValueError as exc:
        raise IntegrityError("declared common clock or horizon absent from prepared categories") from exc
    f = matrix.fields
    for name in ("date","origin_ns","endpoint_ns","maturity_at_ns","prior_width_ticks",
                 "anchor_ticks","future_high_ticks","future_low_ticks","future_close_ticks"):
        _exact_field(matrix,name)
    anchor_identified = np.asarray(f["anchor_identified"])
    if anchor_identified.dtype != np.bool_ or anchor_identified.shape != (matrix.size,):
        raise ContractError("aligned causal anchor identity mask required")
    for name in ("root","clock","horizon","path"):
        if np.asarray(f[name]).dtype.kind not in "iu" or np.asarray(f[name]).shape != (matrix.size,):
            raise ContractError("aligned integer prepared category fields required")
    selected = np.flatnonzero((f["horizon"]==horizon_code) & np.isin(f["clock"],clock_codes))
    # Date/root population is inherited from all original declared source rows,
    # not selected by whether any common-clock formation or future succeeded.
    intended = np.unique(np.column_stack((f["root"],f["date"])),axis=0)
    selected_pairs = np.column_stack((f["root"][selected],f["date"][selected]))
    observed_pairs, inverse, pair_counts = np.unique(selected_pairs,axis=0,return_inverse=True,return_counts=True)
    if not np.array_equal(intended,observed_pairs) or np.any(pair_counts!=len(clocks)):
        raise IntegrityError("common comparison lost an intended root/date/clock row")
    if len(selected) and len(np.unique(np.column_stack((selected_pairs,f["clock"][selected])),axis=0)) != len(selected):
        raise IntegrityError("duplicate common comparison root/date/clock")
    features = matrix.features[selected].copy()
    fields = {name:np.asarray(value)[selected].copy() for name,value in f.items()}
    n = len(selected)
    fields["original_prepared_row"] = selected.astype(np.int64)
    for name in ("common_known_reference_row","common_future_reference_row","common_prior_width_ticks",
                 "common_anchor_ticks","common_maturity_at_ns"):
        fields[name] = np.full(n,-1,dtype=np.int64)
    for name in ("common_known_dependency_available","common_own_features_available","common_target_eligible"):
        fields[name] = np.zeros(n,dtype=np.bool_)
    for name in COMMON_TARGETS:
        fields[name] = np.full(n,np.nan,dtype=np.float64)
    feature_index = {name:i for i,name in enumerate(names)}
    explicit = tuple(name for name in names if name.startswith("prior_actual_RTH_"))
    common_names = tuple(name for name in COMMON_FEATURES if name in names) + explicit
    common_names = tuple(dict.fromkeys(common_names))
    common_columns = np.asarray([feature_index[name] for name in common_names],dtype=np.int64)
    own_columns = np.asarray([i for i,name in enumerate(names) if name not in common_names],dtype=np.int64)
    age = matrix.features[:,feature_index["last_close_age_minutes"]]
    known = anchor_identified & (age==1) & (f["prior_width_ticks"]>0)
    order = np.argsort(inverse,kind="stable")
    boundaries = np.concatenate(([0],np.cumsum(pair_counts)))
    groups = [order[boundaries[i]:boundaries[i+1]] for i in range(len(pair_counts))]
    # PASS ONE: only features/known identities. Future fields are never read.
    for members in groups:
        original = selected[members]
        if (np.any(f["origin_ns"][original]!=f["origin_ns"][original[0]])
                or np.any(f["endpoint_ns"][original]!=f["endpoint_ns"][original[0]])):
            raise IntegrityError("declared common receiver endpoints disagree across clocks")
        refs = original[known[original]]
        if not len(refs):
            # No causal shared dependency: retain each row and its independently
            # known calendar controls; all optional geometry is marked missing.
            features[np.ix_(members,own_columns)] = np.nan
            continue
        reference = int(refs[0])
        anchor, prior = int(f["anchor_ticks"][reference]),int(f["prior_width_ticks"][reference])
        if np.any(f["anchor_ticks"][refs]!=anchor) or np.any(f["prior_width_ticks"][refs]!=prior):
            raise IntegrityError("causal common anchor or exact prior width disagrees")
        fields["common_known_reference_row"][members] = reference
        fields["common_anchor_ticks"][members] = anchor
        fields["common_prior_width_ticks"][members] = prior
        fields["common_known_dependency_available"][members] = True
        for column in common_columns:
            values = matrix.features[refs,column]
            available = values[np.isfinite(values)]
            if len(available) and np.any(available!=available[0]):
                raise IntegrityError("available common control disagrees across clocks")
            features[members,column] = available[0] if len(available) else np.nan
        own = anchor_identified[original] & (age[original]==1) & (f["anchor_ticks"][original]==anchor)
        fields["common_own_features_available"][members] = own
        features[np.ix_(members[~own],own_columns)] = np.nan
    # PASS TWO: identify shared ground truth without revisiting feature masks.
    observed = (f["path"]>=0)&(f["path"]<len(PATH_CLASSES))
    for members in groups:
        if not fields["common_known_dependency_available"][members[0]]:
            continue
        original = selected[members]
        anchor = int(fields["common_anchor_ticks"][members[0]])
        prior = int(fields["common_prior_width_ticks"][members[0]])
        refs = original[observed[original] & known[original]]
        if not len(refs):
            continue
        reference = int(refs[0])
        # These are integer values in one receiver coordinate, including its
        # actual publication maturity; no floating-price equality is accepted.
        for name in ("anchor_ticks","prior_width_ticks","future_high_ticks","future_low_ticks",
                     "future_close_ticks","maturity_at_ns","origin_ns","endpoint_ns"):
            if np.any(f[name][refs]!=f[name][reference]):
                raise IntegrityError("complete common receiver ground truth disagrees across clocks")
        high,low,close = (int(f[name][reference]) for name in ("future_high_ticks","future_low_ticks","future_close_ticks"))
        maturity = int(f["maturity_at_ns"][reference])
        if not low<=close<=high or maturity<int(f["endpoint_ns"][reference]):
            raise IntegrityError("impossible common receiver extrema or publication maturity")
        fields["common_future_reference_row"][members] = reference
        fields["common_maturity_at_ns"][members] = maturity
        fields["common_target_eligible"][members] = True
        for name,value in zip(COMMON_TARGETS,((high-anchor)/prior,(anchor-low)/prior,(close-anchor)/prior),strict=True):
            fields[name][members] = value
    manifest = dict(version=VERSION,source_matrix=matrix.manifest["id"],rows=n,clock_ids=list(clocks),horizon=HORIZON,
       intended_root_dates=len(intended),common_features=list(common_names),feature_columns=["x_"+name for name in names],feature_groups=matrix.manifest.get("feature_groups",{}),target_names=list(COMMON_TARGETS),
       known_reference_rule="first original row with feature age1, identified exact anchor and positive exact prior width; independent of future",
       own_feature_rule="feature age1 and identified same anchor; all other optional own/multi-range inputs missing; independent of future",
       target_rule="same common receiver exact H/L/C relative to known published anchor, normalized by prior completed range width",
       target_eligibility="shared complete receiver with agreeing exact raw outcomes and full publication maturity; no prior means unavailable",
       row_identity="original_prepared_row indexes unchanged immutable source matrix; no missing-clock row is dropped",
       original_row_digest=digest(selected.tobytes()),feature_digest=digest(features.tobytes()),
       target_digest=digest({name:fields[name].tobytes() for name in (*COMMON_TARGETS,"common_maturity_at_ns")}))
    manifest["id"] = digest(manifest)
    return PreparedPaths(manifest,features,fields,matrix.categories,matrix.shards)

"""Fixed equation and time/identity cases; no historical product admission."""

from dataclasses import replace
from decimal import Decimal, localcontext
from fractions import Fraction as F
import json
from pathlib import Path
import unittest

from trading_research.data.definitions import futures_retirement
from trading_research.errors import ContractError, DependencyUnavailable
from trading_research.foundations.contracts import InstrumentKey
from trading_research.foundations.instruments import (
    InstrumentDefinition, InstrumentRegistry, InstrumentRetirement, instrument_identity,
)
from trading_research.foundations.payoffs import (
    AffineCoordinate, Cash, ContractCalendar, Deliverable, FxRate, PayoffKernel,
    PayoffTerms, PriceDomain, PriceObservation, TickBand, TickSchedule,
    calendar_time_derivative, compile_payoff, literal_option_payoff,
)
from trading_research.foundations.time import AvailabilityBasis, Clocks
from trading_research.foundations.units import ES_REFERENCE, NQ_REFERENCE, Ticks, mini_equivalents
from trading_research.operations.artifacts import digest


GOLDEN = json.loads((Path(__file__).parent / 'golden/f02-kernels.json').read_text())['cases']


def clocks(known=20, *, event=10, start=0, end=1000, version='synthetic-clock'):
    return Clocks(event, known, version, AvailabilityBasis.ASSUMED,
                  valid_from=start, valid_until=end, assumption_id='synthetic-known-time')


def future(*, root='NQ', id='1', version='future-v1', start=0, end=1000,
           known=20, multiplier='20', symbol=None):
    key = InstrumentKey('quantpad', 'GLBX.MDP3', id, symbol or root + 'H5', root, version, end)
    return InstrumentDefinition(key, clocks(known, start=start, end=end), 'future', Decimal(multiplier), Decimal('.25'))


def ticks(step=F(1, 4), *, signed=False):
    lower = None if signed else F(0)
    return TickSchedule('synthetic-grid', PriceDomain(lower), (TickBand(lower, None, step),))


def linear(definition):
    expiry = definition.key.expiry_at
    return PayoffTerms('synthetic-linear', definition.key.definition_version, 'linear_future', 'USD',
                       'future_points', F(definition.multiplier), definition.key.underlying,
                       instrument_identity(definition), 'future_points', PriceDomain(None), ticks(signed=True),
                       ContractCalendar(expiry, expiry, expiry, expiry, expiry, 'synthetic-calendar'),
                       definition.clocks)


def option(*, kind='cash_index_option', right='C', strike='8250', exercise='european',
           fixing='XQC-test', expiry=100, last_trade=None, underlying=None, multiplier='100'):
    root = 'NDX' if kind == 'cash_index_option' else 'SSSS' if kind == 'physical_equity_option' else 'NQ'
    settlement = {'cash_index_option': 'cash', 'physical_equity_option': 'equity', 'physical_future_option': 'future'}[kind]
    key = InstrumentKey('synthetic', 'fixture', 'option-1', root + '-test-' + right, root,
                        f'option-{kind}-{right}-{strike}-{expiry}', expiry, right, Decimal(strike), exercise, settlement)
    definition = InstrumentDefinition(key, clocks(end=expiry + 1), 'option', Decimal(multiplier), Decimal('.05'),
                                      underlying.key.instrument_id if underlying else None)
    calendar = ContractCalendar(expiry if last_trade is None else last_trade,
                                0 if exercise == 'american' else expiry, expiry, expiry, expiry + 20, 'synthetic-calendar')
    identity = instrument_identity(underlying) if underlying else root + '-raw'
    unit = 'USD/share' if kind == 'physical_equity_option' else 'future_points' if underlying else 'index_points'
    basket = (Deliverable('SSSS-raw', F(138), unit, price_currency='USD'),) if kind == 'physical_equity_option' else ()
    terms = PayoffTerms('synthetic-option-terms', key.definition_version, kind, 'USD', 'premium_points', F(multiplier),
                       root, identity, unit, PriceDomain(F(0)), ticks(F(1, 20)), calendar, clocks(end=expiry + 1),
                       fixing_identity=fixing, strike=F(strike), right=right, exercise=exercise,
                       deliverables=basket, deliverable_cash=F('10.94') if basket else F(0),
                       exercise_cash=F(1000) if basket else None)
    return definition, terms


def observation(identity, value, *, at=100, known=110, unit='index_points', price_currency=None):
    return PriceObservation(identity, unit, F(value), clocks(known, event=at, start=at, end=at + 50),
                            price_currency=price_currency)


def compiled(pair, *, underlying=None, valid_at=30, known_at=30):
    return compile_payoff(*pair, valid_at=valid_at, known_at=known_at, underlying_definition=underlying)


class RegistryLifetimeTests(unittest.TestCase):
    def setUp(self):
        self.old = future(end=100)
        self.new = future(version='reused-v1', start=150, end=300, known=160, symbol='NQM5')
        self.retirement = InstrumentRetirement('delete-v1', self.old.key.definition_version,
                                              instrument_identity(self.old), 50, clocks(60, event=50))

    def resolve(self, registry, valid_at, known_at):
        return registry.resolve(provider='quantpad', venue='GLBX.MDP3', instrument_id='1',
                                valid_at=valid_at, known_at=known_at)

    def test_reused_id_retirement_delayed_knowledge_and_json_restart(self):
        registry = InstrumentRegistry()
        registry.append(self.old)
        prefix = registry.checkpoint()
        registry.append(self.new)
        registry.retire(self.retirement)
        restarted = InstrumentRegistry.restore(json.loads(json.dumps(registry.checkpoint())))
        prefix_restarted = InstrumentRegistry.restore(prefix)
        for r in (registry, restarted):
            self.assertEqual(self.resolve(r, 49, 200), self.old)
            self.assertEqual(self.resolve(r, 50, 59), self.old)
            self.assertIsNone(self.resolve(r, 50, 60))
            self.assertIsNone(self.resolve(r, 120, 200))
            self.assertEqual(self.resolve(r, 150, 200), self.new)
        self.assertEqual(self.resolve(prefix_restarted, 80, 200), self.old)
        prefix_restarted.append(self.new)
        prefix_restarted.retire(self.retirement)
        self.assertEqual(prefix_restarted.checkpoint(), registry.checkpoint())

    def test_late_correction_cannot_reactivate_and_old_kernel_stays_frozen(self):
        registry = InstrumentRegistry()
        registry.append(self.old)
        old_kernel = compiled((self.old, linear(self.old)))
        old_version = old_kernel.version
        corrected = replace(self.old, key=replace(self.old.key, definition_version='corrected-v2'),
                            multiplier=Decimal(40), clocks=replace(self.old.clocks, known_at=70))
        registry.retire(self.retirement)
        registry.append(corrected)
        self.assertIsNone(self.resolve(registry, 80, 90))
        self.assertEqual(self.resolve(registry, 49, 90), corrected)
        self.assertEqual(self.resolve(registry, 49, 69), self.old)
        new_kernel = compiled((corrected, linear(corrected)), known_at=80)
        self.assertEqual(old_kernel.linear_pnl(F(1), F(5, 4)).amount, 5)
        self.assertEqual(new_kernel.linear_pnl(F(1), F(5, 4)).amount, 10)
        self.assertEqual(old_kernel.version, old_version)
        self.assertNotEqual(new_kernel.version, old_version)

    def test_ambiguous_definitions_immutable_versions_and_corrupt_checkpoint_fail(self):
        registry = InstrumentRegistry()
        registry.append(self.old)
        with self.assertRaises(ContractError):
            registry.append(replace(self.old, multiplier=Decimal(40)))
        registry.append(replace(self.old, key=replace(self.old.key, definition_version='ambiguous-v2')))
        with self.assertRaises(ContractError):
            self.resolve(registry, 40, 40)
        with self.assertRaises(DependencyUnavailable):
            InstrumentRegistry().retire(self.retirement)
        for retirement in (replace(self.retirement, instrument_lifetime=instrument_identity(self.new)),
                           replace(self.retirement, effective_at=-1),
                           replace(self.retirement, clocks=clocks(20))):
            with self.subTest(retirement=retirement), self.assertRaises(ContractError):
                registry.retire(retirement)
        checkpoint = registry.checkpoint()
        checkpoint['definitions'][0]['multiplier'] = {'$decimal': '40'}
        with self.assertRaises(ContractError):
            InstrumentRegistry.restore(checkpoint)

        overlapping = InstrumentRegistry()
        overlapping.append(self.old)
        overlapping.retire(self.retirement)
        overlapping.append(replace(self.old, key=replace(self.old.key, expiry_at=101, definition_version='changed-lifetime'),
                                   clocks=replace(self.old.clocks, known_at=70)))
        with self.assertRaises(ContractError):
            self.resolve(overlapping, 80, 90)
        checkpoint = registry.checkpoint()
        checkpoint['definitions'].append(checkpoint['definitions'][0])
        checkpoint['content_hash'] = digest({k: v for k, v in checkpoint.items() if k != 'content_hash'})
        with self.assertRaises(ContractError):
            InstrumentRegistry.restore(checkpoint)

    def test_raw_deletion_binds_provider_lifetime_clocks_and_unused_fields(self):
        row = {'instrument_id': 1, 'raw_symbol': 'NQH5', 'security_update_action': 'D',
               'instrument_class': 'F', 'activation': 0, 'expiration': 100, 't': 50, 'ts_recv': 60, 'unused': b'a'}
        kwargs = dict(previous=self.old, source_id='raw-delete:1', source_version='raw-hash',
                      latency_ns=0, latency_scenario='synthetic-delay')
        result = futures_retirement(row, **kwargs)
        self.assertEqual((result.effective_at, result.clocks.known_at), (50, 60))
        self.assertNotEqual(result.id, futures_retirement({**row, 'unused': b'b'}, **kwargs).id)
        for change in ({'instrument_id': 2}, {'raw_symbol': 'NQM5'}, {'activation': 150},
                       {'expiration': 300}, {'instrument_class': 'S'}, {'security_update_action': 'A'}):
            with self.subTest(change=change), self.assertRaises((ContractError, DependencyUnavailable)):
                futures_retirement({**row, **change}, **kwargs)
        with self.assertRaises(DependencyUnavailable):
            futures_retirement(row, **{**kwargs, 'previous': replace(self.old, key=replace(self.old.key, provider='other'))})
        registry = InstrumentRegistry()
        registry.append(self.old)
        registry.retire(result)
        with self.assertRaises(ContractError):
            registry.retire(replace(result, effective_at=51))


class PayoffTests(unittest.TestCase):
    def test_nq_es_tick_cash_matches_frozen_golden_and_existing_one_mini_arithmetic(self):
        for name, reference in (('nq_tick', NQ_REFERENCE), ('es_tick', ES_REFERENCE)):
            case = GOLDEN[name]
            definition = future(root=reference.root, multiplier=case['multiplier'])
            kernel = compiled((definition, linear(definition)))
            with localcontext() as context:
                context.prec = 2
                actual = kernel.linear_pnl(F(20000), F(20000) + F(case['price_change']))
                self.assertEqual(actual, Cash(F(case['cash']), 'USD'))
                self.assertEqual(actual.amount, F(reference.pnl(Ticks(80000), Ticks(80001), side=1).value))
                self.assertEqual(kernel.linear_pnl(F(20000), F('20000.25'), side=-1).amount, -actual.amount)
            for side in (0, 2, True):
                with self.subTest(side=side), self.assertRaises(ContractError):
                    kernel.linear_pnl(F(0), F(1), side=side)
            with self.assertRaises(ContractError):
                kernel.linear_pnl(F(1), F('1.01'))
            self.assertFalse(kernel.can_trade(cut=definition.key.expiry_at))

    def test_nasdaq_cash_call_put_and_zero_exercise_match_frozen_equations(self):
        for name, right in (('ndxp_call', 'C'), ('ndxp_put', 'P')):
            case = GOLDEN[name]
            kernel = compiled(option(right=right, strike=case['strike']))
            inputs = (observation('XQC-test', case['fixing']),)
            result = kernel.exercise_obligation(inputs, at=100, cut=110)
            self.assertEqual(result.intrinsic, Cash(F(case['cash']), 'USD'))
            self.assertEqual(result.cash_transfer, result.intrinsic)
            self.assertEqual((result.positions, result.cash_due_at, result.known_at), ((), 120, 110))
            self.assertEqual(result.intrinsic.amount, literal_option_payoff(
                right=right, strike=F(case['strike']), multiplier=F(case['multiplier']), underlying=F(case['fixing'])))
            for price in (F(case['strike']), F(case['strike']) + (-1 if right == 'C' else 1)):
                zero = kernel.exercise_obligation((observation('XQC-test', price),), at=100, cut=110)
                self.assertEqual((zero.intrinsic.amount, zero.cash_transfer.amount, zero.positions), (0, 0, ()))

    def test_am_pm_fixing_identity_trade_deadline_and_revised_payment_are_distinct(self):
        pm = compiled(option(fixing='XQC-PM', expiry=100))
        am = compiled(option(fixing='XQO-AM', expiry=80, last_trade=70))
        self.assertTrue(am.can_trade(cut=69))
        self.assertFalse(am.can_trade(cut=70))
        with self.assertRaises(DependencyUnavailable):
            am.exercise_obligation((observation('XQC-PM', 8500, at=80),), at=80, cut=110)
        with self.assertRaises(DependencyUnavailable):
            am.exercise_obligation((observation('XQO-AM', 8500),), at=100, cut=110)
        self.assertEqual(am.exercise_obligation((observation('XQO-AM', 8500, at=80),), at=80, cut=110).cash_due_at, 100)
        revised_terms = replace(pm.terms, id='revised-payment', calendar=replace(pm.terms.calendar, payment_at=121, source_version='calendar-v2'))
        revised = compiled((pm.definition, revised_terms))
        self.assertNotEqual(pm.version, revised.version)
        self.assertEqual((pm.terms.calendar.payment_at, revised.terms.calendar.payment_at), (120, 121))

    def test_future_delivery_uses_exact_underlier_and_does_not_round_fixing_to_future_tick(self):
        case = GOLDEN['nq_future_delivery_call']
        underlier = future(end=200)
        for right, price, sign in (('C', case['fixing'], 1), ('P', '12249.99', -1)):
            pair = option(kind='physical_future_option', right=right, strike=case['strike'], underlying=underlier, multiplier='20')
            kernel = compiled(pair, underlying=underlier)
            result = kernel.exercise_obligation((observation('XQC-test', price, unit='future_points'),), at=100, cut=110)
            self.assertEqual(result.intrinsic.amount, F(case['intrinsic']))
            self.assertEqual(result.cash_transfer.amount, F(case['cash_transfer']))
            self.assertEqual((result.positions[0].asset_identity, result.positions[0].quantity,
                              result.positions[0].exercise_basis), (instrument_identity(underlier), sign, F(case['strike'])))
            for wrong in (None, future(id='2', end=200), future(end=90), future(end=300),
                          replace(underlier, deliverable_supported=False)):
                with self.subTest(wrong=wrong), self.assertRaises(DependencyUnavailable):
                    compiled(pair, underlying=wrong)

    def test_adjusted_share_cash_basket_and_put_delivery_signs(self):
        case = GOLDEN['adjusted_call']
        for right, price, intrinsic, sign in (('C', case['synthetic_share_price'], case['intrinsic'], 1),
                                               ('P', '7', '23.06', -1)):
            kernel = compiled(option(kind='physical_equity_option', right=right, strike='10'))
            inputs = (observation('SSSS-raw', price, unit='USD/share', price_currency='USD'),)
            result = kernel.exercise_obligation(inputs, at=100, cut=110)
            self.assertEqual(result.intrinsic.amount, F(intrinsic))
            self.assertEqual(result.cash_transfer.amount, sign * F(case['exercise_cash_transfer']))
            self.assertEqual((result.positions[0].quantity, result.positions[0].exercise_basis), (sign * F(case['shares']), None))
            self.assertEqual(result.intrinsic.amount, literal_option_payoff(right=right, strike=F(10), multiplier=F(100),
                basket=((F(case['shares']), F(price)),), deliverable_cash=F(case['deliverable_cash']),
                exercise_cash=F(case['synthetic_exercise_cash'])))
        with self.assertRaises(DependencyUnavailable):
            kernel.exercise_obligation((), at=100, cut=110)
        with self.assertRaises(DependencyUnavailable):
            kernel.exercise_obligation((replace(inputs[0], price_currency='EUR'),), at=100, cut=110)

    def test_marks_are_distinct_from_fixings_and_unavailable_inputs_emit_no_result(self):
        kernel = compiled(option())
        mark = observation('NDX-raw', '8487.71', at=90, known=91)
        self.assertEqual(kernel.intrinsic((mark,), at=92, cut=95, maximum_age_ns=2).amount, 23771)
        with self.assertRaises(DependencyUnavailable):
            kernel.exercise_obligation((mark,), at=90, cut=95)
        fixture = observation('XQC-test', '8487.71')
        for bad in (replace(fixture, identity='NDX-adjusted-display'), replace(fixture, price_unit='ETF_price'),
                    replace(fixture, clocks=clocks(111, event=100, start=100)),
                    replace(fixture, clocks=clocks(110, event=99, start=99)),
                    replace(fixture, clocks=clocks(110, event=101, start=99)), replace(fixture, value=F(-1))):
            with self.subTest(bad=bad), self.assertRaises(DependencyUnavailable):
                kernel.exercise_obligation((bad,), at=100, cut=110)
        with self.assertRaises(DependencyUnavailable):
            kernel.intrinsic((mark,), at=93, cut=95, maximum_age_ns=2)
        with self.assertRaises(DependencyUnavailable):
            kernel.intrinsic((observation('NDX-raw', 8500, at=105, known=110),), at=105, cut=110, maximum_age_ns=0)
        with self.assertRaises(ContractError):
            kernel.exercise_obligation((fixture, fixture), at=100, cut=110)
        with self.assertRaises(ContractError):
            kernel.exercise_obligation([fixture], at=100, cut=110)

    def test_american_intrinsic_available_but_early_payment_schedule_is_not_invented(self):
        kernel = compiled(option(exercise='american'))
        mark = observation('NDX-raw', 8500, at=90, known=91)
        self.assertEqual(kernel.intrinsic((mark,), at=90, cut=91, maximum_age_ns=0).amount, 25000)
        with self.assertRaises(DependencyUnavailable):
            kernel.exercise_obligation((mark,), at=90, cut=91)

    def test_definition_term_conflicts_missing_support_and_public_constructor_fail_closed(self):
        definition, terms = option()
        mutations = (replace(terms, definition_version='wrong'), replace(terms, underlying_root='SPX'),
                     replace(terms, quote_multiplier=F(20)), replace(terms, strike=F(1)), replace(terms, right='P'),
                     replace(terms, exercise='american'), replace(terms, ticks=ticks(F(1, 10))),
                     replace(terms, calendar=ContractCalendar(99, 99, 99, 99, 120, 'wrong-expiry')))
        for changed in mutations:
            with self.subTest(changed=changed), self.assertRaises(ContractError):
                compiled((definition, changed))
            with self.assertRaises(ContractError):
                PayoffKernel(definition, changed, None, 30, 30)
        for changed in (replace(terms, deliverable_complete=False), replace(terms, unsupported_reason='unsupported test'),
                        replace(terms, clocks=clocks(31)), replace(terms, clocks=clocks(end=30))):
            with self.subTest(changed=changed), self.assertRaises(DependencyUnavailable):
                compiled((definition, changed))
        with self.assertRaises(DependencyUnavailable):
            compiled((replace(definition, tick_size=None), terms))
        with self.assertRaises(ContractError):
            compiled((definition, terms), valid_at=40, known_at=30)
        outright = future(end=100)
        with self.assertRaises(ContractError):
            compiled((outright, replace(linear(outright), calendar=ContractCalendar(200, 200, 200, 200, 200, 'bad'))))
        physical, basket_terms = option(kind='physical_equity_option')
        with self.assertRaises(ContractError):
            compiled((physical, replace(basket_terms, currency='EUR')))

    def test_fixed_grid_literal_compiled_parity_and_late_fixing_revision(self):
        for kind in ('cash_index_option', 'physical_equity_option', 'physical_future_option'):
            for right in ('C', 'P'):
                underlier = future(end=200) if kind == 'physical_future_option' else None
                kernel = compiled(option(kind=kind, right=right, strike='10', underlying=underlier,
                                         multiplier='20' if underlier else '100'), underlying=underlier)
                for price in map(F, ('0', '7', '10', '10.01', '20')):
                    basket = kind == 'physical_equity_option'
                    unit = 'USD/share' if basket else 'future_points' if underlier else 'index_points'
                    inputs = (observation('SSSS-raw' if basket else 'XQC-test', price, unit=unit,
                                          price_currency='USD' if basket else None),)
                    expected = literal_option_payoff(right=right, strike=F(10), multiplier=kernel.terms.quote_multiplier,
                        underlying=None if basket else price, basket=((F(138), price),) if basket else None,
                        deliverable_cash=F('10.94') if basket else F(0), exercise_cash=F(1000) if basket else None)
                    self.assertEqual(kernel.exercise_obligation(inputs, at=100, cut=110).intrinsic.amount, expected)
        kernel = compiled(option())
        original = observation('XQC-test', '8487.71')
        original_result = kernel.exercise_obligation((original,), at=100, cut=110)
        revised = replace(original, value=F(8500), clocks=replace(original.clocks, known_at=115, source_version='fixing-correction'))
        with self.assertRaises(DependencyUnavailable):
            kernel.exercise_obligation((revised,), at=100, cut=110)
        updated = kernel.exercise_obligation((revised,), at=100, cut=115)
        self.assertEqual(original_result.intrinsic.amount, 23771)
        self.assertEqual(updated.intrinsic.amount, 25000)
        self.assertNotEqual(original_result.input_versions, updated.input_versions)


class TickAndCoordinateTests(unittest.TestCase):
    def test_premium_threshold_and_signed_or_bounded_grids(self):
        case = GOLDEN['ndxp_tick_boundary']
        schedule = TickSchedule('NDXP-equation-reference', PriceDomain(F(0)),
                                (TickBand(F(0), F(case['threshold']), F(case['below_tick'])),
                                 TickBand(F(case['threshold']), None, F(case['from_threshold_tick']))))
        for price in ('2.95', '3.00', '3.10'):
            self.assertEqual(schedule.require(F(price)), F(price))
        with self.assertRaises(ContractError):
            schedule.require(F(case['input']))
        for price, floor, ceiling in ((case['input'], case['floor'], case['ceil']), ('2.99', '2.95', '3.00')):
            self.assertEqual(schedule.rounded(F(price), direction='floor'), F(floor))
            self.assertEqual(schedule.rounded(F(price), direction='ceil'), F(ceiling))
        signed = ticks(signed=True)
        self.assertEqual((signed.rounded(F('-.1'), direction='floor'), signed.rounded(F('-.1'), direction='ceil')), (F('-.25'), F(0)))
        bounded = TickSchedule('bounded', PriceDomain(F(0), F('1.05')), (TickBand(F(0), None, F('.1')),))
        self.assertEqual(bounded.rounded(F('1.05'), direction='floor'), F(1))
        with self.assertRaises(DependencyUnavailable):
            bounded.rounded(F('1.05'), direction='ceil')
        with self.assertRaises(ContractError):
            TickSchedule('gap', PriceDomain(F(0)), (TickBand(F(0), F(3), F('.05')), TickBand(F(4), None, F('.1'))))
        kernel = compiled(option())
        self.assertEqual(kernel.premium_cash(F('2.95')), Cash(F(295), 'USD'))

    def test_fx_units_availability_and_informational_mini_conversion(self):
        fx = FxRate('EUR', 'USD', F('1.1'), clocks(50, event=40, start=40, end=70))
        self.assertEqual(fx.convert(Cash(F(100), 'EUR'), cut=60), Cash(F(110), 'USD'))
        for cut in (49, 70):
            with self.subTest(cut=cut), self.assertRaises(DependencyUnavailable):
                fx.convert(Cash(F(100), 'EUR'), cut=cut)
        with self.assertRaises(DependencyUnavailable):
            fx.convert(Cash(F(100), 'USD'), cut=60)
        kernel = compiled(option())
        delta = kernel.quote_sensitivity_cash(F('0.5'), quote_unit='premium_points', with_respect_to='index_point')
        self.assertEqual((delta['value'], delta['numerator_unit'], delta['denominator_unit']), (50, 'USD', 'index_point'))
        self.assertEqual(mini_equivalents(Decimal(50), Decimal(2), NQ_REFERENCE), F(5, 4))
        self.assertEqual(mini_equivalents(Decimal(50), Decimal(-2), NQ_REFERENCE), F(-5, 4))
        with self.assertRaises(DependencyUnavailable):
            mini_equivalents(Decimal(50), Decimal(0), NQ_REFERENCE)
        with self.assertRaises(ContractError):
            kernel.quote_sensitivity_cash(F('0.5'), quote_unit='USD', with_respect_to='index_point')

    def test_exact_inverse_conditional_mean_refusal_and_fixed_expiry_time_sign(self):
        mapping = AffineCoordinate('x', 'y', F(2), F(3), 20, 'synthetic-affine')
        self.assertEqual(mapping.apply(F(4), source='x', cut=20), 11)
        self.assertEqual(mapping.inverse().apply(F(11), source='y', cut=20), 4)
        with self.assertRaises(DependencyUnavailable):
            replace(mapping, interpretation='conditional_mean').inverse()
        with self.assertRaises(DependencyUnavailable):
            replace(mapping, slope=F(0)).inverse()
        with self.assertRaises(DependencyUnavailable):
            mapping.apply(F(4), source='x', cut=19)
        self.assertEqual(calendar_time_derivative(F(7), fixed_expiry=True), -7)
        with self.assertRaises(ContractError):
            calendar_time_derivative(F(7), fixed_expiry=False)

    def test_immutable_contract_terms_and_explicit_exact_types(self):
        with self.assertRaises(ContractError):
            replace(future(), leg_ids=['mutable'])
        with self.assertRaises(ContractError):
            TickBand(F(0), None, .25)
        with self.assertRaises(ContractError):
            PriceObservation('x', 'points', 1.1, clocks())
        with self.assertRaises(ContractError):
            Cash(F(1), 'usd')
        with self.assertRaises(ContractError):
            TickSchedule('mutable', PriceDomain(F(0)), [TickBand(F(0), None, F(1))])
        with self.assertRaises(ContractError):
            ContractCalendar(100, 90, 100, 100, 99, 'bad-payment')
        with self.assertRaises(ContractError):
            PriceObservation('x', 'points', F(1), {})
        with self.assertRaises(ContractError):
            replace(option()[1], ticks={})

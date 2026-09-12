"""Evaluate the pack's small, closed SQL expression language with Kleene logic."""

from dataclasses import dataclass
from decimal import Decimal
from functools import lru_cache
import re

from .catalog import METHOD_BY_ID
from .contracts import fields_for, sections
from .logic import kleene_and, kleene_or, kleene_not, kleene_cmp

TOKEN = re.compile(r"\s*('[^']*'|-?\d+(?:\.\d+)?|[A-Za-z_][A-Za-z_0-9]*|<=|>=|<>|!=|[()<>=])")


class Parser:
    def __init__(self, source):
        self.tokens = []
        while source.strip():
            match = TOKEN.match(source)
            if not match:
                raise ValueError(f'unsupported FORMULAS expression: {source[:60]}')
            self.tokens.append(match[1])
            source = source[match.end():]
        self.i = 0

    def take(self, token=None):
        current = self.tokens[self.i] if self.i < len(self.tokens) else None
        if token is not None and current != token:
            raise ValueError(f'expected {token}, got {current}')
        self.i += 1
        return current

    def peek(self):
        return self.tokens[self.i] if self.i < len(self.tokens) else None

    def parse(self):
        result = self.expression()
        if self.i != len(self.tokens):
            raise ValueError(f'unconsumed expression tokens: {self.tokens[self.i:]}')
        return result

    def expression(self):
        left = self.conjunction()
        while self.peek() == 'OR':
            self.take()
            left = ('OR', left, self.conjunction())
        return left

    def conjunction(self):
        left = self.comparison()
        while self.peek() == 'AND':
            self.take()
            left = ('AND', left, self.comparison())
        return left

    def comparison(self):
        if self.peek() == 'NOT':
            self.take()
            return ('NOT', self.comparison())
        left = self.atom()
        operator = self.peek()
        if operator in ('<', '<=', '>', '>=', '=', '<>', '!='):
            self.take()
            return (operator, left, self.atom())
        if operator == 'BETWEEN':
            self.take()
            lo = self.atom()
            self.take('AND')
            return ('AND', ('>=', left, lo), ('<=', left, self.atom()))
        return left

    def atom(self):
        token = self.take()
        if token == '(':
            result = self.expression()
            self.take(')')
            return result
        if token == 'CASE':
            selector = self.atom()
            branches = []
            while self.peek() == 'WHEN':
                self.take()
                key = self.atom()
                self.take('THEN')
                branches.append((key, self.expression()))
            self.take('ELSE')
            default = self.expression()
            self.take('END')
            return ('CASE', selector, branches, default)
        if token in ('NULL', 'TRUE', 'FALSE'):
            return ('literal', {'NULL': None, 'TRUE': True, 'FALSE': False}[token])
        if token is None:
            raise ValueError('incomplete FORMULAS expression')
        if token.startswith("'"):
            return ('literal', token[1:-1])
        if re.fullmatch(r'-?\d+(?:\.\d+)?', token):
            return ('literal', Decimal(token))
        return ('field', token)


@lru_cache(maxsize=64)
def expression_for(method_id, predicate, branch=None):
    section = sections()[METHOD_BY_ID[method_id]]
    if predicate in ('sires_branch_ok', 'case_description') and method_id == 'SIRES':
        heading = f'**{branch}**'
    else:
        heading = f'### {METHOD_BY_ID[method_id]} predicate: {predicate}'
    start = section.find(heading)
    if start < 0:
        raise ValueError(f'unsupported predicate {method_id}/{predicate}/{branch}')
    match = re.search(r'```sql\n(.*?)```', section[start:], re.S)
    return Parser(match[1]).parse()


@dataclass
class Evaluation:
    value: bool | None
    fields: set[str]
    failed: list[str]
    unknown: list[str]


def evaluate(method_id, predicate, values):
    contracts = fields_for(method_id)

    def side_guard(node):
        while node[0] == 'AND':
            node = node[1]
        if node[0] == '=' and node[1] == ('field', 'side') and node[2][0] == 'literal':
            return node[2][1]
        return None

    def walk(node):
        operator = node[0]
        if operator == 'literal':
            return Evaluation(node[1], set(), [], [])
        if operator == 'field':
            name = node[1]
            if name == 'sires_branch_ok':
                try:
                    return walk(expression_for(method_id, name, values.get('branch')))
                except ValueError:
                    return Evaluation(None, {'branch'}, [], ['sires_branch_ok'])
            value = values.get(name)
            return Evaluation(value, {name}, [name] if value is False else [], [name] if value is None else [])
        if operator == 'CASE':
            selector = walk(node[1])
            selected = next((body for key, body in node[2] if key[1] == selector.value), node[3])
            result = walk(selected)
            result.fields |= selector.fields
            result.unknown += selector.unknown
            return result
        if operator == 'NOT':
            child = walk(node[1])
            value = kleene_not(child.value)
            failed = [] if value is True else ['NOT ' + ' '.join(sorted(child.fields))] if value is False else []
            return Evaluation(value, child.fields, failed, child.unknown)
        if operator == 'OR':
            left_side, right_side = side_guard(node[1]), side_guard(node[2])
            if left_side is not None and right_side is not None and left_side != right_side:
                if values.get('side') == left_side:
                    return walk(node[1])
                if values.get('side') == right_side:
                    return walk(node[2])
                return Evaluation(None if values.get('side') is None else False, {'side'}, ['unsupported side'], ['side'] if values.get('side') is None else [])
        left = walk(node[1])
        if operator == 'OR' and left.value is True:
            return left
        right = walk(node[2])
        if operator == 'OR' and right.value is True:
            return right
        fields = left.fields | right.fields
        failed, unknown = left.failed + right.failed, left.unknown + right.unknown
        if operator == 'AND':
            value = kleene_and(left.value, right.value)
        elif operator == 'OR':
            value = kleene_or(left.value, right.value)
        else:
            value = kleene_cmp({'=': '==', '<>': '!='}.get(operator, operator), left.value, right.value)
            event_fields = [node[i][1] for i in (1, 2) if node[i][0] == 'field' and node[i][1] in contracts and contracts[node[i][1]].type.startswith('event_key')]
            if operator in {'<', '>'} and len(event_fields) == 2 and left.value is not None and left.value == right.value:
                value = None
                unknown.append('unknown_order:' + ':'.join(event_fields))
            if value is False:
                failed.append(' '.join(sorted(fields)) + f' ({operator})')
            elif value is None:
                unknown.append(' '.join(sorted(fields)))
        return Evaluation(value, fields, failed, unknown)

    result = walk(expression_for(method_id, predicate, values.get('branch')))
    parent = {('SIRES', 'reentry'): 'sequence',
              ('REFILL-STUDY', 'selected_order_configuration'): 'touch_causality',
              ('JETBUNDLE-STATES', 'transition_observation'): 'state_observation',
              ('STOIC-DATA', 'macro_application'): 'process'}.get((method_id, predicate))
    if parent:
        extra = evaluate(method_id, parent, values)
        result.value = kleene_and(result.value, extra.value)
        result.fields |= extra.fields
        result.failed += extra.failed
        result.unknown += extra.unknown
    result.failed = list(dict.fromkeys(result.failed))
    result.unknown = list(dict.fromkeys(result.unknown))
    return result

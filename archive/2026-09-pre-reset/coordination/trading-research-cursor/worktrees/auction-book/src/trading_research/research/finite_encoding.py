"""Exact wire-size admission before constructing an encoded record tree."""
from dataclasses import fields
from fractions import Fraction
import json

from trading_research.errors import ContractError


def encode_wire(value, *, records, maximum, max_depth, frame_type=None):
    """Encode the existing tagged wire representation after an exact size pass.

    Each pass visits the original immutable values. Neither pass materializes a
    second recursive wire tree, and byte buffers are converted to hex only after
    their entire output has passed the configured bound.
    """
    if type(maximum) is not int or maximum < 1 or type(max_depth) is not int or max_depth < 1:
        raise ContractError('positive exact wire bounds required')
    def object_tokens(items, depth):
        if depth > max_depth:
            raise ContractError('wire nesting capacity exceeded')
        yield 'literal', '{'
        for index, (key, member) in enumerate(items):
            if index:
                yield 'literal', ','
            yield 'string', key
            yield 'literal', ':'
            yield from walk(member, depth)
        yield 'literal', '}'

    def walk(v, depth):
        if type(v) in records:
            if depth + 2 > max_depth:
                raise ContractError('wire nesting capacity exceeded')
            yield 'literal', '{"fields":'
            yield from object_tokens(((f.name, getattr(v, f.name)) for f in sorted(fields(v), key=lambda f:f.name)), depth+2)
            yield 'literal', ',"type":'
            yield 'string', type(v).__name__
            yield 'literal', '}'
        elif frame_type is not None and type(v) is frame_type:
            yield from object_tokens((('frame',v.value),),depth+1)
        elif type(v) is Fraction:
            yield from object_tokens((('fraction',[v.numerator,v.denominator]),),depth+1)
        elif type(v) is bytes:
            if depth + 1 > max_depth:
                raise ContractError('wire nesting capacity exceeded')
            yield 'literal', '{"bytes":"'
            yield 'hex', v
            yield 'literal', '"}'
        elif type(v) in (tuple,list):
            extra = 2 if type(v) is tuple else 1
            if depth+extra > max_depth or len(v) > maximum:
                raise ContractError('wire tuple/depth capacity exceeded')
            yield 'literal', '{"tuple":[' if type(v) is tuple else '['
            for i, member in enumerate(v):
                if i:
                    yield 'literal', ','
                yield from walk(member,depth+extra)
            yield 'literal', ']}' if type(v) is tuple else ']'
        elif type(v) is dict:
            if len(v)>maximum or any(type(k) is not str for k in v):
                raise ContractError('bounded exact wire object keys required')
            yield from object_tokens(((key,v[key]) for key in sorted(v)),depth+1)
        elif type(v) is str:
            yield 'string', v
        elif v is None or type(v) in (int,bool):
            yield 'scalar', v
        else:
            raise ContractError('unsupported wire record value')

    total=0
    for kind, part in walk(value,0):
        if kind=='string':
            total+=2
            for char in part:
                code=ord(char)
                total += (2 if char in '\"\\\b\f\n\r\t' else 6 if code<32 else
                          1 if code<128 else 2 if code<2048 else 3 if code<65536 else 4)
                if 0xD800<=code<=0xDFFF:
                    raise ContractError('invalid UTF8 surrogate in wire string')
                if total>maximum:
                    raise ContractError('wire byte capacity exceeded')
        elif kind=='hex':
            total+=2*len(part)
        elif kind=='scalar':
            try:
                total+=len(json.dumps(part,separators=(',',':')))
            except ValueError as exc:
                raise ContractError('wire integer capacity exceeded') from exc
        else:
            total+=len(part)
        if total>maximum:
            raise ContractError('wire byte capacity exceeded')
    chunks=[]
    for kind,part in walk(value,0):
        if kind=='hex':
            chunk=part.hex().encode()
        elif kind in ('string','scalar'):
            chunk=json.dumps(part,ensure_ascii=False,separators=(',',':')).encode()
        else:
            chunk=part.encode()
        chunks.append(chunk)
    return b''.join(chunks)

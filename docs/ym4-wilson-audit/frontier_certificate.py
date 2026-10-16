#!/usr/bin/env python3
"""Exact integer enclosures for the activity budget specified in YM4 Coherence Map.
Python 3 standard library only. This certifies the specified sums, not a polymer theorem.
All real-number bounds use rational series and integer outward rounding; no floats.
"""
from dataclasses import dataclass
from fractions import Fraction as F
from functools import lru_cache
from itertools import product
from math import factorial
from pathlib import Path
import argparse
import json

DIGITS = 100
S = 10 ** DIGITS
EPS = F(1, 10 ** (DIGITS + 15))

def ceil_div(a, b):
    return -(-a // b)

@dataclass(frozen=True)
class I:
    """Closed interval [lo/S, hi/S], with nonnegative integer endpoints."""
    lo: int
    hi: int
    def __post_init__(self):
        assert 0 <= self.lo <= self.hi
    def __add__(self, other):
        return I(self.lo + other.lo, self.hi + other.hi)
    def __mul__(self, other):
        return I(self.lo * other.lo // S, ceil_div(self.hi * other.hi, S))
    def div(self, other):
        assert other.lo > 0
        return I(self.lo * S // other.hi, ceil_div(self.hi * S, other.lo))
    def scale(self, c):
        c = F(c)
        assert c >= 0
        return I(self.lo*c.numerator//c.denominator,
                 ceil_div(self.hi*c.numerator, c.denominator))
    def square(self):
        return self * self

ONE = I(S, S)

def enclose(lo, hi=None):
    lo, hi = F(lo), F(lo if hi is None else hi)
    assert 0 <= lo <= hi
    return I(lo.numerator*S//lo.denominator,
             ceil_div(hi.numerator*S, hi.denominator))

def exp_positive(u):
    """Bound exp(u). Reduce argument to <=1, use positive series, then square."""
    u = F(u)
    assert u >= 0
    halvings = 0
    while u > 1:
        u /= 2
        halvings += 1
    term = total = F(1)
    k = 0
    while True:
        first = term * u / (k+1)
        ratio = u / (k+2)
        tail = first / (1-ratio)
        if tail <= EPS:
            break
        term = first
        total += term
        k += 1
    out = enclose(total, total+tail)
    for _ in range(halvings):
        out = out.square()
    return out

def exp_negative(u):
    return ONE.div(exp_positive(u))

def bessel(n, x):
    """I_n(x) = sum_{k>=0}(x/2)^(2k+n)/(k! (k+n)!)."""
    x = F(x)
    assert n >= 0 and x > 0
    term = total = (x/2)**n / factorial(n)
    k = 0
    while True:
        first = term*x*x/(4*(k+1)*(k+n+1))
        ratio = x*x/(4*(k+2)*(k+n+2))
        if ratio < 1:
            tail = first/(1-ratio)
            if tail <= EPS:
                return enclose(total, total+tail)
        term = first
        total += term
        k += 1

@lru_cache(None)
def index_tuples(M):
    labels = range(1, M+1)
    triples = [(a,b,c) for a,b,c in product(labels, repeat=3)
               if (a+b+c)%2 == 0 and abs(a-b) <= c <= a+b]
    quads = [(a,b,c,d) for a,b,c,d in product(labels, repeat=4)
             if (a+b-c-d)%2 == 0
             and max(abs(a-b),abs(c-d)) <= min(a+b,c+d)]
    return triples, quads

def decimal_endpoint(n, digits=DIGITS):
    return str(n//10**digits)+'.'+str(n%10**digits).zfill(digits)

def formatted_interval(lo, hi, power=1):
    # Exact, terminating decimals; no conversion through floating point.
    return {'lower':decimal_endpoint(lo, DIGITS*power),
            'upper':decimal_endpoint(hi, DIGITS*power)}

def negative_log_at(r):
    """Bound -log(r) with an outward-rounded atanh series."""
    r = F(r)
    assert 0 < r < 1
    q = enclose((1-r)/(1+r))
    q2 = q.square()
    k = 0
    power = q
    total = I(0,0)
    while True:
        total = total + power.scale(F(2,2*k+1))
        first_power = power*q2
        tail = F(2*first_power.hi*S, (2*k+3)*(S*S-q.hi*q.hi))
        if tail <= F(1,10**95):
            return I(total.lo,total.hi+ceil_div(tail.numerator*S,tail.denominator))
        power = first_power
        k += 1

def calculate(kind, value, M=14):
    z = F(value)
    assert M >= 1 and z > 0
    if kind == 'wilson':
        base = bessel(1,z)
        weights = [I(0,0)] + [bessel(a+1,z).div(base).scale(a+1).square()
                               for a in range(1,M+2)]
        # For a>=M+1: xi_(a+1)/xi_a <= z^2/[4(a+1)^2].
        alpha = enclose(z*z/(4*(M+2)**2))
    elif kind == 'heat':
        weights = [I(0,0)] + [exp_negative(z*a*(a+2)/4).scale((a+1)**2)
                               for a in range(1,M+2)]
        alpha = exp_negative(z*(2*M+5)/4).scale(F((M+3)**2,(M+2)**2))
    else:
        raise ValueError(kind)
    assert alpha.hi < S, 'Tail ratio must be less than one; increase cutoff.'
    tail = ceil_div(weights[M+1].hi*S, S-alpha.hi)
    wlo, whi = [w.lo for w in weights[:M+1]], [w.hi for w in weights[:M+1]]
    total = sum(whi)+tail
    triples, quads = index_tuples(M)
    q2lo = sum(v*v for v in wlo)
    q2hi = sum(v*v for v in whi) + tail*tail
    q3lo = sum(wlo[a]*wlo[b]*wlo[c] for a,b,c in triples)
    q3hi = sum(whi[a]*whi[b]*whi[c] for a,b,c in triples) + 3*tail*total**2
    q4lo = sum(wlo[a]*wlo[b]*wlo[c]*wlo[d] for a,b,c,d in quads)
    q4hi = sum(whi[a]*whi[b]*whi[c]*whi[d] for a,b,c,d in quads) + 4*tail*total**3
    e = exp_positive(1)
    rho_lo = e.lo*(39*q2lo*S*S+95*(q3lo*S+q4lo))
    rho_hi = e.hi*(39*q2hi*S*S+95*(q3hi*S+q4hi))
    denominator = S**5
    result = {
        'action':kind,'parameter':str(value),'cutoff_doubled_spin':M,
        'arithmetic':'exact integers; rational series with geometric remainders',
        'scope':'specified activity sums only; polymer grammar and physical gap not certified',
        'xi_first':[formatted_interval(w.lo,w.hi) for w in weights[1:4]],
        'first_omitted_xi':formatted_interval(weights[M+1].lo,weights[M+1].hi),
        'sum_omitted_xi_upper':decimal_endpoint(tail),
        'Q2':formatted_interval(q2lo,q2hi,2),
        'Q3':formatted_interval(q3lo,q3hi,3),
        'Q4_indicator':formatted_interval(q4lo,q4hi,4),
        'rho':formatted_interval(rho_lo,rho_hi,5),
        'rho_strictly_below_one':rho_hi < denominator,
        'rho_strictly_above_one':rho_lo > denominator,
    }
    if rho_hi < denominator:
        ml = negative_log_at(F(rho_hi,denominator))
        mh = negative_log_at(F(rho_lo,denominator))
        result['minus_log_rho_activity_rate'] = formatted_interval(ml.lo,mh.hi)
    return result

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',default='results.json')
    parser.add_argument('--cutoff',type=int,default=14)
    args=parser.parse_args()
    cases=[('heat','3'),('heat','4'),('heat','4.5'),('heat','5'),('heat','6'),
           ('heat','4.9742'),('heat','4.9743'),
           ('wilson','0.3'),('wilson','0.5'),('wilson','0.6'),('wilson','0.623'),
           ('wilson','0.6273'),('wilson','0.6273001'),('wilson','0.6273002'),('wilson','0.7')]
    results=[calculate(k,v,args.cutoff) for k,v in cases]
    Path(args.output).write_text(json.dumps({'digits':DIGITS,'results':results},indent=2)+'\n')
    for r in results:
        status='BELOW' if r['rho_strictly_below_one'] else ('ABOVE' if r['rho_strictly_above_one'] else 'UNRESOLVED')
        print(r['action'],r['parameter'],r['rho']['lower'][:22],status)
    lookup={(r['action'],r['parameter']):r for r in results}
    assert lookup['wilson','0.6273001']['rho_strictly_below_one']
    assert lookup['wilson','0.6273002']['rho_strictly_above_one']
    print('Wilson crossing bracket verified: (0.6273001, 0.6273002).')

if __name__=='__main__':
    main()

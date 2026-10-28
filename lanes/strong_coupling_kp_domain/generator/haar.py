"""Exact SU(2) Haar integrals of products of plaquette characters (generator side).

Method: Gaussian (quaternion) moment formula.  Identify SU(2) with the unit
sphere S^3 in R^4, U = q0 + i q.sigma.  A product of K entries of U is a
homogeneous degree-K polynomial in q, so its sphere average equals its Gaussian
average divided by E|G|^K = 2^{K/2} (K/2+1)!.  Wick's theorem then gives, for
K even,

    int U_{s1 t1} ... U_{sK tK} dU = (1/(K/2+1)!) * sum over pairings sigma of
        prod_{(i,j) in sigma} eps_{s_i s_j} eps_{t_i t_j},

because E[M_ab M_cd] = 2 eps_ac eps_bd for the Gaussian matrix M(G).  (K = 2
gives the familiar (1/2) eps eps.)  Odd K gives zero.

A face with label a (spin a/2) is written as Tr(P_sym U_p^{(x)a}), P_sym the
symmetriser on (C^2)^{(x)a}; the face becomes a bundle of a fundamental strands
with P_sym inserted at its corners (compressed to Sym^a by an integer basis).  The whole integral is one tensor
network: a node per link (the averaged K-strand tensor, reshaped into one
bundle index per incident face at each end), a diagonal corner weight for each
corner of a face with a >= 2, and a bond per face corner.  Everything is
integer up to the explicit denominators prod_e (K_e/2+1)! and prod_p (a_p!)^4, so the result is an exact
Fraction.  The network is contracted exactly by a multi-modular int64 scheme (primes below
2^21, Chinese remainder reconstruction, the number of primes fixed by a rigorous
bound from the absolute-value network); a float64 contraction of the same
network is used as a cross-check.
"""
from __future__ import annotations

import itertools
import math
from fractions import Fraction
from functools import lru_cache

import numpy as np
import opt_einsum as oe

from supports import plaq_links, links_of

EPS = np.array([[0, 1], [-1, 0]], dtype=np.int64)
EPS_INV = np.array([[0, -1], [1, 0]], dtype=np.int64)


def pairings(n):
    """All perfect matchings of range(n) as tuples of pairs."""
    if n == 0:
        return [()]
    out = []
    for j in range(1, n):
        rest = [k for k in range(1, n) if k != j]
        for m in pairings_list(tuple(rest)):
            out.append(((0, j),) + m)
    return out


@lru_cache(maxsize=None)
def pairings_list(items):
    if not items:
        return [()]
    a = items[0]
    out = []
    for j in range(1, len(items)):
        rest = items[1:j] + items[j + 1:]
        for m in pairings_list(rest):
            out.append(((a, items[j]),) + m)
    return out


@lru_cache(maxsize=None)
def strand_tensor(K):
    """Integer tensor T[s1..sK, t1..tK] = sum_sigma prod eps eps; Haar = T / (K/2+1)!."""
    T = np.zeros((2,) * (2 * K), dtype=np.int64)
    if K % 2:
        return T
    for m in pairings_list(tuple(range(K))):
        # outer product of eps over pairs, on s and t indices separately
        for s in itertools.product((0, 1), repeat=K):
            vs = 1
            for i, j in m:
                vs *= EPS[s[i], s[j]]
                if not vs:
                    break
            if not vs:
                continue
            for t in itertools.product((0, 1), repeat=K):
                vt = vs
                for i, j in m:
                    vt *= EPS[t[i], t[j]]
                    if not vt:
                        break
                if vt:
                    T[s + t] += vt
    return T


@lru_cache(maxsize=None)
def link_tensor(groups):
    """Averaged link tensor for incident faces given as ((a_1, o_1), ..., (a_k, o_k)).

    a_i = label (number of strands), o_i = +1 forward / -1 backward traversal.
    Returns (integer array with indices [S_1..S_k, T_1..T_k], each of dim 2^{a_i},
    integer denominator).  Backward strands carry conj(U) = eps U eps^{-1}.
    """
    K = sum(a for a, _ in groups)
    if K % 2:
        return None, 1
    T = strand_tensor(K).copy()
    # apply eps on s and eps^{-1} on t for backward strands
    pos = 0
    for a, o in groups:
        for _ in range(a):
            if o == -1:
                T = np.moveaxis(np.tensordot(EPS, T, axes=([1], [pos])), 0, pos)
                T = np.moveaxis(np.tensordot(T, EPS_INV, axes=([K + pos], [0])), -1, K + pos)
            pos += 1
    # group strands into bundles
    shape = [2 ** a for a, _ in groups] * 2
    T = T.reshape(shape)
    return T, math.factorial(K // 2 + 1)


@lru_cache(maxsize=None)
def sym_projector(a):
    """Integer a! * P_sym on (C^2)^{(x)a}, as a (2^a x 2^a) matrix."""
    n = 2 ** a
    P = np.zeros((n, n), dtype=np.int64)
    for idx in itertools.product((0, 1), repeat=a):
        r = int("".join(map(str, idx)), 2) if a else 0
        for perm in itertools.permutations(range(a)):
            j = tuple(idx[perm[k]] for k in range(a))
            c = int("".join(map(str, j)), 2) if a else 0
            P[r, c] += 1
    return P, math.factorial(a)


def inv_mult_from_labels(labels):
    """dim Inv(V_a1 x ... x V_ak) for SU(2) (doubled spins), Clebsch-Gordan recursion."""
    dist = {0: 1}
    for a in labels:
        new = {}
        for c, m in dist.items():
            for d in range(abs(c - a), c + a + 1, 2):
                new[d] = new.get(d, 0) + m
        dist = new
    return dist.get(0, 0)


@lru_cache(maxsize=None)
def sym_basis(a):
    """Integer basis B (2^a x (a+1)) of Sym^a(C^2) and corner weights j!(a-j)!.

    P_sym = B D^{-1} B^T with D = diag C(a, j); a! D^{-1} = diag j!(a-j)!.
    """
    B = np.zeros((2 ** a, a + 1), dtype=np.int64)
    for idx in itertools.product((0, 1), repeat=a):
        r = int("".join(map(str, idx)), 2)
        B[r, sum(idx)] = 1
    wts = np.array([math.factorial(j) * math.factorial(a - j) for j in range(a + 1)], dtype=np.int64)
    return B, wts


@lru_cache(maxsize=None)
def reduced_link_tensor(groups):
    """link_tensor with every bundle of a face of label a >= 2 compressed by B_a."""
    T, d = link_tensor(groups)
    if T is None:
        return None, 1
    k = len(groups)
    for i, (a, _) in enumerate(groups):
        if a >= 2:
            B, _ = sym_basis(a)
            for pos in (i, k + i):
                T = np.moveaxis(np.tensordot(T, B, axes=([pos], [0])), -1, pos)
    return T, d


PRIMES = []


def _primes():
    """Primes just below 2^21, used for multi-modular exact contraction."""
    if not PRIMES:
        n = (1 << 21) - 1
        while len(PRIMES) < 40:
            if all(n % d for d in range(2, int(n ** 0.5) + 1)):
                PRIMES.append(n)
            n -= 2
    return PRIMES


def _run_path(syms, tensors, path, reduce=None):
    """Execute a pairwise contraction path; optionally reduce mod p after every step."""
    ops = list(zip(tensors, syms))
    for pos in path:
        pos = sorted(pos, reverse=True)
        picked = [ops.pop(k) for k in pos]
        rest = "".join(s for _, s in ops)
        letters = "".join(dict.fromkeys("".join(s for _, s in picked)))
        out = "".join(c for c in letters if c in rest)
        # numpy einsum needs ASCII letters: relabel this step's indices locally
        loc = {c: chr(97 + k) if k < 26 else chr(65 + k - 26) for k, c in enumerate(letters)}
        assert len(loc) <= 52
        sub = ",".join("".join(loc[c] for c in s) for _, s in picked) + "->" + "".join(loc[c] for c in out)
        res = np.einsum(sub, *[t for t, _ in picked])
        if reduce is not None:
            res = np.mod(res, reduce)
        ops.append((res, out))
    assert len(ops) == 1 and ops[0][1] == ""
    return ops[0][0]


def exact_contract(syms, tensors):
    """Exact integer value of a closed network of integer tensors.

    Multi-modular: contract mod several primes p < 2^21 in int64 (every partial sum
    stays below 2^63 because each contracted dimension product is checked to be
    < 2^21), and reconstruct by the Chinese remainder theorem.  The number of
    primes is chosen from a rigorous bound on |value| obtained by contracting the
    absolute values in float64 (rounded up by a factor 2).
    """
    expr = ",".join(syms) + "->"
    path, info = oe.contract_path(expr, *tensors, optimize="greedy")
    # contracted-dimension guard
    ops_syms = list(syms)
    dims = {}
    for t, s in zip(tensors, syms):
        for d, c in zip(t.shape, s):
            dims[c] = d
    for pos in path:
        pos = sorted(pos, reverse=True)
        picked = [ops_syms.pop(k) for k in pos]
        rest = "".join(ops_syms)
        letters = "".join(dict.fromkeys("".join(picked)))
        out = "".join(c for c in letters if c in rest)
        summed = 1
        for c in letters:
            if c not in out:
                summed *= dims[c]
        if summed >= (1 << 21):
            raise ArithmeticError("contracted dimension too large for the modular scheme")
        ops_syms.append(out)
    bound = float(_run_path(syms, [np.abs(t).astype(np.float64) for t in tensors], path))
    bound = 2 * bound + 2
    primes = _primes()
    M = 1
    residues = []
    for p in primes:
        r = int(_run_path(syms, [np.mod(t, p).astype(np.int64) for t in tensors], path, reduce=p))
        residues.append((r, p))
        M *= p
        if M > 2 * bound:
            break
    else:
        raise ArithmeticError("not enough primes for the CRT bound")
    x = 0
    for r, p in residues:
        Mp = M // p
        x += r * Mp * pow(Mp, -1, p)
    x %= M
    if x > M // 2:
        x -= M
    # float cross-check
    vf = float(_run_path(syms, [t.astype(np.float64) for t in tensors], path))
    if abs(x - vf) > 1e-6 * max(1.0, abs(vf), 1e-12 * bound):
        raise ArithmeticError("modular and float64 contractions disagree")
    return x


def haar_integral(labels):
    """Exact int prod_p chi_{a_p}(U_p) dU for labels: dict plaquette -> a >= 1.

    chi_a(U_p) = Tr(P_sym U_p^{(x)a}); since P_sym commutes with U^{(x)a} and is
    idempotent it is inserted at all four corners, P_sym = B D^{-1} B^T, the B's
    are absorbed into the link tensors, and each corner's diag(D^{-1}) is absorbed
    into the link tensor through which the path leaves that corner.
    """
    faces = sorted(labels)
    nsym = [0]

    def new():
        nsym[0] += 1
        return nsym[0]

    corner = {}
    tensors = []
    inds = []
    denom = 1
    for f in faces:
        a = labels[f]
        c = [new() for _ in range(4)]
        c_in, c_out = c, c
        if a >= 2:
            # the corner weight diag(j!(a-j)!) / a! is absorbed into the link tensor on the
            # side where the path leaves the corner (see the link loop below)
            denom *= math.factorial(a) ** 4
        # path: corner0 -L1-> corner1 -L2-> corner2 -L3^-1-> corner3 -L4^-1-> corner0
        # L1 fwd: s = corner0 (out), t = corner1 (in); L2 fwd: s = corner1 (out), t = corner2 (in)
        # L3 bwd: path corner2 -> corner3, s = corner3 (in), t = corner2 (out)
        # L4 bwd: path corner3 -> corner0, s = corner0 (in), t = corner3 (out)
        L = plaq_links(f)
        corner[f] = {L[0][0]: (c_out[0], c_in[1]), L[1][0]: (c_out[1], c_in[2]),
                     L[2][0]: (c_in[3], c_out[2]), L[3][0]: (c_in[0], c_out[3])}
    inc = {}
    for f in faces:
        for e, s in plaq_links(f):
            inc.setdefault(e, []).append((f, s))
    for e, lst in inc.items():
        groups = tuple((labels[f], s) for f, s in lst)
        T, d = reduced_link_tensor(groups)
        if T is None:
            return Fraction(0)
        k = len(lst)
        for i, (f, sgn) in enumerate(lst):
            a = labels[f]
            if a >= 2:
                _, wts = sym_basis(a)
                axis = i if sgn == 1 else k + i  # the path leaves the corner through this index
                shape = [1] * T.ndim
                shape[axis] = a + 1
                T = T * wts.reshape(shape)
        tensors.append(T)
        inds.append(tuple(corner[f][e][0] for f, _ in lst) + tuple(corner[f][e][1] for f, _ in lst))
        denom *= d
    syms = ["".join(oe.get_symbol(i) for i in ix) for ix in inds]
    vi = exact_contract(syms, tensors)
    return Fraction(vi, denom)


if __name__ == "__main__":
    # self-test: Gaussian bond constant, and the cube
    rng = np.random.default_rng(1)
    def su2(q):
        a, b = complex(q[0], q[3]), complex(q[2], q[1])
        return np.array([[a, b], [-b.conjugate(), a.conjugate()]])
    acc = np.zeros((2, 2, 2, 2), dtype=complex)
    n = 200000
    G = rng.standard_normal((n, 4))
    for g in G[:20000]:
        M = su2(g)
        acc += np.einsum("ab,cd->abcd", M, M)
    acc /= 20000
    target = 2 * np.einsum("ac,bd->abcd", EPS, EPS)
    print("Gaussian bond max dev", np.abs(acc - target).max())
    cube = [((0, 0, 0), 0, 1), ((0, 0, 1), 0, 1), ((0, 0, 0), 0, 2), ((0, 1, 0), 0, 2),
            ((0, 0, 0), 1, 2), ((1, 0, 0), 1, 2)]
    print("cube fund", haar_integral({p: 1 for p in cube}))
    print("cube spin1", haar_integral({p: 2 for p in cube}))

"""Exact enumeration of surviving plaquette supports in Z^3.

A *surviving support* is a finite, link-connected set X of plaquettes in which
every lattice link lies in 0 or at least 2 plaquettes of X.  These are exactly
the supports on which some labelling by nontrivial SU(2) irreps can have a
nonzero Haar integral (a link in exactly one active face integrates to zero).

Encoding (decision encoding).  Grow X from the root plaquette.  At each step
pick an undecided link that lies in some chosen plaquette: first the smallest
link lying in exactly one chosen plaquette, otherwise the smallest undecided
touched link.  *Decide* that link: choose the complete set J of further
plaquettes of X containing it, from the plaquettes on that link that are not
chosen and contain no already-decided link.  The final count must be >= 2.
Every surviving support through the root is produced exactly once: at each
decision the only consistent choice is J = X ∩ (available plaquettes), and a
plaquette of X is always available at the first of its links to be decided.
"""
from __future__ import annotations

import time

DIM = 3
ROOT = ((0, 0, 0), 0, 1)


def add(x, mu, k=1):
    y = list(x)
    y[mu] += k
    return tuple(y)


def plaq_links(p):
    """Links of plaquette p with traversal signs (counterclockwise in (mu,nu))."""
    x, mu, nu = p
    return (((x, mu), 1), ((add(x, mu), nu), 1), ((add(x, nu), mu), -1), ((x, nu), -1))


def link_plaquettes(e):
    """The 2(d-1) = 6 plaquettes containing link e = (x, mu)."""
    x, mu = e
    out = []
    for nu in range(DIM):
        if nu == mu:
            continue
        a, b = (mu, nu) if mu < nu else (nu, mu)
        out.append((x, a, b))
        out.append((add(x, nu, -1), a, b))
    return tuple(out)


_LINKS = {}


def links_of(p):
    r = _LINKS.get(p)
    if r is None:
        r = tuple(e for e, _ in plaq_links(p))
        _LINKS[p] = r
    return r


def enumerate_supports(f_max, root=ROOT, deadline=None):
    """Yield every surviving support (frozenset) through root with <= f_max plaquettes."""
    chosen = {root}
    count = {e: 1 for e in links_of(root)}
    decided = set()

    def pick():
        best1 = None
        best = None
        for e, c in count.items():
            if e in decided:
                continue
            if c == 1:
                if best1 is None or e < best1:
                    best1 = e
            elif best is None or e < best:
                best = e
        return best1 if best1 is not None else best

    def n_ones():
        return sum(1 for e, c in count.items() if c == 1 and e not in decided)

    def rec():
        if deadline is not None and time.time() > deadline:
            raise TimeoutError
        e = pick()
        if e is None:
            yield frozenset(chosen)
            return
        n = len(chosen)
        if n + (n_ones() + 3) // 4 > f_max:
            return
        c = count[e]
        avail = [q for q in link_plaquettes(e)
                 if q not in chosen and not any(l in decided for l in links_of(q))]
        k = len(avail)
        decided.add(e)
        for mask in range(1 << k):
            J = [avail[i] for i in range(k) if mask >> i & 1]
            if c + len(J) < 2 or n + len(J) > f_max:
                continue
            for q in J:
                chosen.add(q)
                for l in links_of(q):
                    count[l] = count.get(l, 0) + 1
            yield from rec()
            for q in J:
                chosen.discard(q)
                for l in links_of(q):
                    v = count[l] - 1
                    if v:
                        count[l] = v
                    else:
                        del count[l]
        decided.discard(e)

    yield from rec()


def valence_profile(X):
    cnt = {}
    for p in X:
        for e in links_of(p):
            cnt[e] = cnt.get(e, 0) + 1
    prof = [0] * 7
    for v in cnt.values():
        prof[v] += 1
    return tuple(prof), cnt


if __name__ == "__main__":
    import sys
    fmax = int(sys.argv[1])
    t = time.time()
    per = {}
    for X in enumerate_supports(fmax):
        prof, _ = valence_profile(X)
        key = (len(X), prof[2:])
        per[key] = per.get(key, 0) + 1
    for k in sorted(per):
        print(k, per[k])
    print("seconds", round(time.time() - t, 1))

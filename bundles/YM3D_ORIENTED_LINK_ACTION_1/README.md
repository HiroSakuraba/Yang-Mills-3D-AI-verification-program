# Directed-link action of the cubic group

This bundle exports the exact action of all 48 signed-permutation matrices on
integer-lattice directed links. A link is stored as `(x, axis, epsilon)`: its
positive-axis base is x, and epsilon is +1 or -1 for traversal in the forward
or reverse direction. For epsilon=-1 the traversal starts at x+e_axis.

If M e_axis = s e_target, the transformed positive base is Mx for s=+1 and
Mx-e_target for s=-1. The traversal sign becomes epsilon*s. The exported
linear coefficients and constant offsets specify this action for every integer
coordinate; this is not interpolation from a bounded collection of examples.

The independent checker reads only the exported JSON. It reconstructs the group
by coordinate-axis images, derives the canonical edge from transformed endpoints,
and checks the endpoint identities by equality of integer affine coefficients.
It checks all 6,912 group-pair/axis composition identities, the identity, inverses
and faithfulness. These algebraic identities hold on the unbounded lattice.
Integer matrices also descend to every cubic periodic quotient because M(Ln)
is an L-multiple. The checker additionally audits both traversal signs on every
stored edge in periodic boxes of extent 2, 3 and 4, including boundary crossings.
At extent 2, different positive links with the same endpoint pair remain distinct:
the stored base and axis, rather than an unordered endpoint pair, identify edges.

Generator: `tools/build.py`, importing `src/ym3d_link_action` and reading the
already-checked group export. Independent checker: `tools/check_link_action.py`,
which imports no generator package or other bundle code. The audit uses only
integers; malformed exports, duplicate matrices and boolean integer impostors
are rejected. Seven deliberate artifact corruptions exercise rejection paths.

From the repository root with harness dependencies installed:

```sh
python -m unittest discover -s bundles/YM3D_ORIENTED_LINK_ACTION_1/tests -v
make gate GATE=YM3D_ORIENTED_LINK_ACTION_1
make verify
```

Existing group/schema prerequisites must be reproduced first in a fresh checkout.
No composite supports, orbit multiplicities, collision graphs, gauge-field
integrals, correlation bound or physical mass-gap result is established here.
The next program obligation is `YM3D_SUPPORT_LIFT_1`.

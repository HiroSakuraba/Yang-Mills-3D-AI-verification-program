# CLAUDE.md

This repository is driven by the contract in **AGENTS.md** — read it first and
follow it exactly. Quick start:

```bash
make setup     # once
make status    # see the gate board
make next      # the single next gate to work on (JSON)
make gate GATE=<id>   # run/close one gate
```

Core discipline: independent checkers (never import the generator), exact
arithmetic, fail-stop on error, and never let prose claim more than the CLOSED
gates earn (`make claims`). The authoritative DAG is `program.yaml`.

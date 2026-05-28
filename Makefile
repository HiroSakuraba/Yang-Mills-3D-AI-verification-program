# YM3D harness — agent-facing entrypoints.
# A coding agent should prefer these targets over ad-hoc commands.

PY ?= python
RUN := $(PY) orchestrator/run.py

.PHONY: help status next graph all verify kill-check claims setup test-harness

help:           ## show this help
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | \
	 awk 'BEGIN{FS=":.*?## "}{printf "  %-14s %s\n",$$1,$$2}'

setup:          ## install harness deps
	$(PY) -m pip install --break-system-packages -q pyyaml jsonschema

status:         ## show the gate board
	@$(RUN) status

next:           ## print the next runnable gate (JSON, for the agent)
	@$(RUN) next

gate:           ## run one gate: make gate GATE=YM3D_...
	@$(RUN) gate $(GATE)

up-to:          ## run everything needed to close GATE: make up-to GATE=YM3D_...
	@$(RUN) up-to $(GATE)

all:            ## run the whole DAG, fail-stop
	@$(RUN) all

verify:         ## re-run all CLOSED gates from clean (reproducibility)
	@$(RUN) verify

kill-check:     ## evaluate kill / pivot criteria
	@$(RUN) kill-check

graph:          ## emit resolved DAG as mermaid
	@$(RUN) graph

claims:         ## claim ratchet over the design manuscript
	@$(PY) orchestrator/claim_lint.py design/YM3D_CONSTRUCTIVE_RG_DESIGN.md

scaffold:       ## scaffold a new gate: make scaffold GATE=YM3D_... SHORT=link_action
	@$(PY) orchestrator/scaffold_gate.py $(GATE) --short $(SHORT)

ci:             ## full local CI: harness self-test + status + claims
	@$(MAKE) -s status
	@$(MAKE) -s claims

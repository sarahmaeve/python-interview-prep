# Python Interview Prep — developer tasks
#
# Common targets:
#   make test          # run every exercise test via unittest discovery
#   make test-pytest   # same, via pytest (requires `pip install --group dev`)
#   make test-guides   # run the guide files (they're self-verifying)
#   make lint          # ruff check
#   make typecheck     # mypy on guides + exercise 13/14 (which expect types)
#   make check         # lint + typecheck + test (what CI runs)
#
# Single-exercise shortcuts:
#   make ex N=08       # run exercise 08's tests
#   make solution N=08 # cat the solution walkthrough

PY ?= python3

.PHONY: help test test-pytest test-guides lint format typecheck check ex solution clean

help:
	@awk 'BEGIN{FS=":.*#"} /^[a-zA-Z_-]+:.*#/{printf "  %-16s %s\n", $$1, $$2}' $(MAKEFILE_LIST)

test:  ## Run every exercise's tests (each is its own package)
	@# NOTE: exercises contain intentional bugs — expect failures until you fix them.
	@# Shows a pass/fail summary per directory; does NOT stop at the first failure.
	@fail=0; \
	 for d in exercises/*/; do \
	   ( cd "$$d" && $(PY) -m unittest discover -p "test_*.py" -t . > /tmp/_ex.log 2>&1 ) \
	   && echo "  ok   $$d" \
	   || { echo "  FAIL $$d"; fail=1; }; \
	 done; \
	 exit $$fail

test-pytest:  ## Run all exercise tests with pytest (needs dev deps)
	@$(PY) -m pytest exercises

test-guides:  ## Run every guide file (they print and self-check) — used by CI
	@for g in guides/*.py; do \
		echo "━━━ $$g"; \
		$(PY) "$$g" > /dev/null || exit 1; \
	done

lint:  ## ruff check
	@$(PY) -m ruff check .

format:  ## ruff format
	@$(PY) -m ruff format .

typecheck:  ## mypy — strict on guides, lenient on debug exercises
	@$(PY) -m mypy guides exercises/14_add_type_hints exercises/17_property_and_composition

check: lint typecheck test-guides  ## What CI runs (guides only — exercises expect bugs)

# Per-exercise shortcuts. Usage: make ex N=08
ex:
	@test -n "$(N)" || (echo "usage: make ex N=<NN>"; exit 1)
	@dir=$$(ls -d exercises/$(N)_* 2>/dev/null | head -1); \
	test -n "$$dir" || (echo "no exercise matching $(N)_*"; exit 1); \
	echo "━━━ $$dir"; \
	cd "$$dir" && $(PY) -m unittest discover -p "test_*.py"

solution:
	@test -n "$(N)" || (echo "usage: make solution N=<NN>"; exit 1)
	@cat solutions/$(N)_solution.md

clean:  ## Remove __pycache__ and .mypy_cache
	@find . -type d -name __pycache__ -prune -exec rm -rf {} +
	@rm -rf .mypy_cache .ruff_cache .pytest_cache

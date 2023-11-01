PROJ_ROOT := $(shell git rev-parse --show-toplevel)
LILAC_ROOT := $(PROJ_ROOT)/deps/elisp/lilac
PROCS := $(shell nproc)
define run_emacs
	LILAC_ROOT=$(LILAC_ROOT) emacs $(2) --quick --batch --kill \
		--load $(LILAC_ROOT)/lilac.el \
		--load $(PROJ_ROOT)/codex.el \
		--eval="$(1)"
endef
define run_emacs_nobatch
	LILAC_ROOT=$(LILAC_ROOT) emacs $(2) --quick --kill \
		--load $(LILAC_ROOT)/lilac.el \
		--load $(PROJ_ROOT)/codex.el \
		--eval="$(1)"
endef
src = $(shell find problem/ -type f -name '*.org')
src_appendix = $(shell find appendix/ -type f -name '*.org')
woven_html = $(patsubst problem/%.org, problem/%.html, $(src)) \
	$(patsubst appendix/%.org, appendix/%.html, $(src_appendix))
# problem/foo problem/bar ...
problem_dirs = $(shell find problem -maxdepth 1 -type d | sort | tail -n+2)
appendix_dirs = $(shell find appendix -maxdepth 1 -type d | sort | tail -n+2 | grep -v mathematics)
# foo bar ...
problem_dirs_without_prefix = $(subst problem/,,$(problem_dirs))
appendix_dirs_without_prefix = $(subst appendix/,,$(appendix_dirs))

define weave_org

$(1): $(2) build-literate.org
	@echo weaving $(2)
	$(call run_emacs,(lilac-publish),$(2))

endef

all: check weave
.PHONY: all

# Currently we don't have any optimizations for tangling, but we still set
# CODEX_LP_QUICK=1 anyway to align with what we do for weave-quick.
$(all_tangled_sources) tangle &: $(src) appendix/python_tricks/README.org
	@echo tangling in parallel
	CODEX_LP_QUICK=1 make -C $(PROJ_ROOT) -j$(PROCS) $(all_tangled_sources)
	touch tangle

build_literate_org_output = .gitattributes .gitignore Makefile shell.nix
all_tangled_sources = citations.bib $(build_literate_org_output)\
	appendix/python_tricks/__init__.py \
	appendix/python_tricks/test_python_tricks.py \
	$(foreach p,$(problem_dirs_without_prefix),\
		problem/$(p)/__init__.py problem/$(p)/test_$(p).py)

$(build_literate_org_output) &: build-literate.org
	$(call run_emacs,(org-babel-tangle),build-literate.org)

citations.bib: README.org
	$(call run_emacs,(org-babel-tangle),README.org)

appendix/python_tricks/test_python_tricks.py: appendix/python_tricks/README.org
	$(call run_emacs,(org-babel-tangle),appendix/python_tricks/README.org)

define tangle_tests

$(1) $(2) &: $(3)
	@echo tangling $(3)
	$(call run_emacs,(org-babel-tangle),$(3))

endef

# See https://stackoverflow.com/a/9694782/437583.
$(foreach p,$(problem_dirs_without_prefix),\
	$(eval $(call tangle_tests,\
	problem/$(p)/__init__.py,problem/$(p)/test_$(p).py,\
	problem/$(p)/README.org)))

weave: build-html

build-html: README.html $(woven_html)
.PHONY: build-html
.PHONY: appendix/mathematics/twos-complement.html

appendix/mathematics/README.html: appendix/mathematics/README.org appendix/mathematics/twos-complement.org
	$(call run_emacs,(lilac-publish),appendix/mathematics/README.org)

README.html: build-literate.org README.org citations.bib
	$(call run_emacs,(lilac-publish),README.org)

$(foreach d,$(appendix_dirs_without_prefix),\
	$(eval $(call weave_org,\
	appendix/$(d)/README.html,\
	appendix/$(d)/README.org)))

$(foreach d,$(problem_dirs_without_prefix),\
	$(eval $(call weave_org,\
	problem/$(d)/README.html,\
	problem/$(d)/README.org)))

check: lint test
.PHONY: check

test: tangle
	python -m unittest discover -s problem
	python -m unittest discover -s appendix
	touch test

lint: mypy ruff spellcheck
.PHONY: lint

mypy: tangle
	mypy problem appendix
.PHONY: mypy

ruff: tangle
	ruff problem appendix
.PHONY: ruff

ORG_FILES = $(shell find . -type f -name '*.org')

spellcheck: $(ORG_FILES)
	typos
.PHONY: spellcheck

# Enter development environment.
shell:
	nix-shell --pure

nixpkgs_stable_channel := nixos-23.05
update-deps: package/nix/sources.json package/nix/sources.nix
	cd package && niv update nixpkgs --branch $(nixpkgs_stable_channel)
	cd package && niv update
	touch update-deps

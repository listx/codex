PROJ_ROOT := $(shell git rev-parse --show-toplevel)
PROCS := $(shell nproc)
define run_emacs
	emacs $(2) --quick --batch --kill --load $(PROJ_ROOT)/codex.el --eval="$(1)"
endef

all: tangle weave

do-tangle: tangle-sources
.PHONY: do-tangle

# Currently we don't have any optimizations for tangling, but we still set CODEX_LP_QUICK=1 anyway to align with what we do for weave-quick.
tangle:
	CODEX_LP_QUICK=1 make -C $(PROJ_ROOT) -j$(PROCS) do-tangle
.PHONY: tangle

build-literate-org:
	# Generate the toplevel Makefile (this file) and image/Makefile (overwriting
	# them if necessary). In a way this bootstraps the whole
	# literate-programming pipeline. Note that these files are different than
	# the ones used to compile the tangled source code.
	$(call run_emacs,(org-babel-tangle),build-literate.org)

# Generate source code.
tangle-sources: README-org

# Sadly, orgmode does not support including files for tangling. This means we have to tangle each org file separately, even though they all come together into main.org.
README-org: build-literate-org
	$(call run_emacs,(org-babel-tangle),README.org)
	$(call run_emacs,(org-babel-tangle),problem/parity/README.org)

.PHONY: build-literate-org tangle-sources

weave: build-html

weave-quick:
	CODEX_LP_QUICK=1 make -C ${PROJ_ROOT} -j$(PROCS) build-html
.PHONY: weave-quick

build-html: README.html

README.html:
	$(call run_emacs,(batch-org-gen-css-and-exit \"README.org\"),)
	$(call run_emacs,(codex-publish),README.org)
	sed -i 's/.csl-left-margin{float: left; padding-right: 0em/.csl-left-margin{float: left; padding-right: 1em/' README.html
	$(call run_emacs,(codex-publish),problem/parity/README.org)

test:
	python -m unittest discover -s problem

.PHONY: all weave README.html

# Enter development environment.
shell:
	nix-shell --pure

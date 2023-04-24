PROJ_ROOT := $(shell git rev-parse --show-toplevel)
PROCS := $(shell nproc)
define run_emacs
	emacs $(2) --quick --batch --kill --load $(PROJ_ROOT)/codex.el --eval="$(1)"
endef
src = $(shell find problem/ -type f -name '*.org')
woven_html = $(patsubst problem/%.org, problem/%.html, $(src))
# problem/foo problem/bar ...
problem_dirs = $(shell find problem -maxdepth 1 -type d | sort | tail -n+2)
# foo bar ...
problem_dirs_without_prefix = $(subst problem/,,$(problem_dirs))

define weave_org

$(1): $(2)
	@echo weaving $(2)
	$(call run_emacs,(codex-publish),$(2))

endef

all: tangle weave
.PHONY: all

# Currently we don't have any optimizations for tangling, but we still set CODEX_LP_QUICK=1 anyway to align with what we do for weave-quick.
$(all_tangled_sources) tangle &: $(src)
	@echo tangling in parallel
	CODEX_LP_QUICK=1 make -C $(PROJ_ROOT) -j$(PROCS) $(all_tangled_sources)
	touch tangle

build_literate_org_output = codex.el .gitattributes .gitignore Makefile shell.nix style.css syntax-highlighting.css
all_tangled_sources = citations.bib $(build_literate_org_output) $(foreach p,$(problem_dirs_without_prefix),problem/$(p)/__init__.py problem/$(p)/test_$(p).py)

$(build_literate_org_output) &: build-literate.org
	# Generate the toplevel Makefile (this file) and image/Makefile (overwriting
	# them if necessary). In a way this bootstraps the whole
	# literate-programming pipeline. Note that these files are different than
	# the ones used to compile the tangled source code.
	$(call run_emacs,(org-babel-tangle),build-literate.org)

citations.bib: README.org
	$(call run_emacs,(org-babel-tangle),README.org)

define tangle_tests

$(1) $(2) &: $(3)
	@echo tangling $(3)
	$(call run_emacs,(org-babel-tangle),$(3))

endef

# See https://stackoverflow.com/a/9694782/437583.
$(foreach p,$(problem_dirs_without_prefix),$(eval $(call tangle_tests,problem/$(p)/__init__.py,problem/$(p)/test_$(p).py,problem/$(p)/README.org)))

weave: build-html

build-html: README.html $(woven_html)
.PHONY: build-html

README.html: build-literate.org README.org
	$(call run_emacs,(batch-org-gen-css-and-exit \"README.org\"),)
	$(call run_emacs,(codex-publish),README.org)
	sed -i 's/.csl-left-margin{float: left; padding-right: 0em/.csl-left-margin{float: left; padding-right: 1em/' README.html

$(foreach p,$(problem_dirs_without_prefix),$(eval $(call weave_org,problem/$(p)/README.html,problem/$(p)/README.org)))

test: all
	python -m unittest discover -s problem
.PHONY: test

# Enter development environment.
shell:
	nix-shell --pure

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
src_problem = $(shell find problem/ -type f -name 'README.org')
woven_html = $(patsubst problem/%/README.org, problem/%/README.html, $(src_problem)) \
	appendix/mathematics/README.html appendix/python_tricks/README.html README.html
# problem/foo problem/bar ...
problem_dirs = $(shell find problem -maxdepth 1 -type d | sort | tail -n+2)
# foo bar ...
problem_dirs_without_prefix = $(subst problem/,,$(problem_dirs))
test_dirs = $(shell find . -type f -name '__init__.py' | sed 's|/__init__.py||')
# All problem dirs with Tikz-generated images.
image_dirs = $(shell find . -type f -name 'images.org' | sed -e 's|/[^/]*$$||' -e 's|^problem/||' | sort -u)
all_tests_verified = $(patsubst %.py, %.py.verified, $(shell find . -type f -name 'test_*.py'))

define weave_org

$(1): $(2) $(shell find $(3) -type f -name 'images.org' | xargs grep 'img.pdf' | sed -e 's|images.org:#+header: :file ||' -e 's|.img.pdf|.svg|') build-literate.org
	@echo weaving $(2)
	$(call run_emacs,(lilac-publish),$(2))

endef

all: check.verified weave
.PHONY: all

build_literate_tangled = .gitattributes .gitignore codex.css codex.problem.css codex.el _typos.toml Makefile shell.nix
$(build_literate_tangled) &: build-literate.org
	$(call run_emacs,(org-babel-tangle),build-literate.org)
	touch $(build_literate_tangled)

citations.bib: README.org
	$(call run_emacs,(org-babel-tangle),README.org)
	touch citations.bib

define generate_img_pdfs
$(shell grep 'img.pdf' $(1) | sed -e 's|^|$(1):|' -e 's|images.org:#+header: :file ||') &: $(1)
	@echo generating images from $(1)
	$(call run_emacs,(org-html-export-to-html),$(1))
	rm -f $(patsubst %/images.org, %/images.html, $(1))
endef

define generate_img_svgs
$(1:.img.pdf=.svg): $(1)
	@echo generating svg from $(1)
	@echo $(shell pwd)
	pdf2svg $(1) $(1).uncropped.svg
	inkscape \
		--export-plain-svg \
		--export-margin=5 \
		--export-filename=$(1:.img.pdf=.svg) \
		--export-area-drawing \
		$(1).uncropped.svg
	rm $(1).uncropped.svg
endef

$(foreach p,$(image_dirs),\
	$(eval $(call generate_img_pdfs,\
	$(p)/images.org)))

all_img_pdfs = $(shell find . -type f -name 'images.org' | xargs grep 'img.pdf' | sed 's|images.org:#+header: :file ||')
$(foreach img,$(all_img_pdfs),\
	$(eval $(call generate_img_svgs,\
	$(img))))

define tangle_tests
$(1)/__init__.py $(1)/test_$(2).py &: $(1)/README.org
	@echo tangling $(1)/README.org
	$(call run_emacs,(org-babel-tangle),$(1)/README.org)
	touch $(shell find $(1) -type f -name '*.py')
endef

# See https://stackoverflow.com/a/9694782/437583.
$(foreach d,$(test_dirs),\
	$(eval $(call tangle_tests,$(d),$(shell echo $(d) | sed 's|./[^/]\+/||'))))

# $(2) is the name of FOO in problem/FOO/...
define verify_tests
$(1)/test_$(2).py.verified: $(1)/test_$(2).py
	python -m unittest discover --failfast --start-directory $(1) --top $(shell echo $(1) | sed -e 's|./||' -e 's|/.\+||')
	touch $(1)/test_$(2).py.verified
endef

$(foreach d,$(test_dirs),\
	$(eval $(call verify_tests,$(d),$(shell echo $(d) | sed 's|./[^/]\+/||'))))

weave: $(woven_html)
	touch weave

README.html: build-literate.org README.org citations.bib
	$(call run_emacs,(lilac-publish),README.org)

$(foreach d,$(problem_dirs_without_prefix),\
	$(eval $(call weave_org,\
	problem/$(d)/README.html,\
	problem/$(d)/README.org,problem)))

appendix/mathematics/README.html: appendix/mathematics/README.org appendix/mathematics/twos-complement.org
	$(call run_emacs,(lilac-publish),appendix/mathematics/README.org)

appendix/python_tricks/README.html: appendix/python_tricks/README.org
	$(call run_emacs,(lilac-publish),appendix/mathematics/README.org)

check.verified: lint.verified test
	touch check.verified

test: $(all_tests_verified)
	touch test

lint.verified: mypy.verified ruff.verified spellcheck.verified
	touch lint.verified

mypy.verified: $(all_tests_verified)
	mypy problem appendix
	touch mypy.verified

ruff.verified: $(all_tests_verified)
	ruff problem appendix
	touch ruff.verified

ORG_FILES = $(shell find . -type f -name '*.org')

spellcheck.verified: $(ORG_FILES)
	typos
	touch spellcheck.verified

# Enter development environment.
shell:
	nix-shell --pure

nixpkgs_stable_channel := nixos-23.05
update-deps: package/nix/sources.json package/nix/sources.nix
	cd package && niv update nixpkgs --branch $(nixpkgs_stable_channel)
	cd package && niv update
	touch update-deps

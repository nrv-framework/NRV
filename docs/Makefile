# Minimal makefile for Sphinx documentation
#

# You can set these variables from the command line, and also
# from the environment for the first two.
SPHINXOPTS    ?=
SPHINXBUILD   ?= sphinx-build
SOURCEDIR     = .
BUILDDIR      = _build
CODEBUILDDIR  = _nrv

help:
	@echo "Available commands:"
	@echo "  make html     → Build HTML documentation"
	@echo "  make clean    → Remove generated files"
	@echo "  make open     → Open the HTML documentation in your browser"

html:
	$(SPHINXBUILD) -b html $(SOURCEDIR) $(BUILDDIR)/html
	@echo "HTML documentation generated in $(BUILDDIR)/html"

clean:
	rm -rf $(BUILDDIR)
	@echo "Directory $(BUILDDIR) has been cleaned"
	rm -rf $(CODEBUILDDIR)
	@echo "Directory $(CODEBUILDDIR) has been cleaned"

open:
	@echo "Opening documentation in browser..."
	@open $(BUILDDIR)/html/index.html || open $(BUILDDIR)/html/index.html || echo "Please open $(BUILDDIR)/html/index.html manually"


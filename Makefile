# ============================================================
#  Makefile -- HandwerkerKasse Term Project
#  THGA Bochum
# ============================================================
LATEXMK  := latexmk
OUTDIR   := out
LMKFLAGS := -pdf -interaction=nonstopmode -halt-on-error \
            -cd -output-directory=../$(OUTDIR)
TEXENV   := TEXINPUTS="$(CURDIR)/style:.:$$TEXINPUTS"
STYLE    := style/thga-db.sty

.PHONY: all clean distclean help

all: $(OUTDIR)/proposal.pdf $(OUTDIR)/user-doc.pdf $(OUTDIR)/developer-doc.pdf

$(OUTDIR):
	mkdir -p $(OUTDIR)

$(OUTDIR)/proposal.pdf: proposal-template/proposal.tex $(STYLE) | $(OUTDIR)
	$(TEXENV) $(LATEXMK) $(LMKFLAGS) proposal-template/proposal.tex

$(OUTDIR)/user-doc.pdf: user-documentation/documentation.tex $(STYLE) | $(OUTDIR)
	$(TEXENV) $(LATEXMK) $(LMKFLAGS) -jobname=user-doc user-documentation/documentation.tex

$(OUTDIR)/developer-doc.pdf: developer-documentation/documentation.tex $(STYLE) | $(OUTDIR)
	$(TEXENV) $(LATEXMK) $(LMKFLAGS) -jobname=developer-doc developer-documentation/documentation.tex

clean:
	rm -f $(addprefix $(OUTDIR)/, *.aux *.log *.fdb_latexmk *.fls *.out *.toc *.synctex.gz)

distclean:
	rm -rf $(OUTDIR)

help:
	@echo "Available targets:"
	@echo "  all        - build all PDFs  (-> $(OUTDIR)/)"
	@echo "  clean      - remove auxiliary files, keep PDFs"
	@echo "  distclean  - remove everything including $(OUTDIR)/"

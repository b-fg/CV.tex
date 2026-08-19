MAIN=main
OUT_DIR=build
fetch=1

.SUFFIXES:
.SUFFIXES: .bib .pdf .tex
.PHONY: run clean scholar

# Builds $(OUT_DIR)/$(MAIN).pdf. The PDF is never tracked on main: CI publishes
# it to the "latest" GitHub release instead (see .github/workflows/ci.yml).
run: $(OUT_DIR)/$(MAIN).pdf

scholar:
ifeq ($(fetch), 1)
	python get_scholar_data.py
else
	@echo "Not fetching Google Scholar data"
endif

$(OUT_DIR)/$(MAIN).pdf: $(OUT_DIR)/$(MAIN).bbl $(MAIN).tex | scholar
	pdflatex --output-directory=$(OUT_DIR) $(MAIN).tex -draftmode
	pdflatex --output-directory=$(OUT_DIR) $(MAIN).tex

$(OUT_DIR)/$(MAIN).bbl: $(OUT_DIR)/$(MAIN).aux
	bibtex $(OUT_DIR)/$(MAIN)

$(OUT_DIR)/$(MAIN).aux: $(MAIN).bib | scholar
	pdflatex --output-directory=$(OUT_DIR) $(MAIN).tex -draftmode
	pdflatex --output-directory=$(OUT_DIR) $(MAIN).tex -draftmode

clean:
	rm -rf *.aux *.lof *.log *.lot *.toc *.bbl *.blg *.pdf *.out $(OUT_DIR)

$(info $(shell mkdir -p $(OUT_DIR)))

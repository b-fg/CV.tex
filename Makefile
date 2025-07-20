MAIN=main
OUT_DIR=build

.SUFFIXES:
.SUFFIXES: .bib .pdf .tex
.PHONY: clean

run: $(MAIN).pdf

$(MAIN).pdf: $(OUT_DIR)/$(MAIN).bbl $(MAIN).tex
	sh get_scholar_data.sh
	pdflatex --output-directory=$(OUT_DIR) $(MAIN).tex -draftmode
	pdflatex --output-directory=$(OUT_DIR) $(MAIN).tex
	cp $(OUT_DIR)/$(MAIN).pdf .

$(OUT_DIR)/$(MAIN).bbl: $(OUT_DIR)/$(MAIN).aux
	bibtex $(OUT_DIR)/$(MAIN)

$(OUT_DIR)/$(MAIN).aux: $(MAIN).bib
	sh get_scholar_data.sh
	pdflatex --output-directory=$(OUT_DIR) $(MAIN).tex -draftmode
	pdflatex --output-directory=$(OUT_DIR) $(MAIN).tex -draftmode

clean:
	rm -rf *.aux *.lof *.log *.lot *.toc *.bbl *.blg *.pdf *.out build

$(info $(shell mkdir -p $(OUT_DIR)))
TEX=cv

$(TEX).pdf: $(TEX).tex
	# for bibtex to work correctly we need to compile twice
	pdflatex $(TEX)

.PHONY: clean	
clean:
	rm -f *.pdf *.gz *.log

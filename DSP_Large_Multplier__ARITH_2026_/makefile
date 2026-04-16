FileName=egg_dsp.tex 
# LaTeX compiler flags (space-separated list)
# Example: make LATEXFLAGS="-shell-escape -interaction=nonstopmode" run
# Example: make LATEXFLAGS="-shell-escape" run-with-bib
LATEXFLAGS=

# Makefile for building the LaTeX document
run: $(FileName)
	pdflatex $(LATEXFLAGS) $(FileName)
	pdflatex $(LATEXFLAGS) $(FileName)
	@echo "Cleaning auxiliary files..."
	@rm -f *.blg *.nav *.bbl *.aux *.log *.out *.snm *.toc *.vrb *.synctex.gz

# Build without cleaning (useful for debugging)
run-keep: $(LATEXFLAGS) $(FileName)
	pdflatex $(LATEXFLAGS) $(FileName)

# Alternative target if you need bibliography support
run-with-bib: $(FileName)
	pdflatex $(LATEXFLAGS) $(FileName)
	bibtex $(basename $(FileName))
	pdflatex $(LATEXFLAGS) $(FileName)
	pdflatex $(LATEXFLAGS) $(FileName)
# 	open $(basename $(FileName)).pdf
# 	@echo "Cleaning auxiliary files..."
# 	@rm -f *.nav *.bbl *.aux *.log *.out *.snm *.toc *.vrb *.synctex.gz

rmpdf:
	rm -f $(basename $(FileName)).pdf
clean:
	rm -f *.blg *.nav *.bbl *.aux *.log *.out *.snm *.toc *.vrb *.synctex.gz

rmconflict: 
# Remove conflicted files that dropbox sometimes creates 
	find . -type f -name "*conflicted*" -delete

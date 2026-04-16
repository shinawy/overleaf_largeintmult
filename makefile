FileName=dsp_intmult.tex 
# LaTeX compiler flags (space-separated list)
# Example: make LATEXFLAGS="-shell-escape -interaction=nonstopmode" run
# Example: make LATEXFLAGS="-shell-escape" run-with-bib
LATEXFLAGS="-shell-escape"
# LATEXFLAGS=

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
	# 1. Compile to a temporary name so uPDF doesn't lock the main file
	pdflatex $(LATEXFLAGS) -jobname=build_temp $(FileName)
	bibtex build_temp
	pdflatex $(LATEXFLAGS) -jobname=build_temp $(FileName)
	pdflatex $(LATEXFLAGS) -jobname=build_temp $(FileName)
	
	# 2. Delete the old corrupted PDF if it exists
	rm -f $(basename $(FileName)).pdf
	
	# 3. Rename the fresh build to the real name (Atomic operation)
	mv build_temp.pdf $(basename $(FileName)).pdf
	
	# 4. Cleanup auxiliary temp files
	@rm -f build_temp.* *.nav *.aux *.log *.out *.snm *.toc *.vrb *.synctex.gz
	
	# 5. Small pause to let the filesystem settle, then open
	sleep 0.5
	open $(basename $(FileName)).pdf
# 	open -a Preview $(basename $(FileName)).pdf
# 	open -a Skim $(basename $(FileName)).pdf

# 	@echo "Cleaning auxiliary files..."
# 	@rm -f *.nav *.bbl *.aux *.log *.out *.snm *.toc *.vrb *.synctex.gz

rmpdf:
	rm -f $(basename $(FileName)).pdf
clean:
	rm -f *.blg *.nav *.bbl *.aux *.log *.out *.snm *.toc *.vrb *.synctex.gz

rmconflict: 
# Remove conflicted files that dropbox sometimes creates 
	find . -type f -name "*conflicted*" -delete

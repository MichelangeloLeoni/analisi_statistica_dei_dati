# Main Makefile for the LaTeX document
MAIN=main

all: 
	pdflatex $(MAIN).tex
	pdflatex $(MAIN).tex

clean:
	rm -f *.aux *.log *.out *.toc

cleanall: clean
	rm -f *.aux *.log *.out *.toc
	rm -f main.pdf
# Main Makefile for the LaTeX document

all: 
	pdflatex main.tex
	rm -f *.aux *.log *.out *.toc

clean:
	rm -f *.aux *.log *.out *.toc

cleanall: clean
	rm -f *.aux *.log *.out *.toc
	rm -f main.pdf
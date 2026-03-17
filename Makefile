# Main Makefile for the LaTeX document
MAIN=main

all:
	make build
	make clean

build:
	pdflatex $(MAIN).tex
	pdflatex $(MAIN).tex

clean:
	rm -f *.aux *.log *.out *.toc
	rm -f **/*.aux **/*.log **/*.out **/*.toc

cleanall:
	rm -f *.aux *.log *.out *.toc
	rm -f **/*.aux **/*.log **/*.out **/*.toc
	rm -f main.pdf

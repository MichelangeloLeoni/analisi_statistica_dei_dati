ifeq ($(OS),Windows_NT)
    RM = del /Q /F
    FixPath = $(subst /,\,$1)
else
    RM = rm -f
    FixPath = $1
endif

MAIN = main

all:
	$(MAKE) build
	$(MAKE) clean

build:
	pdflatex $(MAIN).tex
	pdflatex $(MAIN).tex

clean:
	-$(RM) *.aux *.log *.out *.toc
	-$(RM) $(call FixPath,chapters/*.aux chapters/*.log)

cleanall: clean
	-$(RM) $(MAIN).pdf
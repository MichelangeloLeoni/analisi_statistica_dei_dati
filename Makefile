ifeq ($(OS),Windows_NT)
    RM = del /Q /F
    PYTHON = python
    PYFILES = $(subst /,\,$(wildcard $(PY)/*.py))
    FOREACH = for %%f in ($(PYFILES)) do $(PYTHON) %%f
else
    RM = rm -f
    PYTHON = python3
    PYFILES = $(wildcard $(PY)/*.py)
    FOREACH = for file in $(PYFILES); do $(PYTHON) $$file; done
endif

MAIN = main
PY = src
DRAFT_NAME = draft_analisi_statistica_dei_dati
PRODUCTION_NAME = production_analisi_statistica_dei_dati

all:
	$(MAKE) build
	$(MAKE) clean

build:
	pdflatex -jobname=$(DRAFT_NAME) $(MAIN).tex
	pdflatex -jobname=$(DRAFT_NAME) $(MAIN).tex

clean:
	-$(RM) *.aux *.log *.out *.toc

cleanall:
	$(MAKE) clean
	-$(RM) $(DRAFT_NAME).pdf $(PRODUCTION_NAME).pdf

py:
	$(FOREACH)
	$(MAKE) build
	$(MAKE) clean

production:
	$(FOREACH)
	pdflatex -jobname=$(PRODUCTION_NAME) "\def\draft{0}\input{$(MAIN).tex}"
	pdflatex -jobname=$(PRODUCTION_NAME) "\def\draft{0}\input{$(MAIN).tex}"
	$(MAKE) clean
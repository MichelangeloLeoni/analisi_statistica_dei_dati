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

all:
	$(MAKE) build
	$(MAKE) clean

build:
	pdflatex -jobname=draft_analisi_statistica_dei_dati $(MAIN).tex
	pdflatex -jobname=draft_analisi_statistica_dei_dati $(MAIN).tex

clean:
	-$(RM) *.aux *.log *.out *.toc

cleanall:
	$(MAKE) clean
	-$(RM) $(MAIN).pdf

py:
	$(FOREACH)
	$(MAKE) build
	$(MAKE) clean

production:
	$(FOREACH)
	pdflatex -jobname=production_analisi_statistica_dei_dati "\def\draft{0}\input{$(MAIN).tex}"
	pdflatex -jobname=production_analisi_statistica_dei_dati "\def\draft{0}\input{$(MAIN).tex}"
	$(MAKE) clean
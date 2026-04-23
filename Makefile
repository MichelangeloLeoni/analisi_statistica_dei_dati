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

LATEXMK = latexmk -pdf -interaction=nonstopmode -halt-on-error

# ------------------------

all: build

build:
	$(LATEXMK) -jobname=$(DRAFT_NAME) $(MAIN).tex

production:
	$(FOREACH)
	$(LATEXMK) -jobname=$(PRODUCTION_NAME) \
		-pdflatex="pdflatex \\def\\draft{0} %O %S" \
		$(MAIN).tex

py:
	$(FOREACH)
	$(MAKE) build

clean:
	$(LATEXMK) -c
	-$(RM) *.out *.toc *.fls *.log *.fdb_latexmk *.aux

cleanall:
	$(LATEXMK) -C
	-$(RM) *.out *.toc *.fls *.log *.fdb_latexmk *.aux
	-$(RM) $(DRAFT_NAME).pdf $(PRODUCTION_NAME).pdf
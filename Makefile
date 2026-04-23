ifeq ($(OS),Windows_NT)
    RM = del /Q /F
    PYTHON = python
    FIXPATH = $(subst /,\,$1)
    MKDIR = if not exist $(subst /,\,$1) mkdir $(subst /,\,$1)
else
    RM = rm -f
    PYTHON = python3
    FIXPATH = $1
    MKDIR = mkdir -p $1
endif

MAIN = main
PY_DIR = src
STAMP_DIR = .stamps

PY_SOURCES = $(wildcard $(PY_DIR)/*.py)
PY_STAMPS = $(patsubst $(PY_DIR)/%.py, $(STAMP_DIR)/%.stamp, $(PY_SOURCES))

DRAFT_NAME = draft_analisi_statistica_dei_dati
PRODUCTION_NAME = production_analisi_statistica_dei_dati
LATEXMK = latexmk -pdf -interaction=nonstopmode -halt-on-error

# ------------------------

all: build

production: $(PY_STAMPS)
	$(LATEXMK) -jobname=$(PRODUCTION_NAME) \
		-pdflatex='pdflatex %O "\def\draft{0}\input{%S}"' \
		$(MAIN).tex

build:
	$(LATEXMK) -jobname=$(DRAFT_NAME) $(MAIN).tex

$(STAMP_DIR)/%.stamp: $(PY_DIR)/%.py
	@$(call MKDIR, $(STAMP_DIR))
	$(PYTHON) $<
	@echo "Eseguito $<" > $@

py: $(PY_STAMPS)
	$(MAKE) build

clean:
	$(LATEXMK) -c
	-$(RM) *.out *.toc *.fls *.log *.fdb_latexmk *.aux
	-$(if $(filter Windows_NT,$(OS)), rmdir /S /Q $(STAMP_DIR), rm -rf $(STAMP_DIR))

cleanall: clean
	$(LATEXMK) -C
	-$(RM) $(DRAFT_NAME).pdf $(PRODUCTION_NAME).pdf
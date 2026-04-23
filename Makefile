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

MAIN = analisi_statistica_dei_dati
PY_DIR = src
OUT_DIR = .build
STAMP_DIR = .stamps

PY_SOURCES = $(wildcard $(PY_DIR)/*.py)
PY_STAMPS = $(patsubst $(PY_DIR)/%.py, $(STAMP_DIR)/%.stamp, $(PY_SOURCES))

DRAFT_NAME = draft_analisi_statistica_dei_dati
PRODUCTION_NAME = production_analisi_statistica_dei_dati
LATEXMK = latexmk -pdf -interaction=nonstopmode -halt-on-error -auxdir=$(OUT_DIR) -silent

# ------------------------

all: build

production: $(PY_STAMPS)
	$(LATEXMK) -jobname=$(PRODUCTION_NAME) \
		-pdflatex='pdflatex %O "\def\draft{0}\input{%S}"' \
		$(MAIN).tex

build:
	$(LATEXMK) -jobname=$(MAIN) $(MAIN).tex

$(STAMP_DIR)/%.stamp: $(PY_DIR)/%.py
	@$(call MKDIR, $(STAMP_DIR))
	$(PYTHON) $<
	@echo "Executed $<" > $@

py: $(PY_STAMPS)
	$(MAKE) build

clean:
	$(LATEXMK) -c
	-$(RM) *.out *.toc *.fls *.log *.fdb_latexmk *.aux *.synctex.gz
	-$(if $(filter Windows_NT,$(OS)), rmdir /S /Q $(STAMP_DIR), rm -rf $(STAMP_DIR))

cleanall: clean
	$(LATEXMK) -C
	-$(RM) $(MAIN).pdf $(DRAFT_NAME).pdf $(PRODUCTION_NAME).pdf
ifeq ($(OS),Windows_NT)
    RM = del /Q /F
    FixPath = $(subst /,\,$1)
    PYTHON = python
    FOREACH = for %%f in ($(subst /,\,$(PY))/*.py) do $(PYTHON) %%f
else
    RM = rm -f
    FixPath = $1
    PYTHON = python3
    FOREACH = for file in $(PY)/*.py; do $(PYTHON) $$file; done
endif

MAIN = main
PY = src

all: 
	$(MAKE) build
	$(MAKE) clean

build:
	pdflatex $(MAIN).tex
	pdflatex $(MAIN).tex

clean:
	-$(RM) *.aux *.log *.out *.toc
	-$(RM) $(call FixPath,chapters/*.aux chapters/*.log appendices/*.aux appendices/*.log)

cleanall: 
	clean
	-$(RM) $(MAIN).pdf

py:
	$(FOREACH)
	$(MAKE) build
	$(MAKE) clean

production:
	$(FOREACH)
	pdflatex "\def\draft{0} \input{$(MAIN).tex}"
	pdflatex "\def\draft{0} \input{$(MAIN).tex}"
	$(MAKE) clean
# Building the Project

## Linux and macOS

### 1. Clone the repository

```bash
git clone <repository-url>
cd <repository-name>
```

### 2. Install LaTeX dependencies

Make sure you have a working LaTeX distribution installed, such as:

- TeX Live
- MacTeX
- MiKTeX

The build system also requires `latexmk` for the optimized compilation workflow provided by the Makefile.

Depending on your LaTeX distribution, you may also need to install additional packages.

### 3. Create a Python virtual environment (optional but recommended)

```bash
python -m venv venv
source venv/bin/activate
```

### 4. Install the Python package and dependencies

```bash
pip install .
```

### 5. Build the PDF document

Run:

```bash
make
```

This command automatically:

- executes the required Python scripts
- generates figures and tables
- compiles the LaTeX sources
- and produces the final PDF document

To speed up the build process using multiple CPU cores, you can run:

```bash
make -j
```

For additional targets and advanced usage, refer to the comments inside the `Makefile`.

---

## Manual (Brute-Force) Compilation

If you prefer not to use the Makefile, follow the previous instructions up to step 4, then proceed manually.

### 1. Run the required Python scripts

The scripts used to generate figures, tables, and auxiliary data are located in the `scripts/` directory.

For example:

```bash
python scripts/*.py
```

Make sure to execute all scripts required by the document.

### 2. Compile the LaTeX document manually

Compile the main document file (you can also do this from an IDE like TeXstudio or Overleaf):

```bash
pdflatex analisi_statistica_dei_dati.tex
```

You may need to run the command multiple times to correctly resolve references, citations, and indexes.

---

## Warning

Manual compilation is significantly less efficient than using the provided Makefile.

In particular:

- compilation may take longer
- auxiliary files may clutter the project directory
- and multiple compilation passes may be required

For these reasons, using the Makefile-based workflow is strongly recommended.

# Preface:

These notes are intended to be a comprehensive introduction to the field of statistical data analysis, covering both theoretical foundations and practical applications through examples, exercises, and tests. 

The material is organized into chapters that follow the _Analisi statistica dei dati_ course at the univeristy of Pisa, followed by the authors during the 2024-2026 academic years, and held by professors _Paolo Francavilla_, _Andrea Carlo Marini_ and _Giovanni Punzi_. 

For this reason, the text will follow their lecture notes very closely, and many of the formulations, examples, and concepts are taken directly from those sources, for which we thank the professors. It is by no means an exhaustive treatment, but we hope to leave the readers with a solid understanding of the core concepts and techniques in statistical data analysis, as well as the ability to apply them to exam-style problems. 

As the authors are themselves approaching this complex field, there will surely be some errors and inconsistencies in this text. any errors, typos, or suggestions for improvement are very welcome. Please feel free to add a pull request or reach out to us directly via email. 

These notes will therefore most likely evolve with time, and hopefully will be ever-changing until they converge to something readable. To quote a wise man and a mentor: **"do not print it! :-)"**

We wish you the best of luck in your studies!

---

**Michelangelo and Jacopo**


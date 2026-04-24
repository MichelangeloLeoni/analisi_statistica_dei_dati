'''Utilities for the Analisi Statistica dei Dati notes.'''
import matplotlib

def pgf_generator(**kwargs):
    '''
    Generates a matplotlib figure and axis with PGF settings for LaTeX integration.
    
    Parameters:
        **kwargs: Keyword arguments to pass to plt.subplots() for figure and axis creation.
    '''

    matplotlib.use("pgf")
    matplotlib.rcParams.update({
        "pgf.texsystem": "pdflatex",
        "text.usetex": True,
        "pgf.rcfonts": False,
        "font.family": "serif", 
        "font.size": 10,  
        "pgf.preamble": r"""
            \usepackage{amsmath}
            \usepackage{mathrsfs}
        """
    })

    return matplotlib.pyplot.subplots(**kwargs)

def table_generator(n_columns: int, labels: tuple, content: tuple, output_file_name: str):
    '''
    Generates a LaTeX table and writes it to a file. At the moment the content is expected to be 
    already formatted as LaTeX math mode strings, but this can be extended in the future to allow
    for more flexible content formatting.

    Parameters:
        n_columns: Number of columns in the table.
        labels: Tuple of column labels.
            e.g. ("$n$", "Wilks", "Feldman-Cousins", "Central interval")
        content: Tuple of numpy arrays or lists, each containing the content for a column.
            e.g. (n_table, wilks_intervals, lr_intervals, central_intervals)
        output_file_name: Name of the output .tex file to write the table to.
    '''

    table = r"""
    \begin{center}
    \begin{tabular}{|""" + "c|"*n_columns + r"""}
    \hline
    """

    for i, label in enumerate(labels):
        table += f" {label} "
        if i < n_columns - 1:
            table += "& "

    table += r"""\\
    \hline
    """

    for i in range(len(content[0])):
        for j, col in enumerate(content):
            table += f" {col[i]} "
            if j < n_columns - 1:
                table += "& "
        table += r"""\\
            \hline
            """

    table += r"""
    \end{tabular}
    \end{center}
    """

    with open(f"tables/{output_file_name}", "w", encoding="utf-8") as f:
        f.write(table)

def code_snippet_generator():
    pass

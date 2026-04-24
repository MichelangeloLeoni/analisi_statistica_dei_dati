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

def code_snippet_generator():
    pass

def table_generator():
    pass

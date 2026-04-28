"""
Script to settle a quasi-philosophical argument between M.L and J.O.

For a binomial distribution, do the "implicit" (tail inversion)
and "explicit" (Neyman belt with central ordering) methods coincide?
"""

import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import binom
from scipy.optimize import root_scalar

from asd.interval_estimation import interval as asdinterval

# =========================
# Parameters
# =========================
N = 20
ALPHA = 0.05
CL = 1 - ALPHA


# =========================
# Implicit (Clopper-Pearson)
# =========================
def calculate_central_interval_mu(n_obs, cl=CL):
    """
    Central confidence interval via tail inversion (Clopper-Pearson).

    Parameters
    ----------
    n_obs : int
        Observed number of successes
    cl : float
        Confidence level

    Returns
    -------
    (low, high)
    """
    alpha = 1 - cl

    # ---- Lower bound ----
    if n_obs == 0:
        low = 0.0
    else:
        def f_low(p):
            return (1 - binom.cdf(n_obs - 1, N, p)) - alpha / 2

        low = root_scalar(
            f_low,
            bracket=[1e-12, 1 - 1e-12],
            method="bisect"
        ).root

    # ---- Upper bound ----
    if n_obs == N:
        high = 1.0
    else:
        def f_high(p):
            return binom.cdf(n_obs, N, p) - alpha / 2

        high = root_scalar(
            f_high,
            bracket=[1e-12, 1 - 1e-12],
            method="bisect"
        ).root

    return (low, high)


# =========================
# Binomial model
# =========================
def binomial(x, p):
    """Binomial PMF wrapper"""
    return binom.pmf(x, N, p)


# =========================
# Explicit Neyman belt
# =========================
estimator = asdinterval.IntervalEstimator(
    prob_func=binomial,
    cl=CL,
    x_range=np.arange(0, N + 1),
    mu_grid=np.linspace(0, 1, 200)
)


# =========================
# Compute intervals
# =========================
n_obs = np.arange(0, N + 1)

intervals_expl = []
intervals_imp = []

for n in n_obs:
    # Explicit (Neyman belt)
    intervals_expl.append(
        estimator.neyman.find_interval(
            n,
            method="pdf",
            ordering_type="central"
        )
    )

    # Implicit (tail inversion)
    intervals_imp.append(
        calculate_central_interval_mu(n, cl=CL)
    )


# =========================
# Print comparison
# =========================
print("\nComparison explicit vs implicit:\n")

for n, (e, i) in enumerate(zip(intervals_expl, intervals_imp)):
    print(
        f"n = {n:2d} | "
        f"expl = ({e[0]:.5f}, {e[1]:.5f}) | "
        f"impl = ({i[0]:.5f}, {i[1]:.5f}) | "
        f"diff = ({e[0]-i[0]:+.2e}, {e[1]-i[1]:+.2e})"
    )


# =========================
# Plot comparison
# =========================
expl_low = [e[0] for e in intervals_expl]
expl_high = [e[1] for e in intervals_expl]

imp_low = [i[0] for i in intervals_imp]
imp_high = [i[1] for i in intervals_imp]

plt.figure(figsize=(8, 5))

plt.plot(n_obs, expl_low, label="Explicit low", linestyle="--")
plt.plot(n_obs, expl_high, label="Explicit high", linestyle="--")

plt.plot(n_obs, imp_low, label="Implicit low")
plt.plot(n_obs, imp_high, label="Implicit high")

plt.xlabel("Observed counts n")
plt.ylabel("p interval")
plt.title("Binomial central intervals: explicit vs implicit")

plt.legend()
plt.grid(True)
plt.tight_layout()
plt.show()

'''
Deepseek take on the matter:

Ottima domanda! La risposta breve è: **No, non c'è una vera distinzione — sono due facce della stessa medaglia, ma con sfumature computazionali diverse.**

Analizziamo il tuo script e la teoria sottostante.

## Cosa mostrano i risultati

Se esegui lo script, vedrai che le differenze tra i due metodi sono dell'ordine di `1e-16` — puro rumore numerico. Questo non è un caso: **per una distribuzione binomiale con ordinamento centrale, il metodo "implicito" (Clopper-Pearson) e il metodo "esplicito" (cintura di Neyman con ordinamento centrale) sono matematicamente identici.**

## Perché sono equivalenti

Il punto cruciale è la scelta dell'**ordinamento centrale** (`ordering_type="central"`).

1. **Metodo esplicito (Neyman belt)**:
   - Costruisci la cintura di Neyman nello spazio `(p, x)`
   - Per ogni `p`, selezioni un intervallo `[x₁(p), x₂(p)]` tale che `P(x ∈ [x₁, x₂] | p) = CL`
   - Con ordinamento centrale, prendi le code simmetricamente: `α/2` a sinistra e `α/2` a destra
   - Poi "inverti" la cintura: per ogni `x` osservato, l'intervallo di confidenza è l'insieme dei `p` per cui `x` cade nell'intervallo di accettazione

2. **Metodo implicito (tail inversion / Clopper-Pearson)**:
   - Per un `x` osservato, risolvi direttamente:
     - `P(X ≥ x | p_low) = α/2`
     - `P(X ≤ x | p_high) = α/2`
   - L'intervallo è `[p_low, p_high]`

3. **L'equivalenza**:
   - Con l'ordinamento centrale, la cintura di Neyman seleziona esattamente le code simmetriche
   - Il processo di inversione della cintura produce esattamente gli stessi valori di `p` che soddisfano le equazioni di coda del metodo implicito
   - È una conseguenza del teorema della probabilità integrale: i due approcci sono duali

## La "vera" distinzione

La distinzione **non** è tra "implicito" ed "esplicito" in senso assoluto, ma tra **diversi tipi di ordinamento nella cintura di Neyman**:

- **Ordinamento centrale**: code simmetriche → Clopper-Pearson
- **Ordinamento per likelihood ratio**: intervalli più stretti ma non simmetrici nelle code
- **Ordinamento minimax**: minimizza la lunghezza massima

Il metodo implicito (tail inversion) **può essere generalizzato a qualsiasi ordinamento** — non è esclusivo dell'ordinamento centrale. Infatti, il Clopper-Pearson è solo un caso particolare di tail inversion con ordinamento centrale.

## Sfumature computazionali

Nel tuo script:
- **Implicito**: Risolvi equazioni di coda per ogni `n` osservato (2N equazioni totali)
- **Esplicito**: Costruisci l'intera cintura Neyman (N×M operazioni) e poi la inverti

Il metodo esplicito è computazionalmente più pesante ma concettualmente più trasparente: costruisci prima tutti gli intervalli di accettazione e poi li inverti. Il metodo implicito è più diretto ma nasconde la struttura duale.

## Conclusione

La vera distinzione filosofica è tra:
- **Metodi di inversione di test** (come il tuo "implicito"), che partono dallo spazio di osservazione
- **Metodi di cintura di confidenza** (come il tuo "esplicito"), che partono dallo spazio dei parametri

Ma per l'**ordinamento centrale**, convergono esattamente. La distinzione diventa rilevante solo quando cambi il criterio di ordinamento — e lì emergono differenze reali negli intervalli risultanti.

Quindi M.L. e J.O. hanno entrambi ragione: stanno guardando lo stesso oggetto matematico da due prospettive diverse!
'''

'''
Useful links:
https://www.statisticshowto.com/clopper-pearson-exact-method/
https://www.statisticshowto.com/binomial-confidence-interval/
'''
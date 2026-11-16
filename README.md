# Pricing d’options européennes

Projet personnel pour comparer Black–Scholes et Monte Carlo, puis calculer et valider les grecques. Le code et les résultats seront ajoutés progressivement.

## Structure

```text
option-pricing/
├── README.md
├── requirements.txt
├── src/
│   └── option_pricing/
├── notebooks/
├── figures/
└── tests/
```

## Installation

```bash
python -m venv .venv
source .venv/bin/activate  # Windows : .venv\Scripts\activate
python -m pip install -r requirements.txt
PYTHONPATH=src python -m option_pricing.gui
```

L’interface PyQt5 permet de saisir les paramètres, de choisir call/put et Black–Scholes/Monte Carlo, puis d’afficher le premium, l’intervalle de confiance Monte Carlo et les grecques Black–Scholes. Sur macOS, double-cliquer sur `Lancer le pricer.command` pour ouvrir l’application.

## État du projet

- [x] Black–Scholes : code et tests
- [x] Monte Carlo : prix et intervalle de confiance
- [x] Convergence : RMSE, pente log-log et figure
- [x] Grecques et différences finies
- [x] Analyse paramétrique : spot, volatilité, maturité et payoff à l’échéance
- [x] Interface PyQt5
- [ ] Bonus technique : antithétiques, variable de contrôle, option asiatique
- [ ] Notebook d’analyse

Les figures disponibles sont `figures/convergence.png` et `figures/parametric_study.png`. Le notebook d’analyse, le bonus Monte Carlo et la ligne de CV restent à réaliser. Projet développé avec assistance IA.

# SMA E-commerce avec Mesa

Ce projet implemente un systeme multi-agents (SMA) pour la recommandation e-commerce en Python avec Mesa.

## Contenu

- `sma_system/model.py` : environnement partage (Model Mesa), bus de messages, cycle par tick.
- `sma_system/agents.py` : agents autonomes avec phases `perceive -> decide -> act`.
- `run_simulation.py` : simulation console (logs + metriques).
- `app.py` : visualisation navigateur avec Solara.

## Agents

- AgentProfiling
- AgentRecommendation
- AgentMarketing
- AgentArbitre
- AgentFeedback

## Propriete SMA garanties

- Pas de pipeline sequentiel.
- Tous les agents tournent par phases sur chaque tick.
- Perception locale et decision locale.
- Communication via message bus + environnement partage.
- Cooperation et competition (Recommendation vs Marketing, arbitre).

## Installation

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

Si vous utilisez le Python global au lieu d'activer l'env :

```powershell
c:/Users/nourg/Desktop/sma/.venv/Scripts/python.exe -m pip install -r requirements.txt
```

## Execution simulation (CLI)

```powershell
c:/Users/nourg/Desktop/sma/.venv/Scripts/python.exe run_simulation.py
```

## Execution visualisation web (navigateur)

```powershell
c:/Users/nourg/Desktop/sma/.venv/Scripts/python.exe -m solara run app.py --host 127.0.0.1 --port 8765
```

Puis ouvrir : http://127.0.0.1:8765

## Metriques incluses

- CTR
- Conversion
- Satisfaction moyenne
- Diversite

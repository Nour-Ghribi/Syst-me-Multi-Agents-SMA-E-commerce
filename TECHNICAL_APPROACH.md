# ⚙️ Approche Technique – Système Multi-Agents (SMA) E-commerce

---

## 1. Introduction technique

Ce document décrit l’implémentation technique de notre système multi-agents pour la recommandation e-commerce.

L’objectif est de concevoir une architecture :
- modulaire
- distribuée
- évolutive
- conforme aux principes des systèmes multi-agents (SMA)

---

## 2. Choix technologiques

### 🐍 Langage : Python

Python a été choisi pour :
- sa simplicité et lisibilité
- son écosystème riche en data science
- sa compatibilité avec Mesa

---

### 🤖 Framework SMA : Mesa

Nous avons utilisé **Mesa**, un framework Python dédié à la simulation de systèmes multi-agents.

#### Pourquoi Mesa ?

Mesa permet :

- la création d’agents autonomes
- la simulation par cycles (ticks)
- la gestion d’un environnement partagé
- la séparation claire entre modèle et agents
- l’intégration facile avec des outils de visualisation

👉 Mesa est particulièrement adapté aux SMA car il reproduit :
- perception locale
- décision locale
- interaction entre agents
- comportement émergent

---

### 🌐 Visualisation : Solara

Nous utilisons **Solara** pour :
- afficher les métriques en temps réel
- créer un dashboard web
- interagir avec la simulation

---

## 3. Architecture technique du système

Le système est structuré en plusieurs fichiers :

### 📁 agents.py
Contient la définition des agents :
- AgentProfiling
- AgentRecommendation
- AgentMarketing
- AgentArbitre
- AgentFeedback

Chaque agent implémente :
- perception()
- decision()
- action()

---

### 📁 model.py

Contient le modèle principal (hérite de Mesa Model) :

- environnement partagé
- données utilisateurs et produits
- gestion des messages
- simulation des interactions utilisateur
- calcul des métriques

---

### 📁 run_simulation.py

Permet de lancer la simulation en CLI :

- exécution des ticks
- affichage des résultats
- suivi des métriques

---

### 📁 app.py

Interface web (Solara) :

- affichage des métriques
- visualisation des recommandations
- interaction avec la simulation

---

## 4. Fonctionnement du système

Le système fonctionne selon un modèle de simulation par cycles :

### 🔁 Cycle (Tick)

À chaque tick :

1. Tous les agents perçoivent leur environnement
2. Tous les agents prennent des décisions
3. Tous les agents agissent
4. L’environnement est mis à jour
5. L’utilisateur simulé interagit (clic / achat)

👉 Aucun ordre fixe entre agents  
👉 Pas de dépendance séquentielle  

---

## 5. Gestion des agents

Chaque agent est défini comme une entité autonome avec :

- un état interne
- une perception locale
- une logique de décision
- une action sur l’environnement

### Exemple :

AgentRecommendation :
- lit le profil utilisateur
- calcule un score pour chaque produit
- génère une liste de recommandations

---

## 6. Communication entre agents

La communication est implémentée via :

### 1. Environnement partagé
Les agents lisent et écrivent dans des structures communes :

```python
model.user_profiles
model.recommendations
model.promotions
model.feedback
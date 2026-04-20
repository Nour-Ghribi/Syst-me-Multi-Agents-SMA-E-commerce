# 📘 Système Multi-Agents pour Recommandation E-commerce Intelligente

---

## 1. Introduction

Dans le domaine du e-commerce, proposer des recommandations pertinentes aux utilisateurs est un défi complexe, car il implique l’analyse de données dynamiques, des préférences utilisateurs et des contraintes commerciales.

Dans notre première approche, le système était organisé sous forme de **pipeline séquentiel**. Cependant, cette structure ne respecte pas les principes des systèmes multi-agents (SMA).

Nous avons donc transformé notre architecture en un **système multi-agents (SMA)** où plusieurs agents autonomes interagissent dans un environnement partagé afin de produire des recommandations intelligentes et adaptatives.

---

## 2. Objectif du système

L’objectif du système est de :

- Analyser le comportement utilisateur
- Générer des recommandations personnalisées
- Intégrer des contraintes business (promotions, stock…)
- S’adapter dynamiquement aux interactions utilisateur

---

## 3. Environnement du système

Le système repose sur un **environnement e-commerce partagé**, contenant :

- Profils utilisateurs
- Catalogue de produits
- Promotions et campagnes marketing
- Historique des clics et achats
- Interactions utilisateur

⚠️ Aucun agent ne possède une vision globale complète de cet environnement.

---

## 4. Architecture du système multi-agents

Le système est composé de plusieurs agents autonomes fonctionnant selon un cycle :

👉 **Perception → Décision → Action (tick)**

À chaque tick :
1. Les agents perçoivent leur environnement local
2. Ils prennent des décisions indépendantes
3. Ils agissent
4. Ils communiquent entre eux
5. Le système évolue

✔ Aucun ordre séquentiel fixe  
✔ Pas de pipeline  
✔ Exécution parallèle des agents  

---

## 5. Types d’agents

### 5.1 Agent Profiling

**Perception :**
- Historique d’achat
- Clics récents
- Navigation utilisateur

**Décision :**
- Mise à jour du profil utilisateur
- Détection des préférences

**Action :**
- Mise à jour du profil dans l’environnement

**Communication :**
- Envoie des mises à jour aux autres agents

---

### 5.2 Agent Recommandation

**Perception :**
- Profil utilisateur
- Catalogue produit
- Disponibilité

**Décision :**
- Sélection des produits pertinents
- Calcul de scores

**Action :**
- Génération de recommandations

**Communication :**
- Envoie les résultats à Marketing

---

### 5.3 Agent Marketing

**Perception :**
- Recommandations
- Promotions
- Marges et stock

**Décision :**
- Priorisation des produits
- Mise en avant

**Action :**
- Ajustement du ranking final

**Communication :**
- Influence les choix de Recommendation

---

### 5.4 Agent Feedback

**Perception :**
- Clics
- Achats
- Temps d’interaction

**Décision :**
- Évaluation de performance

**Action :**
- Mise à jour des signaux d’apprentissage

**Communication :**
- Envoie feedback aux autres agents

---

### 5.5 Agent Arbitre

**Rôle :**
- Résoudre les conflits entre Recommendation et Marketing

**Décision :**
- Choisir le compromis optimal entre pertinence et rentabilité

---

## 6. Communication entre agents

Les agents communiquent via :

- Messages directs
- Environnement partagé

### Exemples :
- Profiling → Recommendation : mise à jour du profil
- Recommendation → Marketing : liste produits
- Marketing → Recommendation : priorité promotionnelle
- Feedback → tous : ajustement

✔ Communication bidirectionnelle  
✔ Pas de flux unique  

---

## 7. Coopération et compétition

### 🤝 Coopération
- Les agents collaborent pour améliorer :
  - la pertinence
  - l’expérience utilisateur
  - le taux de conversion

### ⚔️ Compétition
- Recommendation → maximise pertinence utilisateur
- Marketing → maximise rentabilité

👉 L’agent Arbitre résout ce conflit

---

## 8. Fonctionnement global

À chaque tick :

1. Les agents perçoivent
2. Les agents décident
3. Les agents agissent
4. L’utilisateur est simulé (clic / achat)
5. Le feedback est généré
6. Le système s’améliore

---

## 9. Simulation utilisateur

Les interactions utilisateur sont simulées avec des probabilités :

- Clic → dépend de la pertinence + promotion
- Achat → dépend du prix + intérêt utilisateur

👉 Cela permet de tester le système sans données réelles.

---

## 10. Métriques du système

Le système mesure :

- **CTR** (Click Through Rate)
- **Conversion rate**
- **Satisfaction**
- **Diversity**

Ces métriques évoluent à chaque tick.

---

## 11. Implémentation technique

- Langage : Python
- Framework SMA : Mesa
- Simulation : CLI (run_simulation.py)
- Visualisation : Solara (app.py)

---

## 12. Exécution du projet

### ▶️ Simulation CLI

```bash
python run_simulation.py
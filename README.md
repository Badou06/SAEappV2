# Comparateur de villes françaises

**SAE Outils Décisionnels – BUT Science des Données (parcours VCOD)**  
**Année 2024-2025 – 3ème année**

---

## 🎯 Objectif

Développer une interface web permettant de comparer deux villes françaises de plus de 20 000 habitants sur différents critères :
- Données générales (population, région, département)
- Emploi (taux de chômage localisé)
- Logement (loyers et prix d'achat au m²)
- Météo (normales climatiques + prévisions 7 jours)
- Culture (musées, cinémas, salles de sport)
- Formation (nombre d'étudiants)

---

## 📁 Structure du projet

```
.
├── app.py                      # Application Streamlit (point d'entrée)
├── build_data.py               # Script de génération du CSV (à lancer 1 fois)
├── requirements.txt            # Dépendances Python
├── data/
│   ├── villes.csv              # Fichier généré par build_data.py
│   └── raw/                    # Fichiers sources exportés manuellement
│       ├── population_insee_2020.csv
│       ├── geo_simplifie.csv
│       ├── chomage_insee_2023.csv
│       ├── loyers_olap_2024.csv
│       ├── prix_achat_2024.csv
│       ├── meteo_normales.csv
│       ├── etudiants_mesr_2023.csv
│       └── equipements_bpe_2022.csv
```

---

## 🚀 Installation et lancement

### 1. Cloner / copier le projet

```bash
cd comparateur-villes
```

### 2. Créer un environnement virtuel (recommandé)

```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Mac / Linux
source venv/bin/activate
```

### 3. Installer les dépendances

```bash
pip install -r requirements.txt
```

### 4. Générer la base de données

```bash
python build_data.py
```

Ce script va :
- Essayer de télécharger les populations INSEE automatiquement
- Lire les fichiers sources dans `data/raw/`
- Les fusionner et nettoyer
- Générer `data/villes.csv`

> **Note** : si le téléchargement INSEE échoue (timeout, site en maintenance...), le script utilise automatiquement le fichier `data/raw/population_insee_2020.csv` que j'ai préparé au cas où.

### 5. Lancer l'application Streamlit

```bash
streamlit run app.py
```

L'application s'ouvre automatiquement dans le navigateur à l'adresse `http://localhost:8501`.

---

## 🖥️ Comment utiliser l'interface

1. **Choisir les villes** dans la barre latérale gauche (deux menus déroulants)
2. **Naviguer entre les onglets** en haut de la page :
   - 🏙️ **Général** : carte d'identité + graphique radar global
   - 💼 **Emploi** : taux de chômage avec seuil national
   - 🏠 **Logement** : loyers, prix d'achat, simulateur de budget interactif
   - ☀️ **Météo** : courbes de température, précipitations, prévisions 7 jours
   - 🎭 **Culture** : équipements + ratio par habitant + carte
   - 🎓 **Formation** : nombre d'étudiants et ratio / 1000 hab
3. **Changer de ville** à tout moment : tous les graphiques se mettent à jour instantanément

---

## 📊 Sources de données

| Donnée | Source | Récupération |
|--------|--------|--------------|
| Population | INSEE – Populations légales 2020 | Téléchargement auto (fallback manuel) |
| Région/Département | COG INSEE 2023 | Export manuel simplifié |
| Chômage | INSEE – TCL zones d'emploi 2023 | Export Excel INSEE |
| Loyers | OLAP – Observatoire Local des Loyers 2024 | Export PDF/Excel |
| Prix achat | DVF / MeilleursAgents T3 2024 | Agrégation manuelle |
| Météo (normales) | Météo France – Normales 1991-2020 | Export meteo.data.gouv.fr |
| Météo (7 jours) | Open-Meteo API | Appel API direct dans `app.py` |
| Équipements | BPE INSEE 2022 | Export data.gouv.fr |
| Étudiants | MESR – SISE 2023-24 | Export data.enseignementsup |

---

## 🛠️ Choix techniques

- **Streamlit** : choisi car on connaît bien Python en BUT SD, pas besoin de gérer du HTML/JS, déploiement simple sur Streamlit Cloud
- **Plotly** : graphiques interactifs (hover, zoom) plus sympas que matplotlib pour une appli web
- **Pandas** : manipulation des données (merge, filtre, groupby)
- **Requests** : appel à l'API Open-Meteo pour la météo en temps réel

---

## 🌐 Déploiement en ligne (optionnel)

L'application peut être déployée gratuitement sur [Streamlit Community Cloud](https://share.streamlit.io) :

1. Pousser le projet sur GitHub
2. Se connecter sur share.streamlit.io avec son compte GitHub
3. Sélectionner le repo et indiquer `app.py` comme fichier principal
4. Cliquer sur **Deploy**

---

## 📝 Auteurs

- [Riade EL ATTAR]
- [Baye-Badou Dieng]
- [Rakib Buyhan]

**Enseignant responsable** : [Mr. Jollois]  
**IUT – Département Science des Données – Parcours VCOD**

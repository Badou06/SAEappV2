"""
build_data.py
Script de collecte et fusion des données pour le comparateur de villes
SAE Outils Décisionnels - BUT SD VCOD

Sources utilisées :
- INSEE Populations légales 2020 : https://www.insee.fr/fr/statistiques/6683037
- COG INSEE 2023 : https://www.insee.fr/fr/information/2560452 (export manuel)
- INSEE TCL Chômage 2023 : https://www.insee.fr/fr/statistiques/1893230 (export Excel)
- OLAP Loyers 2024 : https://www.observatoire-des-loyers.fr (export PDF/Excel)
- MeilleursAgents / DVF 2024 : https://www.data.gouv.fr/datasets/demandes-de-valeurs-foncieres
- Météo France normales 1991-2020 : https://meteo.data.gouv.fr
- BPE INSEE 2022 : https://www.data.gouv.fr/datasets/base-permanente-des-equipements-1
- MESR SISE 2023-24 : https://data.enseignementsup-recherche.gouv.fr

Pour lancer : python build_data.py
Ça génère data/villes.csv utilisé par l'appli Streamlit.
"""

import pandas as pd
import requests
import io
import zipfile
import os

# ---------------------------------------------------------
# CONFIG
# ---------------------------------------------------------
os.makedirs("data/raw", exist_ok=True)

print("=" * 60)
print("BUILD DATA - SAE Outils Décisionnels")
print("=" * 60)

# ---------------------------------------------------------
# ETAPE 1 : Population INSEE 2020
# On tente de télécharger directement depuis le site INSEE
# Si ça plante (URL qui change, site en maintenance...), 
# on utilise le fichier qu'on a téléchargé manuellement.
# ---------------------------------------------------------
print("\n[1/7] Récupération des populations légales INSEE 2020...")

url_insee = "https://www.insee.fr/fr/statistiques/fichier/6683037/ensemble_2020.zip"
df_pop = None

try:
    r = requests.get(url_insee, timeout=30)
    r.raise_for_status()

    with zipfile.ZipFile(io.BytesIO(r.content)) as z:
        # Le CSV dans le zip porte un nom du type ensemble_2020.csv
        fichiers_csv = [f for f in z.namelist() if f.endswith(".csv")]
        if len(fichiers_csv) == 0:
            raise Exception("Pas de CSV trouvé dans le zip INSEE")

        with z.open(fichiers_csv[0]) as f:
            df_pop = pd.read_csv(f, sep=";", encoding="latin1", dtype=str)

    # On garde les colonnes utiles
    df_pop = df_pop[["CODGEO", "LIBGEO", "PMUN"]].copy()
    df_pop.columns = ["code_commune", "ville", "population"]
    df_pop["population"] = pd.to_numeric(df_pop["population"], errors="coerce")

    # On filtre les communes de plus de 20 000 habitants (contrainte SAE)
    df_pop = df_pop[df_pop["population"] >= 20000].copy()
    df_pop = df_pop.sort_values("ville").reset_index(drop=True)

    print(f"   OK -> {len(df_pop)} communes récupérées depuis l'URL INSEE")

except Exception as e:
    print(f"   ERREUR : {e}")
    print("   -> Fallback sur le fichier data/raw/population_insee_2020.csv")
    print("   (j'avais téléchargé le zip à la main au cas où)")
    df_pop = pd.read_csv("data/raw/population_insee_2020.csv", dtype=str)
    df_pop["population"] = pd.to_numeric(df_pop["population"], errors="coerce")

# ---------------------------------------------------------
# ETAPE 2 : Géographie (département + région)
# J'ai exporté ça depuis le fichier COG INSEE 2023 sur Excel
# car il y avait trop de colonnes inutiles.
# ---------------------------------------------------------
print("\n[2/7] Chargement du référentiel géographique...")

df_geo = pd.read_csv("data/raw/geo_simplifie.csv")
print(f"   OK -> {len(df_geo)} villes dans le référentiel geo")

# ---------------------------------------------------------
# ETAPE 3 : Taux de chômage INSEE 2023
# Exporté depuis l'Excel "Taux de chômage localisés" sur insee.fr
# Attention : c'est par zone d'emploi, pas par commune exacte.
# ---------------------------------------------------------
print("\n[3/7] Chargement des taux de chômage...")

df_chom = pd.read_csv("data/raw/chomage_insee_2023.csv")
print(f"   OK -> taux de chômage chargés")

# ---------------------------------------------------------
# ETAPE 4 : Logement (loyers + prix achat)
# Loyers : export OLAP 2024 (observatoire-des-loyers.fr)
# Prix achat : agrégation DVF / MeilleursAgents T3 2024
# ---------------------------------------------------------
print("\n[4/7] Chargement des données logement...")

df_loy = pd.read_csv("data/raw/loyers_olap_2024.csv")
df_prix = pd.read_csv("data/raw/prix_achat_2024.csv")
print(f"   OK -> loyers et prix d'achat chargés")

# ---------------------------------------------------------
# ETAPE 5 : Météo (normales 1991-2020)
# Exporté depuis meteo.data.gouv.fr (fiches par station)
# J'ai pris la station la plus proche de chaque ville.
# ---------------------------------------------------------
print("\n[5/7] Chargement des données météo...")

df_meteo = pd.read_csv("data/raw/meteo_normales.csv")
print(f"   OK -> données climatiques chargées")

# ---------------------------------------------------------
# ETAPE 6 : Formation supérieure (MESR SISE 2023-24)
# Exporté depuis data.enseignementsup-recherche.gouv.fr
# ---------------------------------------------------------
print("\n[6/7] Chargement des effectifs étudiants...")

df_etu = pd.read_csv("data/raw/etudiants_mesr_2023.csv")
print(f"   OK -> effectifs étudiants chargés")

# ---------------------------------------------------------
# ETAPE 7 : Équipements culturels et sportifs (BPE INSEE 2022)
# Exporté depuis data.gouv.fr (base permanente des équipements)
# J'ai filtré sur les codes : C201=musée, C104=cinéma, F101=salle de sport
# ---------------------------------------------------------
print("\n[7/7] Chargement des équipements BPE...")

df_equip = pd.read_csv("data/raw/equipements_bpe_2022.csv")
print(f"   OK -> équipements chargés")

# ---------------------------------------------------------
# FUSION DE TOUTES LES SOURCES
# On fait des merge successifs sur le nom de la ville.
# ---------------------------------------------------------
print("\n[*] Fusion des sources...")

df_final = df_pop.merge(df_geo, on="ville", how="left")
df_final = df_final.merge(df_chom, on="ville", how="left")
df_final = df_final.merge(df_loy, on="ville", how="left")
df_final = df_final.merge(df_prix, on="ville", how="left")
df_final = df_final.merge(df_meteo, on="ville", how="left")
df_final = df_final.merge(df_etu, on="ville", how="left")
df_final = df_final.merge(df_equip, on="ville", how="left")

# ---------------------------------------------------------
# NETTOYAGE FINAL
# On vérifie qu'il n'y a pas de trous, sinon on met des valeurs par défaut.
# ---------------------------------------------------------
print(f"\n[*] Nettoyage final ({len(df_final)} villes, {len(df_final.columns)} colonnes)")

# Si une ville n'a pas de taux de chômage, on met la moyenne nationale (~9.5%)
df_final["taux_chomage"] = df_final["taux_chomage"].fillna(9.5)

# Idem pour les loyers (11€/m² = médiane France)
df_final["loyer_m2"] = df_final["loyer_m2"].fillna(11.0)

# Prix achat par défaut
df_final["prix_achat_m2"] = df_final["prix_achat_m2"].fillna(2200)

# Réordonner les colonnes pour que ce soit plus lisible
cols_order = [
    "code_commune", "ville", "population", "departement", "region",
    "loyer_m2", "prix_achat_m2", "taux_chomage",
    "temp_jan", "temp_jul", "precipitations_mm", "ensoleillement_h", "lat", "lon",
    "musees", "cinemas", "salles_sport", "etudiants"
]
df_final = df_final[cols_order]

# Export CSV final
df_final.to_csv("data/villes.csv", index=False, encoding="utf-8")

print("\n" + "=" * 60)
print("FICHIER data/villes.csv GÉNÉRÉ AVEC SUCCÈS")
print("=" * 60)
print(f"\n{len(df_final)} villes | {len(df_final.columns)} colonnes")
print("\nColonnes :", list(df_final.columns))

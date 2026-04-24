# =============================================================
# CITY FIGHTING - PLATEFORME D'AIDE À LA DÉCISION URBAINE
# VERSION ULTIME FINALE (V11.2) - FULL MASTER SD 2026
# =============================================================

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px

# 1. CONFIGURATION DE LA PAGE
st.set_page_config(
    page_title="City Fighting | Intelligence Urbaine",
    page_icon="🏙️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 2. DESIGN SYSTEM COMPLET (CSS PREMIUM)
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;600;800&display=swap');

    :root {
        --color-alpha: #6366F1;
        --color-beta: #F43F5E;
        --sidebar-bg: #0F172A;
        --bg-main: #F8FAFC;
    }

    html, body, [class*="css"] {
        font-family: 'Plus Jakarta Sans', sans-serif;
        background-color: var(--bg-main);
    }

    /* --- SIDEBAR EXPERT --- */
    [data-testid="stSidebar"] {
        background-color: var(--sidebar-bg);
        border-right: 1px solid rgba(255,255,255,0.1);
    }
    [data-testid="stSidebar"] label {
        color: #F8FAFC !important;
        font-weight: 600 !important;
        text-transform: uppercase;
        font-size: 0.75rem !important;
        letter-spacing: 0.1em;
    }
    [data-testid="stSidebar"] .stMarkdown p, [data-testid="stSidebar"] .stCaption {
        color: #94A3B8 !important;
        font-size: 0.8rem;
    }
    [data-testid="stSidebar"] h2 {
        color: white !important;
        font-weight: 800 !important;
        letter-spacing: 1px;
    }

    /* --- METRICS (BULLES) --- */
    div[data-testid="stMetric"] {
        background: white;
        border: 1px solid #E2E8F0;
        padding: 22px !important;
        border-radius: 16px !important;
        box-shadow: 0 1px 3px rgba(0,0,0,0.02);
    }
    div[data-testid="stMetricValue"] {
        color: #0F172A !important;
        font-weight: 800 !important;
        font-size: 1.7rem !important;
        white-space: nowrap;
    }
    div[data-testid="stMetricLabel"] {
        font-weight: 600 !important;
        color: #64748B !important;
        text-transform: uppercase;
        font-size: 0.75rem !important;
    }

    /* --- COMPOSANTS DE MISE EN PAGE --- */
    .hero-section {
        background: white;
        padding: 2.5rem;
        border-radius: 20px;
        margin-bottom: 2rem;
        border: 1px solid #E2E8F0;
        text-align: center;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
    }
    
    .analysis-box {
        background: #EEF2FF;
        padding: 25px;
        border-radius: 12px;
        border-left: 5px solid var(--color-alpha);
        margin-bottom: 25px;
    }
    .analysis-title {
        margin: 0;
        color: #1E1B4B;
        font-size: 0.9rem;
        font-weight: 800;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }
    .analysis-text {
        color: #3730A3;
        font-size: 0.95rem;
        margin-top: 8px;
        line-height: 1.5;
    }

    .stTabs [data-baseweb="tab-list"] { gap: 20px; }
    .stTabs [data-baseweb="tab"] { font-weight: 600; color: #64748B; }
    .stTabs [aria-selected="true"] { color: var(--color-alpha) !important; border-bottom: 2px solid var(--color-alpha) !important; }

    #MainMenu, footer, header {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# 3. FONCTIONS DE CALCUL & DATA
@st.cache_data
def load_data():
    return pd.read_csv("data/villes.csv", encoding="utf-8")

def calculer_score_attractivite(data):
    s_emploi = (20 - data['taux_chomage']) / 15 * 100
    s_logement = (35 - data['loyer_m2']) / 26 * 100
    s_soleil = (data['ensoleillement_h'] / 2900) * 100
    return round((s_emploi * 0.4) + (s_logement * 0.4) + (s_soleil * 0.2), 1)

def get_radar_chart(d1, d2, v1, v2):
    cat = ['Emploi', 'Logement', 'Soleil', 'Culture', 'Formation']
    def norm(v, vmin, vmax): return min(100, max(0, (v - vmin) / (vmax - vmin) * 100))
    v1_v = [norm(d1['taux_chomage'], 17, 5), norm(d1['loyer_m2'], 30, 9), norm(d1['ensoleillement_h'], 1500, 2900), norm(d1['musees'], 0, 100), norm(d1['etudiants'], 0, 300000)]
    v2_v = [norm(d2['taux_chomage'], 17, 5), norm(d2['loyer_m2'], 30, 9), norm(d2['ensoleillement_h'], 1500, 2900), norm(d2['musees'], 0, 100), norm(d2['etudiants'], 0, 300000)]
    fig = go.Figure()
    fig.add_trace(go.Scatterpolar(r=v1_v, theta=cat, fill='toself', name=v1, line_color='#6366F1'))
    fig.add_trace(go.Scatterpolar(r=v2_v, theta=cat, fill='toself', name=v2, line_color='#F43F5E'))
    fig.update_layout(polar=dict(radialaxis=dict(visible=False, range=[0, 100]), angularaxis=dict(tickfont=dict(size=11, color="#64748B"))), paper_bgcolor='rgba(0,0,0,0)', height=450)
    return fig

# 4. SIDEBAR
df = load_data()
villes_list = sorted(df['ville'].unique())

with st.sidebar:
    st.markdown("## CITY FIGHTING")
    st.markdown("---")
    v1_name = st.selectbox("VILLE RÉFÉRENCE (ALPHA)", villes_list, index=0)
    v2_name = st.selectbox("VILLE COMPARATIF (BETA)", villes_list, index=1)
    
    st.markdown("<br>"*5, unsafe_allow_html=True)
    with st.expander("NOTES MÉTHODOLOGIQUES"):
        st.caption("ANALYSE : Algorithme décisionnel multicritère.")
        st.caption("FILTRE : Communes > 20 000 habitants.")
    
    st.markdown("---")
    st.markdown("<p style='font-weight:700; color:white; font-size:0.7rem; text-transform:uppercase;'>Sources de données</p>", unsafe_allow_html=True)
    st.caption("• INSEE (Population & Chômage 2023)")
    st.caption("• DVF / OLAP (Immobilier 2024)")
    st.caption("• Météo France (Normales 1991-2020)")
    st.caption("• BPE (Équipements Culturels 2022)")
    
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("<p style='font-weight:800;'>MASTER V11.2</p>", unsafe_allow_html=True)
    st.caption("SAE DÉCISIONNELLE BUT SD")

d1 = df[df['ville'] == v1_name].iloc[0]
d2 = df[df['ville'] == v2_name].iloc[0]

# 5. DASHBOARD
st.markdown(f"""
<div class="hero-section">
    <h1 style='margin:0; font-weight:800; font-size:2.8rem;'>
        <span style='color:#6366F1'>{v1_name.upper()}</span> 
        <span style='color:#94A3B8; font-size:1.2rem; margin:0 20px;'>VS</span> 
        <span style='color:#F43F5E'>{v2_name.upper()}</span>
    </h1>
</div>
""", unsafe_allow_html=True)

tabs = st.tabs(["SYNTHÈSE GÉNÉRALE", "ÉCONOMIE", "LOGEMENT", "ENVIRONNEMENT", "CULTURE & SERVICES"])

# --- TAB 1 : SYNTHÈSE ---
with tabs[0]:
    score1, score2 = calculer_score_attractivite(d1), calculer_score_attractivite(d2)
    st.markdown(f"""<div class="analysis-box"><p class="analysis-title">Synthèse Décisionnelle</p><p class="analysis-text">Analyse comparative : <b>{v1_name if score1 > score2 else v2_name}</b> présente l'indice de performance le plus élevé (Score : {max(score1, score2)}/100).</p></div>""", unsafe_allow_html=True)
    
    col_stats, col_radar = st.columns([1.5, 2.5])
    with col_stats:
        st.metric(f"Score {v1_name}", f"{score1}%")
        st.metric(f"Score {v2_name}", f"{score2}%", delta=round(score2-score1, 1))
        st.divider()
        st.metric(f"Habitants {v1_name}", f"{int(d1['population']):,}".replace(',', ' '))
        st.metric(f"Habitants {v2_name}", f"{int(d2['population']):,}".replace(',', ' '))
    with col_radar:
        st.plotly_chart(get_radar_chart(d1, d2, v1_name, v2_name), use_container_width=True)

# --- TAB 2 : ÉCONOMIE ---
with tabs[1]:
    diff_c = round(d1['taux_chomage'] - d2['taux_chomage'], 1)
    st.markdown(f"""<div class="analysis-box"><p class="analysis-title">Analyse de l'Emploi</p><p class="analysis-text">Le marché est plus dynamique à <b>{v1_name if d1['taux_chomage'] < d2['taux_chomage'] else v2_name}</b>.</p></div>""", unsafe_allow_html=True)
    e1, e2, e3 = st.columns(3)
    e1.metric(f"Chômage {v1_name}", f"{d1['taux_chomage']}%")
    e2.metric(f"Chômage {v2_name}", f"{d2['taux_chomage']}%", delta=-diff_c, delta_color="inverse")
    e3.metric("Moyenne Nationale", "7.3%")
    st.plotly_chart(go.Figure(data=[go.Bar(name=v1_name, x=['Taux'], y=[d1['taux_chomage']], marker_color='#6366F1'), go.Bar(name=v2_name, x=['Taux'], y=[d2['taux_chomage']], marker_color='#F43F5E')]).update_layout(height=400), use_container_width=True)

# --- TAB 3 : LOGEMENT ---
with tabs[2]:
    st.markdown(f"""<div class="analysis-box"><p class="analysis-title">Analyse du Logement</p><p class="analysis-text">Pression immobilière supérieure à <b>{v1_name if d1['prix_achat_m2'] > d2['prix_achat_m2'] else v2_name}</b>.</p></div>""", unsafe_allow_html=True)
    cl1, cl2 = st.columns(2)
    with cl1:
        st.plotly_chart(go.Figure(data=[go.Bar(name=v1_name, x=['Loyer'], y=[d1['loyer_m2']], marker_color='#6366F1'), go.Bar(name=v2_name, x=['Loyer'], y=[d2['loyer_m2']], marker_color='#F43F5E')]).update_layout(height=300, title="Loyer (€/m²)"), use_container_width=True)
    with cl2:
        st.plotly_chart(go.Figure(data=[go.Bar(name=v1_name, x=['Achat'], y=[d1['prix_achat_m2']], marker_color='#6366F1'), go.Bar(name=v2_name, x=['Achat'], y=[d2['prix_achat_m2']], marker_color='#F43F5E')]).update_layout(height=300, title="Prix Achat (€/m²)"), use_container_width=True)
    st.divider()
    surf = st.select_slider("Simulateur de surface (m²)", options=[20, 45, 60, 90, 120], value=60)
    p1, p2 = st.columns(2)
    p1.metric(f"Budget {v1_name}", f"{int(d1['prix_achat_m2']*surf):,} €".replace(',', ' '))
    p2.metric(f"Budget {v2_name}", f"{int(d2['prix_achat_m2']*surf):,} €".replace(',', ' '))

# --- TAB 4 : ENVIRONNEMENT ---
with tabs[3]:
    st.markdown(f"""<div class="analysis-box"><p class="analysis-title">Analyse Climatique</p><p class="analysis-text"><b>{v1_name if d1['ensoleillement_h'] > d2['ensoleillement_h'] else v2_name}</b> bénéficie d'un meilleur ensoleillement annuel.</p></div>""", unsafe_allow_html=True)
    m1, m2 = st.columns(2)
    m1.metric(f"Soleil {v1_name}", f"{int(d1['ensoleillement_h'])} h")
    m2.metric(f"Soleil {v2_name}", f"{int(d2['ensoleillement_h'])} h")
    st.plotly_chart(go.Figure().add_trace(go.Scatter(x=['Jan', 'Juil'], y=[d1['temp_jan'], d1['temp_jul']], name=v1_name, line_color='#6366F1', line_width=4)).add_trace(go.Scatter(x=['Jan', 'Juil'], y=[d2['temp_jan'], d2['temp_jul']], name=v2_name, line_color='#F43F5E', line_width=4)).update_layout(height=400), use_container_width=True)

# --- TAB 5 : CULTURE (MODIFIÉ : BULLS POUR LES 2 COMMUNES) ---
with tabs[4]:
    st.markdown(f"""<div class="analysis-box"><p class="analysis-title">Analyse des Services</p><p class="analysis-text">Comparatif des infrastructures culturelles et de la dynamique académique entre les deux entités.</p></div>""", unsafe_allow_html=True)
    
    st.markdown(f"#### Infrastructures et Services - {v1_name.upper()} (ALPHA)")
    ca1, ca2, ca3 = st.columns(3)
    ca1.metric("Musées", int(d1['musees']))
    ca2.metric("Étudiants", f"{int(d1['etudiants']):,}".replace(',', ' '))
    ca3.metric("Réseau Sportif", f"{int(d1['salles_sport'])}")
    
    st.markdown(f"#### Infrastructures et Services - {v2_name.upper()} (BETA)")
    cb1, cb2, cb3 = st.columns(3)
    cb1.metric("Musées", int(d2['musees']))
    cb2.metric("Étudiants", f"{int(d2['etudiants']):,}".replace(',', ' '))
    cb3.metric("Réseau Sportif", f"{int(d2['salles_sport'])}")
    
    st.divider()
    
    clc1, clc2 = st.columns(2)
    with clc1:
        st.plotly_chart(go.Figure(data=[go.Bar(name=v1_name, x=['Musées'], y=[d1['musees']], marker_color='#6366F1'), go.Bar(name=v2_name, x=['Musées'], y=[d2['musees']], marker_color='#F43F5E')]).update_layout(height=300, title="Comparatif Musées"), use_container_width=True)
    with clc2:
        st.plotly_chart(go.Figure(data=[go.Bar(name=v1_name, x=['Étudiants'], y=[d1['etudiants']], marker_color='#6366F1'), go.Bar(name=v2_name, x=['Étudiants'], y=[d2['etudiants']], marker_color='#F43F5E')]).update_layout(height=300, title="Comparatif Étudiants"), use_container_width=True)
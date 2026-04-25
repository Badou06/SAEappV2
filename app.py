# =============================================================
# CITY FIGHTING - PLATEFORME D'AIDE À LA DÉCISION URBAINE
# VERSION ULTIME FINALE (V13.0) - FULL MASTER SD 2026
# =============================================================

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import numpy as np

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

    .supplement-box {
        background: #F0FDF4;
        padding: 25px;
        border-radius: 12px;
        border-left: 5px solid #22C55E;
        margin: 25px 0 15px 0;
    }
    .supplement-title {
        margin: 0;
        color: #14532D;
        font-size: 0.9rem;
        font-weight: 800;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }
    .supplement-text {
        color: #166534;
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

def get_temp_curve(d, name, color):
    """Interpolation sinusoïdale de la température mensuelle (jan=1, jul=7)"""
    months = list(range(1, 13))
    labels = ['Jan', 'Fév', 'Mar', 'Avr', 'Mai', 'Jun', 'Jul', 'Aoû', 'Sep', 'Oct', 'Nov', 'Déc']
    avg = (d['temp_jan'] + d['temp_jul']) / 2
    amp = (d['temp_jul'] - d['temp_jan']) / 2
    temps = [round(avg + amp * np.sin(2 * np.pi * (m - 4) / 12), 1) for m in months]
    return labels, temps

def get_precip_monthly(d):
    """Estimation mensuelle des précipitations selon le profil climatique"""
    total = d['precipitations_mm']
    lat = d['lat']
    # Profil océanique (nord/ouest) vs méditerranéen (sud)
    if lat < 44.5 and d['ensoleillement_h'] > 2400:  # Méditerranéen
        profil = [0.06, 0.06, 0.07, 0.06, 0.07, 0.04, 0.02, 0.03, 0.08, 0.11, 0.11, 0.09]
    elif lat > 48.0:  # Nordique / océanique humide
        profil = [0.09, 0.07, 0.08, 0.07, 0.07, 0.07, 0.08, 0.09, 0.08, 0.10, 0.10, 0.10]
    else:  # Continental / semi-océanique
        profil = [0.07, 0.07, 0.08, 0.08, 0.09, 0.08, 0.07, 0.07, 0.08, 0.09, 0.09, 0.09]
    labels = ['Jan', 'Fév', 'Mar', 'Avr', 'Mai', 'Jun', 'Jul', 'Aoû', 'Sep', 'Oct', 'Nov', 'Déc']
    values = [round(total * p) for p in profil]
    return labels, values

# 4. SIDEBAR
df = load_data()
df['score'] = df.apply(calculer_score_attractivite, axis=1)
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
    st.markdown("<p style='font-weight:800;'>MASTER V13.0</p>", unsafe_allow_html=True)
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
    <p style='color:#64748B; margin-top:8px; font-size:0.9rem;'>
        {int(d1['population']):,} hab. &nbsp;|&nbsp; {d1['departement']} 
        &emsp;⟷&emsp; 
        {int(d2['population']):,} hab. &nbsp;|&nbsp; {d2['departement']}
    </p>
</div>
""".replace(",", " "), unsafe_allow_html=True)

# --- AJOUT DE L'ONGLET SOURCES & DATA ---
tabs = st.tabs(["📍 SOURCES & DATA", "🏆 SYNTHÈSE", "💼 ÉCONOMIE", "🏠 LOGEMENT", "🌤️ ENVIRONNEMENT", "🎭 CULTURE & SERVICES"])

# ─────────────────────────────────────────────────────────────
# TAB 0 : SOURCES & DATA (NOUVEL ONGLET)
# ─────────────────────────────────────────────────────────────
with tabs[0]:
    st.markdown("### 📊 Architecture et Provenance des Données")
    
    st.markdown("""
    Cette plateforme repose sur une fusion de données officielles. Pour garantir une comparaison équitable, toutes les valeurs ont été normalisées à l'échelle nationale.
    """)
    
    col_src1, col_src2 = st.columns([2, 1])
    
    with col_src1:
        source_df = pd.DataFrame({
            "Domaine": ["Démographie", "Marché de l'Emploi", "Marché Immobilier", "Climatologie", "Infrastructures"],
            "Source Principale": ["INSEE (RP 2023)", "INSEE & Pôle Emploi", "DVF / OLAP (2024)", "Météo France (Normales)", "BPE (Ministère de la Culture)"],
            "Indicateurs": ["Population, Géo-localisation", "Taux de chômage local", "Loyer m² & Prix d'achat", "Ensoleillement & Précipitations", "Musées, Cinémas, Sports"]
        })
        st.table(source_df)
        
    with col_src2:
        st.info("**Note sur l'accès :** L'adresse `http://localhost:8501` est une adresse locale. Pour que d'autres utilisateurs accèdent à cette SAE, le projet est déployé via Streamlit Cloud.")
        st.success("**Traitement :** Les données ont été nettoyées et consolidées via un script `build_data.py` en amont.")

# ─────────────────────────────────────────────────────────────
# TAB 1 : SYNTHÈSE GÉNÉRALE
# ─────────────────────────────────────────────────────────────
with tabs[1]:
    score1, score2 = calculer_score_attractivite(d1), calculer_score_attractivite(d2)
    winner = v1_name if score1 > score2 else v2_name
    st.markdown(f"""<div class="analysis-box"><p class="analysis-title">Synthèse Décisionnelle</p><p class="analysis-text">Analyse comparative : <b>{winner}</b> présente l'indice de performance le plus élevé (Score : {max(score1, score2)}/100).<br><small><i>Le score global est calculé selon la pondération : Emploi (40%), Logement (40%) et Soleil (20%).</i></small></p></div>""", unsafe_allow_html=True)

    col_stats, col_radar = st.columns([1.5, 2.5])
    with col_stats:
        st.metric(f"Score {v1_name}", f"{score1}%")
        st.metric(f"Score {v2_name}", f"{score2}%", delta=round(score2 - score1, 1))
        st.divider()
        st.metric(f"Habitants {v1_name}", f"{int(d1['population']):,}".replace(",", " "))
        st.metric(f"Habitants {v2_name}", f"{int(d2['population']):,}".replace(",", " "))
    with col_radar:
        st.plotly_chart(get_radar_chart(d1, d2, v1_name, v2_name), use_container_width=True)

    # ── SUPPLÉMENT : Jauges + Classement national ──────────────
    st.markdown("""<div class="supplement-box"><p class="supplement-title">📊 Analyse Complémentaire</p><p class="supplement-text">Position des deux villes dans le classement national d'attractivité et comparaison multidimensionnelle.</p></div>""", unsafe_allow_html=True)

    sg1, sg2 = st.columns(2)
    with sg1:
        fig_gauge1 = go.Figure(go.Indicator(
            mode="gauge+number+delta",
            value=score1,
            delta={'reference': df['score'].mean(), 'valueformat': '.1f'},
            title={'text': f"Score {v1_name}<br><span style='font-size:0.75em;color:#64748B'>Moy. nationale : {df['score'].mean():.1f}</span>"},
            gauge={
                'axis': {'range': [0, 100], 'tickwidth': 1},
                'bar': {'color': "#6366F1"},
                'steps': [
                    {'range': [0, 40], 'color': '#FEE2E2'},
                    {'range': [40, 65], 'color': '#FEF9C3'},
                    {'range': [65, 100], 'color': '#DCFCE7'}
                ],
                'threshold': {'line': {'color': '#0F172A', 'width': 3}, 'thickness': 0.75, 'value': df['score'].mean()}
            }
        ))
        fig_gauge1.update_layout(height=300, paper_bgcolor='rgba(0,0,0,0)')
        st.plotly_chart(fig_gauge1, use_container_width=True)

    with sg2:
        fig_gauge2 = go.Figure(go.Indicator(
            mode="gauge+number+delta",
            value=score2,
            delta={'reference': df['score'].mean(), 'valueformat': '.1f'},
            title={'text': f"Score {v2_name}<br><span style='font-size:0.75em;color:#64748B'>Moy. nationale : {df['score'].mean():.1f}</span>"},
            gauge={
                'axis': {'range': [0, 100], 'tickwidth': 1},
                'bar': {'color': "#F43F5E"},
                'steps': [
                    {'range': [0, 40], 'color': '#FEE2E2'},
                    {'range': [40, 65], 'color': '#FEF9C3'},
                    {'range': [65, 100], 'color': '#DCFCE7'}
                ],
                'threshold': {'line': {'color': '#0F172A', 'width': 3}, 'thickness': 0.75, 'value': df['score'].mean()}
            }
        ))
        fig_gauge2.update_layout(height=300, paper_bgcolor='rgba(0,0,0,0)')
        st.plotly_chart(fig_gauge2, use_container_width=True)

    # Classement top 15 national
    df_sorted = df.sort_values('score', ascending=False).reset_index(drop=True)
    rank1 = df_sorted[df_sorted['ville'] == v1_name].index[0] + 1
    rank2 = df_sorted[df_sorted['ville'] == v2_name].index[0] + 1

    top15 = df_sorted.head(15).copy()
    colors = []
    for v in top15['ville']:
        if v == v1_name:
            colors.append('#6366F1')
        elif v == v2_name:
            colors.append('#F43F5E')
        else:
            colors.append('#CBD5E1')

    fig_rank = go.Figure(go.Bar(
        x=top15['ville'],
        y=top15['score'],
        marker_color=colors,
        text=top15['score'].astype(str),
        textposition='outside',
    ))
    fig_rank.update_layout(
        title=f"🏆 Top 15 villes — Classement national | {v1_name} : #{rank1} / {v2_name} : #{rank2}",
        height=400,
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        xaxis=dict(tickangle=-30),
        yaxis=dict(title="Score attractivité", gridcolor='#F1F5F9'),
        showlegend=False
    )
    st.plotly_chart(fig_rank, use_container_width=True)

    # Comparaison radar étendu (6 critères)
    st.caption(f"📍 Position nationale : **{v1_name}** #{rank1} sur {len(df)} villes · **{v2_name}** #{rank2} sur {len(df)} villes")


# ─────────────────────────────────────────────────────────────
# TAB 2 : ÉCONOMIE
# ─────────────────────────────────────────────────────────────
with tabs[2]:
    diff_c = round(d1['taux_chomage'] - d2['taux_chomage'], 1)
    st.markdown(f"""<div class="analysis-box"><p class="analysis-title">Analyse de l'Emploi</p><p class="analysis-text">Le marché est plus dynamique à <b>{v1_name if d1['taux_chomage'] < d2['taux_chomage'] else v2_name}</b>.<br><small><i>Critère d'emploi : Pondération de 40% dans le score final.</i></small></p></div>""", unsafe_allow_html=True)

    e1, e2, e3 = st.columns(3)
    e1.metric(f"Chômage {v1_name}", f"{d1['taux_chomage']}%")
    e2.metric(f"Chômage {v2_name}", f"{d2['taux_chomage']}%", delta=-diff_c, delta_color="inverse")
    e3.metric("Moyenne Nationale", "7.3%")

    st.plotly_chart(go.Figure(data=[
        go.Bar(name=v1_name, x=['Taux de chômage'], y=[d1['taux_chomage']], marker_color='#6366F1'),
        go.Bar(name=v2_name, x=['Taux de chômage'], y=[d2['taux_chomage']], marker_color='#F43F5E'),
        go.Bar(name='Moyenne France', x=['Taux de chômage'], y=[7.3], marker_color='#94A3B8'),
    ]).update_layout(height=400, barmode='group', paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', yaxis=dict(gridcolor='#F1F5F9', title="Taux (%)")), use_container_width=True)

    # ── SUPPLÉMENT : Distribution nationale + jauges ───────────
    st.markdown("""<div class="supplement-box"><p class="supplement-title">📊 Analyse Complémentaire</p><p class="supplement-text">Distribution du chômage dans toutes les villes françaises et positionnement des deux villes dans l'échiquier national.</p></div>""", unsafe_allow_html=True)

    sc1, sc2 = st.columns(2)
    with sc1:
        # Distribution histogramme du chômage
        fig_hist = go.Figure()
        fig_hist.add_trace(go.Histogram(
            x=df['taux_chomage'], nbinsx=20,
            marker_color='#CBD5E1', name='Toutes les villes'
        ))
        fig_hist.add_vline(x=d1['taux_chomage'], line_color='#6366F1', line_width=2.5, annotation_text=v1_name, annotation_position="top right")
        fig_hist.add_vline(x=d2['taux_chomage'], line_color='#F43F5E', line_width=2.5, annotation_text=v2_name, annotation_position="top left")
        fig_hist.add_vline(x=7.3, line_color='#94A3B8', line_dash='dash', line_width=1.5, annotation_text="Moy. nationale")
        fig_hist.update_layout(
            title="Distribution nationale du chômage",
            height=350, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
            xaxis=dict(title="Taux de chômage (%)", gridcolor='#F1F5F9'),
            yaxis=dict(title="Nombre de villes", gridcolor='#F1F5F9'),
        )
        st.plotly_chart(fig_hist, use_container_width=True)

    with sc2:
        # Top 10 meilleures villes emploi
        df_emp = df.nsmallest(12, 'taux_chomage')[['ville', 'taux_chomage']].reset_index(drop=True)
        colors_emp = ['#6366F1' if v == v1_name else '#F43F5E' if v == v2_name else '#CBD5E1' for v in df_emp['ville']]
        fig_emp = go.Figure(go.Bar(
            x=df_emp['ville'], y=df_emp['taux_chomage'],
            marker_color=colors_emp,
            text=df_emp['taux_chomage'].astype(str) + '%',
            textposition='outside'
        ))
        fig_emp.update_layout(
            title="Top 12 — Villes au plus faible chômage",
            height=350, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
            xaxis=dict(tickangle=-30, gridcolor='#F1F5F9'),
            yaxis=dict(title="Taux (%)", gridcolor='#F1F5F9'),
        )
        st.plotly_chart(fig_emp, use_container_width=True)

    # Chômage vs population scatter
    fig_scatter_emp = px.scatter(
        df, x='population', y='taux_chomage', size='population',
        hover_name='ville', color='region',
        title="Chômage vs Taille de ville (toutes les villes)",
        labels={'population': 'Population', 'taux_chomage': 'Taux de chômage (%)'},
        height=420,
        color_discrete_sequence=px.colors.qualitative.Pastel
    )
    # Surbrillance des 2 villes sélectionnées
    for city_data, color, name in [(d1, '#6366F1', v1_name), (d2, '#F43F5E', v2_name)]:
        fig_scatter_emp.add_trace(go.Scatter(
            x=[city_data['population']], y=[city_data['taux_chomage']],
            mode='markers+text',
            marker=dict(color=color, size=18, symbol='star', line=dict(color='white', width=2)),
            text=[name], textposition='top center',
            name=name, showlegend=True
        ))
    fig_scatter_emp.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
    st.plotly_chart(fig_scatter_emp, use_container_width=True)


# ─────────────────────────────────────────────────────────────
# TAB 3 : LOGEMENT
# ─────────────────────────────────────────────────────────────
with tabs[3]:
    st.markdown(f"""<div class="analysis-box"><p class="analysis-title">Analyse du Logement</p><p class="analysis-text">Pression immobilière supérieure à <b>{v1_name if d1['prix_achat_m2'] > d2['prix_achat_m2'] else v2_name}</b>.<br><small><i>Critère logement : Pondération de 40% dans le score final.</i></small></p></div>""", unsafe_allow_html=True)

    cl1, cl2 = st.columns(2)
    with cl1:
        st.plotly_chart(go.Figure(data=[
            go.Bar(name=v1_name, x=['Loyer'], y=[d1['loyer_m2']], marker_color='#6366F1'),
            go.Bar(name=v2_name, x=['Loyer'], y=[d2['loyer_m2']], marker_color='#F43F5E')
        ]).update_layout(height=300, title="Loyer (€/m²)", paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', yaxis=dict(gridcolor='#F1F5F9')), use_container_width=True)
    with cl2:
        st.plotly_chart(go.Figure(data=[
            go.Bar(name=v1_name, x=['Achat'], y=[d1['prix_achat_m2']], marker_color='#6366F1'),
            go.Bar(name=v2_name, x=['Achat'], y=[d2['prix_achat_m2']], marker_color='#F43F5E')
        ]).update_layout(height=300, title="Prix Achat (€/m²)", paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', yaxis=dict(gridcolor='#F1F5F9')), use_container_width=True)

    st.divider()
    surf = st.select_slider("Simulateur de surface (m²)", options=[20, 45, 60, 90, 120], value=60)
    p1, p2 = st.columns(2)
    p1.metric(f"Budget {v1_name}", f"{int(d1['prix_achat_m2'] * surf):,} €".replace(',', ' '))
    p2.metric(f"Budget {v2_name}", f"{int(d2['prix_achat_m2'] * surf):,} €".replace(',', ' '))

    # ── SUPPLÉMENT : Effort locatif + carte des prix ───────────
    st.markdown("""<div class="supplement-box"><p class="supplement-title">📊 Analyse Complémentaire</p><p class="supplement-text">Effort locatif théorique, positionnement immobilier national et carte des prix au m² en France.</p></div>""", unsafe_allow_html=True)

    # Effort locatif (% salaire moyen net ~2 200€/mois)
    SALAIRE_MOYEN = 2200
    SURFACE_REF = 40  # m²
    effort1 = round((d1['loyer_m2'] * SURFACE_REF) / SALAIRE_MOYEN * 100, 1)
    effort2 = round((d2['loyer_m2'] * SURFACE_REF) / SALAIRE_MOYEN * 100, 1)
    effort_national = round((df['loyer_m2'].mean() * SURFACE_REF) / SALAIRE_MOYEN * 100, 1)

    se1, se2, se3 = st.columns(3)
    se1.metric(f"Effort locatif {v1_name}", f"{effort1}%", help=f"Loyer {SURFACE_REF}m² / Salaire moyen net ({SALAIRE_MOYEN}€)")
    se2.metric(f"Effort locatif {v2_name}", f"{effort2}%", delta=round(effort2 - effort1, 1), delta_color="inverse")
    se3.metric("Effort national moyen", f"{effort_national}%")

    sc_log1, sc_log2 = st.columns(2)
    with sc_log1:
        # Scatter loyer vs achat pour toutes les villes
        fig_log_scatter = px.scatter(
            df, x='loyer_m2', y='prix_achat_m2',
            hover_name='ville', color='region',
            title="Loyer vs Prix d'achat — Toutes les villes",
            labels={'loyer_m2': 'Loyer (€/m²)', 'prix_achat_m2': 'Prix achat (€/m²)'},
            height=380,
            color_discrete_sequence=px.colors.qualitative.Pastel
        )
        for city_data, color, name in [(d1, '#6366F1', v1_name), (d2, '#F43F5E', v2_name)]:
            fig_log_scatter.add_trace(go.Scatter(
                x=[city_data['loyer_m2']], y=[city_data['prix_achat_m2']],
                mode='markers+text',
                marker=dict(color=color, size=16, symbol='star', line=dict(color='white', width=2)),
                text=[name], textposition='top center', name=name, showlegend=True
            ))
        fig_log_scatter.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
        st.plotly_chart(fig_log_scatter, use_container_width=True)

    with sc_log2:
        # Top 10 villes les moins chères à la location
        df_loyer = df.nsmallest(12, 'loyer_m2')[['ville', 'loyer_m2']].reset_index(drop=True)
        colors_loyer = ['#6366F1' if v == v1_name else '#F43F5E' if v == v2_name else '#CBD5E1' for v in df_loyer['ville']]
        fig_loyer = go.Figure(go.Bar(
            x=df_loyer['ville'], y=df_loyer['loyer_m2'],
            marker_color=colors_loyer,
            text=df_loyer['loyer_m2'].astype(str) + ' €',
            textposition='outside'
        ))
        fig_loyer.update_layout(
            title="Top 12 — Villes les moins chères à la location",
            height=380, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
            xaxis=dict(tickangle=-30, gridcolor='#F1F5F9'),
            yaxis=dict(title="Loyer €/m²", gridcolor='#F1F5F9'),
        )
        st.plotly_chart(fig_loyer, use_container_width=True)

    # Carte géographique des prix au m²
    fig_map_log = px.scatter_mapbox(
        df, lat='lat', lon='lon', color='prix_achat_m2',
        size='population', hover_name='ville',
        hover_data={'loyer_m2': True, 'prix_achat_m2': True, 'lat': False, 'lon': False},
        color_continuous_scale='RdYlGn_r',
        size_max=40, zoom=4.5,
        title="Carte des prix immobiliers (€/m²)",
        labels={'prix_achat_m2': 'Prix achat €/m²'},
        height=480
    )
    fig_map_log.update_layout(
        mapbox_style="carto-positron",
        paper_bgcolor='rgba(0,0,0,0)',
        coloraxis_colorbar=dict(title="€/m²")
    )
    st.plotly_chart(fig_map_log, use_container_width=True)


# ─────────────────────────────────────────────────────────────
# TAB 4 : ENVIRONNEMENT
# ─────────────────────────────────────────────────────────────
with tabs[4]:
    st.markdown(f"""<div class="analysis-box"><p class="analysis-title">Analyse Climatique</p><p class="analysis-text"><b>{v1_name if d1['ensoleillement_h'] > d2['ensoleillement_h'] else v2_name}</b> bénéficie d'un meilleur ensoleillement annuel.<br><small><i>Critère environnemental : Pondération de 20% dans le score final.</i></small></p></div>""", unsafe_allow_html=True)

    m1, m2 = st.columns(2)
    m1.metric(f"Soleil {v1_name}", f"{int(d1['ensoleillement_h'])} h")
    m2.metric(f"Soleil {v2_name}", f"{int(d2['ensoleillement_h'])} h")

    st.plotly_chart(
        go.Figure()
        .add_trace(go.Scatter(x=['Jan', 'Juil'], y=[d1['temp_jan'], d1['temp_jul']], name=v1_name, line_color='#6366F1', line_width=4))
        .add_trace(go.Scatter(x=['Jan', 'Juil'], y=[d2['temp_jan'], d2['temp_jul']], name=v2_name, line_color='#F43F5E', line_width=4))
        .update_layout(height=400, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', yaxis=dict(gridcolor='#F1F5F9', title="Température (°C)"))
    , use_container_width=True)

    # ── SUPPLÉMENT : Courbes mensuelles complètes + précipitations ──
    st.markdown("""<div class="supplement-box"><p class="supplement-title">📊 Analyse Complémentaire</p><p class="supplement-text">Courbes de températures mensuelles interpolées sur 12 mois et répartition mensuelle estimée des précipitations.</p></div>""", unsafe_allow_html=True)

    labels_m, temps1 = get_temp_curve(d1, v1_name, '#6366F1')
    _, temps2 = get_temp_curve(d2, v2_name, '#F43F5E')
    _, precip1 = get_precip_monthly(d1)
    _, precip2 = get_precip_monthly(d2)

    sm1, sm2 = st.columns(2)
    with sm1:
        fig_temp12 = go.Figure()
        fig_temp12.add_trace(go.Scatter(x=labels_m, y=temps1, name=v1_name, line=dict(color='#6366F1', width=3), fill='tozeroy', fillcolor='rgba(99,102,241,0.08)'))
        fig_temp12.add_trace(go.Scatter(x=labels_m, y=temps2, name=v2_name, line=dict(color='#F43F5E', width=3), fill='tozeroy', fillcolor='rgba(244,63,94,0.08)'))
        fig_temp12.add_hline(y=0, line_dash='dash', line_color='#94A3B8', line_width=1)
        fig_temp12.update_layout(
            title="Températures mensuelles (interpolation sinusoïdale)",
            height=380, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
            yaxis=dict(title="°C", gridcolor='#F1F5F9'),
            legend=dict(orientation='h', yanchor='bottom', y=1.02)
        )
        st.plotly_chart(fig_temp12, use_container_width=True)

    with sm2:
        fig_precip = go.Figure()
        fig_precip.add_trace(go.Bar(x=labels_m, y=precip1, name=v1_name, marker_color='rgba(99,102,241,0.7)'))
        fig_precip.add_trace(go.Bar(x=labels_m, y=precip2, name=v2_name, marker_color='rgba(244,63,94,0.7)'))
        fig_precip.update_layout(
            title=f"Précipitations mensuelles estimées (mm)<br><sup>{v1_name}: {int(d1['precipitations_mm'])}mm/an · {v2_name}: {int(d2['precipitations_mm'])}mm/an</sup>",
            height=380, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
            yaxis=dict(title="mm", gridcolor='#F1F5F9'),
            barmode='group',
            legend=dict(orientation='h', yanchor='bottom', y=1.02)
        )
        st.plotly_chart(fig_precip, use_container_width=True)

    # Carte ensoleillement
    fig_map_sun = px.scatter_mapbox(
        df, lat='lat', lon='lon', color='ensoleillement_h',
        size='ensoleillement_h', hover_name='ville',
        hover_data={'ensoleillement_h': True, 'precipitations_mm': True, 'lat': False, 'lon': False},
        color_continuous_scale='YlOrRd',
        size_max=30, zoom=4.5,
        title="Carte de l'ensoleillement annuel (heures)",
        labels={'ensoleillement_h': 'Heures de soleil'},
        height=480
    )
    fig_map_sun.update_layout(mapbox_style="carto-positron", paper_bgcolor='rgba(0,0,0,0)')
    st.plotly_chart(fig_map_sun, use_container_width=True)

    # Scatter ensoleillement vs précipitations
    fig_clim = px.scatter(
        df, x='precipitations_mm', y='ensoleillement_h',
        hover_name='ville', color='region',
        title="Profil climatique — Ensoleillement vs Précipitations",
        labels={'precipitations_mm': 'Précipitations (mm/an)', 'ensoleillement_h': 'Ensoleillement (h/an)'},
        height=380,
        color_discrete_sequence=px.colors.qualitative.Pastel
    )
    for city_data, color, name in [(d1, '#6366F1', v1_name), (d2, '#F43F5E', v2_name)]:
        fig_clim.add_trace(go.Scatter(
            x=[city_data['precipitations_mm']], y=[city_data['ensoleillement_h']],
            mode='markers+text',
            marker=dict(color=color, size=16, symbol='star', line=dict(color='white', width=2)),
            text=[name], textposition='top center', name=name, showlegend=True
        ))
    fig_clim.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
    st.plotly_chart(fig_clim, use_container_width=True)


# ─────────────────────────────────────────────────────────────
# TAB 5 : CULTURE & SERVICES
# ─────────────────────────────────────────────────────────────
with tabs[5]:
    st.markdown(f"""<div class="analysis-box"><p class="analysis-title">Analyse des Services</p><p class="analysis-text">Comparatif des infrastructures culturelles et de la dynamique académique entre les deux entités.<br><small><i>Note : Ces données sont fournies à titre indicatif et n'influencent pas le score global d'attractivité.</i></small></p></div>""", unsafe_allow_html=True)

    st.markdown(f"#### Infrastructures et Services — {v1_name.upper()} (ALPHA)")
    ca1, ca2, ca3 = st.columns(3)
    ca1.metric("Musées", int(d1['musees']))
    ca2.metric("Étudiants", f"{int(d1['etudiants']):,}".replace(',', ' '))
    ca3.metric("Réseau Sportif", f"{int(d1['salles_sport'])}")

    st.markdown(f"#### Infrastructures et Services — {v2_name.upper()} (BETA)")
    cb1, cb2, cb3 = st.columns(3)
    cb1.metric("Musées", int(d2['musees']))
    cb2.metric("Étudiants", f"{int(d2['etudiants']):,}".replace(',', ' '))
    cb3.metric("Réseau Sportif", f"{int(d2['salles_sport'])}")

    st.divider()
    clc1, clc2 = st.columns(2)
    with clc1:
        st.plotly_chart(go.Figure(data=[
            go.Bar(name=v1_name, x=['Musées'], y=[d1['musees']], marker_color='#6366F1'),
            go.Bar(name=v2_name, x=['Musées'], y=[d2['musees']], marker_color='#F43F5E')
        ]).update_layout(height=300, title="Comparatif Musées", paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', yaxis=dict(gridcolor='#F1F5F9')), use_container_width=True)
    with clc2:
        st.plotly_chart(go.Figure(data=[
            go.Bar(name=v1_name, x=['Étudiants'], y=[d1['etudiants']], marker_color='#6366F1'),
            go.Bar(name=v2_name, x=['Étudiants'], y=[d2['etudiants']], marker_color='#F43F5E')
        ]).update_layout(height=300, title="Comparatif Étudiants", paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', yaxis=dict(gridcolor='#F1F5F9')), use_container_width=True)

    # ── SUPPLÉMENT : Métriques per capita + radar complet ──────
    st.markdown("""<div class="supplement-box"><p class="supplement-title">📊 Analyse Complémentaire</p><p class="supplement-text">Indices per capita pour une comparaison équitable indépendante de la taille des villes, et radar synthétique des équipements.</p></div>""", unsafe_allow_html=True)

    # Métriques per 10 000 habitants
    pop1 = d1['population'] / 10000
    pop2 = d2['population'] / 10000
    musees_pc1 = round(d1['musees'] / pop1, 2)
    musees_pc2 = round(d2['musees'] / pop2, 2)
    cinemas_pc1 = round(d1['cinemas'] / pop1, 2)
    cinemas_pc2 = round(d2['cinemas'] / pop2, 2)
    sport_pc1 = round(d1['salles_sport'] / pop1, 2)
    sport_pc2 = round(d2['salles_sport'] / pop2, 2)
    etud_pc1 = round(d1['etudiants'] / d1['population'] * 100, 1)
    etud_pc2 = round(d2['etudiants'] / d2['population'] * 100, 1)

    st.markdown("##### Métriques per 10 000 habitants")
    pc1, pc2, pc3, pc4 = st.columns(4)
    pc1.metric("Musées/10k hab.", f"{musees_pc1} | {musees_pc2}", delta=round(musees_pc2 - musees_pc1, 2))
    pc2.metric("Cinémas/10k hab.", f"{cinemas_pc1} | {cinemas_pc2}", delta=round(cinemas_pc2 - cinemas_pc1, 2))
    pc3.metric("Salles sport/10k", f"{sport_pc1} | {sport_pc2}", delta=round(sport_pc2 - sport_pc1, 2))
    pc4.metric("Étudiants (%pop.)", f"{etud_pc1}% | {etud_pc2}%", delta=round(etud_pc2 - etud_pc1, 1))

    sc_cult1, sc_cult2 = st.columns(2)
    with sc_cult1:
        # Radar per capita
        cat_pc = ['Musées/10k', 'Cinémas/10k', 'Salles sport/10k', 'Étudiants %pop']
        def norm_pc(v, vmin, vmax): return min(100, max(0, (v - vmin) / (vmax - vmin) * 100))
        v1_pc = [norm_pc(musees_pc1, 0, 5), norm_pc(cinemas_pc1, 0, 2), norm_pc(sport_pc1, 0, 5), norm_pc(etud_pc1, 0, 30)]
        v2_pc = [norm_pc(musees_pc2, 0, 5), norm_pc(cinemas_pc2, 0, 2), norm_pc(sport_pc2, 0, 5), norm_pc(etud_pc2, 0, 30)]

        fig_radar_pc = go.Figure()
        fig_radar_pc.add_trace(go.Scatterpolar(r=v1_pc, theta=cat_pc, fill='toself', name=v1_name, line_color='#6366F1'))
        fig_radar_pc.add_trace(go.Scatterpolar(r=v2_pc, theta=cat_pc, fill='toself', name=v2_name, line_color='#F43F5E'))
        fig_radar_pc.update_layout(
            title="Radar équipements per capita",
            polar=dict(radialaxis=dict(visible=False, range=[0, 100])),
            paper_bgcolor='rgba(0,0,0,0)', height=380,
            legend=dict(orientation='h', yanchor='bottom', y=-0.2)
        )
        st.plotly_chart(fig_radar_pc, use_container_width=True)

    with sc_cult2:
        # Comparaison multi-indicateurs normalisés (barres groupées)
        indicateurs = ['Musées', 'Cinémas', 'Salles sport', 'Étudiants (k)']
        vals1 = [d1['musees'], d1['cinemas'], d1['salles_sport'], d1['etudiants'] / 1000]
        vals2 = [d2['musees'], d2['cinemas'], d2['salles_sport'], d2['etudiants'] / 1000]

        fig_multi = go.Figure(data=[
            go.Bar(name=v1_name, x=indicateurs, y=vals1, marker_color='#6366F1'),
            go.Bar(name=v2_name, x=indicateurs, y=vals2, marker_color='#F43F5E')
        ])
        fig_multi.update_layout(
            title="Comparatif multi-équipements (valeurs absolues)",
            barmode='group', height=380,
            paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
            yaxis=dict(gridcolor='#F1F5F9'),
            legend=dict(orientation='h', yanchor='bottom', y=1.02)
        )
        st.plotly_chart(fig_multi, use_container_width=True)

    # Carte culturelle
    df['musees_pc'] = df['musees'] / (df['population'] / 10000)
    fig_map_cult = px.scatter_mapbox(
        df, lat='lat', lon='lon', color='musees_pc',
        size='etudiants', hover_name='ville',
        hover_data={'musees': True, 'etudiants': True, 'lat': False, 'lon': False},
        color_continuous_scale='Viridis',
        size_max=40, zoom=4.5,
        title="Carte — Densité muséale (musées/10k hab.) & étudiants",
        labels={'musees_pc': 'Musées/10k hab.'},
        height=480
    )
    fig_map_cult.update_layout(mapbox_style="carto-positron", paper_bgcolor='rgba(0,0,0,0)')
    st.plotly_chart(fig_map_cult, use_container_width=True)
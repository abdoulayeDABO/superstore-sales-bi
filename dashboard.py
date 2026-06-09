import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from pathlib import Path
from etl import extract, transform
from settings import BASE_DIR, DATA_DIR

# ── Config ───────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Superstore Dashboard",
    page_icon="🛒",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ── Styles ───────────────────────────────────────────────────────────────────
st.markdown("""
<link href="https://fonts.googleapis.com/icon?family=Material+Icons+Round" rel="stylesheet">
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">

<style>
    /* ── Base ── */
    * { font-family: 'Inter', sans-serif; }
    [data-testid="stAppViewContainer"] { background-color: #0f1117; }
    [data-testid="stSidebar"],
    section[data-testid="stSidebarNav"],
    [data-testid="collapsedControl"] { display: none !important; }
    
    /* Optimisation du viewport pour tout faire tenir sur un seul écran */
    .block-container { padding: 24px 40px !important; max-width: 96% !important; margin: 0 auto !important; }
    #MainMenu, footer, header { visibility: hidden; }

    /* ── Panneau Latéral (Filtres) ── */
    .year-panel-logo {
        display: flex;
        align-items: center;
        gap: 10px;
        margin-bottom: 20px;
        padding-bottom: 14px;
        border-bottom: 1px solid #1a1d2e;
    }
    .year-panel-logo .material-icons-round { color: #5b6af0; font-size: 22px; }
    .year-panel-logo span { font-size: 0.85rem; font-weight: 700; color: #e8eaf0; letter-spacing: 0.05em; }
    
    .year-panel-label {
        font-size: 0.68rem;
        font-weight: 700;
        letter-spacing: 0.1em;
        text-transform: uppercase;
        color: #4a5068;
        margin-bottom: 12px;
        display: flex;
        align-items: center;
        gap: 6px;
    }
    .year-panel-label .material-icons-round { font-size: 12px; }

    /* Cases à cocher alignées */
    .stCheckbox { margin-bottom: 8px !important; }
    .stCheckbox > label {
        display: flex !important;
        align-items: center !important;
        width: 100% !important;
        padding: 10px 14px !important;
        border-radius: 8px !important;
        border: 1px solid #1e2235 !important;
        background: #13151f !important;
        color: #8892b0 !important;
        font-size: 0.85rem !important;
        font-weight: 500 !important;
    }
    .stCheckbox > label:has(input:checked) {
        background: rgba(91,106,240,0.12) !important;
        border-color: #5b6af0 !important;
        color: #a0aaff !important;
    }

    /* ── Header ── */
    .dash-header { margin-bottom: 24px; padding-left: 4px; }
    .dash-title { font-size: 1.5rem; font-weight: 700; color: #e8eaf0; display: flex; align-items: center; gap: 10px; }
    .dash-title .material-icons-round { color: #5b6af0; font-size: 26px; }
    .dash-subtitle { font-size: 0.82rem; color: #4a5068; margin-top: 4px; }

    /* ── Cartes KPI ── */
    .metric-grid { margin-bottom: 28px; }
    .metric-card {
        background: #13151f;
        border: 1px solid #1e2235;
        border-radius: 12px;
        padding: 18px 20px;
        height: 100%;
    }
    .metric-icon { font-size: 18px; color: inherit; display: block; margin-bottom: 10px; }
    .metric-value { font-size: 1.6rem; font-weight: 700; line-height: 1.1; }
    .metric-label { font-size: 0.7rem; color: #4a5068; margin-top: 6px; font-weight: 600; text-transform: uppercase; letter-spacing: 0.06em; }

    /* ── Titres de Section (CORRIGÉS ET RENDUS VISIBLES EN GRAS BLANC) ── */
    .section-container { margin-bottom: 16px; padding-left: 2px; }
    .section-title {
        font-size: 0.95rem;
        font-weight: 700;
        color: #e8eaf0;
        display: flex;
        align-items: center;
        gap: 8px;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }
    .section-title .material-icons-round { font-size: 20px; color: #5b6af0; }
</style>
""", unsafe_allow_html=True)


# ── Load data ────────────────────────────────────────────────────────────────
@st.cache_data
def load_data():
    sales_path = DATA_DIR / "sales.csv"
    raw_path   = DATA_DIR / "superstore.csv"

    if sales_path.exists() and (DATA_DIR / "order.csv").exists():
        try:
            sales     = pd.read_csv(sales_path)
            orders    = pd.read_csv(DATA_DIR / "order.csv", parse_dates=["order_date", "ship_date"])
            products  = pd.read_csv(DATA_DIR / "product.csv")
            customers = pd.read_csv(DATA_DIR / "customer.csv")
            df = (
                sales
                .merge(orders,    on="order_id",    how="left")
                .merge(products,  on="product_id",  how="left")
                .merge(customers, on="customer_id", how="left")
            )
        except Exception as e:
            st.error(f"Erreur lecture CSV : {e}"); st.stop()
    elif raw_path.exists():
        try:
            df = transform(extract(raw_path))
        except Exception as e:
            st.error(f"Erreur ETL : {e}"); st.stop()
    else:
        st.warning("⚠️ Fichiers de données introuvables.")
        return pd.DataFrame(columns=[
            "order_date","year","month","sales","profit",
            "region","category","segment","order_id","product_name","sub_category"
        ])

    df["order_date"] = pd.to_datetime(df["order_date"])
    df["year"]  = df["order_date"].dt.year
    df["month"] = df["order_date"].dt.to_period("M").astype(str)
    return df

df = load_data()
years = sorted(df["year"].unique())

# ── Grid Principal ───────────────────────────────────────────────────────────
left, main = st.columns([1.2, 5.8], gap="large")

# ── COLONNE GAUCHE : Panneau de Filtrage ──────────────────────────────────────
with left:
    st.markdown("""
    <div class="year-panel-logo">
        <span class="material-icons-round">storefront</span>
        <span>SUPERSTORE</span>
    </div>
    <div class="year-panel-label">
        <span class="material-icons-round">calendar_month</span>
        Années
    </div>
    """, unsafe_allow_html=True)

    selected_years = [y for y in years if st.checkbox(str(y), value=True, key=f"y_{y}")]

# ── COLONNE DROITE : Vue unique condensée ─────────────────────────────────────
with main:
    mask = df["year"].isin(selected_years) if selected_years else pd.Series([False] * len(df))
    fdf  = df[mask]

    # En-tête
    st.markdown(f"""
    <div class="dash-header">
        <div class="dash-title">
            <span class="material-icons-round">analytics</span> Sales Dashboard
        </div>
        <div class="dash-subtitle">
            {len(fdf):,} transactions &middot; {fdf['order_id'].nunique():,} commandes uniques
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ── KPIs Rendu ───────────────────────────────────────────────────────────
    total_sales   = fdf["sales"].sum()
    total_profit  = fdf["profit"].sum()
    profit_margin = (total_profit / total_sales * 100) if total_sales else 0

    kpis = [
        ("payments",      f"${total_sales:,.0f}",   "Chiffre d'affaires", "#5b6af0"),
        ("trending_up",   f"${total_profit:,.0f}",  "Profit total",       "#22c55e" if total_profit >= 0 else "#ef4444"),
        ("percent",       f"{profit_margin:.1f}%",  "Marge globale",      "#f59e0b"),
    ]
    
    st.markdown('<div class="metric-grid">', unsafe_allow_html=True)
    k_cols = st.columns(3, gap="medium")
    for col, (icon, val, label, color) in zip(k_cols, kpis):
        with col:
            st.markdown(f"""
            <div class="metric-card">
                <span class="material-icons-round metric-icon" style="color:{color}">{icon}</span>
                <div class="metric-value" style="color:{color}">{val}</div>
                <div class="metric-label">{label}</div>
            </div>""", unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    # ── Configurations Graphiques Globales ───────────────────────────────────
    LAYOUT_CONFIG = dict(
        paper_bgcolor="rgba(0,0,0,0)", 
        plot_bgcolor="rgba(0,0,0,0)",
        font_color="#c8cdd8", 
        font_family="Inter",
        margin=dict(t=20, b=10, l=10, r=10),
    )

    if not fdf.empty:
        # Layout 50/50
        graph_col1, graph_col2 = st.columns(2, gap="large")

        # ── BLOC 1 : Évolution Mensuelle ─────────────────────────────────────
        with graph_col1:
            st.markdown('<div class="section-container"><div class="section-title"><span class="material-icons-round">show_chart</span>Évolution mensuelle</div></div>', unsafe_allow_html=True)
            
            monthly = fdf.groupby("month")[["sales", "profit"]].sum().reset_index()
            fig_trend = go.Figure()
            fig_trend.add_trace(go.Scatter(
                x=monthly["month"], y=monthly["sales"],
                name="Ventes", line=dict(color="#5b6af0", width=3),
                fill="tozeroy", fillcolor="rgba(91,106,240,0.05)"
            ))
            fig_trend.add_trace(go.Scatter(
                x=monthly["month"], y=monthly["profit"],
                name="Profit", line=dict(color="#22c55e", width=2.5, dash="dot")
            ))
            fig_trend.update_layout(
                **LAYOUT_CONFIG, 
                height=290,
                legend=dict(bgcolor="rgba(0,0,0,0)", orientation="h", yanchor="bottom", y=1.05, xanchor="right", x=1),
                xaxis=dict(showgrid=False, tickangle=-45, color="#4a5068"),
                yaxis=dict(showgrid=True, gridcolor="#161925", color="#4a5068")
            )
            st.plotly_chart(fig_trend, use_container_width=True, config={'displayModeBar': False})

        # ── BLOC 2 : Top Produit ─────────────────────────────────────────────
        with graph_col2:
            st.markdown('<div class="section-container"><div class="section-title"><span class="material-icons-round">emoji_events</span>Top 5 Produits les plus vendus</div></div>', unsafe_allow_html=True)
            
            top_products = fdf.groupby("product_name")["sales"].sum().nlargest(5).reset_index().sort_values("sales", ascending=True)
            
            fig_prod = px.bar(
                top_products, 
                x="sales", 
                y="product_name", 
                orientation="h",
                color_discrete_sequence=["#5b6af0"]
            )
            fig_prod.update_layout(
                **LAYOUT_CONFIG,
                height=290,
                xaxis=dict(showgrid=True, gridcolor="#161925", color="#4a5068", title=None),
                yaxis=dict(showgrid=False, color="#c8cdd8", title=None)
            )
            fig_prod.update_yaxes(ticktext=[name[:30] + '...' if len(name) > 30 else name for name in top_products["product_name"]])
            st.plotly_chart(fig_prod, use_container_width=True, config={'displayModeBar': False})

    else:
        st.info("Veuillez sélectionner au moins une année dans le panneau de gauche.")

    # Footer
    st.markdown(
        "<div style='font-size:0.65rem; color:#1e2235; text-align:right; margin-top:32px; letter-spacing: 0.05em;'>"
        "Superstore Sales BI &middot; Streamlit & Plotly</div>",
        unsafe_allow_html=True
    )
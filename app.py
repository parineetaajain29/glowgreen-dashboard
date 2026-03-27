import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import plotly.figure_factory as ff
from scipy import stats
import warnings
warnings.filterwarnings('ignore')

# ── PAGE CONFIG ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="GlowGreen Analytics",
    page_icon="🌿",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── THEME / CSS ───────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Serif+Display:ital@0;1&family=DM+Sans:wght@300;400;500;600&display=swap');

html, body, [class*="css"] {
    font-family: 'DM Sans', sans-serif;
}

/* Sidebar */
section[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #1B4332 0%, #2D6A4F 60%, #40916C 100%);
    border-right: none;
}
section[data-testid="stSidebar"] * {
    color: #D8F3DC !important;
}
section[data-testid="stSidebar"] .stRadio label {
    font-size: 15px !important;
    padding: 4px 0;
}
section[data-testid="stSidebar"] hr {
    border-color: #52B788 !important;
}

/* Main background */
.main { background-color: #F8FAF9; }

/* Hero banner */
.hero-banner {
    background: linear-gradient(135deg, #1B4332 0%, #2D6A4F 50%, #40916C 100%);
    border-radius: 16px;
    padding: 36px 40px;
    margin-bottom: 28px;
    position: relative;
    overflow: hidden;
}
.hero-banner::before {
    content: '';
    position: absolute;
    top: -40px; right: -40px;
    width: 200px; height: 200px;
    background: rgba(82,183,136,0.15);
    border-radius: 50%;
}
.hero-title {
    font-family: 'DM Serif Display', serif;
    font-size: 2.6rem;
    color: #FFFFFF;
    margin: 0 0 6px 0;
    line-height: 1.15;
}
.hero-sub {
    font-size: 1rem;
    color: #B7E4C7;
    margin: 0;
    font-weight: 300;
    letter-spacing: 0.3px;
}
.hero-badge {
    display: inline-block;
    background: rgba(255,255,255,0.15);
    border: 1px solid rgba(255,255,255,0.3);
    border-radius: 20px;
    padding: 4px 14px;
    font-size: 0.8rem;
    color: #D8F3DC;
    margin-bottom: 14px;
    letter-spacing: 1px;
    text-transform: uppercase;
}

/* KPI Cards */
.kpi-grid { display: flex; gap: 16px; flex-wrap: wrap; margin-bottom: 24px; }
.kpi-card {
    flex: 1; min-width: 150px;
    background: white;
    border-radius: 14px;
    padding: 20px 22px;
    border-left: 4px solid #52B788;
    box-shadow: 0 2px 12px rgba(27,67,50,0.07);
}
.kpi-value {
    font-family: 'DM Serif Display', serif;
    font-size: 2rem;
    color: #1B4332;
    line-height: 1;
    margin-bottom: 4px;
}
.kpi-label { font-size: 0.78rem; color: #6B9080; font-weight: 500; text-transform: uppercase; letter-spacing: 0.5px; }
.kpi-delta { font-size: 0.82rem; color: #52B788; font-weight: 600; margin-top: 6px; }

/* Section headers */
.section-header {
    font-family: 'DM Serif Display', serif;
    font-size: 1.5rem;
    color: #1B4332;
    margin: 28px 0 16px 0;
    padding-bottom: 8px;
    border-bottom: 2px solid #D8F3DC;
}

/* Insight boxes */
.insight-box {
    background: linear-gradient(135deg, #F0FFF4, #E8F5E9);
    border-left: 4px solid #2D6A4F;
    border-radius: 0 10px 10px 0;
    padding: 14px 18px;
    margin: 12px 0;
    font-size: 0.9rem;
    color: #1B4332;
    line-height: 1.6;
}
.insight-box b { color: #2D6A4F; }

/* Tab styling */
.stTabs [data-baseweb="tab-list"] {
    gap: 4px;
    background: white;
    border-radius: 12px;
    padding: 6px;
    box-shadow: 0 2px 8px rgba(0,0,0,0.06);
}
.stTabs [data-baseweb="tab"] {
    border-radius: 8px;
    padding: 8px 18px;
    font-weight: 500;
    font-size: 0.88rem;
    color: #6B9080;
}
.stTabs [aria-selected="true"] {
    background: #2D6A4F !important;
    color: white !important;
}

/* Metric override */
div[data-testid="metric-container"] {
    background: white;
    border-radius: 12px;
    padding: 16px;
    box-shadow: 0 2px 8px rgba(0,0,0,0.05);
    border-top: 3px solid #52B788;
}
</style>
""", unsafe_allow_html=True)

# ── COLOUR PALETTE ─────────────────────────────────────────────────────────────
COLORS = {
    'primary':   '#2D6A4F',
    'secondary': '#52B788',
    'accent':    '#D4A853',
    'light':     '#95D5B2',
    'sage':      '#B7E4C7',
    'dark':      '#1B4332',
    'muted':     '#6B9080',
    'cream':     '#F5F0E8',
}
PALETTE = ['#2D6A4F','#52B788','#D4A853','#95D5B2','#40916C','#B7E4C7','#74C69D','#1B4332']
DIVERGING = px.colors.diverging.RdYlGn

# ── LOAD DATA ─────────────────────────────────────────────────────────────────
@st.cache_data
def load_data():
    df = pd.read_csv('GlowGreen_SAS_JMP_Ready.csv', encoding='utf-8-sig')
    return df

df = load_data()

# ── SIDEBAR ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div style='text-align:center; padding: 10px 0 20px 0;'>
        <div style='font-size:2.8rem;'>🌿</div>
        <div style='font-family:"DM Serif Display",serif; font-size:1.4rem; color:white; line-height:1.2;'>GlowGreen</div>
        <div style='font-size:0.75rem; color:#95D5B2; letter-spacing:1px; text-transform:uppercase;'>Analytics Dashboard</div>
    </div>
    """, unsafe_allow_html=True)
    st.markdown("---")

    st.markdown("<div style='font-size:0.75rem; color:#95D5B2; letter-spacing:1px; text-transform:uppercase; margin-bottom:8px;'>🔽 Filters</div>", unsafe_allow_html=True)

    city_tier_filter = st.multiselect(
        "City Tier", options=df['City_Tier'].unique().tolist(),
        default=df['City_Tier'].unique().tolist())

    gender_filter = st.multiselect(
        "Gender", options=df['Gender'].unique().tolist(),
        default=df['Gender'].unique().tolist())

    income_order = ['Below ₹25,000','₹25,000–₹50,000','₹50,000–₹1,00,000','Above ₹1,00,000']
    income_options = [i for i in income_order if i in df['Monthly_Household_Income'].unique()]
    income_filter = st.multiselect(
        "Income Bracket", options=income_options, default=income_options)

    age_range = st.slider("Age Range", int(df['Age'].min()), int(df['Age'].max()),
                          (int(df['Age'].min()), int(df['Age'].max())))

    st.markdown("---")
    st.markdown(f"<div style='font-size:0.8rem; color:#95D5B2;'>📊 Showing <b style='color:white;'>{{n}}</b> of {len(df)} respondents</div>".replace('{n}', '...'), unsafe_allow_html=True)
    st.markdown("<div style='font-size:0.72rem; color:#6B9080; margin-top:16px;'>GlowGreen Consumer Survey<br>Pan-India · March 2025<br>n = 2,058 (cleaned)</div>", unsafe_allow_html=True)

# ── APPLY FILTERS ─────────────────────────────────────────────────────────────
dff = df[
    df['City_Tier'].isin(city_tier_filter) &
    df['Gender'].isin(gender_filter) &
    df['Monthly_Household_Income'].isin(income_filter) &
    df['Age'].between(age_range[0], age_range[1])
].copy()

n = len(dff)

# ── HERO BANNER ───────────────────────────────────────────────────────────────
st.markdown(f"""
<div class="hero-banner">
    <div class="hero-badge">🌿 Business Validation Dashboard</div>
    <div class="hero-title">GlowGreen Sustainable Skincare</div>
    <div class="hero-sub">D2C Brand · Pan-India Consumer Survey Analysis · {n:,} respondents in view</div>
</div>
""", unsafe_allow_html=True)

# ── TABS ──────────────────────────────────────────────────────────────────────
tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    "📊 Overview",
    "👥 Demographics",
    "🌱 Eco & Behaviour",
    "🔗 Correlations",
    "🚀 Sales Pipeline",
    "🗺️ City Analysis",
])

# ═══════════════════════════════════════════════════════════════════════════════
# TAB 1 — OVERVIEW
# ═══════════════════════════════════════════════════════════════════════════════
with tab1:
    # KPI row
    nps_val = round((len(dff[dff['NPS_Score_0to10']>=9]) - len(dff[dff['NPS_Score_0to10']<=6])) / n * 100, 1) if n > 0 else 0
    avg_spend = int(dff['Current_Monthly_Skincare_Spend_INR'].mean()) if n > 0 else 0
    pct_positive_intent = round(dff['Positive_Trial_Intent'].mean()*100, 1) if n > 0 else 0
    pct_switchers = round(dff['Switching_Risk'].mean()*100, 1) if n > 0 else 0
    avg_eco = round(dff['Eco_Awareness_Score_1to5'].mean(), 2) if n > 0 else 0
    pct_sub = round(dff['Subscription_Code'].isin([3,4]).mean()*100 if 'Subscription_Code' in dff.columns else 0, 1)

    c1, c2, c3, c4, c5, c6 = st.columns(6)
    with c1:
        st.metric("Respondents", f"{n:,}", help="After filters applied")
    with c2:
        st.metric("NPS Score", f"{nps_val}", delta="Market Gap ↑" if nps_val < 0 else None)
    with c3:
        st.metric("Avg Monthly Spend", f"₹{avg_spend:,}")
    with c4:
        st.metric("Trial Intent (+ve)", f"{pct_positive_intent}%")
    with c5:
        st.metric("Switching Risk", f"{pct_switchers}%", delta="High opportunity" if pct_switchers > 30 else None)
    with c6:
        st.metric("Eco Awareness", f"{avg_eco}/5")

    st.markdown("---")

    col_l, col_r = st.columns([1.1, 1])

    with col_l:
        st.markdown('<div class="section-header">NPS Distribution</div>', unsafe_allow_html=True)
        nps_counts = dff['NPS_Score_0to10'].round().value_counts().sort_index().reset_index()
        nps_counts.columns = ['Score','Count']
        nps_counts['Segment'] = nps_counts['Score'].apply(
            lambda x: 'Detractor (0–6)' if x<=6 else ('Passive (7–8)' if x<=8 else 'Promoter (9–10)'))
        color_map = {'Detractor (0–6)':'#C0392B','Passive (7–8)':'#D4A853','Promoter (9–10)':'#2D6A4F'}
        fig_nps = px.bar(nps_counts, x='Score', y='Count', color='Segment',
                         color_discrete_map=color_map,
                         text='Count', template='plotly_white')
        fig_nps.update_traces(textposition='outside', textfont_size=11)
        fig_nps.update_layout(
            plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)',
            legend=dict(orientation='h', yanchor='bottom', y=1.02, xanchor='left', x=0),
            margin=dict(t=40, b=20, l=0, r=0), height=330,
            xaxis_title='NPS Score', yaxis_title='Respondents',
            font=dict(family='DM Sans'))
        st.plotly_chart(fig_nps, use_container_width=True)

        st.markdown(f"""<div class="insight-box">
        <b>Market Opportunity:</b> With an NPS of <b>{nps_val}</b>, existing brands are failing to delight consumers.
        The {round(len(dff[dff['NPS_Score_0to10']<=6])/n*100,1)}% detractor base represents GlowGreen's
        most immediately convertible audience — actively seeking alternatives.
        </div>""", unsafe_allow_html=True)

    with col_r:
        st.markdown('<div class="section-header">Purchase Channel Preference</div>', unsafe_allow_html=True)
        ch = dff['Preferred_Purchase_Channel'].value_counts().reset_index()
        ch.columns = ['Channel','Count']
        fig_ch = px.pie(ch, names='Channel', values='Count',
                        color_discrete_sequence=PALETTE,
                        hole=0.45, template='plotly_white')
        fig_ch.update_traces(textposition='outside', textinfo='percent+label',
                              pull=[0.05]*len(ch))
        fig_ch.update_layout(
            showlegend=False,
            margin=dict(t=10, b=10, l=10, r=10), height=330,
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(family='DM Sans'))
        st.plotly_chart(fig_ch, use_container_width=True)

        st.markdown("""<div class="insight-box">
        <b>Channel Strategy:</b> Amazon/Flipkart & Nykaa/Purplle together command ~49% of preference.
        Instagram social commerce at 22% validates an influencer-led D2C launch.
        </div>""", unsafe_allow_html=True)

    # Bottom row
    st.markdown('<div class="section-header">Trial Intent Overview</div>', unsafe_allow_html=True)
    col_a, col_b = st.columns(2)

    with col_a:
        intent_order = ['Definitely would try','Probably would try','Neutral','Probably not','Definitely not']
        ti = dff['Trial_Intent'].value_counts().reindex(intent_order).fillna(0).reset_index()
        ti.columns = ['Intent','Count']
        ti['Pct'] = (ti['Count']/n*100).round(1)
        colors_intent = [COLORS['primary'], COLORS['secondary'], COLORS['accent'],
                         '#E07B54','#C0392B']
        fig_ti = px.bar(ti, x='Pct', y='Intent', orientation='h',
                        color='Intent', color_discrete_sequence=colors_intent,
                        text=ti['Pct'].apply(lambda x: f'{x}%'),
                        template='plotly_white')
        fig_ti.update_traces(textposition='outside', showlegend=False)
        fig_ti.update_layout(margin=dict(t=10,b=10,l=0,r=60), height=280,
                             xaxis_title='% of Respondents', yaxis_title='',
                             paper_bgcolor='rgba(0,0,0,0)',
                             plot_bgcolor='rgba(0,0,0,0)',
                             font=dict(family='DM Sans'))
        st.plotly_chart(fig_ti, use_container_width=True)

    with col_b:
        heard = dff['Heard_of_Sustainable_Skincare'].value_counts().reset_index()
        heard.columns = ['Status','Count']
        fig_heard = px.pie(heard, names='Status', values='Count',
                           color_discrete_sequence=[COLORS['primary'],COLORS['secondary'],COLORS['accent']],
                           hole=0.5, template='plotly_white',
                           title='Awareness of Sustainable Skincare')
        fig_heard.update_layout(margin=dict(t=40,b=10,l=0,r=0), height=280,
                                paper_bgcolor='rgba(0,0,0,0)',
                                font=dict(family='DM Sans'))
        st.plotly_chart(fig_heard, use_container_width=True)

# ═══════════════════════════════════════════════════════════════════════════════
# TAB 2 — DEMOGRAPHICS
# ═══════════════════════════════════════════════════════════════════════════════
with tab2:
    st.markdown('<div class="section-header">Demographic Profile</div>', unsafe_allow_html=True)

    c1, c2 = st.columns(2)

    with c1:
        # Age histogram
        fig_age = px.histogram(dff, x='Age', nbins=25,
                               color_discrete_sequence=[COLORS['primary']],
                               template='plotly_white',
                               title='Age Distribution')
        mean_age = dff['Age'].mean()
        fig_age.add_vline(x=mean_age, line_dash='dash', line_color=COLORS['accent'],
                          annotation_text=f'Mean: {mean_age:.1f}',
                          annotation_position='top right')
        fig_age.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
                               bargap=0.05, margin=dict(t=50,b=20,l=0,r=0),
                               font=dict(family='DM Sans'))
        st.plotly_chart(fig_age, use_container_width=True)

    with c2:
        # Gender donut
        gc = dff['Gender'].value_counts().reset_index()
        gc.columns = ['Gender','Count']
        fig_g = px.pie(gc, names='Gender', values='Count',
                       color_discrete_sequence=[COLORS['primary'], COLORS['secondary'], COLORS['accent']],
                       hole=0.55, template='plotly_white', title='Gender Distribution')
        fig_g.update_layout(paper_bgcolor='rgba(0,0,0,0)', margin=dict(t=50,b=10),
                             font=dict(family='DM Sans'))
        st.plotly_chart(fig_g, use_container_width=True)

    c3, c4 = st.columns(2)

    with c3:
        # Income distribution
        inc_order = ['Below ₹25,000','₹25,000–₹50,000','₹50,000–₹1,00,000','Above ₹1,00,000']
        inc = dff['Monthly_Household_Income'].value_counts().reindex(inc_order).fillna(0).reset_index()
        inc.columns = ['Income','Count']
        inc['Pct'] = (inc['Count']/n*100).round(1)
        fig_inc = px.bar(inc, x='Income', y='Count',
                         color='Income', color_discrete_sequence=PALETTE,
                         text=inc['Pct'].apply(lambda x: f'{x}%'),
                         template='plotly_white', title='Income Distribution')
        fig_inc.update_traces(textposition='outside', showlegend=False)
        fig_inc.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
                               xaxis_tickangle=-20, margin=dict(t=50,b=60,l=0,r=0),
                               font=dict(family='DM Sans'))
        st.plotly_chart(fig_inc, use_container_width=True)

    with c4:
        # Education
        edu_order = ['High School','Undergraduate','Postgraduate','Doctoral']
        edu = dff['Education'].value_counts().reindex(edu_order).fillna(0).reset_index()
        edu.columns = ['Education','Count']
        fig_edu = px.bar(edu, x='Count', y='Education', orientation='h',
                         color='Education', color_discrete_sequence=PALETTE,
                         template='plotly_white', title='Education Level')
        fig_edu.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
                               showlegend=False, margin=dict(t=50,b=10,l=0,r=0),
                               font=dict(family='DM Sans'))
        st.plotly_chart(fig_edu, use_container_width=True)

    # Occupation & Skin Type
    c5, c6 = st.columns(2)
    with c5:
        occ = dff['Occupation'].value_counts().reset_index()
        occ.columns = ['Occupation','Count']
        fig_occ = px.bar(occ, x='Count', y='Occupation', orientation='h',
                         color='Occupation', color_discrete_sequence=PALETTE,
                         template='plotly_white', title='Occupation Breakdown')
        fig_occ.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
                               showlegend=False, margin=dict(t=50,b=10,l=0,r=0),
                               font=dict(family='DM Sans'))
        st.plotly_chart(fig_occ, use_container_width=True)

    with c6:
        sk = dff['Skin_Type'].value_counts().reset_index()
        sk.columns = ['Skin Type','Count']
        fig_sk = px.pie(sk, names='Skin Type', values='Count',
                        color_discrete_sequence=PALETTE, hole=0.4,
                        template='plotly_white', title='Skin Type Distribution')
        fig_sk.update_layout(paper_bgcolor='rgba(0,0,0,0)', margin=dict(t=50,b=10),
                             font=dict(family='DM Sans'))
        st.plotly_chart(fig_sk, use_container_width=True)

    # Spend by income boxplot
    st.markdown('<div class="section-header">Monthly Skincare Spend by Income Bracket</div>', unsafe_allow_html=True)
    fig_box = px.box(dff, x='Monthly_Household_Income', y='Current_Monthly_Skincare_Spend_INR',
                     color='Monthly_Household_Income',
                     category_orders={'Monthly_Household_Income': inc_order},
                     color_discrete_sequence=PALETTE,
                     template='plotly_white',
                     labels={'Current_Monthly_Skincare_Spend_INR':'Monthly Spend (₹)',
                             'Monthly_Household_Income':'Income Bracket'})
    fig_box.update_layout(showlegend=False, paper_bgcolor='rgba(0,0,0,0)',
                           plot_bgcolor='rgba(0,0,0,0)', height=360,
                           font=dict(family='DM Sans'),
                           margin=dict(t=20,b=60,l=0,r=0))
    st.plotly_chart(fig_box, use_container_width=True)
    st.markdown("""<div class="insight-box">
    <b>Key Finding (r = 0.83):</b> Income is the strongest single predictor of skincare spend.
    Median spend jumps from ~₹400 (lowest bracket) to ~₹2,800 (highest), validating a
    3-tier product line strategy for GlowGreen.
    </div>""", unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════════════════════
# TAB 3 — ECO & BEHAVIOUR
# ═══════════════════════════════════════════════════════════════════════════════
with tab3:
    st.markdown('<div class="section-header">Sustainability & Purchase Behaviour</div>', unsafe_allow_html=True)

    c1, c2 = st.columns(2)

    with c1:
        # Eco awareness by education
        eco_edu = dff.groupby('Education')['Eco_Awareness_Score_1to5'].mean().reindex(
            ['High School','Undergraduate','Postgraduate','Doctoral']).reset_index()
        eco_edu.columns = ['Education','Avg Eco Score']
        fig_ee = px.bar(eco_edu, x='Education', y='Avg Eco Score',
                        color='Education', color_discrete_sequence=PALETTE,
                        text=eco_edu['Avg Eco Score'].round(2),
                        template='plotly_white',
                        title='Avg Eco Awareness Score by Education Level')
        fig_ee.update_traces(textposition='outside')
        fig_ee.update_yaxes(range=[0, 5])
        fig_ee.update_layout(showlegend=False, paper_bgcolor='rgba(0,0,0,0)',
                              plot_bgcolor='rgba(0,0,0,0)',
                              font=dict(family='DM Sans'), margin=dict(t=50,b=20,l=0,r=0))
        st.plotly_chart(fig_ee, use_container_width=True)

    with c2:
        # WTP premium distribution
        wtp_order = ['0%','5–10%','11–20%','21–30%','>30%']
        wtp = dff['Willingness_to_Pay_Premium'].value_counts().reindex(wtp_order).fillna(0).reset_index()
        wtp.columns = ['WTP','Count']
        wtp['Pct'] = (wtp['Count']/n*100).round(1)
        fig_wtp = px.bar(wtp, x='WTP', y='Pct',
                         color='WTP', color_discrete_sequence=PALETTE,
                         text=wtp['Pct'].apply(lambda x: f'{x}%'),
                         template='plotly_white',
                         title='Willingness to Pay Sustainability Premium')
        fig_wtp.update_traces(textposition='outside', showlegend=False)
        fig_wtp.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
                               font=dict(family='DM Sans'), margin=dict(t=50,b=10,l=0,r=0),
                               yaxis_title='% of Respondents', xaxis_title='Premium Range')
        st.plotly_chart(fig_wtp, use_container_width=True)

    c3, c4 = st.columns(2)

    with c3:
        # Ingredient preference by tier
        ing = dff.groupby(['City_Tier','Preferred_Ingredients']).size().reset_index(name='Count')
        ing_total = ing.groupby('City_Tier')['Count'].transform('sum')
        ing['Pct'] = (ing['Count']/ing_total*100).round(1)
        fig_ing = px.bar(ing, x='Preferred_Ingredients', y='Pct', color='City_Tier',
                         barmode='group', color_discrete_sequence=[COLORS['primary'], COLORS['accent']],
                         template='plotly_white',
                         title='Ingredient Preference: Tier 1 vs Tier 2 (%)',
                         labels={'Pct':'% of Tier','Preferred_Ingredients':'Ingredient Type'})
        fig_ing.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
                               xaxis_tickangle=-20, font=dict(family='DM Sans'),
                               margin=dict(t=50,b=80,l=0,r=0),
                               legend=dict(orientation='h',y=1.12))
        st.plotly_chart(fig_ing, use_container_width=True)

    with c4:
        # Packaging preference
        pkg = dff['Preferred_Packaging'].value_counts().reset_index()
        pkg.columns = ['Packaging','Count']
        fig_pkg = px.pie(pkg, names='Packaging', values='Count',
                         color_discrete_sequence=PALETTE, hole=0.42,
                         template='plotly_white', title='Packaging Preference')
        fig_pkg.update_layout(paper_bgcolor='rgba(0,0,0,0)', font=dict(family='DM Sans'),
                               margin=dict(t=50,b=10))
        st.plotly_chart(fig_pkg, use_container_width=True)

    # Eco awareness vs WTP heatmap
    st.markdown('<div class="section-header">Eco Awareness × WTP Premium (Heatmap)</div>', unsafe_allow_html=True)
    dff2 = dff.copy()
    dff2['Eco_Round'] = dff2['Eco_Awareness_Score_1to5'].round().clip(1,5).astype(int)
    heat = dff2.groupby(['Eco_Round','Willingness_to_Pay_Premium']).size().unstack(fill_value=0)
    heat = heat[[c for c in wtp_order if c in heat.columns]]
    heat_pct = (heat.div(heat.sum(axis=1), axis=0)*100).round(1)
    fig_heat = px.imshow(heat_pct,
                         color_continuous_scale='Greens',
                         aspect='auto', text_auto='.1f',
                         template='plotly_white',
                         labels=dict(x='WTP Premium', y='Eco Awareness Score', color='%'),
                         title='% of Respondents per Eco Score willing to pay each premium level')
    fig_heat.update_layout(paper_bgcolor='rgba(0,0,0,0)', font=dict(family='DM Sans'),
                            margin=dict(t=60,b=20,l=0,r=0), height=320)
    st.plotly_chart(fig_heat, use_container_width=True)

    st.markdown("""<div class="insight-box">
    <b>Eco Education → Premium Pricing:</b> As Eco Awareness Score rises from 1 to 5, the proportion
    willing to pay >20% premium increases dramatically. This validates a content-first, education-led
    marketing strategy for GlowGreen — awareness building directly lifts willingness to pay.
    </div>""", unsafe_allow_html=True)

    # Social platform & brand trust
    c5, c6 = st.columns(2)
    with c5:
        soc = dff['Primary_Social_Platform'].value_counts().reset_index()
        soc.columns = ['Platform','Count']
        fig_soc = px.bar(soc, x='Count', y='Platform', orientation='h',
                         color='Platform', color_discrete_sequence=PALETTE,
                         text='Count', template='plotly_white',
                         title='Primary Social Media Platform')
        fig_soc.update_layout(showlegend=False, paper_bgcolor='rgba(0,0,0,0)',
                               plot_bgcolor='rgba(0,0,0,0)', font=dict(family='DM Sans'),
                               margin=dict(t=50,b=10,l=0,r=0))
        st.plotly_chart(fig_soc, use_container_width=True)

    with c6:
        trust = dff['Primary_Brand_Trust_Source'].value_counts().reset_index()
        trust.columns = ['Source','Count']
        fig_trust = px.pie(trust, names='Source', values='Count',
                           color_discrete_sequence=PALETTE, hole=0.4,
                           template='plotly_white', title='Brand Trust Source')
        fig_trust.update_layout(paper_bgcolor='rgba(0,0,0,0)', font=dict(family='DM Sans'),
                                 margin=dict(t=50,b=10))
        st.plotly_chart(fig_trust, use_container_width=True)

# ═══════════════════════════════════════════════════════════════════════════════
# TAB 4 — CORRELATIONS
# ═══════════════════════════════════════════════════════════════════════════════
with tab4:
    st.markdown('<div class="section-header">Correlation Analysis</div>', unsafe_allow_html=True)

    corr_cols = {
        'Age': 'Age',
        'Income_Code': 'Income',
        'Education_Code': 'Education',
        'Current_Monthly_Skincare_Spend_INR': 'Skincare Spend',
        'Eco_Awareness_Score_1to5': 'Eco Awareness',
        'WTP_Premium_Code': 'WTP Premium',
        'Trial_Intent_Code': 'Trial Intent',
        'Satisfaction_Current_Brand_1to5': 'Satisfaction',
        'Likelihood_to_Switch_1to5': 'Switch Likelihood',
        'NPS_Score_0to10': 'NPS Score',
        'Subscription_Code': 'Subscription Interest',
        'Influencer_Trust_1to5': 'Influencer Trust',
    }

    corr_df = dff[list(corr_cols.keys())].rename(columns=corr_cols)
    cm = corr_df.corr().round(3)

    fig_corr = px.imshow(cm,
                         color_continuous_scale='RdYlGn',
                         zmin=-1, zmax=1,
                         text_auto='.2f',
                         aspect='auto',
                         template='plotly_white',
                         title='Pearson Correlation Matrix – 12 Key Variables')
    fig_corr.update_layout(
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(family='DM Sans', size=11),
        margin=dict(t=60, b=20, l=0, r=0),
        height=520,
        coloraxis_colorbar=dict(title='r value', tickvals=[-1,-0.5,0,0.5,1])
    )
    st.plotly_chart(fig_corr, use_container_width=True)

    # Key correlation pairs
    st.markdown('<div class="section-header">Deep-Dive: Key Variable Pairs</div>', unsafe_allow_html=True)

    pairs = [
        ('Income_Code', 'Current_Monthly_Skincare_Spend_INR', 'Income', 'Monthly Spend (₹)', COLORS['primary']),
        ('Satisfaction_Current_Brand_1to5', 'Likelihood_to_Switch_1to5', 'Satisfaction (Current Brand)', 'Switch Likelihood', COLORS['accent']),
        ('Eco_Awareness_Score_1to5', 'Trial_Intent_Code', 'Eco Awareness Score', 'Trial Intent (Encoded)', COLORS['secondary']),
    ]

    for i in range(0, len(pairs), 3):
        cols = st.columns(3)
        for j, (xc, yc, xl, yl, color) in enumerate(pairs[i:i+3]):
            with cols[j]:
                r, p = stats.pearsonr(dff[xc].dropna(), dff[yc].dropna())
                fig_sc = px.scatter(dff.sample(min(500, n), random_state=42),
                                    x=xc, y=yc,
                                    trendline='ols',
                                    color_discrete_sequence=[color],
                                    opacity=0.45,
                                    template='plotly_white',
                                    labels={xc: xl, yc: yl},
                                    title=f'r = {r:.3f} {"***" if p < 0.001 else "**" if p < 0.01 else "*"}')
                fig_sc.update_traces(marker=dict(size=5))
                fig_sc.update_layout(paper_bgcolor='rgba(0,0,0,0)',
                                      plot_bgcolor='rgba(0,0,0,0)',
                                      font=dict(family='DM Sans'),
                                      height=300, margin=dict(t=50,b=20,l=0,r=0))
                st.plotly_chart(fig_sc, use_container_width=True)

    # Correlation summary table
    st.markdown('<div class="section-header">Correlation Summary Table</div>', unsafe_allow_html=True)
    summary_pairs = [
        ('Income → Skincare Spend', 0.83, '< 0.001', 'Strong +'  , 'Income-based product tiering is validated'),
        ('Satisfaction → Switch Likelihood', -0.86, '< 0.001', 'Strong −', 'Dissatisfied customers are near-certain switchers'),
        ('NPS ↔ Satisfaction', 0.72, '< 0.001', 'Strong +', 'Satisfaction drives brand advocacy'),
        ('Income → WTP Premium', 0.38, '< 0.001', 'Moderate +', 'Premium pricing viable for ₹50K+ households'),
        ('Eco Awareness → Trial Intent', 0.29, '< 0.001', 'Moderate +', 'Eco education lifts trial intent'),
        ('Age → Skincare Spend', 0.00, '0.997', 'None', 'Age alone should not drive targeting'),
        ('Eco Awareness → Skincare Spend', -0.03, '0.633', 'None', 'High spenders are not automatically eco-conscious'),
    ]
    df_summ = pd.DataFrame(summary_pairs, columns=['Variable Pair','r','p-value','Strength','Business Implication'])
    st.dataframe(df_summ, use_container_width=True, hide_index=True)

# ═══════════════════════════════════════════════════════════════════════════════
# TAB 5 — SALES PIPELINE
# ═══════════════════════════════════════════════════════════════════════════════
with tab5:
    st.markdown('<div class="section-header">D2C Sales Pipeline Validation</div>', unsafe_allow_html=True)

    n_aware   = len(dff[dff['Heard_of_Sustainable_Skincare'] != 'No, not aware'])
    n_intent  = len(dff[dff['Positive_Trial_Intent'] == 1])
    n_channel = len(dff[dff['Preferred_Purchase_Channel'].isin(
        ['Brand website (D2C)','Instagram / Social commerce','Nykaa / Purplle'])])
    n_sub     = len(dff[dff['Subscription_Interest'].isin(['Very interested','Somewhat interested'])])

    stages = ['Total Sample','Aware of\nSustainable Skincare',
              'Positive\nTrial Intent','Reachable via\nD2C Channel','Subscription\nInterested']
    values = [n, n_aware, n_intent, n_channel, n_sub]
    pcts   = [100] + [round(v/n*100, 1) for v in values[1:]]

    fig_funnel = go.Figure(go.Funnel(
        y=stages, x=values,
        textinfo='value+percent initial',
        textfont=dict(size=13, family='DM Sans'),
        marker=dict(color=[COLORS['dark'], COLORS['primary'], COLORS['secondary'],
                            COLORS['light'], COLORS['accent']]),
        connector=dict(line=dict(color='#B7E4C7', width=2, dash='dot')),
    ))
    fig_funnel.update_layout(
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(family='DM Sans'),
        height=420,
        margin=dict(t=20,b=20,l=60,r=60),
        title=dict(text='GlowGreen Acquisition Funnel (Survey-Derived)', x=0.5,
                   font=dict(size=15, family='DM Serif Display'))
    )
    st.plotly_chart(fig_funnel, use_container_width=True)

    # Pipeline metrics
    m1, m2, m3, m4 = st.columns(4)
    with m1: st.metric("Aware Audience", f"{n_aware:,}", f"{round(n_aware/n*100,1)}% of sample")
    with m2: st.metric("Positive Trial Intent", f"{n_intent:,}", f"{round(n_intent/n*100,1)}% of sample")
    with m3: st.metric("Reachable via D2C/Social", f"{n_channel:,}", f"{round(n_channel/n*100,1)}% of sample")
    with m4: st.metric("Subscription-Ready", f"{n_sub:,}", f"{round(n_sub/n*100,1)}% of sample")

    st.markdown("---")
    c1, c2 = st.columns(2)

    with c1:
        # Subscription interest by income
        sub_inc = dff.groupby(['Monthly_Household_Income','Subscription_Interest']).size().reset_index(name='Count')
        sub_total = sub_inc.groupby('Monthly_Household_Income')['Count'].transform('sum')
        sub_inc['Pct'] = (sub_inc['Count']/sub_total*100).round(1)
        sub_order = ['Very interested','Somewhat interested','Neutral','Not interested']
        inc_order = ['Below ₹25,000','₹25,000–₹50,000','₹50,000–₹1,00,000','Above ₹1,00,000']
        fig_sub = px.bar(sub_inc, x='Monthly_Household_Income', y='Pct',
                         color='Subscription_Interest',
                         category_orders={'Monthly_Household_Income': inc_order,
                                          'Subscription_Interest': sub_order},
                         color_discrete_sequence=PALETTE,
                         template='plotly_white',
                         labels={'Pct':'%','Monthly_Household_Income':'Income','Subscription_Interest':'Interest'},
                         title='Subscription Interest by Income Bracket (%)')
        fig_sub.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
                               font=dict(family='DM Sans'), xaxis_tickangle=-15,
                               margin=dict(t=50,b=60,l=0,r=0),
                               legend=dict(orientation='h', y=-0.3))
        st.plotly_chart(fig_sub, use_container_width=True)

    with c2:
        # Ideal price point
        price_order = ['Below ₹300','₹300–₹600','₹600–₹1,000','Above ₹1,000']
        pp = dff['Ideal_Price_Point_30ml_Serum'].value_counts().reindex(price_order).fillna(0).reset_index()
        pp.columns = ['Price Point','Count']
        pp['Pct'] = (pp['Count']/n*100).round(1)
        fig_pp = px.bar(pp, x='Price Point', y='Pct',
                        color='Price Point', color_discrete_sequence=PALETTE,
                        text=pp['Pct'].apply(lambda x: f'{x}%'),
                        template='plotly_white',
                        title='Ideal Price Point – 30ml Sustainable Serum')
        fig_pp.update_traces(textposition='outside', showlegend=False)
        fig_pp.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
                              font=dict(family='DM Sans'), margin=dict(t=50,b=20,l=0,r=0),
                              yaxis_title='% of Respondents')
        st.plotly_chart(fig_pp, use_container_width=True)

    # Certification importance
    st.markdown('<div class="section-header">Certification & Trust Signals</div>', unsafe_allow_html=True)
    c3, c4 = st.columns(2)

    with c3:
        cert_order = ['Extremely important','Important','Somewhat important','Not important']
        cert = dff['Certification_Importance'].value_counts().reindex(cert_order).fillna(0).reset_index()
        cert.columns = ['Importance','Count']
        cert['Pct'] = (cert['Count']/n*100).round(1)
        fig_cert = px.bar(cert, x='Importance', y='Pct',
                          color='Importance', color_discrete_sequence=PALETTE,
                          text=cert['Pct'].apply(lambda x: f'{x}%'),
                          template='plotly_white',
                          title='Importance of Organic / Cruelty-free Certification')
        fig_cert.update_traces(textposition='outside', showlegend=False)
        fig_cert.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
                                font=dict(family='DM Sans'), margin=dict(t=50,b=20,l=0,r=0),
                                yaxis_title='% of Respondents')
        st.plotly_chart(fig_cert, use_container_width=True)

    with c4:
        st.markdown('<div class="section-header">Pipeline Key Metrics</div>', unsafe_allow_html=True)
        nps_promoters = round(len(dff[dff['NPS_Score_0to10']>=9])/n*100,1)
        nps_detractors = round(len(dff[dff['NPS_Score_0to10']<=6])/n*100,1)
        nps_passives = round(100-nps_promoters-nps_detractors,1)
        pct_wtp_11plus = round(len(dff[dff['Willingness_to_Pay_Premium'].isin(['11–20%','21–30%','>30%'])])/n*100,1)
        pct_cert_imp = round(len(dff[dff['Certification_Importance'].isin(['Extremely important','Important'])])/n*100,1)

        metrics_data = {
            'Metric': ['Net Promoter Score','NPS: Promoters','NPS: Passives','NPS: Detractors',
                       'WTP ≥ 11% Premium','Certification Important/Very Important',
                       'Avg Eco Awareness','Avg Influencer Trust'],
            'Value': [f'{nps_val}', f'{nps_promoters}%', f'{nps_passives}%', f'{nps_detractors}%',
                      f'{pct_wtp_11plus}%', f'{pct_cert_imp}%',
                      f'{round(dff["Eco_Awareness_Score_1to5"].mean(),2)}/5',
                      f'{round(dff["Influencer_Trust_1to5"].mean(),2)}/5'],
        }
        st.dataframe(pd.DataFrame(metrics_data), use_container_width=True, hide_index=True, height=320)

# ═══════════════════════════════════════════════════════════════════════════════
# TAB 6 — CITY ANALYSIS
# ═══════════════════════════════════════════════════════════════════════════════
with tab6:
    st.markdown('<div class="section-header">City & Geographic Analysis</div>', unsafe_allow_html=True)

    city_metrics = dff.groupby('City').agg(
        Respondents=('Respondent_ID','count'),
        Avg_Spend=('Current_Monthly_Skincare_Spend_INR','mean'),
        Avg_Eco=('Eco_Awareness_Score_1to5','mean'),
        Avg_NPS=('NPS_Score_0to10','mean'),
        Pct_Positive_Intent=('Positive_Trial_Intent','mean'),
        City_Tier=('City_Tier','first'),
    ).reset_index()
    city_metrics['Avg_Spend'] = city_metrics['Avg_Spend'].round(0).astype(int)
    city_metrics['Avg_Eco'] = city_metrics['Avg_Eco'].round(2)
    city_metrics['Avg_NPS'] = city_metrics['Avg_NPS'].round(2)
    city_metrics['Pct_Positive_Intent'] = (city_metrics['Pct_Positive_Intent']*100).round(1)

    c1, c2 = st.columns(2)

    with c1:
        fig_city_spend = px.bar(city_metrics.sort_values('Avg_Spend', ascending=True),
                                x='Avg_Spend', y='City',
                                color='City_Tier',
                                color_discrete_map={'Tier 1': COLORS['primary'], 'Tier 2': COLORS['accent']},
                                orientation='h', template='plotly_white',
                                text='Avg_Spend',
                                labels={'Avg_Spend':'Avg Monthly Spend (₹)','City_Tier':'Tier'},
                                title='Average Monthly Skincare Spend by City')
        fig_city_spend.update_traces(texttemplate='₹%{text:,}', textposition='outside')
        fig_city_spend.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
                                      font=dict(family='DM Sans'), height=500,
                                      margin=dict(t=50,b=20,l=0,r=80))
        st.plotly_chart(fig_city_spend, use_container_width=True)

    with c2:
        fig_city_nps = px.bar(city_metrics.sort_values('Avg_NPS', ascending=True),
                              x='Avg_NPS', y='City',
                              color='City_Tier',
                              color_discrete_map={'Tier 1': COLORS['primary'], 'Tier 2': COLORS['accent']},
                              orientation='h', template='plotly_white',
                              text='Avg_NPS',
                              labels={'Avg_NPS':'Avg NPS Score (0–10)','City_Tier':'Tier'},
                              title='Average NPS Score by City')
        fig_city_nps.update_traces(texttemplate='%{text:.2f}', textposition='outside')
        fig_city_nps.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
                                    font=dict(family='DM Sans'), height=500,
                                    margin=dict(t=50,b=20,l=0,r=60))
        st.plotly_chart(fig_city_nps, use_container_width=True)

    # Bubble chart: Spend vs NPS by city
    st.markdown('<div class="section-header">City Opportunity Matrix: Avg Spend vs NPS Score</div>', unsafe_allow_html=True)
    fig_bubble = px.scatter(city_metrics,
                            x='Avg_NPS', y='Avg_Spend',
                            size='Respondents', color='City_Tier',
                            text='City',
                            color_discrete_map={'Tier 1': COLORS['primary'], 'Tier 2': COLORS['accent']},
                            template='plotly_white',
                            labels={'Avg_NPS':'Avg NPS Score','Avg_Spend':'Avg Monthly Spend (₹)',
                                    'City_Tier':'City Tier'},
                            title='City Opportunity Matrix — Bubble size = number of respondents')
    fig_bubble.update_traces(textposition='top center', textfont_size=11)
    fig_bubble.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
                              font=dict(family='DM Sans'), height=480,
                              margin=dict(t=60,b=20,l=0,r=0))
    st.plotly_chart(fig_bubble, use_container_width=True)

    st.markdown("""<div class="insight-box">
    <b>Geographic Prioritisation:</b> Cities in the <b>bottom-left quadrant</b> (low NPS, low spend) are
    low-priority. Cities with <b>high spend + low NPS</b> (upper-left) represent GlowGreen's highest-value
    launch targets — consumers spending heavily but dissatisfied with current brands.
    Tier 1 cities (green) generally show higher spend; Tier 2 (gold) show opportunity for value-range entry.
    </div>""", unsafe_allow_html=True)

    # Full city table
    st.markdown('<div class="section-header">Full City Metrics Table</div>', unsafe_allow_html=True)
    city_display = city_metrics[['City','City_Tier','Respondents','Avg_Spend','Avg_Eco','Avg_NPS','Pct_Positive_Intent']].copy()
    city_display.columns = ['City','Tier','Respondents','Avg Spend (₹)','Avg Eco Score','Avg NPS','% Positive Trial Intent']
    city_display = city_display.sort_values('Avg Spend (₹)', ascending=False)
    st.dataframe(city_display, use_container_width=True, hide_index=True)

# ── FOOTER ────────────────────────────────────────────────────────────────────
st.markdown("---")
st.markdown("""
<div style='text-align:center; color:#6B9080; font-size:0.8rem; padding: 10px 0 20px 0;'>
    🌿 <b>GlowGreen Analytics Dashboard</b> &nbsp;·&nbsp;
    Data Analytics Assignment &nbsp;·&nbsp;
    GlowGreen Consumer Survey, Pan-India, March 2025 &nbsp;·&nbsp;
    n = 2,058 (cleaned) &nbsp;·&nbsp;
    Built with Streamlit & Plotly
</div>
""", unsafe_allow_html=True)

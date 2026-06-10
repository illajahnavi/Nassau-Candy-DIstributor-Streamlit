import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

print("test update")


st.set_page_config(
    page_title="Nassau Candy distributor Analysis",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>

/* KPI Cards */
div[data-testid="metric-container"] {
    background: linear-gradient(135deg, #1E293B, #334155);
    border: 2px solid #60A5FA;
    padding: 20px;
    border-radius: 18px;
    box-shadow: 0 8px 20px rgba(0,0,0,0.4);
}

/* KPI Label */
div[data-testid="metric-container"] label {
    color: #E2E8F0 !important;
    font-size: 16px !important;
    font-weight: 600 !important;
}

/* KPI Value */
div[data-testid="metric-container"] div[data-testid="stMetricValue"] {
    color: #60A5FA !important;
    font-size: 32px !important;
    font-weight: bold !important;
}

</style>
""", unsafe_allow_html=True)

#css block

st.markdown("""
<style>
/* ── Sidebar Filter Accent Override ── */

/* Selectbox & Multiselect selected highlight */
section[data-testid="stSidebar"] [data-baseweb="select"] [aria-selected="true"],
section[data-testid="stSidebar"] [data-baseweb="option"]:hover,
section[data-testid="stSidebar"] [data-baseweb="option"][aria-selected="true"] {
    background: linear-gradient(90deg, #1E3A5F 0%, #1A4A6B 100%) !important;
    color: #E0F0FF !important;
}

/* Multiselect tags/pills */
section[data-testid="stSidebar"] [data-baseweb="tag"] {
    background: linear-gradient(90deg, #1B3A5C 0%, #1E5070 100%) !important;
    color: #BAD9F5 !important;
    border: none !important;
}

/* Radio button selected dot */
section[data-testid="stSidebar"] [data-testid="stRadio"] input:checked + div,
section[data-testid="stSidebar"] input[type="radio"]:checked + label {
    color: #60A5FA !important;
}
section[data-testid="stSidebar"] [role="radio"][aria-checked="true"] {
    background: linear-gradient(135deg, #1D4ED8 0%, #0891B2 100%) !important;
    border-color: #3B82F6 !important;
}

/* Slider thumb & active track */
section[data-testid="stSidebar"] [data-testid="stSlider"] div[role="slider"] {
    background: linear-gradient(135deg, #2563EB 0%, #0891B2 100%) !important;
    border-color: #60A5FA !important;
}
section[data-testid="stSidebar"] [data-testid="stSlider"] [data-testid="stSliderTrackFill"] {
    background: linear-gradient(90deg, #1D4ED8 0%, #0EA5E9 100%) !important;
}

/* Checkbox checked state */
section[data-testid="stSidebar"] input[type="checkbox"]:checked + div {
    background: linear-gradient(135deg, #1D4ED8 0%, #0891B2 100%) !important;
    border-color: #3B82F6 !important;
}

/* Active/focused input border */
section[data-testid="stSidebar"] [data-baseweb="select"] div:focus-within,
section[data-testid="stSidebar"] [data-baseweb="input"]:focus-within {
    border-color: #3B82F6 !important;
    box-shadow: 0 0 0 2px rgba(59,130,246,0.2) !important;
}

/* Dropdown menu background */
[data-baseweb="popover"] ul,
[data-baseweb="menu"] {
    background: #0F172A !important;
    border: 1px solid #1E3A5F !important;
    border-radius: 8px !important;
}
[data-baseweb="menu"] li:hover {
    background: linear-gradient(90deg, #1E3A5F 0%, #1A4A6B 100%) !important;
}
</style>
""", unsafe_allow_html=True)

#load data


@st.cache_data
def load_data():
    store = pd.read_csv(r"C:\Users\jahna\Downloads\Nassau Candy Distributor.csv")
    store["Order Date"] = pd.to_datetime(store["Order Date"], dayfirst=True)

    # Add this line right below it:
    store["Month"] = store["Order Date"].dt.to_period("M").dt.to_timestamp()
    store.columns = store.columns.str.strip()
    store.write(store.columns.tolist())
    store.drop_duplicates(inplace=True)
def format_number(num):
    if num >= 1_000_000:
        return f"{num/1_000_000:.2f}M"
    elif num >= 1_000:
        return f"{num/1_000:.1f}K"
    else:
        return f"{num:.0f}" 
    
    store.columns = (
        store.columns
        .str.replace(' ','_')
        .str.replace('-','_')
    )
#feature engineering 
    
    store['Gross_Margin_%'] = (
        store['Gross_Profit'] / store['Sales']
    ) * 100

    store['Profit_Per_Unit'] = (
        store['Gross_Profit'] / store['Units']
    )

    store['Cost_Efficiency_%'] = (
        store['Gross_Profit'] / store['Cost']
    ) * 100

    store['Product_Performance'] = np.where(
        store['Gross_Profit'] > store['Gross_Profit'].median(),
        'Top Performer',
        'Needs Attention'
    )

    store['Sales_Category'] = pd.cut(
        store['Sales'],
        bins=[0,1000,5000,10000,store['Sales'].max()],
        labels=['Low','Medium','High','Very High']
    )

    return store
store = pd.read_csv(r"C:\Users\jahna\Downloads\Nassau Candy Distributor.csv")
store["Month"] = pd.to_datetime(store["Order Date"], dayfirst=True).dt.to_period("M").dt.to_timestamp()

prod_div = store.groupby(["Division", "Product Name"]).agg(
    Sales=("Sales", "sum"),
    Gross_Profit=("Gross Profit", "sum"),
    Cost=("Cost", "sum"),
    Units=("Units", "sum"),
).reset_index()
prod_div["Gross Margin %"] = (prod_div["Gross_Profit"] / prod_div["Sales"] * 100).round(1)


#SIDE BARS
st.sidebar.header("Dashboard Filters")


region = st.sidebar.multiselect(
    "Select Region",
    options=store['Region'].unique(),
    default = store['Region'].unique()
)

division = st.sidebar.multiselect(
    "Select Division",
    options=store['Division'].unique(),
    default=store['Division'].unique()
)

product = st.sidebar.multiselect(
    "Select Product",
    options=store['Product Name'].unique(),
    default=store['Product Name'].unique()
)

ship_mode = st.sidebar.multiselect(
    "Select Ship Mode",
    options=store['Ship Mode'].unique(),
    default=store['Ship Mode'].unique()
)



#header
st.title("Nassau Candy Distributor Analysis")
st.markdown("## Product Line Profitability & Margin Performance Analysis Dashboard ")


# create filtered data frame

filtered_df = store[
    (store["Region"].isin(region)) &
    (store["Division"].isin(division)) &
    (store["Product Name"].isin(product)) &
    (store["Ship Mode"].isin(ship_mode))
]
# DEBUG CHECK
st.write("Total Rows:", len(store))
st.write("Filtered Rows:", len(filtered_df))


# KPI section
# ==========================
# KPI CALCULATIONS
# ==========================

def format_number(num):

    if num >= 1_000_000:
        return f"{num/1_000_000:.2f}M"

    elif num >= 1_000:
        return f"{num/1_000:.1f}K"

    else:
        return f"{num:.0f}"


total_sales = filtered_df['Sales'].sum()


profit_per_unit = (
    filtered_df['Gross Profit'].sum()
    / filtered_df['Units'].sum()
)

gross_margin = (
    filtered_df['Gross Profit'].sum()
    / filtered_df['Sales'].sum()
) * 100

revenue_contribution = (
    filtered_df['Sales'].sum()
    / store['Sales'].sum()
) * 100

profit_contribution = (
    filtered_df['Gross Profit'].sum()
    / store['Gross Profit'].sum()
) * 100

# ==========================
# KPI SECTION
# ==========================

st.markdown("----")
st.subheader("Business Overview")

col1, col2, col3, col4, col5= st.columns(5)

# Total Sales
with col1:
    st.markdown(f"""
    <div style="
        background: linear-gradient(135deg,#0A192F,#2563EB);
        padding:20px;
        border-radius:18px;
        text-align:center;
        color:white;
        box-shadow:0px 6px 15px rgba(0,0,0,0.4);
    ">
        <h4>Total Sales</h4>
        <h2>${format_number(total_sales)}</h2>
    </div>
    """, unsafe_allow_html=True)


# Profit Per Unit
with col3:
    st.markdown(f"""
    <div style="
        background: linear-gradient(135deg,#581C87,#A855F7);
        padding:20px;
        border-radius:18px;
        text-align:center;
        color:white;
        box-shadow:0px 6px 15px rgba(0,0,0,0.4);
    ">
        <h4>Profit Per Unit</h4>
        <h2>${profit_per_unit:.2f}</h2>
    </div>
    """, unsafe_allow_html=True)

# Gross Margin %
with col4:
    st.markdown(f"""
    <div style="
        background: linear-gradient(135deg,#9A3412,#F97316);
        padding:20px;
        border-radius:18px;
        text-align:center;
        color:white;
        box-shadow:0px 6px 15px rgba(0,0,0,0.4);
    ">
        <h4>Gross Margin %</h4>
        <h2>{gross_margin:.1f}%</h2>
    </div>
    """, unsafe_allow_html=True)

    #revenue contribution

with col2:
    st.markdown(f"""
<div style="
    background: linear-gradient(135deg,#0A192F,#2563EB);
    padding:20px;
    border-radius:18px;
    text-align:center;
    color:white;
">
    <h4>Revenue Contribution</h4>
    <h2>{revenue_contribution:.1f}%</h2>
</div>
""", unsafe_allow_html=True)
    
with col3:
    st.markdown(f"""
    <div style="
        background: linear-gradient(135deg,#14532D,#22C55E);
        padding:20px;
        border-radius:18px;
        text-align:center;
        color:white;
        box-shadow:0px 6px 15px rgba(0,0,0,0.4);
    ">
        <h4>Profit Contribution</h4>
        <h2>{profit_contribution:.1f}%</h2>
    </div>
    """, unsafe_allow_html=True)




    DIV_COLORS = {"Chocolate": "#6B3A2A", "Sugar": "#E8A838", "Other": "#5B8DB8"}

# ══════════════════════════════════════════════════════════════════════════════
# CHART 1 – Revenue Contribution by Product Name  (Clustered Bar)
# ══════════════════════════════════════════════════════════════════════════════
# ══════════════════════════════════════════════════════════════════════════════
# CHART 1 – Revenue Contribution by Product Name (Clustered Bar)
# ══════════════════════════════════════════════════════════════════════════════
st.header("1 · Revenue Contribution by Product Name")

rev_prod = (
    filtered_df.groupby(["Product Name", "Division"])["Sales"]
    .sum().reset_index()
)
rev_prod["Revenue %"] = (rev_prod["Sales"] / rev_prod["Sales"].sum() * 100).round(2)
rev_prod = rev_prod.sort_values("Sales", ascending=False).reset_index(drop=True)

fig1 = go.Figure()
for div, grp in rev_prod.groupby("Division"):
    fig1.add_trace(go.Bar(
        name=div,
        x=grp["Product Name"],
        y=grp["Revenue %"],
        marker_color=DIV_COLORS[div],
        text=grp["Revenue %"].apply(lambda v: f"{v:.1f}%"),
        textposition="auto",                # ← auto handles inside/outside
        textfont=dict(size=11, color="white"),
        customdata=grp["Sales"],
        hovertemplate=(
            "<b>%{x}</b><br>"
            "Revenue: $%{customdata:,.2f}<br>"
            "Share: %{y:.2f}%"
            "<extra></extra>"
        ),
    ))

fig1.update_layout(
    barmode="group",
    title="Revenue Contribution (%) by Product",
    xaxis_title="Product Name",
    yaxis_title="Revenue Share (%)",
    yaxis_ticksuffix="%",
    xaxis_tickangle=-35,
    legend_title="Division",
    height=580,                                         # ← taller chart
    plot_bgcolor="white",
    yaxis=dict(
        gridcolor="#f0f0f0",
        range=[0, rev_prod["Revenue %"].max() * 1.35], # ← 35% headroom
    ),
    uniformtext_minsize=9,
    uniformtext_mode="hide",
    margin=dict(t=60, b=140),                          # ← bottom margin for angled labels
    bargap=0.15,
    bargroupgap=0.05,
)
st.plotly_chart(fig1, use_container_width=True)

# CHART 2 – Gross Margin by Month  (Line Chart)
# ══════════════════════════════════════════════════════════════════════════════
st.header("2 · Gross Margin by Month")

gm_month = (
    filtered_df.groupby(["Month", "Division"])
    .apply(lambda x: x["Gross Profit"].sum() / x["Sales"].sum(), include_groups=False)
    .reset_index(name="Gross Margin %")
)
gm_month["Gross Margin %"] = (gm_month["Gross Margin %"] * 100).round(2)

gm_overall = (
    filtered_df.groupby("Month")
    .apply(lambda x: x["Gross Profit"].sum() / x["Sales"].sum(), include_groups=False)
    .reset_index(name="Gross Margin %")
)
gm_overall["Gross Margin %"] = (gm_overall["Gross Margin %"] * 100).round(2)

fig2 = px.line(
    gm_month, x="Month", y="Gross Margin %", color="Division",
    color_discrete_map=DIV_COLORS, markers=True,
    title="Gross Margin % by Month & Division",
    labels={"Month": "Month", "Gross Margin %": "Gross Margin (%)"},
)
fig2.add_trace(go.Scatter(
    x=gm_overall["Month"], y=gm_overall["Gross Margin %"],
    mode="lines+markers", name="Overall",
    line=dict(color="#333333", width=2, dash="dot"),
    marker=dict(symbol="diamond", size=7),
))
fig2.update_xaxes(tickformat="%b %Y")
fig2.update_layout(
    yaxis_ticksuffix="%", height=430,
    plot_bgcolor="white", yaxis=dict(gridcolor="#f0f0f0"),
)
st.plotly_chart(fig2, use_container_width=True)



# CHART 3 – Revenue vs Profit by Division  (Grouped Bar)
# ══════════════════════════════════════════════════════════════════════════════
st.header("3 · Revenue vs Profit by Division")

rev_prof_div = (
    filtered_df.groupby("Division")
    .agg(Revenue=("Sales", "sum"), Profit=("Gross Profit", "sum"))
    .reset_index()
)

fig3 = go.Figure()
fig3.add_trace(go.Bar(
    name="Revenue",
    x=rev_prof_div["Division"],
    y=rev_prof_div["Revenue"],
    marker_color=[DIV_COLORS.get(d, "#999") for d in rev_prof_div["Division"]],
    text=rev_prof_div["Revenue"].apply(lambda v: f"${v:,.0f}"),
    textposition="inside",
    textfont=dict(color="white", size=12),
))
fig3.add_trace(go.Bar(
    name="Gross Profit",
    x=rev_prof_div["Division"],
    y=rev_prof_div["Profit"],
    marker_color=["#c07860", "#f3cc7a", "#92b8d8"],
    text=rev_prof_div["Profit"].apply(lambda v: f"${v:,.0f}"),
    textposition="inside",
    textfont=dict(color="white", size=12),
))
fig3.update_layout(
    barmode="group",
    title="Revenue vs Gross Profit by Division",
    yaxis_title="Amount ($)", yaxis_tickprefix="$",
    height=480, uniformtext_minsize=10, uniformtext_mode="show",
    plot_bgcolor="white", yaxis=dict(gridcolor="#f0f0f0"),
)
st.plotly_chart(fig3, use_container_width=True)


# ══════════════════════════════════════════════════════════════════════════════
# CHART 5 – Revenue Pareto Chart
# ══════════════════════════════════════════════════════════════════════════════
st.header("5 · Revenue Pareto Chart")

pareto = (
    filtered_df.groupby("Product Name")["Sales"]
    .sum().reset_index()
    .sort_values("Sales", ascending=False)
    .reset_index(drop=True)        # ← clean index after sort
)
pareto["Cumulative %"] = pareto["Sales"].cumsum() / pareto["Sales"].sum() * 100

cross_idx = pareto[pareto["Cumulative %"] >= 80].index[0]
cross_pos = cross_idx              # ← index is now 0-based after reset_index

bar_colors = ["#6B3A2A" if i <= cross_pos else "#c9a898" for i in range(len(pareto))]

fig5 = go.Figure()

# Bars – Total Sales
fig5.add_trace(go.Bar(
    name="Total Sales",
    x=pareto["Product Name"],
    y=pareto["Sales"],
    marker_color=bar_colors,
    yaxis="y1",
    text=pareto["Sales"].apply(lambda v: f"${v:,.0f}"),
    textposition="auto",           # ← auto picks inside/outside based on space
    textfont=dict(size=10, color="white"),
    hovertemplate="<b>%{x}</b><br>Sales: $%{y:,.2f}<extra></extra>",
))

# Line – Cumulative %
fig5.add_trace(go.Scatter(
    name="Cumulative Revenue %",
    x=pareto["Product Name"],
    y=pareto["Cumulative %"],
    mode="lines+markers",
    line=dict(color="#E8A838", width=2.5),
    marker=dict(size=7),
    yaxis="y2",
    hovertemplate="%{y:.1f}%<extra>Cumulative</extra>",
))

# 80% reference line
fig5.add_shape(
    type="line",
    x0=-0.5, x1=len(pareto) - 0.5,
    y0=80, y1=80,
    yref="y2",
    line=dict(color="red", width=1.5, dash="dash"),
)
fig5.add_annotation(
    x=len(pareto) - 1, y=80, yref="y2",
    text="80% Target", showarrow=False,
    font=dict(color="red", size=12),
    xanchor="right", yanchor="bottom",
)

# Vertical marker at 80% crossover product
fig5.add_shape(
    type="line",
    x0=cross_pos, x1=cross_pos,
    y0=0, y1=1, yref="paper",
    line=dict(color="red", width=1, dash="dot"),
)
fig5.add_annotation(
    x=cross_pos, y=1, yref="paper",
    text=f"  {pareto.loc[cross_pos, 'Product Name']}",
    showarrow=False,
    font=dict(color="red", size=10),
    xanchor="left", yanchor="top",
)

fig5.update_layout(
    title="Revenue Pareto – Products driving 80% of Revenue",
    xaxis_title="Product Name",
    xaxis_tickangle=-35,
    yaxis=dict(
        title="Total Sales ($)",
        tickprefix="$",
        gridcolor="#f0f0f0",
        range=[0, pareto["Sales"].max() * 1.3],    # ← 30% headroom for labels
    ),
    yaxis2=dict(
        title="Cumulative Revenue %",
        overlaying="y",
        side="right",
        range=[0, 115],                             # ← extra room at top
        ticksuffix="%",
        showgrid=False,
    ),
    plot_bgcolor="white",
    legend=dict(x=0.65, y=0.15),
    height=520,                                     # ← taller chart
    margin=dict(t=60, b=120),                       # ← bottom margin for angled labels
)
st.plotly_chart(fig5, use_container_width=True)



# CHART 6 – Gross Profit Decomposition Treemap
# ══════════════════════════════════════════════════════════════════════════════
st.header("6 · Gross Profit Breakdown by Division & Product")

fig_tree = px.treemap(
    prod_div,
    path=[px.Constant("All Divisions"), "Division", "Product Name"],
    values="Gross_Profit",
    color="Gross Margin %",
    color_continuous_scale="RdYlGn",
    color_continuous_midpoint=prod_div["Gross Margin %"].mean(),
    custom_data=["Sales", "Cost", "Units", "Gross Margin %"],
    title="Gross Profit Decomposition — Division → Product",
)
fig_tree.update_traces(
    texttemplate="<b>%{label}</b><br>GP: $%{value:,.0f}<br>Margin: %{customdata[3]:.1f}%",
    hovertemplate=(
        "<b>%{label}</b><br>Gross Profit: $%{value:,.2f}<br>"
        "Sales: $%{customdata[0]:,.2f}<br>Cost: $%{customdata[1]:,.2f}<br>"
        "Units: %{customdata[2]:,}<br>Gross Margin: %{customdata[3]:.1f}%<extra></extra>"
    ),
    root_color="lightgrey",
)
fig_tree.update_layout(
    height=520,
    coloraxis_colorbar=dict(title="Gross Margin %", ticksuffix="%"),
    margin=dict(t=50, l=10, r=10, b=10),
)
st.plotly_chart(fig_tree, use_container_width=True)
st.caption("💡 Click any Division block to drill into its products. Click the top bar to go back.")


# CHART 2 – Cost vs Sales Scatter Plot by Product
# ══════════════════════════════════════════════════════════════════════════════
st.header("7 · Cost vs Product Sales — Scatter Plot")

fig_scatter = px.scatter(
    prod_div, x="Cost", y="Sales",
    color="Division", size="Units", text="Product Name",
    color_discrete_map=DIV_COLORS, hover_name="Product Name",
    custom_data=["Gross_Profit", "Gross Margin %", "Units"],
    title="Cost vs Sales by Product  (bubble size = units sold)",
    labels={"Cost": "Total Cost ($)", "Sales": "Total Sales ($)"},
)
fig_scatter.update_traces(
    textposition="top center",
    textfont=dict(size=10, color="black"),
    marker=dict(opacity=0.85, line=dict(width=1, color="white")),
    hovertemplate=(
        "<b>%{hovertext}</b><br>Sales: $%{y:,.2f}<br>Cost: $%{x:,.2f}<br>"
        "Gross Profit: $%{customdata[0]:,.2f}<br>Gross Margin: %{customdata[1]:.1f}%<br>"
        "Units: %{customdata[2]:,}<extra></extra>"
    ),
)
max_val = max(prod_div["Sales"].max(), prod_div["Cost"].max()) * 1.15
fig_scatter.add_shape(
    type="line", x0=0, y0=0, x1=max_val, y1=max_val,
    line=dict(color="red", dash="dash", width=1.5),
)
fig_scatter.add_annotation(
    x=max_val * 0.82, y=max_val * 0.92,
    text="Break-even (Sales = Cost)", showarrow=False,
    font=dict(color="red", size=11),
)
fig_scatter.update_layout(
    height=600, plot_bgcolor="white",
    xaxis=dict(tickprefix="$", gridcolor="#f0f0f0", zeroline=False,
               range=[0, prod_div["Cost"].max() * 1.35]),
    yaxis=dict(tickprefix="$", gridcolor="#f0f0f0", zeroline=False,
               range=[0, prod_div["Sales"].max() * 1.3]),
)
st.plotly_chart(fig_scatter, use_container_width=True)


# CHART 3 – Sales, Gross Profit, Cost — Funnel Chart
# ══════════════════════════════════════════════════════════════════════════════
st.header("8 · Sales → Gross Profit → Cost — Funnel")

f_sales = filtered_df["Sales"].sum()
f_gp    = filtered_df["Gross Profit"].sum()
f_cost  = filtered_df["Cost"].sum()

funnel_df = pd.DataFrame({
    "Stage": ["Total Sales", "Gross Profit", "Total Cost"],
    "Value": [f_sales, f_gp, f_cost],
    "Color": ["#6B3A2A", "#E8A838", "#5B8DB8"],
})
funnel_df["Label"] = funnel_df.apply(
    lambda r: f"${r['Value']:,.0f}  ({r['Value']/f_sales*100:.1f}% of Sales)", axis=1
)

fig_funnel = go.Figure(go.Funnel(
    y=funnel_df["Stage"],
    x=funnel_df["Value"],
    text=funnel_df["Label"],
    textinfo="text",
    textposition="inside",
    textfont=dict(size=13, color="white"),
    marker=dict(color=funnel_df["Color"].tolist()),
    connector=dict(line=dict(color="#cccccc", width=1)),
    hovertemplate="<b>%{y}</b><br>Value: $%{x:,.2f}<extra></extra>",
))
fig_funnel.update_layout(
    title="Financial Funnel — Sales vs Gross Profit vs Cost",
    height=430,
    margin=dict(l=160, r=60, t=60, b=30),
    plot_bgcolor="white",
)
st.plotly_chart(fig_funnel, use_container_width=True)

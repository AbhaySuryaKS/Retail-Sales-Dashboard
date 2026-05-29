"""
app.py
------
Retail Sales Analytics Dashboard — Dash application entry point.
Initialises the app, builds layout, registers all callbacks.
Run with:  python app.py
"""

import os
import logging
import pandas as pd
from dotenv import load_dotenv
from dash import Dash, dcc, html, Input, Output, State, dash_table
from flask import jsonify
from dash.exceptions import PreventUpdate

load_dotenv()

import utils
import charts
import models

# Configure logging
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()
logging.basicConfig(
    level=LOG_LEVEL,
    format="%(asctime)s %(levelname)s %(name)s — %(message)s",
)
logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Initialise app
# ---------------------------------------------------------------------------

app = Dash(
    __name__,
    title="Retail Analytics Dashboard",
    suppress_callback_exceptions=True,
    meta_tags=[{"name": "viewport", "content": "width=device-width, initial-scale=1"}],
)
server = app.server  # for gunicorn


# Health endpoint for orchestration/healthchecks
@server.route("/health", methods=["GET"])
def _health():
    return jsonify(status="ok")

# ---------------------------------------------------------------------------
# Load data once at startup
# ---------------------------------------------------------------------------

try:
    DF_FULL = utils.load_data()
except Exception:
    logger.exception("Failed to load dataset")
    DF_FULL = pd.DataFrame()

MIN_DATE = DF_FULL["Date"].min() if not DF_FULL.empty else pd.Timestamp("2023-01-01")
MAX_DATE = DF_FULL["Date"].max() if not DF_FULL.empty else pd.Timestamp("2024-12-31")
CATEGORIES = sorted(DF_FULL["Product Category"].unique()) if not DF_FULL.empty else []
REGIONS = sorted(DF_FULL["Region"].unique()) if not DF_FULL.empty else []

# ---------------------------------------------------------------------------
# Helper builders
# ---------------------------------------------------------------------------

def _kpi_card(card_id: str, icon: str, label: str, css_class: str):
    return html.Div(
        className=f"kpi-card {css_class}",
        children=[
            html.Span(icon, className="kpi-icon"),
            html.Div(label, className="kpi-label"),
            html.Div(id=card_id, className="kpi-value", children="—"),
        ],
    )


def _chart_card(graph_id: str, height: int = 340):
    return html.Div(
        className="chart-card",
        children=[
            dcc.Graph(
                id=graph_id,
                config={"displayModeBar": False},
                style={"height": f"{height}px"},
            )
        ],
    )


def _section(section_id: str, icon: str, title: str, children):
    return html.Section(
        id=section_id,
        className="section",
        children=[
            html.Div(className="section-header", children=[
                html.Span(icon, className="section-icon"),
                html.H2(title),
            ]),
            *children,
        ],
    )


# ---------------------------------------------------------------------------
# Sidebar
# ---------------------------------------------------------------------------

SIDEBAR_LINKS = [
    ("🏠", "Executive Overview", "exec-section"),
    ("📈", "Sales Analytics", "sales-section"),
    ("📦", "Product Analytics", "product-section"),
    ("👥", "Customer Analytics", "customer-section"),
    ("🏪", "Inventory Analytics", "inventory-section"),
    ("💰", "Financial Analytics", "financial-section"),
]

sidebar = html.Aside(
    className="sidebar",
    children=[
        html.Div(className="sidebar-logo", children=[
            html.H2("📊 Retail"),
            html.P("Analytics Dashboard"),
        ]),
        html.Nav(
            className="sidebar-nav",
            children=[
                html.A(
                    href=f"#{link_id}",
                    className="nav-item",
                    children=[
                        html.Span(icon, className="nav-icon"),
                        html.Span(label),
                    ],
                )
                for icon, label, link_id in SIDEBAR_LINKS
            ],
        ),
    ],
)


# ---------------------------------------------------------------------------
# Filter Bar
# ---------------------------------------------------------------------------

filter_bar = html.Div(
    className="filter-bar",
    children=[
        html.Div(className="filter-group", children=[
            html.Div("Category", className="filter-label"),
            dcc.Dropdown(
                id="filter-category",
                options=[{"label": c, "value": c} for c in CATEGORIES],
                multi=True,
                placeholder="All Categories",
                clearable=True,
                style={"minWidth": "180px"},
            ),
        ]),
        html.Div(className="filter-group", children=[
            html.Div("Region", className="filter-label"),
            dcc.Dropdown(
                id="filter-region",
                options=[{"label": r, "value": r} for r in REGIONS],
                multi=True,
                placeholder="All Regions",
                clearable=True,
                style={"minWidth": "180px"},
            ),
        ]),
        html.Div(className="filter-group", children=[
            html.Div("Gender", className="filter-label"),
            dcc.Dropdown(
                id="filter-gender",
                options=[{"label": g, "value": g} for g in ["Male", "Female"]],
                multi=True,
                placeholder="All Genders",
                clearable=True,
                style={"minWidth": "140px"},
            ),
        ]),
        html.Div(className="filter-group", children=[
            html.Div("Date Range", className="filter-label"),
            dcc.DatePickerRange(
                id="filter-date",
                min_date_allowed=MIN_DATE,
                max_date_allowed=MAX_DATE,
                start_date=MIN_DATE,
                end_date=MAX_DATE,
                display_format="YYYY-MM-DD",
                style={"fontSize": "12px"},
            ),
        ]),
    ],
)


# ---------------------------------------------------------------------------
# Executive Overview
# ---------------------------------------------------------------------------

exec_section = _section(
    "exec-section", "🏠", "Executive Overview",
    [
        html.Div(
            className="kpi-grid",
            children=[
                _kpi_card("kpi-revenue",  "💵", "Total Revenue",     "revenue"),
                _kpi_card("kpi-profit",   "📈", "Total Profit",      "profit"),
                _kpi_card("kpi-margin",   "💹", "Gross Margin %",    "margin"),
                _kpi_card("kpi-orders",   "🧾", "Total Orders",      "orders"),
                _kpi_card("kpi-units",    "📦", "Units Sold",        "units"),
                _kpi_card("kpi-aov",      "💳", "Avg Order Value",   "aov"),
                _kpi_card("kpi-returns",  "↩️",  "Return Rate",       "returns"),
            ],
        ),
    ],
)


# ---------------------------------------------------------------------------
# Sales Analytics
# ---------------------------------------------------------------------------

sales_section = _section(
    "sales-section", "📈", "Sales Analytics",
    [
        html.Div(className="grid-full", children=[_chart_card("chart-daily", height=300)]),
        html.Div(className="grid-2", children=[
            _chart_card("chart-monthly"),
            _chart_card("chart-category-donut"),
        ]),
        html.Div(className="grid-2", children=[
            _chart_card("chart-region"),
            _chart_card("chart-weekday"),
        ]),
        html.Div(className="grid-full", children=[_chart_card("chart-heatmap", height=300)]),
    ],
)


# ---------------------------------------------------------------------------
# Product Analytics
# ---------------------------------------------------------------------------

product_section = _section(
    "product-section", "📦", "Product Analytics",
    [
        html.Div(className="grid-full", children=[_chart_card("chart-treemap", height=380)]),
        html.Div(className="grid-2", children=[
            _chart_card("chart-top-products"),
            _chart_card("chart-product-scatter"),
        ]),
        html.Div(className="grid-full", children=[_chart_card("chart-return-rate")]),
    ],
)


# ---------------------------------------------------------------------------
# Customer Analytics
# ---------------------------------------------------------------------------

customer_section = _section(
    "customer-section", "👥", "Customer Analytics",
    [
        html.Div(
            id="cluster-stats-container",
            className="cluster-table",
            children=[html.H3("Customer Segment Statistics")],
        ),
        html.Div(className="grid-2", children=[
            _chart_card("chart-cluster"),
            _chart_card("chart-spend-dist"),
        ]),
        html.Div(className="grid-2", children=[
            _chart_card("chart-gender-age"),
            _chart_card("chart-purchase-freq"),
        ]),
    ],
)


# ---------------------------------------------------------------------------
# Inventory Analytics
# ---------------------------------------------------------------------------

inventory_section = _section(
    "inventory-section", "🏪", "Inventory Analytics",
    [
        html.Div(className="grid-full", children=[_chart_card("chart-inv-trend", height=320)]),
        html.Div(className="grid-2", children=[
            _chart_card("chart-stock-heatmap"),
            _chart_card("chart-inv-bubble"),
        ]),
    ],
)


# ---------------------------------------------------------------------------
# Financial Analytics
# ---------------------------------------------------------------------------

financial_section = _section(
    "financial-section", "💰", "Financial Analytics",
    [
        html.Div(className="grid-2", children=[
            _chart_card("chart-waterfall", height=380),
            _chart_card("chart-margin-trend"),
        ]),
        html.Div(className="grid-full", children=[_chart_card("chart-discount-impact")]),
    ],
)


# ---------------------------------------------------------------------------
# Full Layout
# ---------------------------------------------------------------------------

app.layout = html.Div(
    className="dashboard-shell",
    children=[
        sidebar,
        html.Main(
            className="main-content",
            children=[
                html.Div(className="page-header", children=[
                    html.H1("Retail Sales Analytics"),
                    html.P("Interactive business intelligence dashboard"),
                ]),
                filter_bar,
                exec_section,
                sales_section,
                product_section,
                customer_section,
                inventory_section,
                financial_section,
            ],
        ),
    ],
)


# ---------------------------------------------------------------------------
# Utilities
# ---------------------------------------------------------------------------

def _apply_filters(category, region, gender, start_date, end_date) -> pd.DataFrame:
    """Return a filtered copy of DF_FULL based on sidebar filter values."""
    df = DF_FULL.copy()
    if df.empty:
        return df

    if category:
        df = df[df["Product Category"].isin(category)]
    if region:
        df = df[df["Region"].isin(region)]
    if gender:
        df = df[df["Gender"].isin(gender)]
    if start_date:
        df = df[df["Date"] >= pd.Timestamp(start_date)]
    if end_date:
        df = df[df["Date"] <= pd.Timestamp(end_date)]

    return df


FILTER_INPUTS = [
    Input("filter-category", "value"),
    Input("filter-region",   "value"),
    Input("filter-gender",   "value"),
    Input("filter-date",     "start_date"),
    Input("filter-date",     "end_date"),
]


# ---------------------------------------------------------------------------
# Callback — KPI Cards
# ---------------------------------------------------------------------------

@app.callback(
    Output("kpi-revenue",  "children"),
    Output("kpi-profit",   "children"),
    Output("kpi-margin",   "children"),
    Output("kpi-orders",   "children"),
    Output("kpi-units",    "children"),
    Output("kpi-aov",      "children"),
    Output("kpi-returns",  "children"),
    FILTER_INPUTS,
)
def update_kpis(category, region, gender, start_date, end_date):
    df = _apply_filters(category, region, gender, start_date, end_date)
    kpis = utils.compute_kpis(df)
    return (
        utils.fmt_currency(kpis["total_revenue"]),
        utils.fmt_currency(kpis["total_profit"]),
        utils.fmt_pct(kpis["gross_margin_pct"]),
        utils.fmt_number(kpis["total_orders"]),
        utils.fmt_number(kpis["units_sold"]),
        utils.fmt_currency(kpis["avg_order_value"]),
        utils.fmt_pct(kpis["return_rate"]),
    )


# ---------------------------------------------------------------------------
# Callback — Sales Charts
# ---------------------------------------------------------------------------

@app.callback(
    Output("chart-daily",         "figure"),
    Output("chart-monthly",       "figure"),
    Output("chart-category-donut","figure"),
    Output("chart-region",        "figure"),
    Output("chart-weekday",       "figure"),
    Output("chart-heatmap",       "figure"),
    FILTER_INPUTS,
)
def update_sales_charts(category, region, gender, start_date, end_date):
    df = _apply_filters(category, region, gender, start_date, end_date)
    return (
        charts.daily_sales_chart(df),
        charts.monthly_sales_chart(df),
        charts.category_sales_chart(df),
        charts.region_sales_chart(df),
        charts.weekday_sales_chart(df),
        charts.sales_heatmap(df),
    )


# ---------------------------------------------------------------------------
# Callback — Product Charts
# ---------------------------------------------------------------------------

@app.callback(
    Output("chart-treemap",        "figure"),
    Output("chart-top-products",   "figure"),
    Output("chart-product-scatter","figure"),
    Output("chart-return-rate",    "figure"),
    FILTER_INPUTS,
)
def update_product_charts(category, region, gender, start_date, end_date):
    df = _apply_filters(category, region, gender, start_date, end_date)
    return (
        charts.product_treemap(df),
        charts.top_products_bar(df),
        charts.product_scatter(df),
        charts.return_rate_chart(df),
    )


# ---------------------------------------------------------------------------
# Callback — Customer Charts
# ---------------------------------------------------------------------------

@app.callback(
    Output("chart-cluster",       "figure"),
    Output("chart-spend-dist",    "figure"),
    Output("chart-gender-age",    "figure"),
    Output("chart-purchase-freq", "figure"),
    Output("cluster-stats-container", "children"),
    FILTER_INPUTS,
)
def update_customer_charts(category, region, gender, start_date, end_date):
    df = _apply_filters(category, region, gender, start_date, end_date)

    # Clustering
    try:
        clustered = models.cluster_customers(df, n_clusters=3)
        cluster_stats = models.get_cluster_stats(clustered)
    except Exception:
        clustered = utils.customer_summary(df)
        if "Cluster" not in clustered.columns:
            clustered["Cluster"] = 0
        cluster_stats = pd.DataFrame()

    # Cluster scatter needs the Cluster column in the customer df
    fig_cluster = charts.customer_cluster_scatter(df, cluster_col="Cluster") \
        if "Cluster" in clustered.columns else charts._empty_fig()

    # We need to merge cluster labels back for the scatter
    cust_with_cluster = clustered
    fig_cluster = _cluster_scatter_from_df(cust_with_cluster)

    # Stats table
    stats_children = [html.H3("Customer Segment Statistics")]
    if not cluster_stats.empty:
        stats_children.append(
            dash_table.DataTable(
                columns=[{"name": col, "id": col} for col in cluster_stats.columns],
                data=cluster_stats.to_dict("records"),
                style_table={"overflowX": "auto"},
                page_size=10,
            )
        )

    return (
        fig_cluster,
        charts.customer_spend_distribution(df),
        charts.gender_age_heatmap_chart(df),
        charts.purchase_frequency_chart(df),
        stats_children,
    )


def _cluster_scatter_from_df(cust_df: pd.DataFrame):
    """Build cluster scatter directly from the clustered customer df."""
    import plotly.graph_objects as go
    from charts import COLORS, LAYOUT_DEFAULTS, _apply_layout

    if cust_df.empty or "Cluster" not in cust_df.columns:
        return charts._empty_fig()

    cluster_colors = ["#6c63ff", "#00d4ff", "#ffd166", "#00c98d", "#ef476f"]
    fig = go.Figure()
    for cluster_id in sorted(cust_df["Cluster"].unique()):
        sub = cust_df[cust_df["Cluster"] == cluster_id]
        fig.add_trace(go.Scatter(
            x=sub["Num_Orders"],
            y=sub["Total_Spend"],
            mode="markers",
            name=f"Segment {cluster_id}",
            marker=dict(
                color=cluster_colors[int(cluster_id) % len(cluster_colors)],
                size=8, opacity=0.75,
                line=dict(width=0.5, color=COLORS["border"]),
            ),
            hovertemplate="Orders: %{x}<br>Spend: $%{y:,.0f}<extra></extra>",
        ))
    return _apply_layout(
        fig,
        title="Customer Segments (KMeans Clustering)",
        xaxis=dict(**LAYOUT_DEFAULTS["xaxis"], title="Number of Orders"),
        yaxis=dict(**LAYOUT_DEFAULTS["yaxis"], title="Total Spend ($)"),
    )


# ---------------------------------------------------------------------------
# Callback — Inventory Charts
# ---------------------------------------------------------------------------

@app.callback(
    Output("chart-inv-trend",    "figure"),
    Output("chart-stock-heatmap","figure"),
    Output("chart-inv-bubble",   "figure"),
    FILTER_INPUTS,
)
def update_inventory_charts(category, region, gender, start_date, end_date):
    df = _apply_filters(category, region, gender, start_date, end_date)
    return (
        charts.inventory_trend_chart(df),
        charts.stock_heatmap(df),
        charts.inventory_bubble_chart(df),
    )


# ---------------------------------------------------------------------------
# Callback — Financial Charts
# ---------------------------------------------------------------------------

@app.callback(
    Output("chart-waterfall",      "figure"),
    Output("chart-margin-trend",   "figure"),
    Output("chart-discount-impact","figure"),
    FILTER_INPUTS,
)
def update_financial_charts(category, region, gender, start_date, end_date):
    df = _apply_filters(category, region, gender, start_date, end_date)
    return (
        charts.waterfall_chart(df),
        charts.margin_trend_chart(df),
        charts.discount_impact_chart(df),
    )


# ---------------------------------------------------------------------------
# Run
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8050))
    debug = os.getenv("FLASK_DEBUG", os.getenv("DEBUG", "false")).lower() in ("1", "true", "yes")
    logger.info(f"Starting app on 0.0.0.0:{port} (debug={debug})")
    app.run(debug=debug, host="0.0.0.0", port=port)

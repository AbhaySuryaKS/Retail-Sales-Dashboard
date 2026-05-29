"""
charts.py
---------
All Plotly chart factory functions for the Retail Sales Analytics Dashboard.
Each function accepts a (filtered) dataframe and returns a go.Figure.
"""

import numpy as np
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots

import utils

# ---------------------------------------------------------------------------
# Theme / Palette
# ---------------------------------------------------------------------------

COLORS = {
    "bg": "#0f1117",
    "card": "#1a1d27",
    "border": "#2a2d3e",
    "primary": "#6c63ff",
    "secondary": "#00d4ff",
    "success": "#00c98d",
    "warning": "#ffd166",
    "danger": "#ef476f",
    "text": "#e0e0e0",
    "subtext": "#8b8fa8",
    "grid": "#2a2d3e",
}

CATEGORY_COLORS = {
    "Electronics": "#6c63ff",
    "Clothing": "#00d4ff",
    "Beauty": "#ffd166",
}

REGION_COLORS = {
    "North": "#6c63ff",
    "South": "#00c98d",
    "East": "#00d4ff",
    "West": "#ffd166",
    "Central": "#ef476f",
}

LAYOUT_DEFAULTS = dict(
    paper_bgcolor=COLORS["card"],
    plot_bgcolor=COLORS["card"],
    font=dict(family="Inter, sans-serif", color=COLORS["text"], size=12),
    margin=dict(l=40, r=20, t=40, b=40),
    legend=dict(
        bgcolor=COLORS["card"],
        bordercolor=COLORS["border"],
        borderwidth=1,
        font=dict(color=COLORS["text"]),
    ),
    xaxis=dict(
        gridcolor=COLORS["grid"],
        linecolor=COLORS["border"],
        tickfont=dict(color=COLORS["subtext"]),
        title_font=dict(color=COLORS["subtext"]),
    ),
    yaxis=dict(
        gridcolor=COLORS["grid"],
        linecolor=COLORS["border"],
        tickfont=dict(color=COLORS["subtext"]),
        title_font=dict(color=COLORS["subtext"]),
    ),
)


def _apply_layout(fig: go.Figure, title: str = "", **kwargs) -> go.Figure:
    layout = dict(**LAYOUT_DEFAULTS)
    layout.update(kwargs)
    if title:
        layout["title"] = dict(text=title, font=dict(color=COLORS["text"], size=14), x=0.01)
    fig.update_layout(**layout)
    return fig


def _empty_fig(message: str = "No data available") -> go.Figure:
    fig = go.Figure()
    fig.add_annotation(
        text=message, xref="paper", yref="paper",
        x=0.5, y=0.5, showarrow=False,
        font=dict(color=COLORS["subtext"], size=14),
    )
    return _apply_layout(fig)


# ---------------------------------------------------------------------------
# Sales Analytics
# ---------------------------------------------------------------------------

def daily_sales_chart(df: pd.DataFrame) -> go.Figure:
    """Area chart of daily revenue."""
    if df.empty:
        return _empty_fig()
    data = utils.daily_sales(df)
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=data["Date"], y=data["Revenue"],
        mode="lines",
        fill="tozeroy",
        name="Daily Revenue",
        line=dict(color=COLORS["primary"], width=2),
        fillcolor="rgba(108,99,255,0.15)",
        hovertemplate="<b>%{x|%b %d, %Y}</b><br>Revenue: $%{y:,.0f}<extra></extra>",
    ))
    return _apply_layout(fig, title="Daily Revenue Trend")


def monthly_sales_chart(df: pd.DataFrame) -> go.Figure:
    """Grouped bar chart of monthly revenue and profit."""
    if df.empty:
        return _empty_fig()
    data = utils.monthly_sales(df)
    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=data["YearMonth"], y=data["Revenue"],
        name="Revenue", marker_color=COLORS["primary"],
        hovertemplate="<b>%{x}</b><br>Revenue: $%{y:,.0f}<extra></extra>",
    ))
    fig.add_trace(go.Bar(
        x=data["YearMonth"], y=data["Profit"],
        name="Profit", marker_color=COLORS["success"],
        hovertemplate="<b>%{x}</b><br>Profit: $%{y:,.0f}<extra></extra>",
    ))
    return _apply_layout(fig, title="Monthly Revenue vs Profit", barmode="group")


def region_sales_chart(df: pd.DataFrame) -> go.Figure:
    """Horizontal bar chart — revenue by region."""
    if df.empty:
        return _empty_fig()
    data = utils.region_sales(df).sort_values("Revenue")
    colors = [REGION_COLORS.get(r, COLORS["primary"]) for r in data["Region"]]
    fig = go.Figure(go.Bar(
        x=data["Revenue"], y=data["Region"],
        orientation="h",
        marker_color=colors,
        hovertemplate="<b>%{y}</b><br>Revenue: $%{x:,.0f}<extra></extra>",
    ))
    return _apply_layout(fig, title="Revenue by Region")


def category_sales_chart(df: pd.DataFrame) -> go.Figure:
    """Donut chart — category revenue split."""
    if df.empty:
        return _empty_fig()
    data = utils.category_sales(df)
    fig = go.Figure(go.Pie(
        labels=data["Product Category"],
        values=data["Revenue"],
        hole=0.55,
        marker_colors=[CATEGORY_COLORS.get(c, COLORS["primary"]) for c in data["Product Category"]],
        textfont=dict(color=COLORS["text"]),
        hovertemplate="<b>%{label}</b><br>Revenue: $%{value:,.0f}<br>Share: %{percent}<extra></extra>",
    ))
    return _apply_layout(fig, title="Category Revenue Distribution",
                         legend=dict(**LAYOUT_DEFAULTS["legend"], orientation="h", y=-0.1))


def sales_heatmap(df: pd.DataFrame) -> go.Figure:
    """Heatmap: Month × Category revenue."""
    if df.empty:
        return _empty_fig()
    pivot = utils.heatmap_data(df)
    fig = go.Figure(go.Heatmap(
        z=pivot.values,
        x=pivot.columns.tolist(),
        y=pivot.index.astype(str).tolist(),
        colorscale=[[0, "#0f1117"], [0.5, "#6c63ff"], [1, "#00d4ff"]],
        hovertemplate="Month: <b>%{y}</b><br>Category: <b>%{x}</b><br>Revenue: $%{z:,.0f}<extra></extra>",
        showscale=True,
        colorbar=dict(tickfont=dict(color=COLORS["subtext"])),
    ))
    return _apply_layout(fig, title="Revenue Heatmap — Month × Category")


def weekday_sales_chart(df: pd.DataFrame) -> go.Figure:
    """Bar chart of average revenue by day of week."""
    if df.empty:
        return _empty_fig()
    order = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    data = (
        df.groupby("DayOfWeek")["Total Amount"].mean().reindex(order).reset_index()
    )
    data.columns = ["Day", "Avg_Revenue"]
    fig = go.Figure(go.Bar(
        x=data["Day"], y=data["Avg_Revenue"],
        marker_color=COLORS["secondary"],
        hovertemplate="<b>%{x}</b><br>Avg Revenue: $%{y:,.0f}<extra></extra>",
    ))
    return _apply_layout(fig, title="Average Revenue by Day of Week")


# ---------------------------------------------------------------------------
# Product Analytics
# ---------------------------------------------------------------------------

def product_treemap(df: pd.DataFrame) -> go.Figure:
    """Treemap of revenue by Category → Gender."""
    if df.empty:
        return _empty_fig()
    data = (
        df.groupby(["Product Category", "Gender"])
        .agg(Revenue=("Total Amount", "sum"))
        .reset_index()
    )
    data["All"] = "All Sales"
    fig = px.treemap(
        data,
        path=["All", "Product Category", "Gender"],
        values="Revenue",
        color="Product Category",
        color_discrete_map=CATEGORY_COLORS,
    )
    fig.update_traces(
        textfont=dict(color="white"),
        hovertemplate="<b>%{label}</b><br>Revenue: $%{value:,.0f}<extra></extra>",
    )
    return _apply_layout(fig, title="Revenue Treemap — Category & Gender")


def product_scatter(df: pd.DataFrame) -> go.Figure:
    """Scatter: Profit Margin vs Units Sold (bubble = Revenue)."""
    if df.empty:
        return _empty_fig()
    data = utils.product_performance(df)
    fig = go.Figure()
    for _, row in data.iterrows():
        cat = row["Product Category"]
        fig.add_trace(go.Scatter(
            x=[row["Units"]],
            y=[row["Profit_Margin"]],
            mode="markers+text",
            name=cat,
            text=[cat],
            textposition="top center",
            marker=dict(
                size=row["Revenue"] / data["Revenue"].max() * 60 + 20,
                color=CATEGORY_COLORS.get(cat, COLORS["primary"]),
                opacity=0.85,
                line=dict(width=1, color=COLORS["border"]),
            ),
            hovertemplate=(
                f"<b>{cat}</b><br>"
                "Units Sold: %{x:,.0f}<br>"
                "Profit Margin: %{y:.1f}%<extra></extra>"
            ),
        ))
    fig.update_layout(showlegend=False)
    return _apply_layout(
        fig,
        title="Profit Margin vs Units Sold (bubble = Revenue)",
        xaxis=dict(**LAYOUT_DEFAULTS["xaxis"], title="Units Sold"),
        yaxis=dict(**LAYOUT_DEFAULTS["yaxis"], title="Profit Margin (%)"),
    )


def top_products_bar(df: pd.DataFrame) -> go.Figure:
    """Horizontal bar — categories by revenue (with return rate annotation)."""
    if df.empty:
        return _empty_fig()
    data = utils.product_performance(df).sort_values("Revenue", ascending=True)
    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=data["Revenue"], y=data["Product Category"],
        orientation="h",
        marker_color=[CATEGORY_COLORS.get(c, COLORS["primary"]) for c in data["Product Category"]],
        name="Revenue",
        hovertemplate="<b>%{y}</b><br>Revenue: $%{x:,.0f}<extra></extra>",
    ))
    return _apply_layout(fig, title="Category Revenue & Returns")


def return_rate_chart(df: pd.DataFrame) -> go.Figure:
    """Bar chart of return rates by category."""
    if df.empty:
        return _empty_fig()
    data = utils.product_performance(df).sort_values("Return_Rate", ascending=False)
    fig = go.Figure(go.Bar(
        x=data["Product Category"],
        y=data["Return_Rate"],
        marker_color=COLORS["danger"],
        hovertemplate="<b>%{x}</b><br>Return Rate: %{y:.2f}%<extra></extra>",
    ))
    return _apply_layout(fig, title="Return Rate by Category",
                         yaxis=dict(**LAYOUT_DEFAULTS["yaxis"], title="Return Rate (%)"))


# ---------------------------------------------------------------------------
# Customer Analytics
# ---------------------------------------------------------------------------

def customer_cluster_scatter(df: pd.DataFrame, cluster_col: str = "Cluster") -> go.Figure:
    """Scatter of customer clusters (Total Spend vs Num Orders)."""
    cust = utils.customer_summary(df)
    if cust.empty or cluster_col not in cust.columns:
        return _empty_fig()

    cluster_colors = ["#6c63ff", "#00d4ff", "#ffd166", "#00c98d", "#ef476f"]
    fig = go.Figure()
    for cluster_id in sorted(cust[cluster_col].unique()):
        sub = cust[cust[cluster_col] == cluster_id]
        fig.add_trace(go.Scatter(
            x=sub["Num_Orders"],
            y=sub["Total_Spend"],
            mode="markers",
            name=f"Segment {cluster_id}",
            marker=dict(
                color=cluster_colors[int(cluster_id) % len(cluster_colors)],
                size=8,
                opacity=0.75,
                line=dict(width=0.5, color=COLORS["border"]),
            ),
            hovertemplate=(
                "Orders: %{x}<br>"
                "Total Spend: $%{y:,.0f}<extra></extra>"
            ),
        ))
    return _apply_layout(
        fig,
        title="Customer Segments (KMeans Clustering)",
        xaxis=dict(**LAYOUT_DEFAULTS["xaxis"], title="Number of Orders"),
        yaxis=dict(**LAYOUT_DEFAULTS["yaxis"], title="Total Spend ($)"),
    )


def gender_age_heatmap_chart(df: pd.DataFrame) -> go.Figure:
    """Heatmap: Gender × Age Band spending."""
    if df.empty:
        return _empty_fig()
    pivot = utils.gender_age_heatmap(df)
    fig = go.Figure(go.Heatmap(
        z=pivot.values,
        x=pivot.columns.astype(str).tolist(),
        y=pivot.index.tolist(),
        colorscale=[[0, "#0f1117"], [0.5, "#6c63ff"], [1, "#ffd166"]],
        hovertemplate="Gender: <b>%{y}</b><br>Age: <b>%{x}</b><br>Revenue: $%{z:,.0f}<extra></extra>",
        colorbar=dict(tickfont=dict(color=COLORS["subtext"])),
    ))
    return _apply_layout(fig, title="Spending Heatmap — Gender × Age Band")


def customer_spend_distribution(df: pd.DataFrame) -> go.Figure:
    """Histogram of per-customer total spending."""
    if df.empty:
        return _empty_fig()
    cust = utils.customer_summary(df)
    fig = go.Figure(go.Histogram(
        x=cust["Total_Spend"],
        nbinsx=30,
        marker_color=COLORS["primary"],
        opacity=0.8,
        hovertemplate="Spend Range: $%{x:,.0f}<br>Customers: %{y}<extra></extra>",
    ))
    return _apply_layout(
        fig,
        title="Customer Spend Distribution",
        xaxis=dict(**LAYOUT_DEFAULTS["xaxis"], title="Total Spend ($)"),
        yaxis=dict(**LAYOUT_DEFAULTS["yaxis"], title="# Customers"),
    )


def purchase_frequency_chart(df: pd.DataFrame) -> go.Figure:
    """Bar chart of purchase frequency buckets."""
    if df.empty:
        return _empty_fig()
    cust = utils.customer_summary(df)
    bins = [0, 1, 2, 3, 5, 100]
    labels = ["1 order", "2 orders", "3 orders", "4-5 orders", "6+ orders"]
    cust["Freq_Bucket"] = pd.cut(cust["Num_Orders"], bins=bins, labels=labels, right=True)
    freq = cust["Freq_Bucket"].value_counts().reindex(labels).fillna(0).reset_index()
    freq.columns = ["Bucket", "Count"]
    fig = go.Figure(go.Bar(
        x=freq["Bucket"],
        y=freq["Count"],
        marker_color=COLORS["secondary"],
        hovertemplate="<b>%{x}</b><br>Customers: %{y:,.0f}<extra></extra>",
    ))
    return _apply_layout(fig, title="Purchase Frequency Distribution",
                         yaxis=dict(**LAYOUT_DEFAULTS["yaxis"], title="# Customers"))


# ---------------------------------------------------------------------------
# Inventory Analytics
# ---------------------------------------------------------------------------

def inventory_trend_chart(df: pd.DataFrame) -> go.Figure:
    """Line chart of units sold per month per category."""
    if df.empty:
        return _empty_fig()
    data = utils.inventory_df(df)
    fig = go.Figure()
    for cat, grp in data.groupby("Product Category"):
        fig.add_trace(go.Scatter(
            x=grp["YearMonth"], y=grp["Units_Sold"],
            mode="lines+markers",
            name=cat,
            line=dict(color=CATEGORY_COLORS.get(cat, COLORS["primary"]), width=2),
            marker=dict(size=5),
            hovertemplate=f"<b>{cat}</b><br>Month: %{{x}}<br>Units: %{{y:,.0f}}<extra></extra>",
        ))
    return _apply_layout(fig, title="Monthly Units Sold by Category")


def inventory_bubble_chart(df: pd.DataFrame) -> go.Figure:
    """Bubble chart: Category — Revenue vs Units (bubble = Profit)."""
    if df.empty:
        return _empty_fig()
    data = utils.product_performance(df)
    fig = go.Figure()
    for _, row in data.iterrows():
        cat = row["Product Category"]
        fig.add_trace(go.Scatter(
            x=[row["Units"]],
            y=[row["Revenue"]],
            mode="markers+text",
            name=cat,
            text=[cat],
            textposition="top center",
            marker=dict(
                size=row["Profit"] / data["Profit"].max() * 60 + 20,
                color=CATEGORY_COLORS.get(cat, COLORS["primary"]),
                opacity=0.8,
                line=dict(width=1, color=COLORS["border"]),
            ),
            hovertemplate=(
                f"<b>{cat}</b><br>"
                "Units Sold: %{x:,.0f}<br>"
                "Revenue: $%{y:,.0f}<extra></extra>"
            ),
        ))
    fig.update_layout(showlegend=False)
    return _apply_layout(
        fig,
        title="Inventory Valuation Bubble Chart",
        xaxis=dict(**LAYOUT_DEFAULTS["xaxis"], title="Units Sold"),
        yaxis=dict(**LAYOUT_DEFAULTS["yaxis"], title="Revenue ($)"),
    )


def stock_heatmap(df: pd.DataFrame) -> go.Figure:
    """Heatmap: YearMonth × Category units sold."""
    if df.empty:
        return _empty_fig()
    data = utils.inventory_df(df)
    pivot = data.pivot_table(values="Units_Sold", index="YearMonth", columns="Product Category", fill_value=0)
    fig = go.Figure(go.Heatmap(
        z=pivot.values,
        x=pivot.columns.tolist(),
        y=pivot.index.tolist(),
        colorscale=[[0, "#0f1117"], [0.5, "#00c98d"], [1, "#ffd166"]],
        hovertemplate="Month: <b>%{y}</b><br>Category: <b>%{x}</b><br>Units: %{z:,.0f}<extra></extra>",
        colorbar=dict(tickfont=dict(color=COLORS["subtext"])),
    ))
    return _apply_layout(fig, title="Stock Movement Heatmap — Month × Category")


# ---------------------------------------------------------------------------
# Financial Analytics
# ---------------------------------------------------------------------------

def waterfall_chart(df: pd.DataFrame) -> go.Figure:
    """Waterfall: Gross Revenue → Discounts → Net Profit."""
    if df.empty:
        return _empty_fig()
    wf = utils.financial_waterfall(df)
    colors = []
    for m, v in zip(wf["measure"], wf["values"]):
        if m == "total":
            colors.append(COLORS["primary"])
        elif v < 0:
            colors.append(COLORS["danger"])
        else:
            colors.append(COLORS["success"])

    fig = go.Figure(go.Waterfall(
        name="Financials",
        orientation="v",
        measure=wf["measure"],
        x=wf["labels"],
        y=wf["values"],
        connector=dict(line=dict(color=COLORS["border"], width=1)),
        decreasing=dict(marker_color=COLORS["danger"]),
        increasing=dict(marker_color=COLORS["success"]),
        totals=dict(marker_color=COLORS["primary"]),
        textposition="outside",
        text=[f"${abs(v):,.0f}" for v in wf["values"]],
        textfont=dict(color=COLORS["text"]),
        hovertemplate="<b>%{x}</b><br>$%{y:,.0f}<extra></extra>",
    ))
    return _apply_layout(fig, title="Financial Waterfall")


def margin_trend_chart(df: pd.DataFrame) -> go.Figure:
    """Line chart of quarterly gross margin %."""
    if df.empty:
        return _empty_fig()
    data = utils.quarterly_margin(df)
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=data["Label"], y=data["Margin_Pct"],
        mode="lines+markers",
        line=dict(color=COLORS["warning"], width=2),
        marker=dict(size=8, color=COLORS["warning"]),
        fill="tozeroy",
        fillcolor="rgba(255,209,102,0.1)",
        hovertemplate="<b>%{x}</b><br>Margin: %{y:.1f}%<extra></extra>",
    ))
    return _apply_layout(
        fig,
        title="Quarterly Gross Margin Trend",
        yaxis=dict(**LAYOUT_DEFAULTS["yaxis"], title="Gross Margin (%)"),
    )


def discount_impact_chart(df: pd.DataFrame) -> go.Figure:
    """Bar comparison: Revenue vs Net Revenue by category."""
    if df.empty:
        return _empty_fig()
    data = (
        df.groupby("Product Category")
        .agg(Revenue=("Total Amount", "sum"), Net_Revenue=("Net_Revenue", "sum"))
        .reset_index()
    )
    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=data["Product Category"], y=data["Revenue"],
        name="Gross Revenue", marker_color=COLORS["primary"],
    ))
    fig.add_trace(go.Bar(
        x=data["Product Category"], y=data["Net_Revenue"],
        name="Net Revenue (after discount)", marker_color=COLORS["success"],
    ))
    return _apply_layout(fig, title="Discount Impact by Category", barmode="group")


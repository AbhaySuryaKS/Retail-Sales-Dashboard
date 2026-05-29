"""
utils.py
--------
Dataset loading, preprocessing, feature engineering, KPI calculations,
and helper functions for the Retail Sales Analytics Dashboard.
"""

import numpy as np
import pandas as pd


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

REGIONS = ["North", "South", "East", "West", "Central"]
CATEGORY_MARGIN = {"Electronics": 0.22, "Clothing": 0.38, "Beauty": 0.45}
CATEGORY_RETURN_RATE = {"Electronics": 0.08, "Clothing": 0.05, "Beauty": 0.03}
CATEGORY_DISCOUNT = {"Electronics": 0.12, "Clothing": 0.08, "Beauty": 0.05}
CATEGORY_STOCK_BASE = {"Electronics": 200, "Clothing": 500, "Beauty": 350}

DATA_PATH = "data/retail_sales_dataset.csv"


# ---------------------------------------------------------------------------
# Loading & Preprocessing
# ---------------------------------------------------------------------------

def load_data(path: str = DATA_PATH) -> pd.DataFrame:
    """Load and preprocess the retail sales CSV dataset."""
    try:
        df = pd.read_csv(path)
    except FileNotFoundError:
        raise FileNotFoundError(f"Dataset not found at: {path}")

    df = _clean(df)
    df = _engineer_features(df)
    return df


def _clean(df: pd.DataFrame) -> pd.DataFrame:
    """Remove duplicates, handle nulls, normalize dtypes."""
    df = df.drop_duplicates()
    df.columns = [c.strip() for c in df.columns]

    # Parse dates
    df["Date"] = pd.to_datetime(df["Date"], errors="coerce")
    df = df.dropna(subset=["Date"])

    # Ensure numerics
    for col in ["Quantity", "Price per Unit", "Total Amount", "Age"]:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    df = df.dropna(subset=["Quantity", "Price per Unit", "Total Amount"])

    # Strip whitespace from string columns
    for col in ["Gender", "Product Category", "Customer ID"]:
        df[col] = df[col].astype(str).str.strip()

    # Remove invalid rows
    df = df[(df["Quantity"] > 0) & (df["Price per Unit"] > 0) & (df["Total Amount"] > 0)]

    return df.reset_index(drop=True)


def _engineer_features(df: pd.DataFrame) -> pd.DataFrame:
    """Add derived columns needed for all analytics sections."""
    rng = np.random.default_rng(seed=42)
    n = len(df)

    # Time features
    df["Year"] = df["Date"].dt.year
    df["Month"] = df["Date"].dt.month
    df["Month_Name"] = df["Date"].dt.strftime("%b")
    df["Quarter"] = df["Date"].dt.quarter
    df["Week"] = df["Date"].dt.isocalendar().week.astype(int)
    df["DayOfWeek"] = df["Date"].dt.day_name()

    # Region (deterministic from Customer ID hash)
    df["Region"] = df["Customer ID"].apply(
        lambda cid: REGIONS[hash(cid) % len(REGIONS)]
    )

    # Financial features
    df["Gross_Margin_Rate"] = df["Product Category"].map(CATEGORY_MARGIN)
    df["Profit"] = (df["Total Amount"] * df["Gross_Margin_Rate"]).round(2)

    df["Discount_Rate"] = df["Product Category"].map(CATEGORY_DISCOUNT)
    df["Discount_Amount"] = (df["Total Amount"] * df["Discount_Rate"]).round(2)
    df["Net_Revenue"] = (df["Total Amount"] - df["Discount_Amount"]).round(2)
    df["Net_Profit"] = (df["Profit"] - df["Discount_Amount"] * 0.5).round(2)

    # Return flag
    df["Return_Rate"] = df["Product Category"].map(CATEGORY_RETURN_RATE)
    df["Is_Return"] = rng.random(n) < df["Return_Rate"]

    # Inventory
    df["Stock_Level"] = df["Product Category"].map(CATEGORY_STOCK_BASE)
    df["Stock_Remaining"] = (
        df["Stock_Level"] - df.groupby("Product Category")["Quantity"].transform("cumsum")
    ).clip(lower=0)

    # Customer age band
    bins = [0, 25, 35, 45, 55, 100]
    labels = ["18-25", "26-35", "36-45", "46-55", "56+"]
    df["Age_Band"] = pd.cut(df["Age"], bins=bins, labels=labels, right=False)

    return df


# ---------------------------------------------------------------------------
# KPI Calculations
# ---------------------------------------------------------------------------

def compute_kpis(df: pd.DataFrame) -> dict:
    """Return a dict of executive KPI values from a (filtered) dataframe."""
    if df.empty:
        return {k: 0 for k in [
            "total_revenue", "total_profit", "gross_margin_pct",
            "total_orders", "units_sold", "avg_order_value", "return_rate"
        ]}

    total_revenue = df["Total Amount"].sum()
    total_profit = df["Profit"].sum()
    gross_margin_pct = (total_profit / total_revenue * 100) if total_revenue else 0
    total_orders = len(df)
    units_sold = df["Quantity"].sum()
    avg_order_value = total_revenue / total_orders if total_orders else 0
    return_rate = df["Is_Return"].mean() * 100

    return {
        "total_revenue": total_revenue,
        "total_profit": total_profit,
        "gross_margin_pct": gross_margin_pct,
        "total_orders": total_orders,
        "units_sold": units_sold,
        "avg_order_value": avg_order_value,
        "return_rate": return_rate,
    }


# ---------------------------------------------------------------------------
# Aggregation Helpers
# ---------------------------------------------------------------------------

def monthly_sales(df: pd.DataFrame) -> pd.DataFrame:
    """Revenue and profit aggregated by Year-Month."""
    df = df.copy()
    # Use Period objects for correct chronological ordering, then convert to string
    df["YearMonth"] = df["Date"].dt.to_period("M")
    agg = (
        df.groupby("YearMonth")
        .agg(Revenue=("Total Amount", "sum"), Profit=("Profit", "sum"), Orders=("Transaction ID", "count"))
        .reset_index()
    )
    # Sort by the PeriodIndex (chronological) and then convert YearMonth to string for display
    agg = agg.sort_values(by="YearMonth")
    agg["YearMonth"] = agg["YearMonth"].astype(str)
    return agg.reset_index(drop=True)


def daily_sales(df: pd.DataFrame) -> pd.DataFrame:
    """Revenue aggregated by Date."""
    agg = (
        df.groupby("Date")
        .agg(Revenue=("Total Amount", "sum"), Orders=("Transaction ID", "count"))
        .reset_index()
        .sort_values("Date")
    )
    return agg


def category_sales(df: pd.DataFrame) -> pd.DataFrame:
    """Revenue and profit by Product Category."""
    return (
        df.groupby("Product Category")
        .agg(
            Revenue=("Total Amount", "sum"),
            Profit=("Profit", "sum"),
            Units=("Quantity", "sum"),
            Orders=("Transaction ID", "count"),
        )
        .reset_index()
    )


def region_sales(df: pd.DataFrame) -> pd.DataFrame:
    """Revenue by Region."""
    return (
        df.groupby("Region")
        .agg(Revenue=("Total Amount", "sum"), Profit=("Profit", "sum"), Orders=("Transaction ID", "count"))
        .reset_index()
    )


def heatmap_data(df: pd.DataFrame) -> pd.DataFrame:
    """Revenue pivot: Month x Product Category."""
    df = df.copy()
    df["Month_Name"] = pd.Categorical(
        df["Month_Name"],
        categories=["Jan", "Feb", "Mar", "Apr", "May", "Jun",
                    "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"],
        ordered=True,
    )
    pivot = df.pivot_table(
        values="Total Amount", index="Month_Name", columns="Product Category", aggfunc="sum", fill_value=0
    )
    return pivot


def product_performance(df: pd.DataFrame) -> pd.DataFrame:
    """Per-category product metrics."""
    return (
        df.groupby("Product Category")
        .agg(
            Revenue=("Total Amount", "sum"),
            Profit=("Profit", "sum"),
            Units=("Quantity", "sum"),
            Returns=("Is_Return", "sum"),
            Orders=("Transaction ID", "count"),
        )
        .assign(
            Return_Rate=lambda x: x["Returns"] / x["Orders"] * 100,
            Profit_Margin=lambda x: x["Profit"] / x["Revenue"] * 100,
            Avg_Price=lambda x: x["Revenue"] / x["Units"],
        )
        .reset_index()
    )


def customer_summary(df: pd.DataFrame) -> pd.DataFrame:
    """Per-customer summary for clustering."""
    return (
        df.groupby("Customer ID")
        .agg(
            Total_Spend=("Total Amount", "sum"),
            Num_Orders=("Transaction ID", "count"),
            Avg_Order=("Total Amount", "mean"),
            Unique_Categories=("Product Category", "nunique"),
            Age=("Age", "first"),
        )
        .reset_index()
    )


def gender_age_heatmap(df: pd.DataFrame) -> pd.DataFrame:
    """Pivot of Total Amount by Gender x Age_Band."""
    pivot = df.pivot_table(
        values="Total Amount", index="Gender", columns="Age_Band", aggfunc="sum", fill_value=0
    )
    return pivot


def inventory_df(df: pd.DataFrame) -> pd.DataFrame:
    """Stock levels per category and month."""
    df = df.copy()
    df["YearMonth"] = df["Date"].dt.to_period("M").astype(str)
    return (
        df.groupby(["YearMonth", "Product Category"])
        .agg(Units_Sold=("Quantity", "sum"), Revenue=("Total Amount", "sum"))
        .reset_index()
        .sort_values("YearMonth")
    )


def financial_waterfall(df: pd.DataFrame) -> dict:
    """Data for financial waterfall chart."""
    total_revenue = df["Total Amount"].sum()
    discount = df["Discount_Amount"].sum()
    net_rev = df["Net_Revenue"].sum()
    cogs = net_rev - df["Net_Profit"].sum()
    net_profit = df["Net_Profit"].sum()

    return {
        "labels": ["Gross Revenue", "Discounts", "Net Revenue", "COGS", "Net Profit"],
        "values": [total_revenue, -discount, net_rev, -cogs, net_profit],
        "measure": ["absolute", "relative", "total", "relative", "total"],
    }


def quarterly_margin(df: pd.DataFrame) -> pd.DataFrame:
    """Gross margin % by quarter."""
    q = (
        df.groupby(["Year", "Quarter"])
        .agg(Revenue=("Total Amount", "sum"), Profit=("Profit", "sum"))
        .reset_index()
    )
    q["Margin_Pct"] = q["Profit"] / q["Revenue"] * 100
    q["Label"] = "Q" + q["Quarter"].astype(str) + " " + q["Year"].astype(str)
    return q


# ---------------------------------------------------------------------------
# Formatting Helpers
# ---------------------------------------------------------------------------

def fmt_currency(value: float) -> str:
    """Format a number as a currency string."""
    if value >= 1_000_000:
        return f"${value / 1_000_000:.2f}M"
    if value >= 1_000:
        return f"${value / 1_000:.1f}K"
    return f"${value:.0f}"


def fmt_pct(value: float) -> str:
    return f"{value:.1f}%"


def fmt_number(value: float) -> str:
    if value >= 1_000_000:
        return f"{value / 1_000_000:.2f}M"
    if value >= 1_000:
        return f"{value / 1_000:.1f}K"
    return f"{value:.0f}"

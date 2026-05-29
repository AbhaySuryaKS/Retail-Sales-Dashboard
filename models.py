"""
models.py
---------
Machine learning logic for the dashboard:
  - Customer segmentation via KMeans clustering
  - Customer segmentation via KMeans clustering
"""

import numpy as np
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler

import utils


# ---------------------------------------------------------------------------
# Customer Clustering
# ---------------------------------------------------------------------------

def cluster_customers(df: pd.DataFrame, n_clusters: int = 3) -> pd.DataFrame:
    """
    Run KMeans on customer-level summary features.

    Parameters
    ----------
    df          : raw (filtered) dataframe
    n_clusters  : number of segments

    Returns
    -------
    Customer summary dataframe with a 'Cluster' column added.
    """
    cust = utils.customer_summary(df)
    if len(cust) < n_clusters:
        cust["Cluster"] = 0
        return cust

    features = ["Total_Spend", "Num_Orders", "Avg_Order", "Unique_Categories"]
    X = cust[features].fillna(0).values

    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    km = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
    cust["Cluster"] = km.fit_predict(X_scaled)

    return cust


def get_cluster_stats(clustered_df: pd.DataFrame) -> pd.DataFrame:
    """Aggregate stats per cluster for display."""
    return (
        clustered_df.groupby("Cluster")
        .agg(
            Customers=("Customer ID", "count"),
            Avg_Spend=("Total_Spend", "mean"),
            Avg_Orders=("Num_Orders", "mean"),
            Avg_Order_Value=("Avg_Order", "mean"),
        )
        .reset_index()
        .round(2)
    )


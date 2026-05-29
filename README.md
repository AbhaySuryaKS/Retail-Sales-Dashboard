# 📊 Retail Sales Analytics Dashboard

A production-quality, interactive business intelligence dashboard built with Python, Dash, and Plotly. Analyses a retail sales CSV dataset and visualises insights across seven analytics domains.

---

## ✨ Features

| Section                 | What you get                                                                                           |
| ----------------------- | ------------------------------------------------------------------------------------------------------ |
| **Executive Overview**  | 7 live KPI cards — Revenue, Profit, Gross Margin, Orders, Units, AOV, Return Rate                      |
| **Sales Analytics**     | Daily area chart, monthly bar, category donut, region bars, weekday averages, month × category heatmap |
| **Product Analytics**   | Revenue treemap, profit-margin scatter, top-category bars, return-rate chart                           |
| **Customer Analytics**  | KMeans customer segmentation, spend histogram, gender×age heatmap, purchase-frequency distribution     |
| **Inventory Analytics** | Monthly units-sold lines, stock-movement heatmap, inventory-valuation bubble chart                     |
| **Financial Analytics** | Waterfall (revenue → profit), quarterly margin trend, discount-impact grouped bars                     |
| **Forecasting**         | Removed from this project                                                                              |

All charts and KPIs update **instantly** when you change any filter.

---

## 🗂 Project Structure

```
project/
├── app.py                  # Dash app, layout, callbacks
├── utils.py                # Data loading, preprocessing, KPI helpers
├── charts.py               # All Plotly chart functions
├── models.py               # ML — KMeans clustering
├── requirements.txt        # Python dependencies
├── README.md
├── assets/
│   └── styles.css          # Dark theme CSS
└── data/
    └── retail_sales_dataset.csv
```

---

## 🚀 Installation & Running

### 1. Clone / copy the project folder

```bash
cd project/
```

### 2. (Recommended) Create a virtual environment

```bash
python -m venv .venv
source .venv/bin/activate      # macOS/Linux
.venv\Scripts\activate         # Windows
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Run the dashboard

```bash
python app.py
```

Open your browser at **http://localhost:8050**

---

## 📦 Dependencies

| Package        | Version | Purpose                            |
| -------------- | ------- | ---------------------------------- |
| `dash`         | 2.17    | Web framework & reactive callbacks |
| `plotly`       | 5.22    | Interactive charts                 |
| `pandas`       | 2.2     | Data manipulation                  |
| `numpy`        | 1.26    | Numerical operations               |
| `scikit-learn` | 1.5     | KMeans clustering                  |
| `gunicorn`     | 22.0    | Production WSGI server (optional)  |

---

## 🗄 Dataset

The dashboard expects a CSV at `data/retail_sales_dataset.csv` with these columns:

| Column           | Type       | Description                     |
| ---------------- | ---------- | ------------------------------- |
| Transaction ID   | int        | Unique order ID                 |
| Date             | YYYY-MM-DD | Transaction date                |
| Customer ID      | str        | Customer identifier             |
| Gender           | str        | Male / Female                   |
| Age              | int        | Customer age                    |
| Product Category | str        | Electronics / Clothing / Beauty |
| Quantity         | int        | Units purchased                 |
| Price per Unit   | int        | Unit price                      |
| Total Amount     | int        | Quantity × Price per Unit       |

The following columns are **engineered** at startup:

- `Region` — deterministically derived from Customer ID hash
- `Profit`, `Net_Revenue`, `Net_Profit` — from per-category margin rates
- `Discount_Amount` — from per-category discount rates
- `Is_Return` — probabilistic flag per category return rates
- `Age_Band`, time features (`Month`, `Quarter`, `Week`, etc.)

---

## ⚙️ Configuration

All tunable constants live in `utils.py`:

```python
CATEGORY_MARGIN       = {"Electronics": 0.22, "Clothing": 0.38, "Beauty": 0.45}
CATEGORY_RETURN_RATE  = {"Electronics": 0.08, "Clothing": 0.05, "Beauty": 0.03}
CATEGORY_DISCOUNT     = {"Electronics": 0.12, "Clothing": 0.08, "Beauty": 0.05}
```

---

## 🖥 Production Deployment

```bash
gunicorn app:server -b 0.0.0.0:8050 --workers 2
```

## Additional production notes

- Recommended to run behind a process manager or in a container (Docker).
- To run via Gunicorn (container / PaaS):

```bash
gunicorn wsgi:app -b 0.0.0.0:8050 --workers 4
```

Docker quickstart:

```bash
docker build -t retail-dashboard:latest .
docker run -p 8050:8050 --env-file .env -e PORT=8050 retail-dashboard:latest
```

Configuration via environment variables (or a `.env` file):

- `PORT` — port to bind (default: `8050`)
- `DEBUG` or `FLASK_DEBUG` — set to `1`/`true` to enable debug mode
- `LOG_LEVEL` — `INFO`/`DEBUG`/`WARNING`

CI: a GitHub Actions workflow runs a smoke test on push/pull-request.

---

## 📝 License

MIT — free to use and modify.

# 📊 data-consulting-aws-lab

### **End-to-End Data Analytics & Consulting Lab using AWS, Python & Modern Data Architecture**

This project simulates the real work of a **Data Consultant / Data Engineer** inside a mid-sized enterprise struggling with **data silos**.
Your mission is to:

✔ Ingest & unify disconnected datasets
✔ Build a consistent enterprise data model
✔ Generate synthetic data for 5 business domains
✔ Prepare pipelines for AWS (S3, Glue, Athena)
✔ Perform analytics, modeling & dashboarding

It is designed as a **real consulting project**, helping you learn the exact workflow used by AWS partners, Deloitte, Accenture, and real enterprise teams.

---

# 🏢 1. Business Context

The company has **multiple disconnected data sources (“silos”)** across the main business areas:

* Finance
* Marketing
* E-commerce
* CRM
* Web Analytics

Your job is to **centralize all this data**, create a **unified analytical model**, and prepare everything for a cloud data platform.

---

# 🧩 2. Project Architecture (Final Structure)

```
data-consulting-aws-lab/
│
├── .venv/                          ← Local Python virtual environment
│
├── data/
│   ├── raw/                        ← Raw synthetic datasets (bronze layer)
│   │   ├── finance/
│   │   ├── marketing/
│   │   ├── ecommerce/
│   │   ├── crm/                    ← future
│   │   └── web/                    ← future
│   │
│   ├── processed/                  ← Cleaned / transformed datasets (silver)
│   └── docs/                       ← Data dictionaries & domain documentation
│
├── docs/
│   ├── diagrams/                   ← System diagrams, ERDs, architecture
│   ├── domain_definitions.md
│   ├── data_dictionary.md
│   └── architecture.md
│
├── notebooks/                      ← EDA, analytics, experiments
│   ├── finance_analysis.ipynb
│   ├── marketing_analysis.ipynb
│   ├── ecommerce_analysis.ipynb
│   └── aws_setup.ipynb
│
├── src/
│   ├── etl/                        ← ETL pipelines: synthetic data generators
│   │   ├── generate_finance_data.py
│   │   ├── generate_marketing_data.py
│   │   ├── generate_ecommerce_domain.py
│   │   ├── generate_crm_data.py          ← future
│   │   └── generate_web_analytics.py     ← future
│   │
│   ├── analytics/                  ← Business logic, metrics, KPI engines
│   │   ├── finance_metrics.py
│   │   ├── ecommerce_kpis.py
│   │   └── marketing_attribution.py
│   │
│   ├── models/                     ← ML models: churn, LTV, segmentation
│   │   ├── churn_model.py
│   │   └── product_recommender.py
│   │
│   └── utils/                      ← Helpers for logging, configs, validations
│       ├── logger.py
│       ├── file_io.py
│       └── validation.py
│
├── tests/                          ← Unit tests for ETL and analytics modules
│   ├── test_finance_etl.py
│   ├── test_marketing_etl.py
│   └── test_ecommerce_etl.py
│
├── .gitignore
├── requirements.txt
└── README.md
```

---

# 🧱 3. Business Domains & Datasets

The following **five universal enterprise domains** are implemented (or will be):

---

## **Finance Domain**

✔ Accounting & revenue backbone
✔ Source of truth for financial transactions

**Datasets**

* orders
* invoices
* payments
* expenses
* vendors
* chart_of_accounts
* gl_transactions

---

## **Marketing Domain**

✔ Paid media
✔ Funnels: Lead → MQL → Customer → Buyer
✔ Ad attribution & spend tracking

**Datasets**

* campaigns
* ad_groups
* ads
* daily_performance
* leads

---

## **E-commerce Domain**

✔ Online transactions
✔ Customer behavior
✔ Product catalog
✔ Returns & unit economics

**Datasets**

* products
* customers
* orders (linked to Finance)
* order_items
* returns

---

## **CRM Domain** *(upcoming)*

✔ Customer 360°
✔ Segmentation
✔ Interactions & support tickets
✔ Churn predictions

---

## **Web Analytics Domain** *(upcoming)*

✔ User behavior
✔ Digital funnels
✔ Traffic sources
✔ Pageview tracking

---

# 📘 4. Key Consulting & Data Terms (learn these)

These terms are used daily in data engineering, analytics consulting, and AWS workflows:

| Term                 | Meaning                                    |
| -------------------- | ------------------------------------------ |
| **Domain**           | A business area (Finance, Marketing, CRM)  |
| **Entity**           | Logical dataset (Customer, Order, Product) |
| **Silo**             | Data stored in isolation                   |
| **Attribute**        | Column of a dataset                        |
| **Primary Key (PK)** | Unique identifier                          |
| **Foreign Key (FK)** | Reference to another table                 |
| **Fact Table**       | Stores events: orders, payments, clicks    |
| **Dimension Table**  | Stores context: customers, dates           |
| **Star Schema**      | Fact in the center, dimensions around      |
| **Synthetic Data**   | Realistic fake data for learning/testing   |

---

# 🚀 5. Git Workflow (Professional Branching Strategy)

This repo uses a **consulting-standard Git Flow**:

```
main        → stable production code  
test        → integration & QA environment  
feature/*   → active development branches
```

Workflow:

```
feature → test → main
```

No direct pushes to main.

---

# 🌩️ 6. AWS Implementation Roadmap

This project is designed to migrate into a cloud-native AWS pipeline:

### **1. AWS S3 (Data Lake)**

* Raw (bronze)
* Cleaned (silver)
* Curated (gold)

### **2. AWS Glue**

* Crawlers (schema discovery)
* ETL (PySpark jobs)
* Catalog (Hive Metastore)

### **3. AWS Athena**

* Query the data lake
* Build star schemas
* Prepare analytics tables

### **4. Amazon QuickSight**

* Dashboards:

  * Finance
  * Marketing
  * E-commerce
  * Customer 360°

### **5. Optional ML**

* Churn prediction
* Segmentation
* Marketing attribution models
* Demand forecasting

---

# 🔧 7. How to Run Local ETL

Activate your environment:

```bash
source .venv/Scripts/activate
```

Generate each domain:

```bash
python src/etl/generate_finance_data.py
python src/etl/generate_marketing_data.py
python src/etl/generate_ecommerce_domain.py
```

Outputs are saved into:

```
data/raw/<domain>/
```

---

# 📈 8. Purpose of This Lab

This project helps you build skills in:

✔ Data engineering
✔ Analytics consulting
✔ Enterprise data modeling
✔ ETL pipelines
✔ AWS data lake architecture
✔ BI & SQL analysis
✔ ML pipeline integration


# 🙌 Author

**Juan Leon**
Data Engineer • AI & Computing Science Student • AWS + Python Practitioner



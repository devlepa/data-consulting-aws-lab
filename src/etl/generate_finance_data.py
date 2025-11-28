import pandas as pd
import numpy as np

np.random.seed(42)

# ---------------------------
# 1. Chart of Accounts (COA)
# ---------------------------
coa = pd.DataFrame({
    "account_id": [1000, 2000, 3000, 4000, 5000],
    "account_name": [
        "Cash",
        "Accounts Receivable",
        "Accounts Payable",
        "Revenue",
        "Operating Expenses"
    ],
    "category": [
        "Asset",
        "Asset",
        "Liability",
        "Revenue",
        "Expense"
    ]
})


# ---------------------------
# 2. Vendors
# ---------------------------
vendor_ids = np.arange(1, 51)
vendors = pd.DataFrame({
    "vendor_id": vendor_ids,
    "vendor_name": [f"Vendor_{i}" for i in vendor_ids],
    "category": np.random.choice(["Supplies", "Marketing", "Technology", "HR"], len(vendor_ids)),
    "payment_terms": np.random.choice(["Net 30", "Net 45", "Net 60"], len(vendor_ids))
})


# ---------------------------
# 3. Orders (fact)
# ---------------------------
num_orders = 2000
orders = pd.DataFrame({
    "order_id": np.arange(1, num_orders + 1),
    "customer_id": np.random.randint(1, 1000, num_orders),
    "order_date": pd.date_range("2023-01-01", periods=num_orders, freq="h"),
    "order_amount": np.round(np.random.uniform(20, 1000, num_orders), 2),
    "status": np.random.choice(["completed", "pending", "canceled"], num_orders)
})


# ---------------------------
# 4. Invoices
# ---------------------------
invoice_ids = np.arange(1, num_orders + 1)

invoices = pd.DataFrame({
    "invoice_id": invoice_ids,
    "order_id": invoice_ids,
    "invoice_date": orders["order_date"] + pd.to_timedelta(np.random.randint(1,5, num_orders), unit="D"),
    "due_date": orders["order_date"] + pd.to_timedelta(np.random.randint(30,45, num_orders), unit="D"),
    "amount_due": orders["order_amount"],
    "tax": orders["order_amount"] * 0.19,
    "discount": np.round(np.random.uniform(0, 50, num_orders), 2),
    "total_amount": lambda df: df["amount_due"] + df["tax"] - df["discount"],
    "status": np.random.choice(["paid", "unpaid", "partial"], num_orders)
})

# compute final total
invoices["total_amount"] = invoices["amount_due"] + invoices["tax"] - invoices["discount"]


# ---------------------------
# 5. Payments (fact)
# ---------------------------
payments = invoices[invoices["status"] == "paid"].copy()
payments["payment_id"] = np.arange(1, len(payments) + 1)
payments["payment_date"] = payments["invoice_date"] + pd.to_timedelta(np.random.randint(1,30, len(payments)), unit="D")
payments["amount_paid"] = payments["total_amount"]


# ---------------------------
# 6. Expenses (fact)
# ---------------------------
num_expenses = 1000
expenses = pd.DataFrame({
    "expense_id": np.arange(1, num_expenses + 1),
    "vendor_id": np.random.choice(vendor_ids, num_expenses),
    "expense_date": pd.date_range("2023-01-01", periods=num_expenses, freq="12h"),
    "amount": np.round(np.random.uniform(50, 8000, num_expenses), 2),
    "cost_center": np.random.choice(["Marketing", "Operations", "Tech", "HR"], num_expenses),
    "account_id": 5000  # Operating Expenses
})


# ---------------------------
# 7. General Ledger (GL Transactions)
# ---------------------------
gl = []

# revenue entries
for _, row in invoices.iterrows():
    gl.append({
        "gl_id": len(gl) + 1,
        "account_id": 4000,  # Revenue
        "transaction_date": row["invoice_date"],
        "amount": row["total_amount"]
    })
    gl.append({
        "gl_id": len(gl) + 1,
        "account_id": 2000,  # Accounts Receivable
        "transaction_date": row["invoice_date"],
        "amount": row["total_amount"]
    })

# expense entries
for _, row in expenses.iterrows():
    gl.append({
        "gl_id": len(gl) + 1,
        "account_id": 5000,  # Operating Expenses
        "transaction_date": row["expense_date"],
        "amount": -row["amount"]
    })
    gl.append({
        "gl_id": len(gl) + 1,
        "account_id": 3000,  # Accounts Payable
        "transaction_date": row["expense_date"],
        "amount": row["amount"]
    })

gl_transactions = pd.DataFrame(gl)


# ---------------------------
# SAVE ALL DATA
# ---------------------------
import os
path = "../../data/raw/finance/"
os.makedirs(path, exist_ok=True)

coa.to_csv(path + "chart_of_accounts.csv", index=False)
vendors.to_csv(path + "vendors.csv", index=False)
orders.to_csv(path + "orders.csv", index=False)
invoices.to_csv(path + "invoices.csv", index=False)
payments.to_csv(path + "payments.csv", index=False)
expenses.to_csv(path + "expenses.csv", index=False)
gl_transactions.to_csv(path + "gl_transactions.csv", index=False)

print("Full finance domain generated successfully.")

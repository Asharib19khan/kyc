# Power BI "Live" Connection Guide (Python Method)

To make your dashboard update **directly** from the database (without running the export script every time), follow these steps:

## 1. Get Data via Python
1.  In Power BI Desktop, click **Get Data** -> **More...**
2.  Search for **Python script** and select it.
3.  Click **Connect**.

## 2. Paste this Script
Copy and paste the code below. **IMPORTANT**: I have pre-filled your exact database path.

```python
import sqlite3
import pandas as pd
import os

# Your Database Path
db_path = r'C:\Users\pc\Desktop\New folder\data\kyc.sqlite3'

conn = sqlite3.connect(db_path)

# Load Tables directly into Power BI
Customers = pd.read_sql_query("SELECT * FROM Customers", conn)
Verifications = pd.read_sql_query("SELECT * FROM Verifications", conn)
Transactions = pd.read_sql_query("SELECT * FROM Transactions", conn)
FinancialHealth = pd.read_sql_query("SELECT * FROM FinancialHealth", conn)
LoanEligibility = pd.read_sql_query("SELECT * FROM LoanEligibility", conn)

conn.close()
```

## 3. Load & Refresh
1.  Click **OK**.
2.  Select all the tables (Customers, Verifications, etc.) and click **Load**.
3.  **That's it!**

## 4. Create Relationships (Crucial Step)
Power BI loads the tables, but you still need to link them:
1.  Go to the **Model View** (icon on the left sidebar).
2.  Drag `id` from the **Customers** table to `customer_id` in:
    *   **Verifications**
    *   **Transactions**
    *   **FinancialHealth**
    *   **LoanEligibility**
3.  Ensure the relationship is **One to Many** (1 -> *).

## ⚡ How to Update?
Now, whenever you want to see the latest data:
*   Just click the big **Refresh** button in the Power BI Home ribbon.
*   It will pull the latest data straight from your SQLite database.
*   No need to run `export_powerbi.py` ever again!

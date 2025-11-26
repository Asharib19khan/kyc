# Power BI Integration Guide

## 1. Generate Data
1.  Run the export script:
    ```bash
    python export_powerbi.py
    ```
2.  This creates a folder `powerbi_data/` with CSV files.

## 2. Import into Power BI Desktop
1.  Open **Power BI Desktop**.
2.  Click **Get Data** -> **Text/CSV**.
3.  Navigate to the `powerbi_data` folder and select `Customers.csv`.
4.  Click **Load**.
5.  Repeat for `Verifications.csv`, `Transactions.csv`, etc.

## 3. Create Relationships (Model View)
1.  Go to the **Model View** (icon on the left).
2.  Drag `id` from **Customers** table to `customer_id` in **Verifications**, **Transactions**, etc.
3.  Ensure the relationship is **One to Many** (1 -> *).

## 4. Build Your Dashboard
*   **Card**: Count of `Customers[id]`.
*   **Pie Chart**: `Verifications[status]`.
*   **Map**: `Customers[address]` (or City if you split it).
*   **Table**: List of `Transactions`.

## 5. Refresh Data
*   Whenever you want new data, run `python export_powerbi.py` again.
*   In Power BI, just click the **Refresh** button.

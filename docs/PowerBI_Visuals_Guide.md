# Power BI Visuals Guide: Building the "Perfect" Dashboard

Based on your screenshot, you are currently seeing "Sum of id", which is not what we want. Here is how to build a professional dashboard step-by-step.

## 1. The "Big Numbers" (KPI Cards)
*Display total customers and pending requests at the top.*

1.  Click on an empty space in the canvas.
2.  Select the **Card** visual (looks like a big "123").
3.  Drag `Customers[id]` into the **Fields** box.
4.  **Fix the "Sum" issue**:
    *   Click the small arrow next to `Sum of id` in the Fields pane.
    *   Select **Count** (or Count Distinct).
    *   *Result: You should see a number like "3" or "10".*
5.  Rename it to "Total Customers" (Double-click the label in Fields).

## 2. Verification Status (Donut Chart)
*See how many people are Verified vs Rejected.*

1.  Select the **Donut Chart** visual.
2.  **Legend**: Drag `Verifications[status]`.
3.  **Values**: Drag `Verifications[id]`.
    *   *Again, ensure it says "Count of id", not Sum.*
4.  You will now see a nice breakdown of your approval rates.

## 3. Financial Analysis (Bar Chart)
*Where are people spending money?*

1.  Select the **Clustered Bar Chart**.
2.  **Y-Axis**: Drag `Transactions[category]`.
3.  **X-Axis**: Drag `Transactions[amount]`.
4.  **Legend**: Drag `Transactions[type]` (Debit/Credit).
    *   *This will show you Salary (Credit) vs Food/Transport (Debit).*

## 4. Risk Analysis (Gauge)
*What is the average risk in your system?*

1.  Select the **Gauge** visual.
2.  **Value**: Drag `Verifications[risk_score]`.
3.  Change aggregation to **Average** (Click arrow -> Average).
4.  This shows the average risk level of your entire customer base.

---

### 🎨 Pro Tips for "Perfect" UI
*   **Remove Backgrounds**: Click Format (Paintbrush icon) -> General -> Effects -> Turn off Background.
*   **Titles**: Make them bold and centered (Format -> General -> Title).
*   **Theme**: Go to **View** tab -> **Themes** -> Select "Storm" or "Innovate" for a dark/modern look.

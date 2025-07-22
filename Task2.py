import pandas as pd
from datetime import datetime
from reportlab.lib.pagesizes import letter
from reportlab.platypus import (SimpleDocTemplate, Paragraph, Spacer,
                                Table, TableStyle)
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors
import os, random

# ---------- 1. Create / load sales data ---------------------------------
csv_path = "sales_data.csv"

# For demo: build a 30‑day sample dataset (three products)
sample_sales = pd.DataFrame({
    "Date": pd.date_range("2025-06-01", periods=30, freq="D").repeat(3),
    "Prdt": ["Widget A", "Widget B", "Widget C"] * 30,
    "Qty": [random.randint(1, 10) for _ in range(90)],
    "Unit_Price": [20, 15, 25] * 30
})
sample_sales["Revenue"] = sample_sales["Qty"] * sample_sales["Unit_Price"]
sample_sales.to_csv(csv_path, index=False)

# Replace the two lines above with:
# df = pd.read_csv("your_sales_file.csv", parse_dates=["Date"])

df = pd.read_csv(csv_path, parse_dates=["Date"])
df["Month"] = df["Date"].dt.to_period("M")

# ---------- 2. Analysis --------------------------------------------------
monthly_rev = df.groupby("Month")["Revenue"].sum().reset_index()
top_products = (df.groupby("Prdt")["Revenue"]
                  .sum()
                  .sort_values(ascending=False)
                  .reset_index())

kpis = {
    "Total Orders": len(df),
    "Total Units Sold": df["Qty"].sum(),
    "Total Revenue": df["Revenue"].sum(),
    "Average Order Value": round(df["Revenue"].mean(), 2)
}

# ---------- 3. Build the PDF --------------------------------------------
pdf_file = "sales_performance_report.pdf"
doc = SimpleDocTemplate(pdf_file, pagesize=letter)
styles = getSampleStyleSheet()
elements = [Paragraph("Monthly Sales Performance Report", styles["Title"]),
            Spacer(1, 12)]

# KPIs
elements.append(Paragraph("Key Performance Indicators:", styles["Heading2"]))
for k, v in kpis.items():
    elements.append(Paragraph(f"<b>{k}:</b> {v}", styles["Normal"]))
elements.append(Spacer(1, 12))

# Monthly revenue table
elements.append(Paragraph("Revenue by Month:", styles["Heading2"]))
mon_table = Table([monthly_rev.columns.astype(str).tolist()] +
                  monthly_rev.astype(str).values.tolist(),
                  hAlign="LEFT")
mon_table.setStyle(TableStyle([
    ('BACKGROUND', (0,0), (-1,0), colors.lightgrey),
    ('GRID', (0,0), (-1,-1), 0.5, colors.black),
    ('ALIGN', (1,1), (-1,-1), 'RIGHT'),
]))
elements.append(mon_table)
elements.append(Spacer(1, 12))

# Top products table
elements.append(Paragraph("Top Products by Revenue:", styles["Heading2"]))
prod_table = Table([top_products.columns.astype(str).tolist()] +
                   top_products.astype(str).values.tolist(),
                   hAlign="LEFT")
prod_table.setStyle(TableStyle([
    ('BACKGROUND', (0,0), (-1,0), colors.lightgrey),
    ('GRID', (0,0), (-1,-1), 0.5, colors.black),
    ('ALIGN', (1,1), (-1,-1), 'RIGHT'),
]))
elements.append(prod_table)

# Create PDF
doc.build(elements)
print(f"Report saved to {os.path.abspath(pdf_file)}")

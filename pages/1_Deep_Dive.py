import streamlit as st
import pandas as pd
import altair as alt

# Load and prepare data
data = pd.read_csv("Input_Sales_Data_v2.csv")
data["Date"] = pd.to_datetime(data["Date"])

st.title("Deep Dive Analysis")

# Top Filter Section
col1, col2, col3, col4 = st.columns([1, 2, 2, 2])

with col1:
    category = st.selectbox("Category", sorted(data["Category"].dropna().unique()))

with col2:
    filtered_manufacturers = data[data["Category"] == category]["Manufacturer"].dropna().unique()
    manufacturer = st.selectbox("Manufacturer", sorted(filtered_manufacturers))

with col3:
    filtered_brands = data[
        (data["Category"] == category) &
        (data["Manufacturer"] == manufacturer)
    ]["Brand"].dropna().unique()
    brand = st.selectbox("Brand", sorted(filtered_brands))

with col4:
    filtered_skus = data[
        (data["Category"] == category) &
        (data["Manufacturer"] == manufacturer) &
        (data["Brand"] == brand)
    ]["SKU Name"].dropna().unique()
    sku_names = st.multiselect("SKU Name", sorted(filtered_skus))

# Filter Data
filtered_data = data[
    (data["Category"] == category) &
    (data["Manufacturer"] == manufacturer) &
    (data["Brand"] == brand)
]

if sku_names:
    filtered_data = filtered_data[filtered_data["SKU Name"].isin(sku_names)]

# YTD Metrics
ytd_volume = filtered_data["Volume"].sum()
ytd_value = filtered_data["Value"].sum()
market_total_value = data[data["Category"] == category]["Value"].sum()
market_share = (ytd_value / market_total_value) * 100 if market_total_value else 0

col1, col2, col3, col4 = st.columns(4)
col1.metric("YTD Volume Sales", f"{ytd_volume:,.0f}")
col2.metric("YTD $ Sales", f"{ytd_value:,.0f}")
col3.metric("YTD Market Share", f"{market_share:.2f}%")
col4.metric("# SKUs", filtered_data["SKU Name"].nunique())

st.divider()

# Charts Row 1
c1, c2 = st.columns(2)

# Weekly Volume & Value Line Chart
weekly = filtered_data.groupby("Date")[["Volume", "Value"]].sum().reset_index()
if not weekly.empty:
    weekly_chart = alt.Chart(weekly).transform_fold(
        ["Volume", "Value"],
        as_=["Metric", "Value"]
    ).mark_line().encode(
        x="Date:T",
        y="Value:Q",
        color="Metric:N"
    ).properties(title="Weekly Volume & Value Sales", width=400, height=300)
    c1.altair_chart(weekly_chart, use_container_width=True)

# Pie Chart: Top 10 SKUs by Value
top10 = filtered_data.groupby("SKU Name")["Value"].sum().nlargest(10).reset_index()
if not top10.empty:
    pie_chart = alt.Chart(top10).mark_arc().encode(
        theta="Value:Q",
        color="SKU Name:N",
        tooltip=["SKU Name", "Value"]
    ).properties(title="% Value Sales by Top 10 SKUs", width=400, height=300)
    c2.altair_chart(pie_chart, use_container_width=True)

# Charts Row 2
c3, c4 = st.columns(2)

# Price vs Volume Trend Line Chart
if "Price" in filtered_data.columns:
    price_trend = filtered_data.groupby("Date")[["Price", "Volume"]].mean().reset_index()
    if not price_trend.empty:
        price_chart = alt.Chart(price_trend).transform_fold(
            ["Price", "Volume"],
            as_=["Metric", "Value"]
        ).mark_line().encode(
            x="Date:T",
            y="Value:Q",
            color="Metric:N"
        ).properties(title="Price vs Volume Trend", width=400, height=300)
        c3.altair_chart(price_chart, use_container_width=True)

# Price + Value Trend for SKUs
if sku_names:
    sku_trend = filtered_data.groupby(["Date", "SKU Name"])[["Price", "Value"]].mean().reset_index()
    if not sku_trend.empty:
        sku_chart = alt.Chart(sku_trend).mark_line().encode(
            x="Date:T",
            y="Value:Q",
            color="SKU Name:N",
            tooltip=["SKU Name", "Value"]
        ).properties(title="Price & $Value per SKU", width=400, height=300)
        c4.altair_chart(sku_chart, use_container_width=True)

st.divider()

# Bottom Charts
b1, b2 = st.columns(2)

# Line Chart for SKU-wise Weekly Volume/Value
if sku_names:
    sku_weekly = filtered_data.groupby(["Date", "SKU Name"])[["Volume", "Value"]].sum().reset_index()
    if not sku_weekly.empty:
        line_chart = alt.Chart(sku_weekly).transform_fold(
            ["Volume", "Value"],
            as_=["Metric", "Value"]
        ).mark_line().encode(
            x="Date:T",
            y="Value:Q",
            color="Metric:N",
            tooltip=["SKU Name", "Value"]
        ).properties(title="SKU-wise Weekly Sales", width=400, height=300)
        b1.altair_chart(line_chart, use_container_width=True)

# Monthly Avg Value Bar Chart
if sku_names:
    filtered_data["Month"] = filtered_data["Date"].dt.to_period("M").astype(str)
    bar_data = filtered_data.groupby(["Month", "SKU Name"])["Value"].mean().reset_index()

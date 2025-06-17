# IMPORTING REQUIRED LIBRARIES
import streamlit as st
import pandas as pd
import altair as alt

# PAGE CONFIG
st.set_page_config(
    page_title="Manufacturer Sales Dashboard",
    layout="wide"
)

# LOAD DATA
data = pd.read_csv("Input_Sales_Data_v2.csv")
data['Date'] = pd.to_datetime(data['Date'])

# SIDEBAR SETUP
st.sidebar.image("tiger.png", use_container_width=True)
st.sidebar.header("Filter Options")

# Date Range Slider
start_date, end_date = st.sidebar.slider(
    "Select Date Range",
    min_value=data['Date'].min().to_pydatetime(),
    max_value=data['Date'].max().to_pydatetime(),
    value=(data['Date'].min().to_pydatetime(), data['Date'].max().to_pydatetime()),
    format="YYYY-MM-DD"
)

# Metric Selector
metric = st.sidebar.radio(
    "Select Sales Metric for Top 5 Trend",
    options=['Volume', 'Value'],
    index=0
)

# Toggle for table display
show_table = st.sidebar.checkbox("Show Manufacturer-wise Sales Table", value=True)

# Filter Data
filtered_data = data[(data['Date'] >= start_date) & (data['Date'] <= end_date)]

# MAIN PAGE TITLE
st.title("📊 Manufacturer Sales Dashboard")
st.markdown(f"### ⏱ Showing data from **{start_date.date()}** to **{end_date.date()}**")

# TABLE SECTION
if show_table:
    st.subheader("🔢 Total Volume and Value Sales by Manufacturer")
    st.dataframe(
        filtered_data.groupby('Manufacturer')[['Volume', 'Value']].sum().sort_values(by=metric, ascending=False)
    )

# TOP 5 MANUFACTURERS by selected metric
top_5_manufacturers = (
    filtered_data.groupby('Manufacturer')[metric]
    .sum()
    .nlargest(5)
    .index
)

# Filter only top 5
top_data = filtered_data[filtered_data['Manufacturer'].isin(top_5_manufacturers)]

# Group for trend plotting
trend_data = (
    top_data.groupby(['Date', 'Manufacturer'])[metric]
    .sum()
    .reset_index()
)

# LINE CHART
st.subheader(f"📈 Trend of Top 5 Manufacturers by {metric} Over Time")
chart = alt.Chart(trend_data).mark_line(point=True).encode(
    x='Date:T',
    y=f'{metric}:Q',
    color='Manufacturer:N',
    tooltip=['Date:T', 'Manufacturer:N', f'{metric}:Q']
).properties(
    width=1000,
    height=450
)

st.altair_chart(chart, use_container_width=True)

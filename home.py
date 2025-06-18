# Home.py

import streamlit as st
import pandas as pd
import altair as alt

# Load data
data = pd.read_csv("Input_Sales_Data_v2.csv")

# Sidebar
st.sidebar.title("Filters")

data["Date"] = pd.to_datetime(data["Date"])

# Dropdown for Category
category = st.sidebar.selectbox("Select Category", sorted(data["Category"].unique()))

# Slider for Date
date_selected = st.sidebar.slider(
    "Select Date",
    min_value=data["Date"].min().date(),
    max_value=data["Date"].max().date()
)

# Filter data
filtered_data = data[
    (data["Date"].dt.date == date_selected) &
    (data["Category"] == category)
]

# Market share
total_value_sales = filtered_data["Value"].sum()
filtered_data["Market Share"] = (filtered_data["Value"] / total_value_sales) * 100

# Sort
filtered_data = filtered_data.sort_values(by="Value", ascending=False)

# Style
styled_df = filtered_data.style \
    .format({"Value": "{:,.0f}", "Market Share": "{:.2f}%"}) \
    .background_gradient(cmap="Blues", subset=["Market Share"])

# Title
st.title("Sales Dashboard")
st.dataframe(styled_df, use_container_width=True)

# Chart
chart = alt.Chart(filtered_data).mark_bar().encode(
    x="Brand",
    y="Value",
    tooltip=["Brand", "Value", "Market Share"]
).properties(width=700, height=400)

st.altair_chart(chart, use_container_width=True)

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
# from PIL import Image

# icon = Image.open("")

st.set_page_config(
    page_title="Retail Intelligence Dashboard",
    page_icon="",
    layout="wide"
)


@st.cache_data
def load_data():

    df = pd.read_csv("cleaned_online_retail.csv")

    df["InvoiceDate"] = pd.to_datetime(df["InvoiceDate"])

    ## Extract data-time columns 
    df["Year"] = df["InvoiceDate"].dt.year
    df["Month"] = df["InvoiceDate"].dt.month
    df["MonthName"] = df['InvoiceDate'].dt.month_name()
    df["DayName"] = df['InvoiceDate'].dt.day_name()
    df['Hour'] = df["InvoiceDate"].dt.hour

    #converting customerID to string
    df["CustomerID"] = df["CustomerID"].astype(str)

    # Creating the revenue feature
    df["Revenue"] = df['Quantity'] * df['UnitPrice']

    df['YearMonth'] = df['InvoiceDate'].dt.to_period("M").astype(str)

    return df


def classify_customer(revenue):
    if revenue >= 10000:
        return "High Value"
    elif revenue >= 5000:
        return "Medium Value"
    else:
        return "Low Value"


### Use the load data function 
df = load_data()

## Create a Header 
st.title("Retail Intelligence Dashboard")
st.write("Sales, Customer and Product performance analysis")

# add divider
st.divider()

## Dashboard Navigation 
page = st.sidebar.radio(
    "Navigation",
    [
        "Sales Overview",
        "Product Analysis",
        "Customer Analysis",
        "Time Intelligence",
        "Data Explorer",
    ]
)

## Add sidebar filters 
countries = ["All"] + sorted(
    df["Country"].dropna().unique().tolist()
)

selected_country = st.sidebar.selectbox(
    "Country", countries
)

# Apply the filter to df
filtered_df = df.copy()
if selected_country != "All":
    filtered_df = filtered_df[
        filtered_df['Country'] == selected_country
        ]


if page == "Sales Overview":
    st.header("Business Overview")

    # Calculate KPI
    total_revenue = df["Revenue"].sum()
    total_orders = df['InvoiceNo'].nunique()
    total_customers = df['CustomerID'].nunique()
    total_products = df['StockCode'].nunique()
  
    col1, col2, col3, col4 = st.columns(4)

    col1.metric("Revenue", f"N{total_revenue:,.0f}")
    col2.metric("Orders", f"{total_orders}")
    col3.metric("Customers", f"{total_customers}")
    col4.metric("Products", f"{total_products}")

    ## Revenue Trend
    monthly_revenue = (
    filtered_df.groupby("YearMonth")['Revenue'].sum().reset_index()
    )

    fig = px.area(monthly_revenue, x="YearMonth", y="Revenue", 
                markers=True, title="Monthly Revenue Trend")

    st.plotly_chart(fig, use_container_width=True)

    #Plotting 2 charts of Countries and Products 
    col1, col2 = st.columns(2)

    country_sales = (
    filtered_df.groupby("Country")["Revenue"]
    .sum()
    .sort_values(ascending=False)
    .head(10)
    .reset_index()
    )

    #Visualize 
    fig_country = px.bar(
        country_sales, 
        x="Revenue",
        y ="Country", 
        orientation="h",
        title="Top Countries"
    )
    fig.update_layout(yaxis={"categoryorder": "total ascending"})

    col1.plotly_chart(fig_country, use_container_width=True)

    # For Products
    product_revenue = (
    filtered_df.groupby("Description")
    .agg(
        Revenue =('Revenue', "sum"),
        Quantity = ("Quantity", "sum")
    )
    .sort_values("Revenue", ascending=False)
    .reset_index()
    )

    top_products = product_revenue.head(5)

    fig_product = px.bar(
        top_products,
        x="Revenue",
        y="Description",
        orientation="h",
        title="Top 5 Products by Revenue"
    )

    fig.update_layout(yaxis={"categoryorder" : "total ascending"})

    col2.plotly_chart(fig_product, use_container_width=True)


elif page == "Product Analysis":
    st.header("Product Performance")

    products = (
    filtered_df.groupby("Description")
    .agg(
        Revenue =('Revenue', "sum"),
        UnitsSold = ("Quantity", "sum"),
        Orders=("InvoiceNo", "nunique"),
        AveragePrice = ("UnitPrice", "mean")
    )
    .reset_index()
    )

    metric = st.selectbox(
        "Rank Products By",
        [
            "Revenue",
            "UnitsSold",
            "Orders",
            "AveragePrice"
        ]
    )

    top_products= (
        products.sort_values(metric, ascending=False)
        .head(5)
    )

    fig= px.bar(
        top_products,
        x=metric, 
        y="Description",
        orientation="h",
        title=f"Top Products by {metric}"
    )

    st.plotly_chart(fig, use_container_width=True)


elif page == "Customer Analysis":
    st.header("Customer Intelligence")

    col1, col2 = st.columns(2)

    with col1 :
        customer_data = filtered_df.groupby("CustomerID").agg(
                Revenue = ("Revenue", "sum"),
                Orders=("InvoiceNo", "nunique"),
                Units=("Quantity", "sum")         
                    ).reset_index()

        top_customers = (
            customer_data.sort_values("Revenue", ascending=False).head(10)
        )

        fig = px.bar(
            top_customers, 
            x= "CustomerID",
            y="Revenue", 
            title="Top Customers by Revenue"
        )

        fig.update_xaxes(type='category')

        st.plotly_chart(fig, use_container_width=True)


    with col2:
        customer_revenue = (df.groupby("CustomerID")['Revenue']
                        .sum().reset_index())
        
        customer_revenue["CustomerClass"] = (
            customer_revenue["Revenue"].apply(classify_customer)
            )

        class_summary = (customer_revenue.groupby("CustomerClass")
        .agg(
            NumberOfCustomers = ("CustomerID", "nunique"), 
            TotalRevenue = ("Revenue", "sum")
        )
        .reset_index()
        )

        class_summary["RevenuePercentage"] = (
        class_summary['TotalRevenue'] / 
        class_summary['TotalRevenue'].sum() * 100
        )

        fig = px.pie(
        class_summary, 
        names = "CustomerClass",
        values="TotalRevenue",
        title="Revenue Share by Customer Class",
        hole=0.4
        )

        st.plotly_chart(fig, use_container_width=True)


elif page == "Time Intelligence":
    st.header("Time Intelligence")
    col1, col2 = st.columns(2)

    day_revenue = (
        df.groupby("DayName")["Revenue"].sum()
        .reset_index()
        )

    day_order = [
        "Monday",
        "Tuesday",
        "Wednesday",
        "Thursday",
        "Friday",
        "Saturday",
        "Sunday"
    ]

    ## Reorder DayName using the day_order
    day_revenue['DayName'] = pd.Categorical(
        day_revenue['DayName'],
        categories=day_order,
        ordered=True
    )

    day_revenue = day_revenue.sort_values("DayName")

    fig = px.bar(
        day_revenue,
        x="DayName",
        y="Revenue",
        title="Revenue by Day of the week"
    )

    with col1 :
        st.plotly_chart(fig, use_container_width=True)

    ## We need to get how many orders in each hour using Unique InvoiceNo
    hourly_orders = (
        df.groupby("Hour")['InvoiceNo'].nunique()
        .reset_index(name="Orders")
    )

    fig = px.line(
        hourly_orders,
        x="Hour",
        y="Orders",
        markers=True,
        title = "Orders by Hour of Day"
        )

    with col2 :
            st.plotly_chart(fig, use_container_width=True)



elif page == "Data Explorer":

    st.header("Explore Datatset")
    st.dataframe(filtered_df, use_container_width=True)

    #Add Search :
    product_search = st.text_input(
        "Search Product"
    )

    if product_search:
        search_df = filtered_df[
            filtered_df["Description"].str.contains(
                product_search, case=False, na=False
            )
        ]

        st.dataframe(
            search_df, use_container_width=True
        )
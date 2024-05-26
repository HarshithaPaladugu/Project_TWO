import pandas as pd
from sqlalchemy import create_engine
import streamlit as st
import plotly.express as px

# MySQL connection details
host = 'localhost'
user = 'root'
password = '1611'
database = 'PhonePePulse_DVandExp'

# Create a connection to MySQL
engine = create_engine(f"mysql+mysqlconnector://{user}:{password}@{host}/{database}")

# Fetch transaction data
def fetch_transaction_data():
    query = """
    SELECT 
        State, 
        SUM(Transacion_count) AS Total_No_of_Transactions, 
        SUM(Transacion_amount) AS Total_Transaction_Amount 
    FROM agg_transaction 
    GROUP BY State
    """
    df = pd.read_sql(query, engine)
    return df

# Fetch user data
def fetch_user_data():
    query = "SELECT State, SUM(Num_of_Reg_Users) AS Total_Users FROM agg_user GROUP BY State"
    df = pd.read_sql(query, engine)
    return df

# Fetch data by mobile brand
def fetch_brand_data():
    query = """
    SELECT 
        Brand_Name,
        SUM(Transacion_count) AS Total_No_of_Transactions, 
        SUM(Transacion_amount) AS Total_Transaction_Amount, 
        SUM(Num_of_Reg_Users) AS Total_Users 
    FROM 
        agg_transaction 
    JOIN 
        agg_user 
    USING 
        (State) 
    GROUP BY 
        Brand_Name
    """
    df = pd.read_sql(query, engine)
    return df

# Fetch data
transaction_df = fetch_transaction_data()
user_df = fetch_user_data()
brand_df = fetch_brand_data()

# Merge the datasets on the 'State' column
merged_df = pd.merge(transaction_df, user_df, on='State', how='inner')

# Calculate the sum of total transactions
total_transactions_sum = merged_df['Total_No_of_Transactions'].sum()

# Load geojson file
geojson_url = "https://gist.githubusercontent.com/jbrobst/56c13bbbf9d97d187fea01ca62ea5112/raw/e388c4cae20aa53cb5090210a42ebb9b765c0a36/india_states.geojson"

# Streamlit application
st.title("PhonePe Pulse Data Visualization")

# Display the total number of transactions
st.metric(label="Total Number of Transactions (All States)", value=f"{total_transactions_sum:,.0f}")

# Dropdown to select the metric to visualize
metric = st.selectbox("Select Metric", ["Total_Users", "Total_No_of_Transactions", "Brand Correlation"])

if metric == "Total_No_of_Transactions" or metric == "Total_Users":
    # Create a choropleth map
    fig = px.choropleth(
        merged_df,
        geojson=geojson_url,
        featureidkey='properties.ST_NM',
        locations='State',
        color=metric,
        color_continuous_scale='Aggrnyl',
        range_color=(0, merged_df[metric].max()),  # Set the range of the color scale
        title=f'{metric} by State'
    )

    fig.update_geos(fitbounds="locations", visible=False)

    # Display the map
    st.plotly_chart(fig)

    # Create and display a bar graph for transaction count by state if the metric is 'Total_No_of_Transactions'
    if metric == 'Total_No_of_Transactions':
        bar_fig = px.bar(
            merged_df,
            x='State',
            y='Total_No_of_Transactions',
            title='Total Number of Transactions by State',
            labels={'Total_No_of_Transactions': 'Total Transactions', 'State': 'State'}
        )
        st.plotly_chart(bar_fig)

    # Create and display a bar graph for registered users count by state if the metric is 'Total_Users'
    elif metric == 'Total_Users':
        bar_fig = px.bar(
            merged_df,
            x='State',
            y='Total_Users',
            title='Total Number of Registered Users by State',
            labels={'Total_Users': 'Total Registered Users', 'State': 'State'}
        )
        st.plotly_chart(bar_fig)

elif metric == "Brand Correlation":
    # Create scatter plots to visualize the correlation between the number of registered users and transaction volumes for each brand
    scatter_fig = px.scatter(
        brand_df,
        x='Total_Users',
        y='Total_No_of_Transactions',
        size='Total_Transaction_Amount',
        color='Brand_Name',
        title='Correlation between Registered Users and Transaction Volumes by Mobile Brand',
        labels={'Total_Users': 'Total Registered Users', 'Total_No_of_Transactions': 'Total Transactions', 'Total_Transaction_Amount': 'Total Transaction Amount'}
    )
    st.plotly_chart(scatter_fig)

    # Create a bar graph for transaction count by mobile brand
    bar_fig = px.bar(
        brand_df,
        x='Brand_Name',
        y='Total_No_of_Transactions',
        title='Total Number of Transactions by Mobile Brand',
        labels={'Total_No_of_Transactions': 'Total Transactions', 'Mobile_Brand': 'Mobile Brand'}
    )
    st.plotly_chart(bar_fig)
import pandas as pd
from sqlalchemy import create_engine
import streamlit as st
import plotly.express as px

# MySQL connection details
host = 'localhost'
user = 'root'
password = '1611'
database = 'PhonePePulse_DVandExp'

# Create a connection to MySQL
engine = create_engine(f"mysql+mysqlconnector://{user}:{password}@{host}/{database}")

# Streamlit application
st.title("PhonePe Pulse Data Visualization")

# Dropdown to select the insight
insight = st.selectbox("Select Insight", ["User Growth Over Time", "Most Popular Districts", "App Opens", "Brand Market Share", "Top Brands", "Brand Correlation", "Regional Popularity by Brand", "Yearly Growth by Brand","Top States by Transactions","Top Districts by Users","Yearly User Growth","Top Pincodes by Transaction Value"])

# Fetch data and display the selected insight
if insight == "User Growth Over Time":
    query = """
    SELECT Year, Quarter, SUM(Num_of_reg_users) AS Total_Users
    FROM map_user
    GROUP BY Year, Quarter
    ORDER BY Year, Quarter;
    """
    df = pd.read_sql(query, engine)
    df['Year_Quarter'] = df['Year'].astype(str) + ' Q' + df['Quarter'].astype(str)
    fig = px.line(df, x='Year_Quarter', y='Total_Users', title='User Growth Over Time')
    st.plotly_chart(fig)

elif insight == "Most Popular Districts":
    query = """
    SELECT Dist_Name, SUM(Num_of_reg_users) AS Total_Users
    FROM map_user
    GROUP BY Dist_Name
    ORDER BY Total_Users DESC
    LIMIT 10;
    """
    df = pd.read_sql(query, engine)
    fig = px.bar(df, x='Dist_Name', y='Total_Users', title='Most Popular Districts')
    st.plotly_chart(fig)

elif insight == "App Opens":
    query = """
    SELECT Year, Quarter, SUM(Num_of_app_opens) AS Total_App_Opens
    FROM map_user
    GROUP BY Year, Quarter
    ORDER BY Year, Quarter;
    """
    df = pd.read_sql(query, engine)
    df['Year_Quarter'] = df['Year'].astype(str) + ' Q' + df['Quarter'].astype(str)
    fig = px.line(df, x='Year_Quarter', y='Total_App_Opens', title='App Opens Over Time')
    st.plotly_chart(fig)

elif insight == "Brand Market Share":
    query = """
    SELECT Year, Quarter, Brand_Name, SUM(Num_of_Reg_Users) AS Total_Users, AVG(Percent_Share) AS Average_Share
    FROM agg_user
    GROUP BY Year, Quarter, Brand_Name
    ORDER BY Year, Quarter, Total_Users DESC;
    """
    df = pd.read_sql(query, engine)
    df['Year_Quarter'] = df['Year'].astype(str) + ' Q' + df['Quarter'].astype(str)
    fig = px.bar(df, x='Year_Quarter', y='Total_Users', color='Brand_Name', title='Brand Market Share', labels={'Total_Users': 'Total Users', 'Brand_Name': 'Brand'})
    st.plotly_chart(fig)

elif insight == "Top Brands":
    query = """
    SELECT Brand_Name, SUM(Num_of_Reg_Users) AS Total_Users
    FROM agg_user
    GROUP BY Brand_Name
    ORDER BY Total_Users DESC
    LIMIT 10;
    """
    df = pd.read_sql(query, engine)
    fig = px.bar(df, x='Brand_Name', y='Total_Users', title='Top Brands')
    st.plotly_chart(fig)

elif insight == "Brand Correlation":
    query = """
    SELECT 
        au.Brand_Name,
        SUM(au.Num_of_Reg_Users) AS Total_Users,
        SUM(at.Transaction_Count) AS Total_Transactions,
        SUM(at.Transaction_Amount) AS Total_Amount
    FROM 
        agg_user au
    JOIN 
        agg_transaction at
    ON 
        au.State = at.State AND au.Year = at.Year AND au.Quarter = at.Quarter
    GROUP BY 
        au.Brand_Name
    ORDER BY 
        Total_Transactions DESC;
    """
    df = pd.read_sql(query, engine)
    fig = px.scatter(df, x='Total_Users', y='Total_Transactions', size='Total_Amount', color='Brand_Name', title='Brand Correlation')
    st.plotly_chart(fig)

elif insight == "Regional Popularity by Brand":
    query = """
    SELECT 
        au.State,
        au.Brand_Name,
        SUM(au.Num_of_Reg_Users) AS Total_Users,
        AVG(au.Percent_Share) AS Average_Share
    FROM 
        agg_user au
    GROUP BY 
        au.State, au.Brand_Name
    ORDER BY 
        au.State, Total_Users DESC;
    """
    df = pd.read_sql(query, engine)
    fig = px.bar(df, x='State', y='Total_Users', color='Brand_Name', title='Regional Popularity by Brand')
    st.plotly_chart(fig)

elif insight == "Yearly Growth by Brand":
    query = """
    SELECT 
        Year,
        Brand_Name,
        SUM(Num_of_Reg_Users) AS Total_Users
    FROM 
        agg_user
    GROUP BY 
        Year, Brand_Name
    ORDER BY 
        Year, Total_Users DESC;
    """
    df = pd.read_sql(query, engine)
    fig = px.line(df, x='Year', y='Total_Users', color='Brand_Name', title='Yearly Growth by Brand')
    st.plotly_chart(fig)
elif  insight == "Top States by Transactions":
    query = """
    SELECT State, SUM(Tot_No_of_Trans) AS Total_Transactions
    FROM top_trans_state
    GROUP BY State
    ORDER BY Total_Transactions DESC
    LIMIT 10;
    """
    df = pd.read_sql(query, engine)
    fig = px.bar(df, x='State', y='Total_Transactions', title='Top 10 States by Number of Transactions')
    st.plotly_chart(fig)
elif insight == "Top Districts by Users":
    query = """
    SELECT District_Name, SUM(Reg_Users) AS Total_Users
    FROM top_user_dis
    GROUP BY District_Name
    ORDER BY Total_Users DESC
    LIMIT 10;
    """
    df = pd.read_sql(query, engine)
    fig = px.bar(df, x='District_Name', y='Total_Users', title='Top 10 Districts by Number of Users')
    st.plotly_chart(fig)
elif insight == "Yearly User Growth":
    query = """
    SELECT Year, SUM(Reg_Users) AS Total_Users
    FROM top_user_dis
    GROUP BY Year
    ORDER BY Year;
    """
    df = pd.read_sql(query, engine)
    fig = px.line(df, x='Year', y='Total_Users', title='Yearly Growth in Number of Users')
    st.plotly_chart(fig)
elif insight == "Top Pincodes by Transaction Value":
    query = """
    SELECT Pincode, SUM(Tot_Val_of_PTrans) AS Total_Transaction_Value
    FROM top_trans_pin
    GROUP BY Pincode
    ORDER BY Total_Transaction_Value DESC
    LIMIT 10;
    """
    df = pd.read_sql(query, engine)
    fig = px.bar(df, x='Pincode', y='Total_Transaction_Value', title='Top 10 Pincodes by Transaction Value')
    st.plotly_chart(fig)
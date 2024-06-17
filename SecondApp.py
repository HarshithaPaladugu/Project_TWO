import pandas as pd
from sqlalchemy import create_engine
import streamlit as st
import plotly.express as px
import requests
# MySQL connection details
host = 'localhost'
user = 'root'
password = '1611'
database = 'PhonePePulse_DVandExp'

# Create a connection to MySQL
engine = create_engine(f"mysql+mysqlconnector://{user}:{password}@{host}/{database}")

geojson_url = "https://gist.githubusercontent.com/jbrobst/56c13bbbf9d97d187fea01ca62ea5112/raw/e388c4cae20aa53cb5090210a42ebb9b765c0a36/india_states.geojson"

# Function to fetch available years
def fetch_years():
    query = "SELECT DISTINCT Year FROM agg_user ORDER BY Year"
    df = pd.read_sql(query, engine)
    return df['Year'].tolist()

# Function to fetch available quarters
def fetch_quarters(year):
    if year == "Complete Data":
        return ["Whole_Year"]
    query = f"SELECT DISTINCT Quarter FROM agg_user WHERE Year = {year} ORDER BY Quarter"
    df = pd.read_sql(query, engine)
    return df['Quarter'].tolist()

# Fetch transaction data for the selected year and quarter
def fetch_transaction_data(selected_year, selected_quarter):
    if selected_year == "Complete Data":
        query = """
        SELECT 
            State, 
            SUM(Transacion_count) AS Total_No_of_Transactions, 
            SUM(Transacion_amount) AS Total_Transaction_Amount 
        FROM agg_transaction 
        GROUP BY State
        """
    elif selected_quarter == "Whole_Year":
        query = f"""
        SELECT 
            State, 
            SUM(Transacion_count) AS Total_No_of_Transactions, 
            SUM(Transacion_amount) AS Total_Transaction_Amount 
        FROM agg_transaction 
        WHERE Year = {selected_year}
        GROUP BY State
        """
    else:
        query = f"""
        SELECT 
            State, 
            SUM(Transacion_count) AS Total_No_of_Transactions, 
            SUM(Transacion_amount) AS Total_Transaction_Amount 
        FROM agg_transaction 
        WHERE Year = {selected_year} AND Quater = {selected_quarter}
        GROUP BY State
        """
    df = pd.read_sql(query, engine)
    return df

# Fetch user data for the selected year and quarter
def fetch_user_data(selected_year, selected_quarter):
    if selected_year == "Complete Data":
        query = """
        SELECT State, SUM(Num_of_Reg_Users) AS Total_Users 
        FROM agg_user 
        GROUP BY State
        """
    elif selected_quarter == "Whole_Year":
        query = f"""
        SELECT State, SUM(Num_of_Reg_Users) AS Total_Users 
        FROM agg_user 
        WHERE Year = {selected_year}
        GROUP BY State
        """
    else:
        query = f"""
        SELECT State, SUM(Num_of_Reg_Users) AS Total_Users 
        FROM agg_user 
        WHERE Year = {selected_year} AND Quarter = {selected_quarter}
        GROUP BY State
        """
    df = pd.read_sql(query, engine)
    return df

# Streamlit application
st.title("PhonePe Pulse Data Visualization")




# Dropdown to select the insight
insight = st.selectbox("Select Insight", [
    "Number Of Registered_Users for the selected time period", 
    "Number of registered users for each state during the selected time period",  
    "Brand Market Share", 
    "Yearly Growth by Brand",
    "The First six states which had highest values of transaction amount", 
    "The First five states which had least values of transaction amount", 
    "Growth of Registerd_Users for each State over the time period", 
    "The First six states which had highest number of total transactions",
    "The First six states which had least number of total transactions",
    "The highest transaction type count in each state",
    
], key="insight_select")

# Fetch data and display the selected insight
if insight == "Number Of Registered_Users for the selected time period":
    # Dropdown to select the year
    years = ["Complete Data"] + fetch_years()
    selected_year = st.selectbox("Select Year", years, key="year_select")

# Dropdown to select the quarter based on the selected year
    quarters =["Whole_Year"] + fetch_quarters(selected_year)
    selected_quarter = st.selectbox("Select Quarter", quarters, key="quarter_select")
    # Fetch data for the selected year and quarter
    transaction_df = fetch_transaction_data(selected_year, selected_quarter)
    user_df = fetch_user_data(selected_year, selected_quarter)
    merged_df = pd.merge(transaction_df, user_df, on='State', how='inner')
    if selected_year == "Complete Data":
        if selected_quarter == "Whole_Year":
            query = """
            SELECT SUM(Num_of_reg_users) AS Total_Users
            FROM map_user
            """
        else:
            query = f"""
            SELECT Year, SUM(Num_of_reg_users) AS Total_Users
            FROM map_user
            WHERE Quarter = '{selected_quarter}'
            GROUP BY Year
            ORDER BY Year
            """
    elif selected_quarter == "Whole_Year":
        query = f"""
        SELECT SUM(Num_of_reg_users) AS Total_Users
        FROM map_user
        WHERE Year = {selected_year}
        """
    else:
        query = f"""
        SELECT SUM(Num_of_reg_users) AS Total_Users
        FROM map_user
        WHERE Year = {selected_year} AND Quarter = '{selected_quarter}'
        """
    
    df = pd.read_sql(query, engine)

    if selected_year == "Complete Data" and selected_quarter == "Whole_Year":
        total_users = df['Total_Users'].iloc[0]
        title = "Complete Data"
        st.header(f"Number Of Registered Users for {title}")
        st.subheader(f"Total Number of Registered Users: {total_users}")
    elif selected_year == "Complete Data":
        st.header(f"Number Of Registered Users for {selected_quarter}")
        for index, row in df.iterrows():
            st.subheader(f"Year {row['Year']}: {row['Total_Users']} Registered Users")
    else:
        total_users = df['Total_Users'].iloc[0]
        if selected_quarter == "Whole Year":
            title = f"Year {selected_year}"
        else:
            title = f"Year {selected_year} Q{selected_quarter}"
        st.header(f"Number Of Registered Users for {title}")
        st.subheader(f"Total Number of Registered Users: {total_users}")

elif insight ==  "Number of registered users for each state during the selected time period":
    # Dropdown to select the year
    years = ["Complete Data"] + fetch_years()
    selected_year = st.selectbox("Select Year", years, key="year_select")

    # Dropdown to select the quarter based on the selected year
    quarters = ["Whole_Year"] + fetch_quarters(selected_year)
    selected_quarter = st.selectbox("Select Quarter", quarters, key="quarter_select")
    
    if selected_year == "Complete Data":
        query = """
        SELECT Year, State, SUM(Num_of_reg_users) AS Total_Users
        FROM map_user
        GROUP BY Year, State
        ORDER BY Year, State;
        """
    elif selected_quarter == "Whole_Year":
        query = f"""
        SELECT Year, State, SUM(Num_of_reg_users) AS Total_Users
        FROM map_user
        WHERE Year = {selected_year}
        GROUP BY Year, State
        ORDER BY Year, State;
        """
    else:
        query = f"""
        SELECT Year, Quarter, State, SUM(Num_of_reg_users) AS Total_Users
        FROM map_user
        WHERE Year = {selected_year} AND Quarter = {selected_quarter}
        GROUP BY Year, Quarter, State
        ORDER BY Year, Quarter, State;
        """
    
    df = pd.read_sql(query, engine)
    
    # Create the bar chart
    title = "Registered users for each state"
    if selected_year != "Complete Data":
        title += f" in the year {selected_year}"
        if selected_quarter != "Whole_Year":
            title += f" for Q{selected_quarter}"
    
    fig = px.bar(df, x='Year', y='Total_Users', color='State', barmode='group', title=title, labels={'Total_Users': 'Total Users'})
    st.plotly_chart(fig)


elif insight == "Brand Market Share":
    # Dropdown to select the year
    years = ["Complete Data"] + fetch_years()
    selected_year = st.selectbox("Select Year", years, key="year_select")

# Dropdown to select the quarter based on the selected year
    quarters =["Whole_Year"] + fetch_quarters(selected_year)
    selected_quarter = st.selectbox("Select Quarter", quarters, key="quarter_select")

    def fetch_brands():
        query = "SELECT DISTINCT Brand_Name FROM agg_user ORDER BY Brand_Name"
        df = pd.read_sql(query, engine)
        return df['Brand_Name'].tolist()
    
    brands = fetch_brands()
    selected_brand = st.selectbox("Select Brand", brands, key="brand_select")
    
    if selected_year == "Complete Data":
        query = f"""
        SELECT Year, Quarter, Brand_Name, SUM(Num_of_Reg_Users) AS Total_Users, AVG(Percent_Share) AS Average_Share
        FROM agg_user
        WHERE Brand_Name = '{selected_brand}'
        GROUP BY Year, Quarter, Brand_Name
        ORDER BY Year, Quarter, Total_Users DESC;
        """
    elif selected_quarter == "Whole_Year":
        query = f"""
        SELECT Year, Quarter, Brand_Name, SUM(Num_of_Reg_Users) AS Total_Users, AVG(Percent_Share) AS Average_Share
        FROM agg_user
        WHERE Year = {selected_year} AND Brand_Name = '{selected_brand}'
        GROUP BY Year, Quarter, Brand_Name
        ORDER BY Year, Quarter, Total_Users DESC;
        """
    else:
        query = f"""
        SELECT Year, Quarter, Brand_Name, SUM(Num_of_Reg_Users) AS Total_Users, AVG(Percent_Share) AS Average_Share
        FROM agg_user
        WHERE Year = {selected_year} AND Quarter = {selected_quarter} AND Brand_Name = '{selected_brand}'
        GROUP BY Year, Quarter, Brand_Name
        ORDER BY Year, Quarter, Total_Users DESC;
        """
    df = pd.read_sql(query, engine)
    df['Year_Quarter'] = df['Year'].astype(str) + ' Q' + df['Quarter'].astype(str)

    # Display brand market share values
    st.subheader(f'Brand Market Share for {selected_brand}')
    for index, row in df.iterrows():
        st.write(f"{row['Year_Quarter']}: {row['Average_Share']:.2f}%")

    # Pie chart for average market share
    fig_pie = px.pie(df, values='Average_Share', names='Year_Quarter', title=f'Average Market Share for {selected_brand}', labels={'Average_Share': 'Average Share', 'Year_Quarter': 'Year/Quarter'})
    st.plotly_chart(fig_pie)

elif insight == "Growth of Registerd_Users for each State over the time period":
    query = """
    SELECT 
        Year,
        State,
        SUM(Reg_Users) AS Total_Users
    FROM 
        top_user_dis
    GROUP BY 
        Year, State
    ORDER BY 
        Year;
    """
    
    df = pd.read_sql(query, engine)
    
    # Create a dropdown menu for state selection
    states = df['State'].unique()
    selected_state = st.selectbox('Select a state', states)
    
    # Filter the DataFrame based on the selected state
    df_filtered = df[df['State'] == selected_state]
    
    # Create a line chart
    title = f"Yearly Growth in Number of Users for {selected_state}"
    fig_line = px.line(df_filtered, x='Year', y='Total_Users', title=title, labels={'Total_Users': 'Total Users'})
    st.plotly_chart(fig_line)

elif insight == "The First six states which had highest values of transaction amount":
    query = """
    WITH State_Trans_Values AS (
        SELECT 
            State,
            SUM(Tot_Val_of_Trans) AS Total_Transaction_Value
        FROM 
            top_trans_state
        GROUP BY 
            State
    )
    SELECT 
        State,
        Total_Transaction_Value
    FROM 
        State_Trans_Values
    ORDER BY 
        Total_Transaction_Value DESC
    LIMIT 7;
    """
    
    df = pd.read_sql(query, engine)
    
    # Ensure state names in the GeoJSON match those in the DataFrame
    df['State'] = df['State'].str.title()  # Example transformation if necessary
    
    geojson_url = "https://gist.githubusercontent.com/jbrobst/56c13bbbf9d97d187fea01ca62ea5112/raw/e388c4cae20aa53cb5090210a42ebb9b765c0a36/india_states.geojson"
    response = requests.get(geojson_url)
    india_states = response.json()
    # Create the choropleth map
    fig = px.choropleth(
        df,
        geojson=india_states,
        featureidkey='properties.ST_NM',  # Adjust this key to match your GeoJSON properties
        locations='State',
        color='Total_Transaction_Value',
        color_continuous_scale='Viridis',
        title='Top 5 States by Transaction Value',
        labels={'Total_Transaction_Value': 'Total Transaction Value'},
        scope="asia"
    )
    
    fig.update_geos(fitbounds="locations", visible=False)
    st.plotly_chart(fig)
elif insight == "The First five states which had least values of transaction amount":
    query = """
    WITH State_Trans_Values AS (
        SELECT 
            State,
            SUM(Tot_Val_of_Trans) AS Total_Transaction_Value
        FROM 
            top_trans_state
        GROUP BY 
            State
    )
    SELECT 
        State,
        Total_Transaction_Value
    FROM 
        State_Trans_Values
    ORDER BY 
        Total_Transaction_Value ASC
    LIMIT 7;
    """
    
    df = pd.read_sql(query, engine)
    
    # Ensure state names in the GeoJSON match those in the DataFrame
    df['State'] = df['State'].str.title()  # Example transformation if necessary
    
    geojson_url = "https://gist.githubusercontent.com/jbrobst/56c13bbbf9d97d187fea01ca62ea5112/raw/e388c4cae20aa53cb5090210a42ebb9b765c0a36/india_states.geojson"
    response = requests.get(geojson_url)
    india_states = response.json()
    # Create the choropleth map
    fig = px.choropleth(
        df,
        geojson=india_states,
        featureidkey='properties.ST_NM',  # Adjust this key to match your GeoJSON properties
        locations='State',
        color='Total_Transaction_Value',
        color_continuous_scale='Viridis',
        title='Bottom 5 States by Transaction Value',
        labels={'Total_Transaction_Value': 'Total Transaction Value'},
        scope="asia"
    )
    
    fig.update_geos(fitbounds="locations", visible=False)
    st.plotly_chart(fig)
elif insight == "The First six states which had highest number of total transactions":
    query = """
    WITH State_Trans_Numbers AS (
        SELECT 
            State,
            SUM(Tot_No_of_Trans) AS Total_Transaction_Number
        FROM 
            top_trans_state
        GROUP BY 
            State
    )
    SELECT 
        State,
        Total_Transaction_Number
    FROM 
        State_Trans_Numbers
    ORDER BY 
        Total_Transaction_Number DESC
    LIMIT 7;
    """
    
    df = pd.read_sql(query, engine)
    
    # Ensure state names in the GeoJSON match those in the DataFrame
    df['State'] = df['State'].str.title()  # Example transformation if necessary
    
    geojson_url = "https://gist.githubusercontent.com/jbrobst/56c13bbbf9d97d187fea01ca62ea5112/raw/e388c4cae20aa53cb5090210a42ebb9b765c0a36/india_states.geojson"
    response = requests.get(geojson_url)
    india_states = response.json()
    # Create the choropleth map
    fig = px.choropleth(
        df,
        geojson=india_states,
        featureidkey='properties.ST_NM',  # Adjust this key to match your GeoJSON properties
        locations='State',
        color='Total_Transaction_Number',
        color_continuous_scale='Viridis',
        title='Top 5 States by Number of Transactions',
        labels={'Total_Transaction_Number': 'Total Number of Transactions'},
        scope="asia"
    )
    
    fig.update_geos(fitbounds="locations", visible=False)
    st.plotly_chart(fig)

elif insight == "The First six states which had least number of total transactions":
    query = """
    WITH State_Trans_Numbers AS (
        SELECT 
            State,
            SUM(Tot_No_of_Trans) AS Total_Transaction_Number
        FROM 
            top_trans_state
        GROUP BY 
            State
    )
    SELECT 
        State,
        Total_Transaction_Number
    FROM 
        State_Trans_Numbers
    ORDER BY 
        Total_Transaction_Number ASC
    LIMIT 8;
    """
    
    df = pd.read_sql(query, engine)
    
    # Ensure state names in the GeoJSON match those in the DataFrame
    df['State'] = df['State'].str.title()  # Example transformation if necessary
    geojson_url = "https://gist.githubusercontent.com/jbrobst/56c13bbbf9d97d187fea01ca62ea5112/raw/e388c4cae20aa53cb5090210a42ebb9b765c0a36/india_states.geojson"
    response = requests.get(geojson_url)
    india_states = response.json()
    # Create the choropleth map
    fig = px.choropleth(
        df,
        geojson=india_states,
        featureidkey='properties.ST_NM',  # Adjust this key to match your GeoJSON properties
        locations='State',
        color='Total_Transaction_Number',
        color_continuous_scale='Viridis',
        title='Top 5 States by Number of Transactions',
        labels={'Total_Transaction_Number': 'Total Number of Transactions'},
        scope="asia"
    )
    
    fig.update_geos(fitbounds="locations", visible=False)
    st.plotly_chart(fig)

elif insight == "The highest transaction type count in each state":
    
    # Load the GeoJSON data
    geojson_url = "https://gist.githubusercontent.com/jbrobst/56c13bbbf9d97d187fea01ca62ea5112/raw/e388c4cae20aa53cb5090210a42ebb9b765c0a36/india_states.geojson"
    response = requests.get(geojson_url)
    india_states = response.json()

    # SQL query to get the highest transaction count type for each state
    query = """
    WITH State_Max_Trans AS (
        SELECT
            State,
            Transacion_type,
            Transacion_count,
            ROW_NUMBER() OVER (PARTITION BY State ORDER BY Transacion_count DESC) AS rn
        FROM
            agg_transaction
    )
    SELECT
        State,
        Transacion_type,
        Transacion_count AS Max_Transaction_Count
    FROM
        State_Max_Trans
    WHERE
        rn = 1;
    """

    # Load data into DataFrame
    df = pd.read_sql(query, engine)

    # Ensure state names in the GeoJSON match those in the DataFrame
    df['State'] = df['State'].str.title()  # Adjust if necessary to match GeoJSON

    # Debug: Print the DataFrame columns
    st.write("DataFrame columns:", df.columns.tolist())

    # Debug: Check for State column presence and unique values
    st.write("States in DataFrame:", df['State'].unique())

    # Create the choropleth map
    fig = px.choropleth(
        df,
        geojson=india_states,
        featureidkey='properties.ST_NM',  # Adjust this key to match your GeoJSON properties
        locations='State',
        color='Max_Transaction_Count',
        hover_name='Transacion_type',
        color_continuous_scale='Viridis',
        title='Highest Transaction Type Count by State',
        labels={'Max_Transaction_Count': 'Max Transaction Count'},
        scope="asia"
    )

    fig.update_geos(fitbounds="locations", visible=False)
    st.plotly_chart(fig)

elif insight == "Yearly Growth by Brand":
    # Dropdown to select the year
    years = ["Complete Data"]
    selected_year = st.selectbox("Select Year", years, key="year_select")

# Dropdown to select the quarter based on the selected year
    quarters =["Whole_Year"] 
    selected_quarter = st.selectbox("Select Quarter", quarters, key="quarter_select")
    if selected_year == "Complete Data" and selected_quarter=="Whole_Year":
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

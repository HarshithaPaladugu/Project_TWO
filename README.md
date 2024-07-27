# Project_TWO

#SecondApp.py:

### 1. Import Necessary Libraries
Ensure you import all the required libraries at the beginning of your script:
```python
import pandas as pd
from sqlalchemy import create_engine
import streamlit as st
import plotly.express as px
import requests
```

### 2. Database Connection Setup
Establish a connection to the MySQL database:
```python
# MySQL connection details
host = 'localhost'
user = 'root'
password = '1611'
database = 'PhonePePulse_DVandExp'

# Create a connection to MySQL
engine = create_engine(f"mysql+mysqlconnector://{user}:{password}@{host}/{database}")
```

### 3. Load GeoJSON Data
Load the GeoJSON data for mapping Indian states:
```python
geojson_url = "https://gist.githubusercontent.com/jbrobst/56c13bbbf9d97d187fea01ca62ea5112/raw/e388c4cae20aa53cb5090210a42ebb9b765c0a36/india_states.geojson"
```

### 4. Define Helper Functions
Define functions to fetch available years, quarters, transaction data, and user data:
```python
def fetch_years():
    query = "SELECT DISTINCT Year FROM agg_user ORDER BY Year"
    df = pd.read_sql(query, engine)
    return df['Year'].tolist()

def fetch_quarters(year):
    if year == "Complete Data":
        return ["Whole_Year"]
    query = f"SELECT DISTINCT Quarter FROM agg_user WHERE Year = {year} ORDER BY Quarter"
    df = pd.read_sql(query, engine)
    return df['Quarter'].tolist()

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
```

### 5. Build Streamlit Application
Set up the Streamlit app with the necessary components and data fetching logic:
```python
st.title("PhonePe Pulse Data Visualization and Exploration")

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
```

### 6. Fetch Data Based on User Selection
Implement logic for each insight, including data fetching and visualization:
```python
if insight == "Number Of Registered_Users for the selected time period":
    years = ["Complete Data"] + fetch_years()
    selected_year = st.selectbox("Select Year", years, key="year_select")

    quarters = ["Whole_Year"] + fetch_quarters(selected_year)
    selected_quarter = st.selectbox("Select Quarter", quarters, key="quarter_select")

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
```
Continue similarly for other insights, making sure to update the queries and visualization logic as required.

### 7. Visualize Data
Use Plotly to create and display various visualizations such as bar charts, line charts, and choropleth maps:
```python
# Example for bar chart
if insight == "Number of registered users for each state during the selected time period":
    years = ["Complete Data"] + fetch_years()
    selected_year = st.selectbox("Select Year", years, key="year_select")
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
    title = "Registered users for each state"
    if selected_year != "Complete Data":
        title += f" in the year {selected_year}"
        if selected_quarter != "Whole_Year":
            title += f" for Q{selected_quarter}"
    
    fig = px.bar(df, x='Year', y='Total_Users', color='State', barmode='group', title=title, labels={'Total_Users': 'Total Users'})
    st.plotly_chart(fig)
```

### 8. Debugging and Ensuring Proper Functionality
Add debugging statements and check for potential issues:
```python
# Debug: Print the DataFrame columns
st.write("DataFrame

 Columns:", df.columns)

# Check connection to the database
try:
    connection = engine.connect()
    st.write("Successfully connected to the database!")
    connection.close()
except Exception as e:
    st.write("Error connecting to the database:", str(e))
```
By following these steps, you can create a Streamlit application that visualizes and explores PhonePe Pulse data, providing users with insights based on their selections. Adjust the queries and visualization logic for each specific insight to ensure comprehensive data representation.

#SecallTables.ipynb:
Here's a detailed breakdown of the workflow and execution for each part of the provided code:

### 1. Import Necessary Libraries
Import the required libraries at the beginning of your script:
```python
import mysql.connector
from sqlalchemy import create_engine, Column, Integer, String, Float, MetaData, Table
from sqlalchemy.ext.declarative import declarative_base
import pandas as pd
import json
import os
```

### 2. Define MySQL Connection Details
Set up the connection details for your MySQL database:
```python
# MySQL connection details
host = 'localhost'
user = 'root'
password = '1611'
database = 'PhonePePulse_DVandExp'

# Create a connection
conn = mysql.connector.connect(
    host=host,
    user=user,
    password=password,
    database=database
)
```

### 3. Define Helper Function for State Name Conversion
Define a helper function to format state names correctly:
```python
def convert_state_name(input_string):
    # Replace hyphens and special characters with spaces, then capitalize each word
    formatted_string = input_string.replace('-', ' ').replace('&', '&')
    words = formatted_string.split()
    capitalized_words = [word.capitalize() for word in words]
    return ' '.join(capitalized_words)
```

### 4. Create SQLAlchemy Engine
Create an SQLAlchemy engine to interact with the MySQL database:
```python
# Create a SQLAlchemy engine
engine = create_engine(f"mysql+mysqlconnector://{user}:{password}@{host}/{database}")
```

### 5. Load Data from JSON Files
Specify the path to your data and iterate over the files to load and process the JSON data:
```python
# Path to data
path = "C:\\Users\\HP\\GUVI PROJ\\pulse\\data\\aggregated\\transaction\\country\\india\\state\\"
Agg_state_list = os.listdir(path)

# Prepare the DataFrame
clm = {'State': [], 'Year': [], 'Quater': [], 'Transacion_type': [], 'Transacion_count': [], 'Transacion_amount': []}

for i in Agg_state_list:
    p_i = path + i + "/"
    Agg_yr = os.listdir(p_i)
    for j in Agg_yr:
        p_j = p_i + j + "/"
        Agg_yr_list = os.listdir(p_j)
        for k in Agg_yr_list:
            p_k = p_j + k
            with open(p_k, 'r') as Data:
                D = json.load(Data)
                for z in D['data']['transactionData']:
                    Name = z['name']
                    count = z['paymentInstruments'][0]['count']
                    amount = z['paymentInstruments'][0]['amount']
                    clm['Transacion_type'].append(Name)
                    clm['Transacion_count'].append(count)
                    clm['Transacion_amount'].append(amount)
                    clm['State'].append(i)
                    clm['Year'].append(j)
                    clm['Quater'].append(int(k.strip('.json')))
```

### 6. Create and Populate DataFrame
Create a DataFrame from the loaded data and format the state names:
```python
# Create DataFrame
Agg_Trans = pd.DataFrame(clm)
Agg_Trans['State'] = Agg_Trans['State'].apply(convert_state_name)
```

### 7. Store DataFrame to MySQL Table
Store the DataFrame in a MySQL table, replacing any existing data in the table:
```python
# Store DataFrame to MySQL table (ensure the table name is in lowercase)
table_name = 'agg_transaction'
Agg_Trans.to_sql(name=table_name, con=engine, if_exists='replace', index=False)
```

### 8. Close Initial Connection
Close the initial connection to the MySQL database:
```python
# Close the connection
conn.close()
```

### 9. Reopen Connection and Read Table
Reopen the connection using SQLAlchemy to read the table into a DataFrame and display the data:
```python
# Reopen the connection using SQLAlchemy for reading the table
conn = engine.connect()

# Read the table into a DataFrame
df = pd.read_sql_table(table_name, con=conn)

# Display the DataFrame
print(df)

# Close the connection
conn.close()
```


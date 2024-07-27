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
### Workflow and Execution of the Provided Code

The given code processes JSON files containing user data by device, transforms the data, and stores it in a MySQL database. Here is a breakdown of the workflow and execution for each part of the code:

1. **Import Necessary Libraries:**
   ```python
   import os
   import json
   import pandas as pd
   import mysql.connector
   from sqlalchemy import create_engine
   ```
   - **Purpose:** Import libraries needed for file handling (`os`), JSON processing (`json`), data manipulation (`pandas`), and database interaction (`mysql.connector` and `sqlalchemy`).

2. **Define MySQL Connection Details:**
   ```python
   # MySQL connection details
   host = 'localhost'
   user = 'root'
   password = '1611'
   database = 'PhonePePulse_DVandExp'
   ```
   - **Purpose:** Define the necessary details to connect to the MySQL database.

3. **Create a Connection to MySQL:**
   ```python
   # Create a connection to MySQL
   conn = mysql.connector.connect(
       host=host,
       user=user,
       password=password,
       database=database
   )
   ```
   - **Purpose:** Establish a connection to the MySQL database using the defined connection details.

4. **Create SQLAlchemy Engine:**
   ```python
   engine = create_engine(f"mysql+mysqlconnector://{user}:{password}@{host}/{database}")
   ```
   - **Purpose:** Create an SQLAlchemy engine to interact with the MySQL database, facilitating read/write operations.

5. **Define Path to JSON Files and Dictionary to Store Data:**
   ```python
   # Define the path to the directory containing JSON files
   path = "C:\\Users\\HP\\GUVI PROJ\\pulse\\data\\aggregated\\user\\country\\india\\state\\"

   # Dictionary to store extracted data
   clm_user = {'State': [], 'Year': [], 'Quarter': [], 'Brand_Name': [], 'Num_of_Reg_Users': [], 'Percent_Share': []}
   ```
   - **Purpose:** Specify the directory path containing JSON files and create a dictionary to store extracted data.

6. **Define Helper Function for State Name Conversion:**
   ```python
   # Function to convert state names for geovisualization
   def convert_state_name(input_string):
       # Replace hyphens and special characters with spaces, then capitalize each word
       formatted_string = input_string.replace('-', ' ').replace('&', '&')
       words = formatted_string.split()
       capitalized_words = [word.capitalize() for word in words]
       return ' '.join(capitalized_words)
   ```
   - **Purpose:** Define a function to format state names by replacing hyphens and capitalizing each word for better readability and consistency.

7. **Iterate Through JSON Files and Extract Data:**
   ```python
   # Iterate through each state directory
   for state in os.listdir(path):
       state_path = os.path.join(path, state)
       if os.path.isdir(state_path):
           for year in os.listdir(state_path):
               year_path = os.path.join(state_path, year)
               if os.path.isdir(year_path):
                   for quarter_file in os.listdir(year_path):
                       quarter_path = os.path.join(year_path, quarter_file)
                       if quarter_file.endswith('.json'):
                           with open(quarter_path, 'r') as file:
                               data = json.load(file)
                               if data['data'] and 'usersByDevice' in data['data'] and data['data']['usersByDevice'] is not None:
                                   for device in data['data']['usersByDevice']:
                                       clm_user['State'].append(state)
                                       clm_user['Year'].append(year)
                                       clm_user['Quarter'].append(int(quarter_file.strip('.json')))
                                       clm_user['Brand_Name'].append(device['brand'])
                                       clm_user['Num_of_Reg_Users'].append(device['count'])
                                       clm_user['Percent_Share'].append(device['percentage'])
   ```
   - **Purpose:** Traverse the directory structure, open each JSON file, extract relevant data, and populate the dictionary. The nested loops ensure all files are processed.

8. **Create DataFrame and Apply State Name Conversion:**
   ```python
   # Create DataFrame
   Agg_User = pd.DataFrame(clm_user)

   # Update the 'State' column to be suitable for geovisualization
   Agg_User['State'] = Agg_User['State'].apply(convert_state_name)
   ```
   - **Purpose:** Convert the dictionary to a Pandas DataFrame and apply the state name conversion function to the 'State' column.

9. **Store DataFrame in MySQL Table:**
   ```python
   # Store the updated DataFrame into the MySQL table
   table_name = 'agg_user'
   Agg_User.to_sql(name=table_name, con=engine, if_exists='replace', index=False)
   ```
   - **Purpose:** Store the DataFrame in a MySQL table named `agg_user`. The `if_exists='replace'` parameter ensures the table is replaced if it already exists.

10. **Close Initial MySQL Connection:**
    ```python
    # Close the initial MySQL connection
    conn.close()
    ```
    - **Purpose:** Close the initial connection to the MySQL database.

11. **Reopen Connection Using SQLAlchemy and Read Table:**
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
    - **Purpose:** Reopen the connection to the MySQL database using SQLAlchemy, read the `agg_user` table into a Pandas DataFrame, print the DataFrame, and close the connection.

### Workflow 

1. **Import Necessary Libraries:**
   ```python
   import os
   import json
   import pandas as pd
   import mysql.connector
   from sqlalchemy import create_engine
   ```
   - **Purpose:** Import libraries required for file handling (`os`), JSON processing (`json`), data manipulation (`pandas`), and database interaction (`mysql.connector` and `sqlalchemy`).

2. **Define MySQL Connection Details:**
   ```python
   # MySQL connection details
   host = 'localhost'
   user = 'root'
   password = '1611'
   database = 'PhonePePulse_DVandExp'
   ```
   - **Purpose:** Set up connection parameters to connect to the MySQL database.

3. **Create a Connection to MySQL:**
   ```python
   # Create a connection to MySQL
   conn = mysql.connector.connect(
       host=host,
       user=user,
       password=password,
       database=database
   )
   ```
   - **Purpose:** Establish a connection to the MySQL database using the specified parameters.

4. **Create SQLAlchemy Engine:**
   ```python
   engine = create_engine(f"mysql+mysqlconnector://{user}:{password}@{host}/{database}")
   ```
   - **Purpose:** Create an SQLAlchemy engine to facilitate interaction with the MySQL database for reading and writing operations.

5. **Define Path to JSON Files and Dictionary to Store Data:**
   ```python
   # Define the path to the directory containing JSON files
   path = "C:\\Users\\HP\\GUVI PROJ\\pulse\\data\\map\\transaction\\hover\\country\\india\\state\\"

   # Dictionary to store extracted data
   clm_map_ag = {'State': [], 'Year': [], 'Quarter': [], 'District': [], 'Num_of_Transactions_in_that_Yr': [], 'Total_Trans_iin_that_year': []}
   ```
   - **Purpose:** Specify the directory containing JSON files and initialize a dictionary to store the extracted data.

6. **Define Helper Function for State and District Name Conversion:**
   ```python
   # Function to convert state names for geovisualization
   def convert_state_name(input_string):
       # Replace hyphens and special characters with spaces, then capitalize each word
       formatted_string = input_string.replace('-', ' ').replace('&', '&')
       words = formatted_string.split()
       capitalized_words = [word.capitalize() for word in words]
       return ' '.join(capitalized_words)
   ```
   - **Purpose:** Define a function to format state and district names by replacing hyphens with spaces and capitalizing each word for better readability and consistency in visualizations.

7. **Iterate Through JSON Files and Extract Data:**
   ```python
   # Iterate through each state directory
   for state in os.listdir(path):
       state_path = os.path.join(path, state)
       if os.path.isdir(state_path):
           for year in os.listdir(state_path):
               year_path = os.path.join(state_path, year)
               if os.path.isdir(year_path):
                   for quarter_file in os.listdir(year_path):
                       quarter_path = os.path.join(year_path, quarter_file)
                       if quarter_file.endswith('.json'):
                           with open(quarter_path, 'r') as file:
                               data = json.load(file)
                               for item in data['data']['hoverDataList']:
                                   name = item['name']
                                   metric = item['metric'][0]
                                   count = metric['count']
                                   amount = metric['amount']
                                   clm_map_ag['State'].append(state)
                                   clm_map_ag['Year'].append(year)
                                   clm_map_ag['Quarter'].append(int(quarter_file.strip('.json')))
                                   clm_map_ag['District'].append(name)
                                   clm_map_ag['Num_of_Transactions_in_that_Yr'].append(count)
                                   clm_map_ag['Total_Trans_iin_that_year'].append(amount)
   ```
   - **Purpose:** Traverse the directory structure to open and read each JSON file, extract relevant data, and populate the dictionary. This process ensures that all JSON files are processed, and their data is aggregated.

8. **Create DataFrame and Apply Name Conversion:**
   ```python
   # Create DataFrame
   Map_Trans = pd.DataFrame(clm_map_ag)

   # Update the 'State' and 'District' columns to be suitable for geovisualization
   Map_Trans['State'] = Map_Trans['State'].apply(convert_state_name)
   Map_Trans['District'] = Map_Trans['District'].apply(convert_state_name)
   ```
   - **Purpose:** Convert the dictionary to a Pandas DataFrame and apply the name conversion function to the 'State' and 'District' columns to ensure they are formatted correctly for visualization.

9. **Store DataFrame in MySQL Table:**
   ```python
   # Store the updated DataFrame into the MySQL table
   table_name = 'map_trans'
   Map_Trans.to_sql(name=table_name, con=engine, if_exists='replace', index=False)
   ```
   - **Purpose:** Save the DataFrame to a MySQL table named `map_trans`. The `if_exists='replace'` parameter replaces the table if it already exists, ensuring the table is updated with the latest data.

10. **Close Initial MySQL Connection:**
    ```python
    # Close the initial MySQL connection
    conn.close()
    ```
    - **Purpose:** Close the initial MySQL connection established at the start.

11. **Reopen Connection Using SQLAlchemy and Read Table:**
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
    - **Purpose:** Reopen the connection to the MySQL database using SQLAlchemy, read the `map_trans` table into a DataFrame, print the DataFrame to verify the data, and close the connection.

### Workflow 
1. **Import Necessary Libraries:**
   ```python
   import os
   import json
   import pandas as pd
   import mysql.connector
   from sqlalchemy import create_engine
   ```
   - **Purpose:** Import libraries needed for handling files (`os`), processing JSON data (`json`), manipulating data (`pandas`), and interacting with MySQL (`mysql.connector` and `sqlalchemy`).

2. **Define MySQL Connection Details:**
   ```python
   # MySQL connection details
   host = 'localhost'
   user = 'root'
   password = '1611'
   database = 'PhonePePulse_DVandExp'
   ```
   - **Purpose:** Set up parameters for connecting to the MySQL database.

3. **Create MySQL Connection:**
   ```python
   # Create a connection to MySQL
   conn = mysql.connector.connect(
       host=host,
       user=user,
       password=password,
       database=database
   )
   ```
   - **Purpose:** Establish a connection to the MySQL database using the specified credentials.

4. **Create SQLAlchemy Engine:**
   ```python
   engine = create_engine(f"mysql+mysqlconnector://{user}:{password}@{host}/{database}")
   ```
   - **Purpose:** Set up an SQLAlchemy engine to facilitate interaction with the MySQL database for reading and writing operations.

5. **Define Helper Function for State and District Name Conversion:**
   ```python
   def convert_state_name(input_string):
       # Replace hyphens and special characters with spaces, then capitalize each word
       formatted_string = input_string.replace('-', ' ').replace('&', '&')
       words = formatted_string.split()
       capitalized_words = [word.capitalize() for word in words]
       return ' '.join(capitalized_words)
   ```
   - **Purpose:** Define a function to format state and district names by replacing hyphens with spaces and capitalizing each word. This ensures consistency and readability in visualizations.

6. **Define Path and Extract Data from JSON Files:**
   ```python
   path = "C:\\Users\\HP\\GUVI PROJ\\pulse\\data\\map\\user\\hover\\country\\india\\state\\"
   clm_map_user = {'State': [], 'Dist_Name': [], 'Year': [], 'Quarter': [], 'Num_of_reg_users': [], 'Num_of_app_opens': []}
   
   for state in os.listdir(path):
       state_path = os.path.join(path, state)
       if os.path.isdir(state_path):
           for year in os.listdir(state_path):
               year_path = os.path.join(state_path, year)
               if os.path.isdir(year_path):
                   for quarter_file in os.listdir(year_path):
                       quarter_path = os.path.join(year_path, quarter_file)
                       if quarter_file.endswith('.json'):
                           with open(quarter_path, 'r') as file:
                               data = json.load(file)
                               hover_data = data['data']['hoverData']
                               for district, metrics in hover_data.items():
                                   reg_users = metrics['registeredUsers']
                                   app_opens = metrics['appOpens']
                                   dt_name = district
                                   clm_map_user['State'].append(state)
                                   clm_map_user['Year'].append(year)
                                   clm_map_user['Dist_Name'].append(dt_name)
                                   clm_map_user['Quarter'].append(int(quarter_file.strip('.json')))
                                   clm_map_user['Num_of_reg_users'].append(reg_users)
                                   clm_map_user['Num_of_app_opens'].append(app_opens)
   ```
   - **Purpose:** Traverse the directory structure to open and read each JSON file, extract relevant data, and populate the dictionary `clm_map_user`. This process ensures all JSON files are processed and data is collected.

7. **Create DataFrame and Apply Name Conversion:**
   ```python
   # Create DataFrame
   Map_User = pd.DataFrame(clm_map_user)

   # Update the 'State' and 'Dist_Name' columns to be suitable for geovisualization
   Map_User['State'] = Map_User['State'].apply(convert_state_name)
   Map_User['Dist_Name'] = Map_User['Dist_Name'].apply(convert_state_name)
   ```
   - **Purpose:** Convert the dictionary to a Pandas DataFrame. Apply the name conversion function to the 'State' and 'Dist_Name' columns to ensure consistent formatting for visualization.

8. **Store DataFrame in MySQL Table:**
   ```python
   # Store the updated DataFrame into the MySQL table
   table_name = 'map_user'
   Map_User.to_sql(name=table_name, con=engine, if_exists='replace', index=False)
   ```
   - **Purpose:** Save the DataFrame to a MySQL table named `map_user`. The `if_exists='replace'` parameter ensures the table is replaced if it already exists, keeping the data updated.

9. **Close Initial MySQL Connection:**
   ```python
   # Close the initial MySQL connection
   conn.close()
   ```
   - **Purpose:** Close the initial MySQL connection that was established at the beginning.

10. **Reopen Connection Using SQLAlchemy and Read Table:**
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
    - **Purpose:** Reopen the connection using SQLAlchemy to read the `map_user` table into a DataFrame. Print the DataFrame to verify that the data was correctly stored and then close the connection.

### WORKFLOW

### 1. **Import Required Libraries**
```python
import os
import json
import pandas as pd
import mysql.connector
from sqlalchemy import create_engine
```
- **Purpose:** Import the necessary libraries for file handling, JSON parsing, data manipulation, and database interactions.

### 2. **Define MySQL Connection Details**
```python
host = 'localhost'
user = 'root'
password = '1611'
database = 'PhonePePulse_DVandExp'
```
- **Purpose:** Set the parameters for connecting to the MySQL database, including host, user, password, and database name.

### 3. **Create a Connection to MySQL**
```python
conn = mysql.connector.connect(
    host=host,
    user=user,
    password=password,
    database=database
)
```
- **Purpose:** Establish a connection to the MySQL database using the provided credentials.

### 4. **Create SQLAlchemy Engine**
```python
engine = create_engine(f"mysql+mysqlconnector://{user}:{password}@{host}/{database}")
```
- **Purpose:** Create an SQLAlchemy engine to facilitate reading and writing data to the MySQL database.

### 5. **Define Helper Function for Name Conversion**
```python
def convert_state_name(input_string):
    # Replace hyphens and special characters with spaces, then capitalize each word
    formatted_string = input_string.replace('-', ' ').replace('&', '&')
    words = formatted_string.split()
    capitalized_words = [word.capitalize() for word in words]
    return ' '.join(capitalized_words)
```
- **Purpose:** Define a function to format state and district names by replacing hyphens with spaces and capitalizing each word. This helps ensure names are formatted consistently for visualization.

### 6. **Define Path and Extract Data from JSON Files**
```python
path = "C:\\Users\\HP\\GUVI PROJ\\pulse\\data\\top\\transaction\\country\\india\\state\\"
clm_top_trans_state = {'State': [], 'Year': [], 'Quarter': [], 'District': [], 'Tot_No_of_Trans': [], 'Tot_Val_of_Trans': []}

for state in os.listdir(path):
    state_path = os.path.join(path, state)
    if os.path.isdir(state_path):
        for year in os.listdir(state_path):
            year_path = os.path.join(state_path, year)
            if os.path.isdir(year_path):
                for quarter_file in os.listdir(year_path):
                    quarter_path = os.path.join(year_path, quarter_file)
                    if quarter_file.endswith('.json'):
                        with open(quarter_path, 'r') as file:
                            data = json.load(file)
                            
                            # Check if 'data' key exists
                            if 'data' in data:
                                districts_data = data['data'].get('districts', [])
                                
                                for district_data in districts_data:
                                    entity_name = state
                                    district_name = district_data['entityName']
                                    metric = district_data['metric']
                                    count = metric['count']
                                    amount = metric['amount']
                                    clm_top_trans_state['State'].append(entity_name)
                                    clm_top_trans_state['Year'].append(year)
                                    clm_top_trans_state['Quarter'].append(int(quarter_file.strip('.json')))
                                    clm_top_trans_state['District'].append(district_name)
                                    clm_top_trans_state['Tot_No_of_Trans'].append(count)
                                    clm_top_trans_state['Tot_Val_of_Trans'].append(amount)
```
- **Purpose:** Traverse the directory structure to locate and process JSON files. For each file, extract transaction data and append it to the `clm_top_trans_state` dictionary. This gathers data on total transactions and their values by state, year, quarter, and district.

### 7. **Create DataFrame and Apply Name Conversion**
```python
# Create DataFrame
Top_Trans_State = pd.DataFrame(clm_top_trans_state)

# Update the 'State' column to be suitable for geovisualization
Top_Trans_State['State'] = Top_Trans_State['State'].apply(convert_state_name)
Top_Trans_State['District'] = Top_Trans_State['District'].apply(convert_state_name)
```
- **Purpose:** Convert the `clm_top_trans_state` dictionary to a Pandas DataFrame. Apply the `convert_state_name` function to format the 'State' and 'District' columns for consistent naming.

### 8. **Store DataFrame in MySQL Table**
```python
table_name = 'top_trans_state'
Top_Trans_State.to_sql(name=table_name, con=engine, if_exists='replace', index=False)
```
- **Purpose:** Store the DataFrame in a MySQL table named `top_trans_state`. The `if_exists='replace'` parameter ensures that the table is replaced if it already exists, allowing for fresh data insertion.

### 9. **Close Initial MySQL Connection**
```python
conn.close()
```
- **Purpose:** Close the initial MySQL connection that was used to set up the SQLAlchemy engine.

### 10. **Reopen Connection Using SQLAlchemy and Read Table**
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
- **Purpose:** Reopen the connection using SQLAlchemy to read the `top_trans_state` table into a DataFrame. Print the DataFrame to verify that the data has been correctly stored. Finally, close the connection.

### WORKFLOW
### 1. **Import Required Libraries**
```python
import os
import json
import pandas as pd
import mysql.connector
from sqlalchemy import create_engine
```
- **Purpose:** Import libraries necessary for file operations, JSON parsing, data manipulation, and database connections.

### 2. **Define MySQL Connection Details**
```python
host = 'localhost'
user = 'root'
password = '1611'
database = 'PhonePePulse_DVandExp'
```
- **Purpose:** Specify the credentials and database information required to connect to the MySQL server.

### 3. **Create a Connection to MySQL**
```python
conn = mysql.connector.connect(
    host=host,
    user=user,
    password=password,
    database=database
)
```
- **Purpose:** Establish a connection to the MySQL database using the provided credentials.

### 4. **Create SQLAlchemy Engine**
```python
engine = create_engine(f"mysql+mysqlconnector://{user}:{password}@{host}/{database}")
```
- **Purpose:** Create an SQLAlchemy engine to handle database operations such as reading from and writing to MySQL tables.

### 5. **Define Helper Function for Name Conversion**
```python
def convert_state_name(input_string):
    # Replace hyphens and special characters with spaces, then capitalize each word
    formatted_string = input_string.replace('-', ' ').replace('&', '&')
    words = formatted_string.split()
    capitalized_words = [word.capitalize() for word in words]
    return ' '.join(capitalized_words)
```
- **Purpose:** Define a function to format state and district names by replacing hyphens with spaces and capitalizing each word. This ensures names are properly formatted for geovisualization.

### 6. **Define Path and Extract Data from JSON Files**
```python
path = "C:\\Users\\HP\\GUVI PROJ\\pulse\\data\\top\\transaction\\country\\india\\state\\"
clm_top_trans_dist = {'District_Name': [], 'Year': [], 'Quarter': [], 'Tot_No_of_DTrans': [], 'Tot_Val_of_DTrans': []}

for state in os.listdir(path):
    state_path = os.path.join(path, state)
    if os.path.isdir(state_path):
        for year in os.listdir(state_path):
            year_path = os.path.join(state_path, year)
            if os.path.isdir(year_path):
                for quarter_file in os.listdir(year_path):
                    quarter_path = os.path.join(year_path, quarter_file)
                    if quarter_file.endswith('.json'):
                        with open(quarter_path, 'r') as file:
                            data = json.load(file)
                            
                            # Check if 'data' key exists
                            if 'data' in data:
                                districts = data['data']['districts']
                                
                                for district in districts:
                                    entity_name = district['entityName']
                                    metric = district['metric']
                                    count = metric['count']
                                    amount = metric['amount']
                                    clm_top_trans_dist['Year'].append(year)
                                    clm_top_trans_dist['Quarter'].append(int(quarter_file.strip('.json')))
                                    clm_top_trans_dist['District_Name'].append(entity_name)
                                    clm_top_trans_dist['Tot_No_of_DTrans'].append(count)
                                    clm_top_trans_dist['Tot_Val_of_DTrans'].append(amount)
```
- **Purpose:** Traverse the directory structure to locate and process JSON files. For each file, extract data about districts, including transaction counts and amounts, and append this information to the `clm_top_trans_dist` dictionary.

### 7. **Create DataFrame and Apply Name Conversion**
```python
# Create DataFrame
Top_Trans_Dist = pd.DataFrame(clm_top_trans_dist)

# Update the 'District_Name' column to be suitable for geovisualization
Top_Trans_Dist['District_Name'] = Top_Trans_Dist['District_Name'].apply(convert_state_name)
```
- **Purpose:** Convert the `clm_top_trans_dist` dictionary into a Pandas DataFrame. Apply the `convert_state_name` function to format the 'District_Name' column for consistent naming.

### 8. **Store DataFrame in MySQL Table**
```python
table_name = 'top_trans_dist'
Top_Trans_Dist.to_sql(name=table_name, con=engine, if_exists='replace', index=False)
```
- **Purpose:** Save the DataFrame to a MySQL table named `top_trans_dist`. The `if_exists='replace'` parameter ensures that the table is replaced if it already exists, allowing for fresh data insertion.

### 9. **Close Initial MySQL Connection**
```python
conn.close()
```
- **Purpose:** Close the initial MySQL connection that was used to set up the SQLAlchemy engine.

### 10. **Reopen Connection Using SQLAlchemy and Read Table**
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
- **Purpose:** Reopen the connection using SQLAlchemy to read the `top_trans_dist` table into a DataFrame. Print the DataFrame to verify that the data has been correctly stored. Finally, close the connection.

### WORKFLOW

### 1. **Import Required Libraries**
```python
import os
import json
import pandas as pd
import mysql.connector
from sqlalchemy import create_engine
```
- **Purpose:** Import libraries necessary for file operations, JSON parsing, data manipulation, and database interactions.

### 2. **Define MySQL Connection Details**
```python
host = 'localhost'
user = 'root'
password = '1611'
database = 'PhonePePulse_DVandExp'
```
- **Purpose:** Specify the credentials and database information required to connect to the MySQL server.

### 3. **Create a Connection to MySQL**
```python
conn = mysql.connector.connect(
    host=host,
    user=user,
    password=password,
    database=database
)
```
- **Purpose:** Establish a connection to the MySQL database using the provided credentials.

### 4. **Create SQLAlchemy Engine**
```python
engine = create_engine(f"mysql+mysqlconnector://{user}:{password}@{host}/{database}")
```
- **Purpose:** Create an SQLAlchemy engine for handling database operations like reading from and writing to MySQL tables.

### 5. **Define Helper Function for Name Conversion**
```python
def convert_state_name(input_string):
    # Replace hyphens and special characters with spaces, then capitalize each word
    formatted_string = input_string.replace('-', ' ').replace('&', '&')
    words = formatted_string.split()
    capitalized_words = [word.capitalize() for word in words]
    return ' '.join(capitalized_words)
```
- **Purpose:** Define a function to format state names by replacing hyphens with spaces and capitalizing each word. This is done to ensure names are properly formatted for geovisualization.

### 6. **Define Path and Extract Data from JSON Files**
```python
path = "C:\\Users\\HP\\GUVI PROJ\\pulse\\data\\top\\transaction\\country\\india\\state\\"
clm_top_trans_pin = {'Pincode': [], 'State': [], 'Year': [], 'Quarter': [], 'Tot_No_of_PTrans': [], 'Tot_Val_of_PTrans': []}

for state in os.listdir(path):
    state_path = os.path.join(path, state)
    if os.path.isdir(state_path):
        for year in os.listdir(state_path):
            year_path = os.path.join(state_path, year)
            if os.path.isdir(year_path):
                for quarter_file in os.listdir(year_path):
                    quarter_path = os.path.join(year_path, quarter_file)
                    if quarter_file.endswith('.json'):
                        with open(quarter_path, 'r') as file:
                            data = json.load(file)
                            
                            # Check if 'data' key exists
                            if 'data' in data and 'pincodes' in data['data']:
                                pincodes = data['data']['pincodes']

                            for pincode in pincodes:
                                entity_name = pincode['entityName']
                                metric = pincode['metric']
                                count = metric['count']
                                amount = metric['amount']
                                clm_top_trans_pin['Year'].append(year)
                                clm_top_trans_pin['Quarter'].append(int(quarter_file.strip('.json')))
                                clm_top_trans_pin['Pincode'].append(entity_name)
                                clm_top_trans_pin['Tot_No_of_PTrans'].append(count)
                                clm_top_trans_pin['Tot_Val_of_PTrans'].append(amount)
                                clm_top_trans_pin['State'].append(state)
```
- **Purpose:** Traverse the directory structure to locate and process JSON files. For each file, extract data about pincodes, including transaction counts and amounts, and append this information to the `clm_top_trans_pin` dictionary.

### 7. **Create DataFrame and Apply Name Conversion**
```python
# Create DataFrame
Top_Trans_Pin = pd.DataFrame(clm_top_trans_pin)

# Update the 'State' column to be suitable for geovisualization
Top_Trans_Pin['State'] = Top_Trans_Pin['State'].apply(convert_state_name)
```
- **Purpose:** Convert the `clm_top_trans_pin` dictionary into a Pandas DataFrame. Apply the `convert_state_name` function to format the 'State' column for consistent naming.

### 8. **Store DataFrame in MySQL Table**
```python
table_name = 'top_trans_pin'
Top_Trans_Pin.to_sql(name=table_name, con=engine, if_exists='replace', index=False)
```
- **Purpose:** Save the DataFrame to a MySQL table named `top_trans_pin`. The `if_exists='replace'` parameter ensures that the table is replaced if it already exists, allowing for fresh data insertion.

### 9. **Close Initial MySQL Connection**
```python
conn.close()
```
- **Purpose:** Close the initial MySQL connection that was used to set up the SQLAlchemy engine.

### 10. **Reopen Connection Using SQLAlchemy and Read Table**
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
- **Purpose:** Reopen the connection using SQLAlchemy to read the `top_trans_pin` table into a DataFrame. Print the DataFrame to verify that the data has been correctly stored. Finally, close the connection.

### WORKFLOW

### 1. **Import Required Libraries**
```python
import os
import json
import pandas as pd
import mysql.connector
from sqlalchemy import create_engine
```
- **Purpose:** Load the libraries necessary for file operations, JSON parsing, data manipulation, and database interactions.

### 2. **Define MySQL Connection Details**
```python
host = 'localhost'
user = 'root'
password = '1611'
database = 'PhonePePulse_DVandExp'
```
- **Purpose:** Specify the credentials and database information needed to connect to the MySQL server.

### 3. **Create a Connection to MySQL**
```python
conn = mysql.connector.connect(
    host=host,
    user=user,
    password=password,
    database=database
)
```
- **Purpose:** Establish a connection to the MySQL database using the provided credentials.

### 4. **Create SQLAlchemy Engine**
```python
engine = create_engine(f"mysql+mysqlconnector://{user}:{password}@{host}/{database}")
```
- **Purpose:** Create an SQLAlchemy engine for handling database operations, such as reading from and writing to MySQL tables.

### 5. **Define Helper Function for Name Conversion**
```python
def convert_state_name(input_string):
    # Replace hyphens and special characters with spaces, then capitalize each word
    formatted_string = input_string.replace('-', ' ').replace('&', '&')
    words = formatted_string.split()
    capitalized_words = [word.capitalize() for word in words]
    return ' '.join(capitalized_words)
```
- **Purpose:** Define a function to format state names by replacing hyphens with spaces and capitalizing each word. This ensures that names are properly formatted for geovisualization.

### 6. **Define Path and Extract Data from JSON Files**
```python
path = "C:\\Users\\HP\\GUVI PROJ\\pulse\\data\\top\\user\\country\\india\\state"
clm_top_user_dis = {'District_Name': [], 'State': [], 'Year': [], 'Quarter': [], 'Reg_Users': []}

for state in os.listdir(path):
    state_path = os.path.join(path, state)
    if os.path.isdir(state_path):
        for year in os.listdir(state_path):
            year_path = os.path.join(state_path, year)
            if os.path.isdir(year_path):
                for quarter_file in os.listdir(year_path):
                    quarter_path = os.path.join(year_path, quarter_file)
                    if quarter_file.endswith('.json'):
                        with open(quarter_path, 'r') as file:
                            data = json.load(file)

                            if 'data' in data and 'districts' in data['data']:
                                districts = data['data']['districts']

                            for dis in districts:
                                name = dis['name']
                                reg_users = dis['registeredUsers']
                                clm_top_user_dis['Year'].append(year)
                                clm_top_user_dis['Quarter'].append(int(quarter_file.strip('.json')))
                                clm_top_user_dis['District_Name'].append(name)
                                clm_top_user_dis['State'].append(state)
                                clm_top_user_dis['Reg_Users'].append(reg_users)
```
- **Purpose:** Traverse the directory structure to find and process JSON files. For each file, extract data about districts, including the number of registered users, and append this data to the `clm_top_user_dis` dictionary.

### 7. **Create DataFrame and Apply Name Conversion**
```python
# Create DataFrame
Top_User_dis = pd.DataFrame(clm_top_user_dis)

# Update the 'State' column to be suitable for geovisualization
Top_User_dis['State'] = Top_User_dis['State'].apply(convert_state_name)
Top_User_dis['District_Name'] = Top_User_dis['District_Name'].apply(convert_state_name)
```
- **Purpose:** Convert the `clm_top_user_dis` dictionary into a Pandas DataFrame. Apply the `convert_state_name` function to format the 'State' and 'District_Name' columns for consistent naming.

### 8. **Store DataFrame in MySQL Table**
```python
table_name = 'top_user_dis'
Top_User_dis.to_sql(name=table_name, con=engine, if_exists='replace', index=False)
```
- **Purpose:** Save the DataFrame to a MySQL table named `top_user_dis`. The `if_exists='replace'` parameter ensures that the table is replaced if it already exists, allowing for fresh data insertion.

### 9. **Close Initial MySQL Connection**
```python
conn.close()
```
- **Purpose:** Close the initial MySQL connection that was used to set up the SQLAlchemy engine.

### 10. **Reopen Connection Using SQLAlchemy and Read Table**
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
- **Purpose:** Reopen the connection using SQLAlchemy to read the `top_user_dis` table into a DataFrame. Print the DataFrame to verify that the data has been correctly stored. Finally, close the connection.

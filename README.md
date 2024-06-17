# Project_TWO
The code creates a Streamlit app to visualize PhonePe Pulse data with Plotly, connecting to a MySQL database to fetch insights like"Number Of Registered_Users for the selected time period", 
    "User Growth in the given time period",  
    "Brand Market Share", 
    "Yearly Growth by Brand",
    "The First six states which had highest values of transaction amount", 
    "The First five states which had least values of transaction amount", 
    "Growth of Registerd_Users for each State over the time period", 
    "The First six states which had highest number of total transactions",
    "The First six states which had least number of total transactions",
    "The highest transaction type count in each state".
    It includes choropleth maps overlaid on a GeoJSON map of India for geographical insights, providing an interactive data display.

#SecondApp.py
1. Importing Libraries:

    - **pandas**: A library for data manipulation and analysis.
    - **sqlalchemy**: A SQL toolkit and Object-Relational Mapping (ORM) library for Python.
    - **streamlit**: An open-source app framework for Machine Learning and Data Science projects.
    - **plotly.express**: A library for creating interactive plots and visualizations.
    - **requests**: A library for making HTTP requests in Python.

2. MySQL Connection Details:
   
    This section sets up the connection details for a MySQL database.

3. Function to Fetch Available Years:
  
    This function retrieves the distinct years from the `agg_user` table in the MySQL database.

4. Function to Fetch Available Quarters:
    
    This function fetches the distinct quarters for a given year from the `agg_user` table.

5. Function to Fetch Transaction Data:
  
    This function retrieves transaction data based on the selected year and quarter from the `agg_transaction` table.

6. Function to Fetch User Data:
  
    This function fetches user data based on the selected year and quarter from the `agg_user` table.

7. Streamlit Application:
   
    Sets the title of the Streamlit application.

8. Dropdown to Select the Insight:
  
    This creates a dropdown menu in the Streamlit app to select the insight for data visualization.

9. Fetch Data and Display the Selected Insight:
    -Number Of Registered Users for the selected time period:
        - Retrieves and displays the number of registered users for the selected time period.
    - User Growth in the given time period:
        - generates a bar chart displaying the total number of registered users by state, allowing users to filter the data by year and 
          quarter for a detailed view of user growth trends.
    - Brand Market Share:
        - Displays the brand market share and a pie chart for the average market share for the selected brand.
    - Growth of Registered Users for each State over the time period:
        - Creates a line chart showing the yearly growth in the number of users for the selected state.
    - The First six states which had highest values of transaction amount:
        - Generates a choropleth map displaying the top states by transaction value.
    - The First five states which had least values of transaction amount:
        - Generates a choropleth map displaying the bottom states by transaction value.
    - The First six states which had highest number of total transactions
        - Generates a choropleth map displaying the top states by number of transactions.
    - The First six states which had least number of total transactions:
        - Generates a choropleth map displaying the bottom states by number of transactions.
    - The highest transaction type count in each state:
        - Generates a choropleth map showing the highest transaction type count for each state.
   

#SecallTables.ipynb
This file contains the code for the creation of a database and creation of tables into the database and insert data into those tables.

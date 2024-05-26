# Project_TWO
The code creates a Streamlit app to visualize PhonePe Pulse data with Plotly, connecting to a MySQL database to fetch insights like user growth, popular districts, app opens, brand market share, and transactions. It includes choropleth maps overlaid on a GeoJSON map of India for geographical insights, providing an interactive data display.

#SecondApp.py
The code present in the SecondApp.py sets up a Streamlit application for visualizing PhonePe Pulse data using Plotly. The application connects to a MySQL database to fetch various insights, such as user growth, popular districts, app opens, brand market share, and transaction statistics.
The steps involved are:
1.MySQL Connection:
The code connects to a MySQL database using SQLAlchemy. The connection details, including the host, user, password, and database name, are specified.
2.GeoJSON File:
A GeoJSON file for India's states is loaded, which will be used for geographical visualizations.
3.Streamlit Application:
The application is titled "PhonePe Pulse Data Visualization."
A dropdown menu allows users to select different insights to visualize.
4.Data Fetching and Visualization:
For each selected insight, an appropriate SQL query is executed to fetch the relevant data from the database.
The fetched data is then visualized using Plotly:
User Growth Over Time: Displays user growth over time using a line chart.
Most Popular Districts: Shows the top 10 districts by the number of registered users using a bar chart.
App Opens: Visualizes the number of app opens over time with a line chart.
Brand Market Share: Shows market share by brand over time using a bar chart.
Top Brands: Displays the top brands by the number of registered users using a bar chart.
Brand Correlation: Visualizes the correlation between registered users, transaction counts, and transaction amounts by brand using a scatter plot.
Regional Popularity by Brand: Shows the popularity of different brands across various states using a bar chart and a choropleth map.
Yearly Growth by Brand: Displays yearly user growth by brand using a line chart.
5.Geovisualization:
For insights related to geographical data, a choropleth map is added to visualize the data spatially across India's states. This is demonstrated in the "Regional Popularity by Brand" insight.

#SecallTables.ipynb
This file contains the code for the creation of a database and creation of tables into the database and insert data into those tables.

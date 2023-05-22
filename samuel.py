import sqlite3
import pandas as pd
import folium
import seaborn as sns
from folium.plugins import HeatMap
import matplotlib.pyplot as plt

# Connect to the SQLite database
conn = sqlite3.connect('googleplacesdb.db')

# Create a cursor object
cur = conn.cursor()

# Execute a SQL query to select all fields from your table
cur.execute("SELECT * FROM places")

# Fetch all results from the executed SQL query
data = cur.fetchall()

# Load the data into a pandas DataFrame
df = pd.DataFrame(data, columns=['name', 'api_keyword', 'business_status', 'place_id', 'lat', 'lng', 'rating', 'user_ratings_total', 'types', 'vicinity', 'price_level'])

# Convert 'lat', 'lng', 'rating' and 'price_level' to numeric
df['lat'] = pd.to_numeric(df['lat'], errors='coerce')
df['lng'] = pd.to_numeric(df['lng'], errors='coerce')
df['rating'] = pd.to_numeric(df['rating'], errors='coerce')
df['price_level'] = pd.to_numeric(df['price_level'], errors='coerce')

# Create a map centered around the average coordinates
m = folium.Map(location=[df['lat'].mean(), df['lng'].mean()], zoom_start=10, control_scale=True)

# Drop any rows with missing 'lat' or 'lng' data
df = df.dropna(subset=['lat', 'lng'])

# Create a list of coordinates
heat_data = [[row['lat'], row['lng']] for index, row in df.iterrows()]

# Add the heatmap to the map
HeatMap(heat_data).add_to(m)

# Save the map to an HTML file
m.save('heatmap.html')

# Handle NaN values in 'price_level' and 'rating' column
df['price_level'] = df['price_level'].fillna(0)
df['rating'] = df['rating'].fillna(0)

# Check for correlation between 'rating' and 'price_level'
correlation = df['rating'].corr(df['price_level'])
print(f'Correlation between user rating and price: {correlation}')

# Create a scatter plot of 'rating' and 'price_level'
sns.scatterplot(x='price_level', y='rating', data=df)
plt.show()

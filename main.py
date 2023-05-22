import pandas as pd
import numpy as np
import requests
import json
import time
import sqlite3
import folium
import numpy

final_data = []

coordinates = ['48.8588897, 2.320041']
keywords = ['restaurant', 'bar', 'hotel']
radius = '2500'
api_key = 'removedAPIkey'  # ask ali if you really need it

count = 0

# Generate grid coordinates
def generate_grid_coordinates(lat, lng, size, step):
    latitudes = np.arange(lat - size / 2, lat + size / 2, step)
    longitudes = np.arange(lng - size / 2, lng + size / 2, step)
    return [(lat, lng) for lat in latitudes for lng in longitudes]

# Connect to the database
connection = sqlite3.connect("googleplacesdb.db")
print(connection.total_changes)
cursor = connection.cursor()

center_lat = 48.8588897
center_lng = 2.320041
grid_size = 0.1  # in degrees
step_size = 0.025  # in degrees
coordinates = generate_grid_coordinates(center_lat, center_lng, grid_size, step_size)

for coordinate in coordinates:
    lat, lng = coordinate
    for keyword in keywords:
        url = f'https://maps.googleapis.com/maps/api/place/nearbysearch/json?location={lat},{lng}&radius={radius}&keyword={keyword}&key={api_key}'
        while True:
            # Replaced the print(url) line
            print(f"Requesting {keyword} at {lat}, {lng} amount parsed: {count}")
            respon = requests.get(url)
            jj = json.loads(respon.text)
            results = jj['results']
            for result in results:
                name = result['name']
                place_id = result['place_id']
                lat = result['geometry']['location']['lat']
                lng = result['geometry']['location']['lng']
                rating = result['rating']
                user_ratings_total = result['user_ratings_total']
                types = result['types']
                vicinity = result['vicinity']
                business_status = result['business_status']

                price_level = ''
                if 'price_level' in result:
                    price_level = result['price_level']

                data = [name, keyword, business_status, place_id, lat, lng,
                        rating, user_ratings_total, types, vicinity, price_level]
                final_data.append(data)
                count = count + 1

                cursor.execute("INSERT INTO places VALUES (?,?,?,?,?,?,?,?,?,?,?)",
                               (data[0],
                                data[1],
                                data[2],
                                data[3],
                                data[4],
                                data[5],
                                data[6],
                                data[7],
                                ''.join(data[8]),
                                data[9],
                                data[10]))

            time.sleep(1)

            if 'next_page_token' not in jj:
                break
            else:
                next_page_token = jj['next_page_token']
                url = f'https://maps.googleapis.com/maps/api/place/nearbysearch/json?key={api_key}&pagetoken={next_page_token}'

labels = ['name', 'api_keyword', 'business_status', 'place_id', 'lat',
          'lng', 'rating', 'user_ratings_total', 'types', 'vicinity', 'price_level']
export_dataframe_1_medium = pd.DataFrame.from_records(
    final_data, columns=labels)
export_dataframe_1_medium.to_csv('export_places.csv')

# Calculate correlation coefficient between rating and user_ratings_total
rating_data = export_dataframe_1_medium['rating']
user_ratings_data = export_dataframe_1_medium['user_ratings_total']
correlation = np.corrcoef(rating_data, user_ratings_data)[0, 1]

# Visualize data on a map
map = folium.Map(location=[center_lat, center_lng], zoom_start=12)

# Plot data points on the map
for index, row in export_dataframe_1_medium.iterrows():
    lat = row['lat']
    lng = row['lng']
    rating = row['rating']
    user_ratings_total = row['user_ratings_total']

    marker_color = 'red' if rating >= 4.0 else 'blue'  # Adjust the rating condition as per your requirement
    marker = folium.Marker([lat, lng], icon=folium.Icon(color=marker_color))
    marker.add_to(map)

# Add correlation to the map as a popup
folium.Popup(f"Correlation: {correlation:.2f}").add_to(map)

# Save and display the map
map.save('data_points_map.html')
map

print(f"Total Entries Saved: {count}")

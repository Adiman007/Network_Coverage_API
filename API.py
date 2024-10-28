from fastapi import FastAPI
import requests
import pandas as pd
from geopy.distance import geodesic

app = FastAPI()

range_4g = 1.5 # in km
range = 0.008 # in degrees

# get the closest locations to a given coordinate using the distance formula
def closest_locations_distance_formula(coord, data):
    data['distance'] = ((data['lat'] - coord[0])**2 + (data['long'] - coord[1])**2)**0.5
    closest_locations = data[data['distance'] < range]
    closest_locations = closest_locations.sort_values(by='distance', ascending=True)
    return closest_locations

# get the closest locations to a given coordinate using the Haversine formula
def closest_locations_geodesic(coord, data):
    data['distance'] = data.apply(lambda x: geodesic((x['lat'], x['long']), coord).kilometers, axis = 1)
    closest_locations = data[data['distance'] < range_4g]
    closest_locations = closest_locations.sort_values(by='distance', ascending=True)
    return closest_locations

# get the coordinates of an address using the api-adresse.data.gouv.fr API
def address_to_coordinates(q):
    response = requests.get(f'https://api-adresse.data.gouv.fr/search/?q={q}')
    if response.status_code == 200:
        data = response.json()
        if data['features']:
            coords = data['features'][0]['geometry']['coordinates']
            return coords[1], coords[0]

# import the data from a csv file (here clear_data.csv)        
def import_data(file):
    data = pd.read_csv(file, sep = ";")
    return data

#root
@app.get("/")
def read_root():
    return {"Hello": "World"} 

#uses geodesic to calculate the distance with accuracy but way slower
@app.get("/network/geodesic/{q}")
def read_test(q: str):
    coord = address_to_coordinates(q)
    data = import_data('clear_data.csv')
    locs = closest_locations_geodesic(coord, data)
    networks = {}
    for index, row in locs.iterrows():
        if row["Nom_Operateur"] not in networks:
            networks[row["Nom_Operateur"]] = {
                "2G": row['2G'] != 0,
                "3G": row['3G'] != 0,
                "4G": row['4G'] != 0
            }

    result = {
        "Networks": networks,
        "coords": {"lat": coord[0], "long": coord[1]},
        "address" : q
    }
    
    
    return result

#uses distance formula to filter out the closest locations very quickly but with less accuracy
@app.get("/network/distance/{q}")
def read_test(q: str):

    coord = address_to_coordinates(q)
    data = import_data('clear_data.csv')
    locs = closest_locations_distance_formula(coord, data)
    networks = {}
    for index, row in locs.iterrows():
        if row["Nom_Operateur"] not in networks:
            networks[row["Nom_Operateur"]] = {
                "2G": row['2G'] != 0,
                "3G": row['3G'] != 0,
                "4G": row['4G'] != 0
            }

    result = {
        "Networks": networks,
        "coords": {"lat": coord[0], "long": coord[1]},
        "address" : q
    }
    
    return result

#uses distance formula to filter out the closest locations and then geodesic to calculate the distance with accuracy
@app.get("/network/{q}")
def read_test(q: str):
    coord = address_to_coordinates(q)
    data = import_data('clear_data.csv')
    close_locs = closest_locations_distance_formula(coord, data)
    locs = closest_locations_geodesic(coord, close_locs)
    networks = {}
    for index, row in locs.iterrows():
        if row["Nom_Operateur"] not in networks:
            networks[row["Nom_Operateur"]] = {
                "2G": row['2G'] != 0,
                "3G": row['3G'] != 0,
                "4G": row['4G'] != 0
            }

    result = {
        "Networks": networks,
        "coords": {"lat": coord[0], "long": coord[1]},
        "address" : q
    }
    
    return result
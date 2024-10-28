from fastapi import FastAPI
import requests
import pandas as pd
from geopy.distance import geodesic

app = FastAPI()

def three_closest_location_distance_formula(coord, data):
    data['distance'] = ((data['lat'] - coord[0])**2 + (data['long'] - coord[1])**2)**0.5
    three_closest = data.nsmallest(3, 'distance')
    return three_closest

def three_closest_location_geodesic(coord, data):
    data['distance'] = data.apply(lambda x: geodesic((x['lat'], x['long']), coord).kilometers, axis = 1)
    three_closest = data.nsmallest(3, 'distance')
    return three_closest

def address_to_coordinates(q):
    response = requests.get(f'https://api-adresse.data.gouv.fr/search/?q={q}')
    if response.status_code == 200:
        data = response.json()
        if data['features']:
            coords = data['features'][0]['geometry']['coordinates']
            return coords[1], coords[0]
        
def import_data(file):
    data = pd.read_csv(file, sep = ";")
    return data

@app.get("/")
def read_root():
    return {"Hello": "World"} 

@app.get("/network/geodesic/{q}")
def read_test(q: str):
    coord = address_to_coordinates(q)
    data = import_data('clear_data.csv')
    locs = three_closest_location_geodesic(coord, data)

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
        "coords": {"lat": coord[0], "lon": coord[1]}
    }
    
    return result

@app.get("/network/distance/{q}")
def read_test(q: str):

    coord = address_to_coordinates(q)
    data = import_data('clear_data.csv')
    locs = three_closest_location_distance_formula(coord, data)

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
        "coords": {"lat": coord[0], "lon": coord[1]}
    }
    
    return result
import pyproj
import pandas as pd

file_name = '2018_01_Sites_mobiles_2G_3G_4G_France_metropolitaine_L93.csv'

def lamber93_to_gps(x, y):
    lambert = pyproj.Proj('+proj=lcc +lat_1=49 +lat_2=44 +lat_0=46.5 +lon_0=3 +x_0=700000 +y_0=6600000 +ellps=GRS80 +towgs84=0,0,0,0,0,0,0 +units=m +no_defs')
    wgs84 = pyproj.Proj('+proj=longlat +ellps=WGS84 +datum=WGS84 +no_defs')
    long, lat = pyproj.transform(lambert, wgs84, x, y)
    return long, lat

def import_data(file):
    data = pd.read_csv(file, sep = ";")
    return data

def add_gps_to_data(df):
    df['long'] = 0
    df['lat'] = 0
    for index, row in df.iterrows():
        if index % 1000 == 0:
            print(index)
        long,lat = lamber93_to_gps(row['x'],row['y'])
        df.at[index,'long'] = long
        df.at[index,'lat'] = lat
    return df

def clear_nan(df):
    df = df.dropna(subset=['long','lat'])
    return df

def add_operator_name(df):
    code_to_name = {'20801': 'Orange', '20810': 'SFR', '20820': 'Bouygues Telecoms', '20815': 'Free'}
    df['Nom_Operateur'] = 0
    for index, row in df.iterrows():
        if str(int(row["Operateur"])) in code_to_name.keys():
            df.at[index, 'Nom_Operateur'] = code_to_name[str(int(row["Operateur"]))]
    return df

def save_data(df):
    df.to_csv('clear_data.csv', sep = ";")
    
def main():
	df = import_data()
	df = add_gps_to_data(df)
	df = add_operator_name(df)
	df = clear_nan(df)
	save_data(df)
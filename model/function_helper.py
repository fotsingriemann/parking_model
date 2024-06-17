import math
import datetime
import os
import numpy as np
import pandas as pd

from dotenv import load_dotenv

# Charger les variables d'environnement à partir du fichier .env
load_dotenv()

# Accéder aux variables d'environnement
data_path = os.getenv('DATA_PATH')
arival_path = os.getenv('DATA_ARIVAL_PATH')

# Convertie en seconde un temps du format h:m:s
def heure_en_secondes(heure):
    # Décomposer l'heure en heures, minutes et secondes
    h, m, s = heure.hour, heure.minute, heure.second
    
    # Convertir chaque composante en secondes et calculer le total
    total_secondes = h * 3600 + m * 60 + s
    
    return total_secondes


# Calcule du rayon d'une surface connaissant son pluscode
def calculate_radius(olc_code):
    code_length = len(olc_code)
    if code_length >= 10:
        # Rayon pour un code de 10 caractères
        side_length = 3.375  # mètres
    elif code_length >= 8:
        # Rayon pour un code de 8 caractères
        side_length = 13.9  # mètres

    else:
        raise ValueError('Code OLC trop court pour déterminer une zone précise.')

    # Calculer la diagonale du carré
    diagonal = side_length * math.sqrt(2)
    # Le rayon est la moitié de la diagonale
    radius = diagonal / 2
    return radius

# Determiner les lieux frequent de parking des vehicules
def number_of_house(data_parking, immatriculation): # Data segmentation possible parts
    pluscodes = list()
    data_ = data_parking[data_parking["IMMATRICULATION"]==immatriculation]
    data_pluscode = data_["pluscode"].value_counts()
    for (pluscode, taille) in zip(data_pluscode.keys(), data_pluscode.values):
        if(taille > np.mean(data_pluscode.values)):
            pluscodes.append(pluscode)
 
    return pluscodes

# Stockage des detailles sur les lieux de parking frequent d'une voiture connaissant son immatriculation
def excel_details(data_parking, immatriculation):
    dicts = {
        "lieu" : [],
        "lat" : [],
        "lng" : [],
        "pluscode": [],
        "Rayon":[]
    }
    pluscodes = number_of_house(data_parking, immatriculation)

    for pluscode in pluscodes :
        lieux = list(data_parking["lieu"].value_counts().keys())
        dicts["pluscode"].append(pluscode)
        dicts["Rayon"].append(calculate_radius(pluscode))
        for lieu in lieux :
            dicts["lieu"].append(lieu)
            for col in ["lat", "lng"]:
#                 model = ARIMA(data_1[col], order=(2,1,1))
#                 model_fit_ = model.fit()
#                 output = model_fit_.forecast()
#                 toto = output[output.keys().start]
                dicts[col].append(data_parking[col].mean())
            
                
    df = pd.DataFrame(dicts)
    df.to_excel(f'model_save/{immatriculation}/details.xlsx', index=False, sheet_name='place_details')


# Conversion d'u temps des secondes au format heure:minute:seconde
def convert_seconds_to_hms(seconds):
    # Create a timedelta object
    delta = datetime.timedelta(seconds=seconds)
    
    # Extract hours, minutes, and seconds
    hours, remainder = divmod(delta.seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    
    # Format the result as h:m:s
    return f"{hours}:{minutes:02}:{seconds:02}"

# Conversion de seconde en minute        
def convert_seconds_to_ms(seconds):
    # Create a timedelta object
    delta = datetime.timedelta(seconds=seconds)
    
    minutes, seconds = divmod(delta.seconds, 60)
    
    # Format the result as h:m:s
    return f"{minutes:02}"


# stockage des detailles plus approfondie des lieux freqent de parking pour chaque jour (Lundi, Mardi, Mercredi, Jeudi, Vendredi, Samedi, Dimanche)
def excel_detail_each_day(data_parking, immatriculation):
    data_1 = data_parking[data_parking["IMMATRICULATION"]==immatriculation]
    data_1["jour_date_reference_parking"] = data_1["jour_date_reference_parking"].apply(lambda x : x.split(" ")[0])
    data_1["heure_de_parking"] = data_1["heure"]   
    
    jours = ["Lundi", "Mardi", "Mercredi", "Jeudi", "Vendredi", "Samedi", "Dimanche"]
    dicts = {
        "lieu" : [],
        "heure_moyenne_entre" : [],
        "heure_moyenne_sortie": [],
        "marge_heure_entre":[],
        "marge_heure_sortie":[],
        "poid_du_lieu":[]
    }
    
    pluscodes = number_of_house(data_parking, immatriculation)

    for jour in jours :
    
        mes_info = data_1[data_1["jour_date_reference_parking"] == jour]

    #         lieux = list(mes_info["lieu"].value_counts().keys())
        
        for pluscode in pluscodes :
            
            donnee = mes_info[mes_info['pluscode']==pluscode]
            if len(donnee["heure_de_parking"]) >= 5:
                dicts["lieu"].append(pluscode)
#                 model = ARIMA(donnee["heure_de_parking"], order=(2,1,1))
#                 model_fit_ = model.fit()
#                 output_hp = model_fit_.forecast()
                dicts["heure_moyenne_entre"].append(convert_seconds_to_hms(donnee["heure_de_parking"].mean()))
            
#                 model = ARIMA(donnee["heure_sortie_parking"], order=(2,1,1))
#                 model_fit_ = model.fit()
#                 output_hs = model_fit_.forecast()
                dicts["heure_moyenne_sortie"].append(convert_seconds_to_hms(donnee["heure_sortie_parking"].mean()))
                dicts["marge_heure_entre"].append(convert_seconds_to_ms(int(np.std(np.abs(donnee["heure_de_parking"] - donnee["heure_sortie_parking"].mean())))))
                dicts["marge_heure_sortie"].append(convert_seconds_to_ms(int(np.std(np.abs(donnee["heure_sortie_parking"] - donnee["heure_sortie_parking"].mean())))))
                dicts["poid_du_lieu"].append(data_1["pluscode"].value_counts()[pluscode]/len(data_1["pluscode"]) * 100)


        df = pd.DataFrame(dicts)
        if(not os.path.isdir(f"model_save/{immatriculation}/stats")):
            os.mkdir(f"model_save/{immatriculation}/stats")
        df.to_excel(f'model_save/{immatriculation}/stats/{jour}.xlsx', index=False, sheet_name='Sheet1')
        dicts = {
            "lieu" : [],
            "heure_moyenne_entre" : [],
            "heure_moyenne_sortie": [],
            "marge_heure_entre":[],
            "marge_heure_sortie":[],
            "poid_du_lieu":[]
        }

def delete_files(directory):
    for filename in os.listdir(directory):
        file_path = os.path.join(directory, filename)
        try:
            if os.path.isfile(file_path) or os.path.islink(file_path):
                os.remove(file_path)
                print(f"{filename} has been deleted successfully")
            elif os.path.isdir(filename):
                print(f"Skipping directory: {file_path}")
        except Exception as e:
            print(f"Failed to delete {file_path}. Reason: {e}")

    filename_arival = os.listdir(f'{directory}/{arival_path}')[0]
    
    os.remove(os.path.join(directory, arival_path, filename_arival))
    print(f"{filename_arival} has been deleted successfully")
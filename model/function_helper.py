import math
import datetime
import os
import numpy as np
import pandas as pd
import pmdarima as pm
from statsmodels.tsa.arima.model import ARIMA
from dotenv import load_dotenv

# Charger les variables d'environnement à partir du fichier .env
load_dotenv()

# Accéder aux variables d'environnement
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
def number_of_house(data_parking, immatriculation, commande_list): # Data segmentation possible parts
    
        pluscodes = list()
        data_ = data_parking[data_parking["IMMATRICULATION"]==immatriculation]
        data_pluscode = data_["pluscode"].value_counts()
        for (pluscode, taille) in zip(data_pluscode.keys(), data_pluscode.values):
            if(taille > np.mean(data_pluscode.values)):
                pluscodes.append(pluscode)

        for commande in commande_list :
            if(immatriculation == commande[0] ) :
                if not commande[1] in pluscodes:
                    pluscodes.append(commande[1])
 
        return pluscodes

# Stockage des detailles sur les lieux de parking frequent d'une voiture connaissant son immatriculation
def excel_details(data_parking, immatriculation, commande_liste):
    dicts = {
        "lieu" : [],
        "lat" : [],
        "lng" : [],
        "pluscode": [],
        "Rayon":[]
    }
    pluscodes = number_of_house(data_parking, immatriculation, commande_liste)

    for pluscode in pluscodes :
        data_1 = data_parking[data_parking["pluscode"] == pluscode]
        lieux = list(data_1["lieu"].value_counts().keys())
        
        for lieu in lieux :
            dicts["lieu"].append(lieu)
            dicts["pluscode"].append(pluscode)
            dicts["Rayon"].append(calculate_radius(pluscode))
            for col in ["lat", "lng"]:
                auto_arima_model = pm.auto_arima(data_1[col], seasonal=False, error_action='ignore', suppress_warnings=True)
                p, d, q = auto_arima_model.order
                model = ARIMA(data_1[col], order=(p,d,q))
                model_fit_ = model.fit()
                output = model_fit_.forecast()
                value = output[output.keys().start]
                # dicts[col].append(data_1[col].mean())
                dicts[col].append(value)

               
    df = pd.DataFrame(dicts)
    if(os.path.isfile(f'model_save/{immatriculation}/details.xlsx')):
        os.remove('model_save/{immatriculation}/details.xlsx')

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
def excel_detail_each_day(data_parking, immatriculation, commande_liste):
    data_1 = data_parking[data_parking["IMMATRICULATION"]==immatriculation] 
    
    jours = ["Lundi", "Mardi", "Mercredi", "Jeudi", "Vendredi", "Samedi", "Dimanche"]
    dicts = {
        "lieu" : [],
        "heure_moyenne_entre" : [],
        "heure_moyenne_sortie": [],
        "marge_heure_entre":[],
        "marge_heure_sortie":[],
        "poid_du_lieu":[]
    }
    
    pluscodes = number_of_house(data_parking, immatriculation, commande_liste)

    for jour in jours :
    
        mes_info = data_1[data_1["jour_date_reference_parking"] == jour]

    #         lieux = list(mes_info["lieu"].value_counts().keys())
        
        for pluscode in pluscodes :
            
            donnee = mes_info[mes_info['pluscode']==pluscode]
            if len(donnee["heure"]) >= 5:
                dicts["lieu"].append(pluscode)
                
                auto_arima_model = pm.auto_arima(donnee["heure_de_parking"], seasonal=False, error_action='ignore', suppress_warnings=True)
                p, d, q = auto_arima_model.order
                model = ARIMA(donnee["heure_de_parking"], order=(p,d,q))
                model_fit_ = model.fit()
                output = model_fit_.forecast()
                value_entree = output[output.keys().start]
                # dicts["heure_moyenne_entre"].append(convert_seconds_to_hms(donnee["heure"].mean()))
                dicts["heure_moyenne_entre"].append(convert_seconds_to_hms(value_entree))

                auto_arima_model = pm.auto_arima(donnee["heure_sortie_parking"], seasonal=False, error_action='ignore', suppress_warnings=True)
                p, d, q = auto_arima_model.order
                model = ARIMA(donnee["heure_sortie_parking"], order=(p,d,q))
                model_fit_ = model.fit()
                output = model_fit_.forecast()
                value_sortie = output[output.keys().start]

                # dicts["heure_moyenne_sortie"].append(convert_seconds_to_hms(donnee["heure_sortie_parking"].mean()))
                dicts["heure_moyenne_sortie"].append(convert_seconds_to_hms(value_sortie))

                dicts["marge_heure_entre"].append(convert_seconds_to_ms(int(np.std(np.abs(donnee["heure"] - value_entree)))))
                dicts["marge_heure_sortie"].append(convert_seconds_to_ms(int(np.std(np.abs(donnee["heure_sortie_parking"] - value_sortie)))))
                dicts["poid_du_lieu"].append(data_1["pluscode"].value_counts()[pluscode]/len(data_1["pluscode"]) * 100)


        df = pd.DataFrame(dicts)
        if(not os.path.isdir(f"model_save/{immatriculation}/stats")):
            os.mkdir(f"model_save/{immatriculation}/stats")
        
        if(os.path.isfile(f'model_save/{immatriculation}/stats/{jour}.xlsx')):
            os.remove(f'model_save/{immatriculation}/stats/{jour}.xlsx')

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

    filename_arival = os.listdir(arival_path)[0]
    
    os.remove(os.path.join(arival_path, filename_arival))
    print(f"{filename_arival} has been deleted successfully")


def is_file_empty(file_path):
    with open(file_path, 'r') as file:
        return file.read().strip() == ''
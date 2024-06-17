# Chargement des libraries
print("Importation des libraries et les fonction de helpers ...")
from tqdm import tqdm
import pandas as pd
# from statsmodels.tsa.arima.model import ARIMA

import os
from dotenv import load_dotenv

# Charger les variables d'environnement à partir du fichier .env
load_dotenv()

# Accéder aux variables d'environnement
data_path = os.getenv('DATA_PATH')
arival_path = os.getenv('DATA_ARIVAL_PATH')

from function_helper import delete_files, excel_detail_each_day, excel_details, heure_en_secondes


print("Verification des nouvelle sources de donnees . . . \n")

# S'il y a plus d'un fichier source dans le dossier data
if(len(os.listdir(os.path.join(data_path, arival_path))) >= 1) :
    print("Nouvelle source de donnees disponible \n")
    
    print("Chargement des donnees de reference . . . \n")

    reference_data_tracking = pd.read_excel(os.path.join(data_path ,"reference.xlsx"))

    print("Pre-traitement des donnees de references \n")

    reference_data_tracking = reference_data_tracking.drop(columns = ["alertvalue", "parking", "rayon"])
    reference_data_tracking = reference_data_tracking.dropna()
    reference_data_tracking["jour_date_reference_parking"] = reference_data_tracking["jour_date_reference_parking"].apply(lambda x : x.split(" ")[0])
    reference_data_tracking["heure"] = reference_data_tracking["heure"].apply(heure_en_secondes)
    reference_data_tracking["heure_sortie_parking"] = reference_data_tracking["date_sortie_parking"].apply(lambda x : x.time())
    reference_data_tracking["heure_sortie_parking"] = reference_data_tracking["heure_sortie_parking"].apply(heure_en_secondes)

    print("chargement des donnees arrivees . . . \n")

    donnee_ajoutee = pd.read_excel(os.path.join(data_path, arival_path,os.listdir(os.path.join(data_path, arival_path))[0]))
    
    print("Pre-traitement de la donnee arrivees \n")

    donnee_ajoutee = donnee_ajoutee.drop(columns = ["alertvalue", "parking", "rayon"])
    donnee_ajoutee = donnee_ajoutee.dropna()
    donnee_ajoutee["jour_date_reference_parking"] = donnee_ajoutee["jour_date_reference_parking"].apply(lambda x : x.split(" ")[0])
    donnee_ajoutee["heure"] = donnee_ajoutee["heure"].apply(heure_en_secondes)
    donnee_ajoutee["heure_sortie_parking"] = donnee_ajoutee["date_sortie_parking"].apply(lambda x : x.time())
    donnee_ajoutee["heure_sortie_parking"] = donnee_ajoutee["heure_sortie_parking"].apply(heure_en_secondes)

    print("fusion des source de donnees . . . \n")

    reference_data_tracking = reference_data_tracking.reset_index(drop=True)
    donnee_ajoutee = donnee_ajoutee.reset_index(drop=True)

    result = pd.concat([reference_data_tracking, donnee_ajoutee], ignore_index=False, axis=0)

    print("Suppression des source . . . \n")

    delete_files(os.path.join(data_path))

    print("Sauvegarde de la nouvelle source de reference . . . \n")

    result.to_excel(os.path.join(data_path, "reference.xlsx"))

    print("recalcule des statistiques journalier des vehicules . . . \n")

    immatriculations = set(result["IMMATRICULATION"])

    for immatriculation in tqdm(immatriculations) :
        if(not os.path.isdir(f"model_save/{immatriculation}")):
            os.mkdir(f"model_save/{immatriculation}")

        else : pass

        if(not os.path.isfile(f"model_save/{immatriculation}/details.xlsx")):
            excel_details(result, immatriculation)
            excel_detail_each_day(result, immatriculation)

        else: pass

else :
    
    print("Aucune nouvelle source de donnee Pour le moment. Les stats sont Up to date")

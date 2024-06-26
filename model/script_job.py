# Chargement des libraries
print("Importation des libraries et les fonction de helpers ... \n \n")
import datetime
from tqdm import tqdm
import pandas as pd


import os
from dotenv import load_dotenv

# Charger les variables d'environnement à partir du fichier .env
load_dotenv()

# Accéder aux variables d'environnement
data_path = os.getenv('DATA_PATH')
arival_path = os.getenv('DATA_ARIVAL_PATH')
command_path = os.getenv('COMMAND_PATH')

from function_helper import delete_files, excel_detail_each_day, excel_details, heure_en_secondes, is_file_empty

print(f"Ce script s'excute le: {datetime.datetime.now().date()} a {datetime.datetime.now().time()} \n \n")

print("Verification des nouvelle sources de donnees . . . \n \n")

# S'il y a plus d'un fichier source dans le dossier data
if(len(os.listdir(arival_path)) >= 1) :
    print("Nouvelle source de donnees disponible \n \n")
    
    print("Chargement des donnees de reference . . . \n \n")

    reference_data_tracking = pd.read_excel(os.path.join(data_path ,"reference.xlsx"))

    print("chargement des donnees arrivees . . . \n \n")

    donnee_ajoutee = pd.read_excel(os.path.join(arival_path, os.listdir(arival_path)[0]))
    
    print("Pre-traitement de la donnee arrivees \n \n")

    donnee_ajoutee = donnee_ajoutee.drop(columns = ["alertvalue", "parking", "rayon"])
    donnee_ajoutee = donnee_ajoutee.dropna()
    donnee_ajoutee["jour_date_reference_parking"] = donnee_ajoutee["jour_date_reference_parking"].apply(lambda x : x.split(" ")[0])
    donnee_ajoutee["heure"] = donnee_ajoutee["heure"].apply(heure_en_secondes)
    donnee_ajoutee["heure_sortie_parking"] = donnee_ajoutee["date_sortie_parking"].apply(lambda x : x.time())
    donnee_ajoutee["heure_sortie_parking"] = donnee_ajoutee["heure_sortie_parking"].apply(heure_en_secondes)

    print("fusion des source de donnees . . . \n \n")

    reference_data_tracking = reference_data_tracking.reset_index(drop=True)
    donnee_ajoutee = donnee_ajoutee.reset_index(drop=True)

    result = pd.concat([reference_data_tracking, donnee_ajoutee], ignore_index=False, axis=0)

    print("Suppression des source . . . \n \n")

    delete_files(data_path)

    print("Verification de l'entree des commandes  . . .\n \n")

    # if not is_file_empty(os.path.join(command_path, "add_new_location.txt")):
        
    
    
    if(not is_file_empty(os.path.join(command_path, "remove_consideration_location.txt"))) :
        file_commande_remove = open(os.path.join(command_path, "remove_consideration_location.txt"), 'r')
        for line in file_commande_remove:
                if line == '' : break
                print(f"Execution des commande utilisateur de type delete detecter . . .")
                if(not "delete" in line):
                    print("cette commande de type delete n'est pas valide")
                else:
                    chaine = line.split("delete")
                    result = result[result["IMMATRICULATION"] != chaine[0]]
                    result = result[result["pluscode"] != chaine[1]]
            
                print(f"commande du vehicule {chaine[0]} executer sous restriction de sa location {chaine[1]}")

    

    commande_add = list()
  
    if(not is_file_empty(os.path.join(command_path, "add_consideration_location.txt"))) :   
        file_commande_add = open(os.path.join(command_path, "add_consideration_location.txt"), 'r')
        for line in file_commande_add:
                if(line == '') : break
                print(f"traitement des commande utilisateur add detecter . . .")
                if(not "add" in line):
                    print("cette commande de type add n'est pas valide")
                else:
                    commande_add.append(line.split("add"))


    print("Sauvegarde de la nouvelle source de reference . . . \n \n")

    result.to_excel(os.path.join(data_path, "reference.xlsx"))

    print("recalcule des statistiques journalier des vehicules . . . \n \n")

    immatriculations = set(donnee_ajoutee["IMMATRICULATION"])

    for immatriculation in tqdm(immatriculations) :
        if(not os.path.isdir(f"model_save/{immatriculation}")):
            os.mkdir(f"model_save/{immatriculation}")

        else : pass

        if(not os.path.isfile(f"model_save/{immatriculation}/details.xlsx")):
            excel_details(result, immatriculation, commande_add)
            excel_detail_each_day(result, immatriculation, commande_add)

        else: pass

    print("Mise a jour des stats terminer avec succes !")

    print("renitialisation des fichier de commande . . .")

    with open(os.path.join(command_path, "remove_consideration_location.txt"), 'w'):
        pass

    with open(os.path.join(command_path, "add_consideration_location.txt"), 'w'):
        pass

    print("everything done successfully !")

else :
    
    print("Aucune nouvelle source de donnee Pour le moment. Les stats sont Up to date  ")




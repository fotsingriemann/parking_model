# parking_model
définition du model pour l'application des parking des chauffeurs


# demmarer le script dans pm2

pm2 start parking_model/model/script_job.py --interpreter python3

# consulter les logs 

pm2 logs 0

# restart

pm2 restart 0

# stoper

pm2 stop 0


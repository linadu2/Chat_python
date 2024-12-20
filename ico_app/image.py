import sys
import os
from datetime import datetime
from PIL import Image
import logging

#script_directory = "C:/Users/Admin/Pictures/Tools"
script_directory = os.getcwd()

def main():
    if len(sys.argv) > 1:
        file_path = sys.argv[1]
        file_name = os.path.basename(file_path)
        directory = os.path.dirname(file_path)
        base_name, ext = os.path.splitext(file_name)

        # Définir le chemin du fichier .ico
        ico_file = os.path.join(directory, f"{base_name}.ico")

        # Configurer le logging
        log_file = os.path.join(script_directory, "logfile.txt")
        logging.basicConfig(filename=log_file, level=logging.INFO, format='%(asctime)s: %(message)s')

        # Conversion de l'image en .ico
        try:
            img = Image.open(file_path)
            img.save(ico_file, format='ICO')
            logging.info(f"Conversion réussie : {ico_file}")
        except Exception as e:
            logging.error(f"Erreur lors de la conversion de {file_name} en .ico : {e}")
    else:
        logging.error("Aucun fichier fourni en argument.")

if __name__ == "__main__":
    main()
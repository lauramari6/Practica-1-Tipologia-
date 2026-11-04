#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MÒDUL PRINCIPAL: Pipeline d'extracció de dades de XXX
-----------------------------------------------------------------------------

Aquest script actua com a punt d'entrada principal del projecte.
"""

from pathlib import Path
import sys
import csv
from bs4 import BeautifulSoup

from source.config import URL_ORIGINAL, DICT_URL_HISTORIAL_WIKI, CARPETA_DATASET, COLUMNES_DATASET_PARTITS
from source.partits_politics import extreure_dades_partits
from user_agent import headers
from explore import obtencio_html, obtenir_apartats, scrap_data


# ------------------ROSER-------------------------------
# Afegim la carpeta del projecte dins la ruta de cerca de mòduls (sys.path)
CARPETA_PROJECTE = Path(__file__).resolve().parent
if str(CARPETA_PROJECTE) not in sys.path:
    sys.path.insert(0, str(CARPETA_PROJECTE))
# ------------------ROSER-------------------------------


# -----------------LAURA-------------------------------
r = obtencio_html(URL_ORIGINAL, headers=headers)
soup = BeautifulSoup(r, "html.parser")

# SCRAPING PARA LA PESTAÑA EXPLORE
data_url = obtenir_apartats(soup)[1]

scrap_data(data_url, headers)



"""
r = obtencio_html(url_original, headers=headers)
soup = BeautifulSoup(r, "html.parser")

# SCRAPING PARA LA PESTAÑA EXPLORE
explore_url = obtenir_apartats(soup)[0]
r_explore = obtencio_html(explore_url, headers)
soup_explore = BeautifulSoup(r_explore, "html.parser")

# Obtención de todas las url de cada region
url_regions = list_regions(explore_url, soup_explore)[0]
# obtención de cada región
regions = list_regions(explore_url, soup_explore)[1]

# Scrapping de cada articulo
data = scrap_for_region(url_regions, regions)

csv_data(data)

"""
# ------------------LAURA-------------------------------



# ------------------ROSER-------------------------------
# Per extreure les dades de partits_politics
dades_partits_politics = []

for year, url_hist in DICT_URL_HISTORIAL_WIKI.items():
    partits_any = extreure_dades_partits(url_hist, year)
    dades_partits_politics.extend(partits_any)

csv_partits_politics = CARPETA_DATASET / "partits_politics.csv"

with open(csv_partits_politics, "w", newline="", encoding="utf-8-sig") as csvfile:
    partits_writer = csv.DictWriter(csvfile,
                                    fieldnames = COLUMNES_DATASET_PARTITS,
                                    delimiter=";",
                                    quotechar="'",
                                    quoting=csv.QUOTE_MINIMAL)
    partits_writer.writeheader()
    partits_writer.writerows(dades_partits_politics)
# ------------------ROSER-------------------------------
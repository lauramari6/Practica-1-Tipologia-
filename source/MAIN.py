#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MÒDUL PRINCIPAL: Pipeline d'extracció de dades de XXX
-----------------------------------------------------------------------------

Aquest script actua com a punt d'entrada principal del projecte.
"""

from bs4 import BeautifulSoup

from source.config import (
    CARPETA_DATASET,
    DICT_URL_HISTORIAL_WIKI,
    COLUMNES_DATASET_GOVERNS,
    URL_ORIGINAL,
    headers
)
from source.utils import peticio_amb_espaiat, obtencio_html, desar_a_csv
from source.wiki_scraper import extreure_dades_governs
from user_agent import headers  # Eliminem aquest import??

# Eliminem obtencio_html de l'import d'explore?
from explore import obtencio_html, obtenir_apartats, scrap_data


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
print("Extraient dades de governs...")
dades_governs = []

for year, url_hist in DICT_URL_HISTORIAL_WIKI.items():
    print(f"- Recollint dades de l'any {year}")
    governs_any = extreure_dades_governs(url_hist, year)
    dades_governs.extend(governs_any)

csv_partits_politics = CARPETA_DATASET / "partits_politics.csv"
desar_a_csv(dades_governs, csv_partits_politics, COLUMNES_DATASET_GOVERNS)
print("Dades de governs extretes")
# ------------------ROSER-------------------------------
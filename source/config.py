#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from pathlib import Path


CARPETA_SOURCE = Path(__file__).resolve().parent
CARPETA_PROJECTE = CARPETA_SOURCE.parent
CARPETA_DATASET = CARPETA_PROJECTE / "dataset"

# Definim les capçaleres HTTP que enviarem al servidor, identificant-nos i incloent la nostra informació de contacte
# per complir amb les directrius de web scraping ètic.
headers = {
    "User-Agent": "UOC-WebScraping-Practica_1 (Laura Marí <lmaricab@uoc.edu>, Roser Xixons <rxixons@uoc.edu>; "
                  "assignatura_tipologia_i_cicle_de_vida_de_les_dades",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.5",
    "Accept-Encoding": "gzip, deflate, br"
}

URL_ORIGINAL = "https://monitor.civicus.org"

COLUMNES_DATASET_GOVERNS = [
    "país", "any", "sistema de partits", "partit governant", "en coalició?",
    "últimes eleccions parlamentàries", "últimes eleccions presidencials",
    "últimes eleccions generals", "últimes eleccions del Consell",
    "últimes eleccions del Congrés", "últimes eleccions federals",
    "últimes eleccions a la cambra baixa", "últimes eleccions a la cambra alta",
    "últimes eleccions al senat", "últimes eleccions legislatives"
]

# Diccionari per associar el nom del tipus d'eleccions (en l'anglès de Wikipedia) amb la
# clau del nostre diccionari "dict_partits_governants"
DICT_TIPUS_ELECCIONS = {"parliament": "últimes eleccions parlamentàries",
                        "parliamentary": "últimes eleccions parlamentàries",
                        "presidential": "últimes eleccions presidencials",
                        "general": "últimes eleccions generals",
                        "council": "últimes eleccions del Consell",
                        "congressional": "últimes eleccions del Congrés",
                        "congress": "últimes eleccions del Congrés",
                        "federal": "últimes eleccions federals",
                        "lower house": "últimes eleccions a la cambra baixa",
                        "upper house": "últimes eleccions a la cambra alta",
                        "senate": "últimes eleccions al senat",
                        "legislative": "últimes eleccions legislatives"}

# Diccionari amb les URLs d'on agafar les dades històriques per a cada any
DICT_URL_HISTORIAL_WIKI = {
    2018: "https://en.wikipedia.org/w/index.php?title=List_of_ruling_political_parties_by_country&oldid=817674069",
    2019: "https://en.wikipedia.org/w/index.php?title=List_of_ruling_political_parties_by_country&oldid=875356806",
    2020: "https://en.wikipedia.org/w/index.php?title=List_of_ruling_political_parties_by_country&oldid=933534715",
    2021: "https://en.wikipedia.org/w/index.php?title=List_of_ruling_political_parties_by_country&oldid=996435921",
    2022: "https://en.wikipedia.org/w/index.php?title=List_of_ruling_political_parties_by_country&oldid=1062867346",
    2023: "https://en.wikipedia.org/w/index.php?title=List_of_ruling_political_parties_by_country&oldid=1131251336",
    2024: "https://en.wikipedia.org/w/index.php?title=List_of_ruling_political_parties_by_country&oldid=1191897893",
    2025: "https://en.wikipedia.org/w/index.php?title=List_of_ruling_political_parties_by_country&oldid=1263464514"
}
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Nov  2 18:27:24 2026

@author: lauramari
"""

import requests
from user_agent import headers
from bs4 import BeautifulSoup
import re


# Amb la funció get obtenim informació sobre la resposta de la petició
# Definim URL de la pàgina web que consultarem
r = requests.get("https://monitor.civicus.org", headers=headers, timeout=20)
r.raise_for_status()

soup = BeautifulSoup(r.content, "html.parser")
# print(soup.prettify())


# Obtenim el codi HTTP retornat pel servidor
# print("Codi de resposta:", r.status_code)
# Mostram el User Agent que hem definit
# print("User Agent:", headers["User-Agent"])

#Volem obtenir el link de l'apartat Explore. Examinant l'HTML veim que es troba al href de la class='block link' EXPLORE.
for a in soup.find_all("a", href=True):
    if a.get_text(strip=True) == "EXPLORE":
        explore_url = a["href"]
        print(explore_url)
        break

# Una vegada tenim la URL de l'apartat Explore, volem obtenir els URLS per a cada una de les regions.

# Amb la funció get obtenim informació sobre la resposta de la petició, aquesta vegada per l'apartat Explore
r_explore = requests.get(explore_url, headers=headers, timeout=20)
r_explore.raise_for_status()
soup_explore = BeautifulSoup(r_explore.content, "html.parser")


# 1. OBTENIM UNA LLISTA DE LES REGIONS
#Localitzam el contenidor de regions.
region_div = soup_explore.find("div", id="id_region_options")
# Cercam totes les caselles de regió.
regions =[]
for checkbox in region_div.find_all("input", attrs={"name": "region"}):
        # Obtenim el valor de cada regió
        region = checkbox.get("value")
        regions.append(region)

# 2. MODIFICAM ELS ELEMENTS DE REGION PERQUÈ SIGUIN IGUALS QUE ELS DELS URL.

# Bucle per convertir els espais entre paraules en un '+', com a les URL.
for i in range(len(regions)):
    regions[i] = re.sub(r"\s", "+", regions[i])
print(regions)

# 3. CONSTRUIM LES URL DE CADA UNA DE LES REGIONS
url_regions=[]
for i in regions:
    url_nueva = f"{explore_url}?query=&region={i}"
    url_regions.append(url_nueva)
print(url_regions)
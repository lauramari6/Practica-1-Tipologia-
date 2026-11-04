#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Nov  2 19:59:22 2026

@author: lauramari
"""

#from explore import url_regions
import requests
from user_agent import headers
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import time

# Dins cada una de les regions, hi ha la possibilitat de que hi hagi diferents pàgines.


# Cream una llista per guardar les URL de totes les notícies
url_noticias = []
url_regions= ["https://monitor.civicus.org/explore/?query=&country=19"]


# Recorrem totes les regions
for url_region in url_regions:

    # Definim la primera pàgina de cada regió
    url_actual = url_region
    hay_siguiente = True
    contador=0

    # Recorrem totes les pàgines de la regió
    while hay_siguiente:

        # Obtenim l'HTML de la pàgina actual
        contador=contador+1
        #print(contador)
        r = requests.get(url_actual, headers=headers, timeout=20)
        r.raise_for_status()
        soup = BeautifulSoup(r.content, "html.parser")

        # Cercam les notícies de la pàgina
        articles = soup.find_all("article", class_="list-item")

        # Recorrem els articles trobats
        for article in articles:

            a = article.find("a", href=True)

            if a:
                url_noticia = urljoin(r.url, a["href"])
                url_noticias.append(url_noticia)

        # Comprovam si hi ha una pàgina següent
        pagination = soup.find("div", class_="pagination-container")


        # Si no existeix, no hi ha més pàgines
        if pagination is None:
            hay_siguiente = False

        else:
            next_page = pagination.find(id="pagination__next")

            if next_page is None or next_page.has_attr("disabled"):
               hay_siguiente = False

            elif next_page.name == "a" and next_page.has_attr("href"):
                url_actual = f"{url_region}&page={contador}"

            else:
               hay_siguiente = False
 
        if hay_siguiente:
          time.sleep(5)


# Eliminam possibles URL duplicades
url_noticias = list(dict.fromkeys(url_noticias))

# Mostram el nombre total de notícies
print("Total de notícies:", len(url_noticias))

# Mostram les URL obtingudes
for url in url_noticias:
    print(url)




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
from urllib.parse import urljoin
import time
import csv
import os

from config import CARPETA_DATASET


def obtencio_html(url, headers,  tries=3, timeout=20):
    
    for i in range(tries):
        try:
            r = requests.get(url, headers = headers, timeout= timeout)
            r.raise_for_status()
            return r.content
        except Exception:
            None
    return None


def data_article(url_art, headers, region):
    
    r = obtencio_html(url_art, headers)
    
    if r is None:
        return []
    
    soup = BeautifulSoup(r, "html.parser")
    
    #Cercam el contenidor de les metadades
    sidebar = soup.find("div", class_="right-sidebar")
    
    #Inicialitzam les variables
    data = []
    pais = None
    tags = []
    data_publi = None
    
    titulo_elemento = soup.find("h1")

    titulo = titulo_elemento.get_text(strip=True) if titulo_elemento else None
    
    if sidebar:

        # Cercam tots els blocs de metadades
        bloques = sidebar.find_all("div", class_="meta")

        for bloque in bloques:

            # Obtenim el nom del camp
            h6 = bloque.find("h6")

            if not h6:
                continue

            campo = h6.get_text(strip=True)

            # PAÍS
            if campo == "Country":
                a = bloque.find("a")
                if a:
                    pais = a.get_text(strip=True)

            # ETIQUETES
            elif campo == "Tags":
                for a in bloque.find_all("a"):
                    tag = a.get_text(strip=True).rstrip(",")
                    tags.append(tag)

            # DATA DE PUBLICACIÓ
            elif campo == "Date Posted":
                p = bloque.find("p")
                if p:
                    data_publi = p.get_text(strip=True)
    
    data.append({
        "titulo": titulo,
        "data_publicacio": data_publi,
        "país": pais,
        "tags": tags,
        "region": region,
        "url": url_art
        })
    
    return data


def scrap_for_region(url_regions, regions):
    
    columnas = ["titulo","data_publicacio","país","tags","region","url"]
    csv_name = CARPETA_DATASET / "data_articles.csv"
    isfile_data = os.path.isfile(csv_name)
    
    
    with open(csv_name, "a", newline = "") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames = columnas)
        
        
        if not isfile_data:
            writer.writeheader()
            
        # Recorrem totes les regions
        for url_region, region in zip(url_regions, regions):
            
            print(f"Estamos recorriendo {region}")

            # Definim la primera pàgina de cada regió
            url_actual = url_region
            hay_siguiente = True
            contador=0

            # Recorrem totes les pàgines de la regió
            while hay_siguiente:

                # Obtenim l'HTML de la pàgina actual
                contador=contador+1
                r = obtencio_html(url_actual, headers)
                soup = BeautifulSoup(r, "html.parser")

                # Cercam les notícies de la pàgina
                articles = soup.find_all("article", class_="list-item")

                # Recorrem els articles trobats
                for article in articles:

                    a = article.find("a", href=True)

                    if a:
                        url_noticia = urljoin(url_actual, a["href"])
                        # Extraemos los datos del artículo
                        datos_articulo = data_article(url_noticia, headers, region)
                        
                        # Guardamos inmediatamente en el CSV
                        for articulo in datos_articulo:
                            writer.writerow(articulo)
                        # Vaciamos el búfer de escritura
                        csvfile.flush()
                        
                print(f"Se ha añadido los datos de {region} {contador} veces")

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
            

def obtenir_apartats(soup):

    for a in soup.find_all("a", href=True):
        if a.get_text(strip=True) == "EXPLORE":
            explore_url = a["href"]
            break
    
    for a in soup.find_all("a", href=True):
        if a.get_text(strip=True) == "Data":
            data_url = a["href"]
            break
    
    return explore_url, data_url


def list_regions(explore_url, soup_explore):
    region_div = soup_explore.find("div", id="id_region_options")
    # Cercam totes les caselles de regió.
    regions =[]
    url_regions=[]
    
    for checkbox in region_div.find_all("input", attrs={"name": "region"}):
            # Obtenim el valor de cada regió
            region = checkbox.get("value")
            regions.append(region)
            
    # Bucle per convertir els espais entre paraules en un '+', com a les URL.
    for i in range(len(regions)):
        regions[i] = re.sub(r"\s", "+", regions[i])

    # 3. CONSTRUIM LES URL DE CADA UNA DE LES REGIONS
    for i in regions:
        url_nueva = f"{explore_url}?query=&region={i}"
        url_regions.append(url_nueva)
    
    return url_regions, regions
    

def csv_data(data):
    
    columnas = ["titulo","data_publicacio","país","tags","region","url"]
    csv_name = CARPETA_DATASET / "data_articles.csv"
    isfile_data = os.path.isfile(csv_name)
    
    with open(csv_name, "a", newline = "") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames = columnas)
        if not isfile_data:
            writer.writerheader()
        for row in data:
            writer.writerow(row)


def scrap_data(url, headers):

    r = obtencio_html(url, headers)

    if r is None:
        return []

    soup = BeautifulSoup(r, "html.parser")

    # Buscamos la tabla
    tabla = soup.find("table", class_="country-monitor-list")

    if tabla is None:
        print("No se ha encontrado la tabla")
        return []

    data = []

    # Obtenemos los años de las cabeceras
    cabeceras = tabla.select("thead th")
    anys = [th.get_text(strip=True) for th in cabeceras[3:]]

    # Obtenemos todas las filas del cuerpo de la tabla
    filas = tabla.select("tbody tr")

    for fila in filas:

        # Cada td corresponde a una columna
        celdas = fila.find_all("td")

        if len(celdas) != 3 + len(anys):
            continue

        # País
        pais = celdas[0].get("aria-label")
        if not pais:
            pais = celdas[0].get_text(strip=True)

        # Puntuación actual
        score = celdas[1].get_text(strip=True)

        # Clasificación actual
        rating = celdas[2].get_text(strip=True)

        # Creamos el diccionario
        registro = {
            "pais": pais,
            "score_actual": score,
            "rating_actual": rating
        }

        # Añadimos las clasificaciones de cada año
        for any_, celda in zip(anys, celdas[3:]):
            registro[any_] = celda.get_text(strip=True)

        data.append(registro)

    columnas = ["pais","score_actual","rating_actual","2024","2023","2022","2021","2020","2019","2018"]
    csv_name = CARPETA_DATASET / "score_for_years.csv"
    isfile_data = os.path.isfile(csv_name)
    
    with open(csv_name,"a", newline="") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames = columnas)
        
        if not isfile_data:
            writer.writeheader()
            
        for row in data:
            writer.writerow(row)
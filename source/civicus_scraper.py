#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Nov  2 18:27:24 2026

@author: lauramari
"""

import time
import csv
import os
from config import headers
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from utils import obtencio_html
from config import CARPETA_DATASET


def data_article(url_art: str, headers:dict, region:str) -> list:
    """
    Donat un enllaç url, obtenim el contingut html i el parsetjam, per després
    cercar i capturar les metadades dels camps d'interès.
    """

    r = obtencio_html(url_art, headers)

    # En cas de no obtenir cap contingut html, retornam None per evitar errors
    if r is None:
        return []

    soup = BeautifulSoup(r, "html.parser")

    # Cercam el contenidor de les metadades
    sidebar = soup.find("div", class_="right-sidebar")

    # Inicialitzam les variables. Cal dir que el camp regions s'hi incorpora
    # al nomenar la funció
    data = []
    pais = None
    tags = []
    data_publi = None

    titol_element = soup.find("h1")
    titol = titol_element.get_text(strip=True) if titol_element else None

    if sidebar:
        # Cercam tots els blocs de metadades
        blocs = sidebar.find_all("div", class_="meta")
        # Anam bloc per bloc troban els camps i es guarden segons els noms

        for bloc in blocs:
            # Obtenim el nom del camp
            h6 = bloc.find("h6")
            # En cas de no haver-hi res, es passa al següent bloc
            if not h6:
                continue

            camp = h6.get_text(strip=True)
            # Pais
            if camp == "Country":
                a = bloc.find("a")
                if a:
                    pais = a.get_text(strip=True)
            # Etiquetes
            elif camp == "Tags":
                for a in bloc.find_all("a"):
                    tag = a.get_text(strip=True).rstrip(",")
                    tags.append(tag)
            # Data publicació
            elif camp == "Date Posted":
                p = bloc.find("p")
                if p:
                    data_publi = p.get_text(strip=True)

    data.append({
        "titulo": titol,
        "data_publicacio": data_publi,
        "país": pais,
        "tags": ", ".join(tags),
        "region": region,
        "url": url_art
        })

    return data


def scrap_for_region(url_regions: str, regions: list) -> None:
    """
    Donada una llista de urls segons les diferents regions geogràfiques,
    es cerquen per cadascuna els articles associats al llarg de diferents
    pàgines.
    """


    # Per tal d'estalviar temps i no saturar la pàgina, es decideix guardar
    # les dades en el csv mentre es va recorrent cada article. Per
    # aconseguir-ho, no obrirem l'arxiu costantment sinó que el deixarem obert.
    columnas = ["titulo","data_publicacio","país","tags","region","url"]
    csv_name = CARPETA_DATASET / "data_articles.csv"
    isfile_data = os.path.isfile(csv_name)

    url_visitades = set()
    total_regions = len(url_regions)
    total_articles = 0

    with open(csv_name, "a", newline = "", encoding="utf-8-sig") as csvfile:
        writer = csv.DictWriter(csvfile,
                                fieldnames=columnas,
                                delimiter=";",
                                quotechar='"')

        if not isfile_data:
            writer.writeheader()
        # Recorrem totes les regions
        for idx_reg, (url_region, region) in enumerate(zip(url_regions, regions), start=1):
            print(f"[{idx_reg}/{total_regions}] Extraient dadesde la regió: {region}")
            # Definim la primera pàgina de cada regió
            url_actual = url_region
            seguent = True
            contador = 1
            # Recorrem totes les pàgines de la regió fins que no hi hagi 
            # pàgina següent
            while seguent:
                print(f"\n Regió [{idx_reg}/{total_regions}] | Pàgina {contador}...")
                # Obtenim l'html de la pàgina actual
                r = obtencio_html(url_actual, headers)
                if not r:
                    break

                soup = BeautifulSoup(r, "html.parser")
                # Cercam les notícies de la pàgina
                articles = soup.find_all("article", class_="list-item")
                if not articles:
                    break

                articles_pag_actual = 0
                # Recorrem els articles trobats
                for article in articles:

                    a = article.find("a", href=True)

                    if a:
                        url_noticia = urljoin(url_actual, a["href"])

                        if url_noticia in url_visitades:
                            continue

                        url_visitades.add(url_noticia)
                        # Capturam les dades de l'article
                        dades_article = data_article(url_noticia, headers, region)
                        # Ara guardam les dades dins l'arxiu
                        for data in dades_article:
                            writer.writerow(data)
                            total_articles += 1
                            articles_pag_actual +=1
                            print(f"   [Número d'articles processats: {total_articles}]")

                print(f" Pàgina {contador} completada (+{articles_pag_actual} articles nous)")

                # Comprovam si hi ha una pàgina següent
                paginacio = soup.find("div", class_="pagination-container")
                # Si no existeix, no hi ha més pàgines
                if paginacio is None:
                    seguent = False

                else:
                    # En cas d'existir, comprobam que el botó estigui habilitat
                    # i que porti una url
                    seg_pag = paginacio.find(id="pagination__next")

                    if seg_pag is None or seg_pag.has_attr("disabled") or seg_pag.name != "a":
                       seguent = False

                    else:
                        contador +=1
                        url_actual = f"{url_region}&page={contador}"

                if seguent:
                  time.sleep(2)


def scrap_data(url: str, headers: str) -> None:
    """
    Donada la url de la secció Data, cercam dins la taula les dades d'interès.
    Després el guardam dins un arxiu csv.'
    """

    r = obtencio_html(url, headers)
    # En cas de no obtenir cap contingut html, retornam None per evitar errors
    if r is None:
        return []

    soup = BeautifulSoup(r, "html.parser")

    # Cercam taula
    taula = soup.find("table", class_="country-monitor-list")
    # En cas d'haver-hi errors, retornam llista buida
    if taula is None:
        return []

    data = []

    # Obtenim els anys dels headers de la taula
    cap = taula.select("thead th")
    # Els anys es troben a partir del tercer element
    anys = [th.get_text(strip=True) for th in cap[3:]]
    # Obtenim totes les files del cos de la taula
    files = taula.select("tbody tr")

    for fila in files:
        # Cada td correspon a una columna
        cel = fila.find_all("td")

        if len(cel) != 3 + len(anys):
            continue
        # Camp pais
        pais = cel[0].get("aria-label")
        if not pais:
            pais = cel[0].get_text(strip=True)
        # Puntuació actual
        score = cel[1].get_text(strip=True)
        # Classificació actual
        rating = cel[2].get_text(strip=True)
        # Cream diccionari
        registre = {
            "pais": pais,
            "score_actual": score,
            "rating_actual": rating
        }

        # Afegim les classificacions de cada any
        for any_, cel_any in zip(anys, cel[3:]):
            registre[any_] = cel_any.get_text(strip=True)

        data.append(registre)
    # Ara guardam les dades dins un csv
    columnes = ["pais","score_actual","rating_actual","2024","2023","2022","2021","2020","2019","2018"]
    csv_name = CARPETA_DATASET / "score_for_years.csv"
    isfile_data = os.path.isfile(csv_name)

    with open(csv_name,"a", newline="", encoding="utf-8-sig") as csvfile:
        writer = csv.DictWriter(csvfile,
                                fieldnames=columnes,
                                delimiter=";",
                                quotechar='"')

        if not isfile_data:
            writer.writeheader()

        for row in data:
            writer.writerow(row)
#!/usr/bin/env python3
# -*- coding: utf-8 -*-


"""
Gestió de peticions HTTP, exportació de dades i altres funcions genèriques
"""

import time
import requests
from requests.exceptions import RequestException
import csv
from pathlib import Path
from bs4 import BeautifulSoup
import os
from urllib.parse import urljoin, quote_plus

from config import CARPETA_DATASET, URL_ORIGINAL


def peticio_amb_espaiat(url: str, headers: dict, tries: int = 3, factor_mult: float = .0,
                        timeout: int = 10) -> requests.Response | None:
    """
    Realitza una petició HTTP mesurant el temps de resposta del servidor i aplica una
    pausa per complir amb l'ètica de web scraping.
    """

    for i in range(tries):
        t0 = time.time()
        try:
            response = requests.get(url, headers=headers, timeout=timeout)
            response.raise_for_status()

            response_delay = time.time() - t0
            time.sleep(factor_mult * response_delay)

            return response

        except RequestException as e:
            print(f"[ERROR DE XARXA]: L'intent {i + 1}/{tries} ha fallat per {url}: {e}")
            time.sleep(2)

    return None


def obtencio_html(url: str, headers: dict, tries: int = 3, timeout: int = 10) -> bytes | None:
    """
    Utilitza peticio_amb_espaiat i retorna l'objecte "response.content".
    """

    response = peticio_amb_espaiat(url, headers, tries=tries, timeout=timeout)
    return response.content if response else None


def desar_a_csv(dades: list[dict], ruta_fitxer: Path, columnes: list[str]) -> None:
    """Escriu una llista de diccionaris a un fitxer CSV de forma unificada."""


    if not dades:
        print(f"[WARN Utils] No hi ha dades per desar a {ruta_fitxer.name}")
        return

    isfile_data = ruta_fitxer.is_file()
    with open(ruta_fitxer, "a", newline="", encoding="utf-8-sig") as csvfile:
        writer = csv.DictWriter(csvfile,
                                fieldnames=columnes,
                                delimiter=";",
                                quotechar="'")
        if not isfile_data:
            writer.writeheader()
        writer.writerows(dades)


def obtenir_apartats(soup: BeautifulSoup) -> tuple[str, str]:
    """
    Obtenim els enllaços de les seccions Explore i Data.
    """

    explore_url, data_url = "", ""

    for a in soup.find_all("a", href=True):
        txt = a.get_text(strip=True).lower()

        if "explore" in txt and not explore_url:
            explore_url = urljoin(URL_ORIGINAL, a["href"])
        elif "data" in txt and not data_url:
            data_url = urljoin(URL_ORIGINAL, a["href"])

        if explore_url and data_url:
            break

    return explore_url, data_url


def list_regions(explore_url: str, soup_explore: BeautifulSoup) -> tuple[list,list]:
    """
    Obtenim l'etiqueta de cada regió que apareix en el filtre de la pàgina.
    Després es trasnforma adequadament per utilitzar-les amb l'objectiu de
    construir les urls de cada regió'
    """

    region_div = soup_explore.find("div", id="id_region_options")
    # Cercam totes les caselles de regió del filtre.
    if not region_div:
        return [], []

    url_regions = []
    regions_clean = []
    vistos = set()

    for checkbox in region_div.find_all("input", attrs={"name": "region"}):
        raw_val = checkbox.get("value")
        if not raw_val:
            continue

        if isinstance(raw_val, list):
            val = " ".join(raw_val.strip())
        else:
            val = str(raw_val).strip()

        if val and val not in vistos:
            vistos.add(val)
            val_encoded = quote_plus(val)
            url_nova = f"{explore_url}?query=&region={val_encoded}"
            url_regions.append(url_nova)
            regions_clean.append(val)

    return url_regions, regions_clean


def csv_data(data: list) -> None:
    """
    Guardam les dades dins d'un arxiu csv. Especificam el nom de les columnes
    i el nom que tindrá l'arxiu.'
    """

    columnas = ["titulo","data_publicacio","país","tags","region","url"]
    csv_name = CARPETA_DATASET / "data_articles.csv"
    isfile_data = os.path.isfile(csv_name)

    with open(csv_name, "a", newline = "") as csvfile:
        writer = csv.DictWriter(csvfile,
                                fieldnames=columnas,
                                delimiter=";",
                                quotechar="'")
        # En cas de no existir, el cream
        if not isfile_data:
            writer.writeheader()
        # Afegim les dades per fila
        for row in data:
            writer.writerow(row)


def verificar_user_agent(headers: dict) -> str:
    """
    Fa una petició a 'https://httpbin.org/user-agent' per verificar l'User-Agent real rebut a la xarxa
    """

    url_verificacio = "https://httpbin.org/user-agent"
    try:
        response = requests.get(url_verificacio, headers=headers)
        response.raise_for_status()
        ua_real = response.json().get("user-agent")
        print(f"User-Agent confirmat pel servidor: {ua_real}")
        return ua_real
    except RequestException as e:
        print(f"[ERROR DE XARXA]: La verificació de l'user-agent a fallat a {url_verificacio}: {e}")
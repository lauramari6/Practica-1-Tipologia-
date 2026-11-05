#!/usr/bin/env python3
# -*- coding: utf-8 -*-


"""
MÒDUL PRINCIPAL: Pipeline d'extracció de dades de XXX
-----------------------------------------------------------------------------

Aquest script actua com a punt d'entrada principal del projecte.
"""

from bs4 import BeautifulSoup

from config import (
    CARPETA_DATASET,
    COLUMNES_DATASET_GOVERNS,
    URL_ORIGINAL,
    headers
)
from utils import obtencio_html, desar_a_csv, obtenir_apartats, list_regions, verificar_user_agent
from wiki_scraper import WikiGovernsSpider
from civicus_scraper import scrap_data, scrap_for_region
from scrapy.crawler import CrawlerProcess


def main():
    # ==============================================================
    # 0. Verificació de l'User-Agent
    # ==============================================================
    verificar_user_agent(headers)

    #===============================================================
    # 1. Scrapping de les dades de la taula en la pestanya Data
    #===============================================================
    print("Extraient dades de la taula...")

    r = obtencio_html(URL_ORIGINAL, headers=headers)
    soup = BeautifulSoup(r, "html.parser")
    # Pestanya Data
    explore_url, data_url = obtenir_apartats(soup)
    # Scrapping
    scrap_data(data_url, headers)
    print("Dades de la taula extretes")

    #===============================================================
    # 2. Scrapping de les dades dels articles en la pestanya Explore
    #===============================================================
    print("Extraient dades dels articles...")

    r_explore = obtencio_html(explore_url, headers=headers)
    soup_explore = BeautifulSoup(r_explore, "html.parser")
    # Obtenció de l'url i de l'etiqueta de cada regió
    url_regions, regions = list_regions(explore_url, soup_explore)
    # Scrapping de cada article
    scrap_for_region(url_regions, regions)
    print("Dades dels articles extretes")

    #===============================================================
    # 3. Scrapping extern de les dades partits polítics per anys
    #===============================================================
    print("Extraient dades de governs...")

    dades_governs = []

    proces = CrawlerProcess(settings={
        # Utilitzem la capçalera identificadora per un web scraping ètic
        "DEFAULT_REQUEST_HEADERS": headers,

        # Mimetitzem el comportament de la funció "peticio_amb_espaiat"
        "DOWNLOAD_TIMEOUT": 10,
        "RETRY_ENABLED": True,
        "RETRY_TIMES": 3,
        "RETRY_HTTP_CODES": [500, 502, 503, 504, 522, 524, 408, 429],
        "AUTOTHROTTLE_ENABLED": True,
        "AUTOTHROTTLE_START_DELAY": 1.0,
        "AUTOTHROTTLE_MAX_DELAY": 10.0,
        "AUTOTHROTTLE_TARGET_CONCURRENCY": 1.0,

        # Perquè només es mostri informació rellevant sobre l'execució de l'scraping
        "LOG_LEVEL": "INFO"
    })

    proces.crawl(WikiGovernsSpider, dades_sortida=dades_governs)
    proces.start()

    csv_partits_politics = CARPETA_DATASET / "dades_governs.csv"
    desar_a_csv(dades_governs, csv_partits_politics, COLUMNES_DATASET_GOVERNS)
    print("Dades de governs extretes")


if __name__== "__main__":
    main()
#!/usr/bin/env python3
# -*- coding: utf-8 -*-


"""
Funcions per al web scraping a la pàgina "List of ruling political parties by country"
de la Wikipedia
"""


import re
from urllib.parse import urljoin
import pandas as pd
from bs4 import BeautifulSoup
import scrapy

from config import DICT_TIPUS_ELECCIONS, COLUMNES_DATASET_GOVERNS


class WikiGovernsSpider(scrapy.Spider):
    name = "wiki_governs_spider"

    start_urls = [
        "https://en.wikipedia.org/w/index.php?title=List_of_ruling_political_parties_by_country&action=history&limit=5000"
    ]

    def __init__(self, dades_sortida=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.anys = list(range(2017, 2026))
        self.anys_trobats = set()
        self.dades_registrades = dades_sortida if dades_sortida is not None else []

    def parse(self, response):
        """
        Analitza l'historial de la pàgina per extreure dinàmicament les URLs de cadascun dels anys anteriors.
        """
        # Primer verifiquem l'user-agent
        ua_enviat = response.request.headers.get("User-Agent").decode("utf-8")
        self.logger.info(f"User-Agent confirmat pel servidor: {ua_enviat}")

        # I ara ja busquem les revisions a l'hitorial de la Wikipedia
        revisions= response.css("a[href*='oldid=']")

        for rev in revisions:
            url_relativa = rev.css("::attr(href)").get()
            text_data = "".join(rev.css("::text").getall()).strip()

            coincidencia = re.search(r"\b(20\d{2})\b", text_data)
            if coincidencia:
                any_ = int(coincidencia.group(1))

                if any_ in self.anys and any_ not in self.anys_trobats:
                    self.anys_trobats.add(any_)
                    url_completa = urljoin(response.url, url_relativa)

                    yield scrapy.Request(url=url_completa, callback=self.parse_revisio,cb_kwargs={"any_":any_})

            if len(self.anys_trobats) == len(self.anys):
                break


    def parse_revisio(self, response, any_):
        """
        Processa l'HTML descarregat cridant la funció de parseig.
        """

        dades_any = extreure_dades_governs(response.body, any_)
        self.dades_registrades.extend(dades_any)


def extreure_dades_governs(contingut_html: str | bytes, year: int) -> list:
    """
    Extreu, per a un any concret, les dades de partits governants a partir del contingut HTML de la Wikipedia.
    Retorna una llista de diccionaris (files de la/les taula/es de la pàgina de Wikipedia).
    """

    soup = BeautifulSoup(contingut_html, features="html.parser")
    taules = soup.find_all("table", class_="wikitable")

    files_any = []

    for taula in taules:

        # Com que el format de la taula pateix canvis durant el període en què extraiem
        # les dades, identifiquem les capçaleres perquè aquestes sí que es mantenen
        # uniformes.
        head_taula = [th.get_text(strip=True).lower() for th in taula.find_all("th")]

        # Creem una variable per a diferenciar entre format antic i format actual de la
        # taula de wikipèdia
        if len(head_taula) > 4:
            format_taula_antic = True
        else:
            format_taula_antic = False

        # Evitem agafar dades de territoris perquè es confondrien amb les dades
        # del país que l'ha colonitzat
        if any("territory" in h for h in head_taula):
            continue

        # Busquem l'índex de les columnes segons el text de la capçalera de la taula
        idx_pais = next((i for i, h in enumerate(head_taula) if "country" in h), None)
        idx_sistema = next((i for i, h in enumerate(head_taula) if "system" in h), None)
        idx_govern_0 = next((i for i, h in enumerate(head_taula) if "ruling" in h), None)
        idx_eleccions_0 = next((i for i, h in enumerate(head_taula) if "election" in h), None)

        for fila in taula.find_all("tr"):
            idx_govern = idx_govern_0
            idx_eleccions = idx_eleccions_0
            dades_fila = fila.find_all("td")

            if len(dades_fila) > 0:

                # Creem un diccionari-fila temporal per assegurar que s'omplen totes les columnes
                fila_dict = {clau: pd.NA for clau in COLUMNES_DATASET_GOVERNS}

                if idx_pais is not None:
                    fila_dict["país"] = dades_fila[idx_pais].get_text(strip=True)

                fila_dict["any"] = year

                # Les files que només contenen 3 dades no corresponen a països democràtics
                if len(dades_fila) == 3:
                    # Per tant, omplim els valors amb Nones o similar.
                    fila_dict["sistema de partits"] = "Non-partisan"
                    fila_dict["partit governant"] = pd.NA
                    files_any.append(fila_dict)
                    continue

                if format_taula_antic:
                    if len(dades_fila) == 4:
                        if idx_sistema is not None:
                            fila_dict["sistema de partits"] = dades_fila[idx_sistema].get_text(strip=True)

                    else:
                        # La forma de saber a quin sistema pertany cada país és identificant quina columna conté text,
                        # ja que cada columna pertany a un sistema de partits.
                        for i in range(1, 5):
                            text_sistema = dades_fila[i].get_text(strip=True)

                            if text_sistema:
                                ths = taula.find_all("th")
                                if len(ths) >= 8:
                                    fila_dict["sistema de partits"] = [
                                        th.get_text(strip=True).lower() for th in taula.find_all("th")[4:8:][i - 1]
                                    ]
                                break

                        idx_govern = idx_govern_0 + 3 if idx_govern_0 is not None else None
                        idx_eleccions = idx_eleccions_0 + 3 if idx_eleccions_0 is not None else None

                    if idx_govern_0 is not None:
                        govern = dades_fila[idx_govern].get_text(strip=True)
                    else:
                        govern = ""

                    if idx_eleccions is not None:
                        # Extraiem les parelles (any, tipus d'elecció) de cada fila del format
                        # antic
                        anys_eleccions = re.findall(
                            r"(\d{4}(?:[–-]\d{2,4})?)\s+([a-zA-Z\s]+?)\s+election",
                            dades_fila[idx_eleccions].get_text(separator=" ", strip=True),
                            flags=re.IGNORECASE
                        )
                    else:
                        anys_eleccions = []

                else:    # El format de la taula és l'actual
                    if idx_sistema is not None:
                        fila_dict["sistema de partits"] = dades_fila[idx_sistema].get_text(strip=True)

                    if idx_govern is not None:
                        govern = BeautifulSoup(dades_fila[idx_govern].decode_contents().split("<hr")[0],
                                               "html.parser").get_text(strip=True)
                    else:
                        govern = ""

                    if idx_eleccions is not None:
                        # Extraiem les parelles (any, tipus d'elecció) de cada fila del format actual
                        anys_eleccions = re.findall(r"(\d{4}(?:[–-]\d{2,4})?)\s*\(([^)]+)\)",
                                                    dades_fila[idx_eleccions].get_text(separator=" ", strip=True),
                                                    flags=re.IGNORECASE)

                en_coalicio = bool(re.search(r"[,(]", govern))
                fila_dict["en coalició?"] = en_coalicio

                if not en_coalicio:
                    fila_dict["partit governant"] = govern
                else:
                    # En cas que el govern sigui una coalició de partits, només ens quedem
                    # amb el que té més representació
                    fila_dict["partit governant"] = re.split(r"[,(]", govern, maxsplit=1)[0].strip()

                for yr, tipus in anys_eleccions:
                    tipus_minuscules = tipus.lower()
                    if tipus_minuscules in DICT_TIPUS_ELECCIONS:
                        clau_dict = DICT_TIPUS_ELECCIONS[tipus_minuscules]
                        fila_dict[clau_dict] = yr

                files_any.append(fila_dict)

    return files_any
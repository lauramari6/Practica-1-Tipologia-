#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Gestió de peticions HTTP i exportació de dades
"""

import time
import requests
from requests.exceptions import RequestException
import csv
from pathlib import Path


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
            print(f"[ERROR Network] Intent {i + 1}/{tries} fallat a {url}: {e}")
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
                                quotechar="'",
                                quoting=csv.QUOTE_MINIMAL)
        if not isfile_data:
            writer.writeheader()
        writer.writerows(dades)
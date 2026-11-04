#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import time
import requests
from requests.exceptions import RequestException


def peticio_amb_espaiat(url: str, headers: dict, factor_mult: float = 10.0) -> requests.Response:
    """
    Realitza una petició HTTP mesurant el temps de resposta
    i aplica una pausa proporcional delimitada per un mínim i un màxim.
    ------------------------------------------------------------------------------------------------------

    Codi extret de la referència: Subirats, L., Calvo, M. (2018). Web Scraping. Editorial UOC. Pàgina 49
    """

    t0 = time.time()
    try:
        response = requests.get(url, headers=headers, timeout=10)
    except RequestException as e:
        print(f"Error en la petició: {e}")
        return None

    response_delay = time.time() - t0

    time.sleep(factor_mult * response_delay)

    return response
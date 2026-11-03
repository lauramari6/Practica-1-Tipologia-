#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Nov  2 22:31:06 2026

@author: lauramari
"""

import requests
from user_agent import headers
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import time


url= "https://monitor.civicus.org/explore/concerning-legislative-proposals-thousands-of-minors-arrested-amid-nationwide-student-protests/"
r = requests.get(url, headers=headers, timeout=20)
r.raise_for_status()
soup = BeautifulSoup(r.content, "html.parser")


#Cercam el contenidor de les metadades
sidebar = soup.find("div", class_="right-sidebar")

#Inicialitzam les variables
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

    

print("País:", pais)
print("Data:", data_publi)
print("Tags:", tags)
print(titulo)
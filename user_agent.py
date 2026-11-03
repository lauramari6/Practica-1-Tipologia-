#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Nov  1 19:02:07 2026

@author: lauramari
"""


import requests

# Codi de creació del header per al User Agent que farem servir al Web Scrapping
# Codi extret de la referència: Subirats, L., Calvo, M. (2018). Web Scraping. Editorial UOC. Pàgina 47.

# Definim les capçaleres HTTP que enviarem al servidor
headers = {
"Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,\
*/*;q=0.8",
"Accept-Encoding": "gzip, deflate, sdch, br",
"Accept-Language": "en-US,en;q=0.8",
"Cache-Control": "no-cache",
"dnt": "1",
"Pragma": "no-cache",
"Upgrade-Insecure-Requests": "1",
#Hem posat versions actualitzades de macOS i de Chrome
"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/5\
37.36 (KHTML, like Gecko) Chrome/156.0.0.0 Safari/537.36"
}




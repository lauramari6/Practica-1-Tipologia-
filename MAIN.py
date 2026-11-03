#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Nov  1 18:07:46 2026

@author: lauramari
"""

print('hola')

# Per extreure les dades de partits_politics
for year, url_hist in dict_url_historial_wiki.items():
    print(f"Extreient dades de l'any {year}...")
    extreure_dades_partits(url_hist, year)

pd.DataFrame.from_dict(dict_partits_governants)
# Practica-1-Tipologia: Web Scraping-

## Descripció

Aquesta practica s'ha realitzat amb el context de l'assignatura *Tipologia i cicle de vida de les dades* del Màster en Ciència de Dades de la Universitat Oberta de Catalunya (UOC).

L'objectiu és aplicar tècniques de web scraping mitjançant Python per extreure informació de les pàgines web **CIVICUS Monitor** i **Wikipedia**, i generar un conjunt de dades sobre l'espai cívic i el context polític dels països durant el període 2018-2025. 

## Membres de l'equip

La pràctica ha estat realitzada per Roser Xixons i Laura Marí.

## Fitxers del codi font:

- **source/main.py**: punt d'entrada al programa. Executa els processos de recol·lecció de dades.
- **source/civicus_scraper.py**: conté les funcions per extreure les puntuacions, classificacions i articles de CIVICUS Monitor.
- **source/wiki_scraper.py**: conté les funcions per extreure informació sobre els sistemes de partits, els governs i les eleccions de Wikipedia.
- **source/config.py**: conté les configuracions, les URL i les variables necessàries per al projecte.
- **source/utils.py**: inclou funcions auxiliars per gestionar les peticions HTTP i els fitxers CSV.


## Dataset

El conjunt de dades està format per tres fitxers CSV:

- **score_for_years.csv**: puntuacions i classificacions de l'espai cívic dels països.
- **data_articles.csv**: articles i notícies relacionats amb l'espai cívic dels països..
- **partits_politics.csv**: informació sobre els sistemes de partits, els governs i els processos electorals.

## Recursos

1. CIVICUS Monitor (https://monitor.civicus.org)
2. Wikipedia - List of ruling political parties by country (https://en.wikipedia.org/wiki/List_of_ruling_political_parties_by_country)

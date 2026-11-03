# Diccionari amb les URLs d'on agafar les dades històriques per a cada any
from user_agent import headers

dict_partits_governants = {"país": [],
                           "any": [],
                           "sistema de partits": [],
                           "partit governant": [],
                           "en coalició?": [],
                           "últimes eleccions parlamentàries": [],
                           "últimes eleccions presidencials": [],
                           "últimes eleccions generals": [],
                           "últimes eleccions del Consell": [],
                           "últimes eleccions del Congrés": [],
                           "últimes eleccions federals": [],
                           "últimes eleccions a la cambra baixa": [],
                           "últimes eleccions a la cambra alta": [],
                           "últimes eleccions al senat": [],
                           "últimes eleccions legislatives": []}

# Diccionari per associar el nom del tipus d'eleccions (en l'anglès de Wikipedia) amb la
# clau del nostre diccionari "dict_partits_governants"
dict_tipus_eleccions = {"parliament": "últimes eleccions parlamentàries",
                        "parliamentary": "últimes eleccions parlamentàries",
                        "presidential": "últimes eleccions presidencials",
                        "general": "últimes eleccions generals",
                        "council": "últimes eleccions del Consell",
                        "congressional": "últimes eleccions del Congrés",
                        "congress": "últimes eleccions del Congrés",
                        "federal": "últimes eleccions federals",
                        "lower house": "últimes eleccions a la cambra baixa",
                        "upper house": "últimes eleccions a la cambra alta",
                        "senate": "últimes eleccions al senat",

dict_url_historial_wiki = {
    2018: "https://en.wikipedia.org/w/index.php?title=List_of_ruling_political_parties_by_country&oldid=817674069",
    2019: "https://en.wikipedia.org/w/index.php?title=List_of_ruling_political_parties_by_country&oldid=875356806",
    2020: "https://en.wikipedia.org/w/index.php?title=List_of_ruling_political_parties_by_country&oldid=933534715",
    2021: "https://en.wikipedia.org/w/index.php?title=List_of_ruling_political_parties_by_country&oldid=996435921",
    2022: "https://en.wikipedia.org/w/index.php?title=List_of_ruling_political_parties_by_country&oldid=1062867346",
    2023: "https://en.wikipedia.org/w/index.php?title=List_of_ruling_political_parties_by_country&oldid=1131251336",
    2024: "https://en.wikipedia.org/w/index.php?title=List_of_ruling_political_parties_by_country&oldid=1191897893",
    2025: "https://en.wikipedia.org/w/index.php?title=List_of_ruling_political_parties_by_country&oldid=1263464514"
}


def extreure_dades_partits(url, year):
    wiki_partits_governants = requests.get(url, headers=headers)
    soup = BeautifulSoup(wiki_partits_governants.content)
    taules = soup.find_all("table", class_="wikitable")

    for taula in taules:

        # Com que el format de la taula pateix canvis durant el període en què extraiem
        # les dades, identifiquem les capçaleres perqué aquestes sí que es mantenen
        # uniformes
        head_taula = [th.get_text(strip=True).lower() for th in taula.find_all("th")]

        # Creem una variable per a diferneciar entre format antic i format actual de la
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
        idx_eleccions_0 = next(
            (i for i, h in enumerate(head_taula) if "election" in h), None
        )

        for fila in taula.find_all("tr"):
            idx_govern = idx_govern_0
            idx_eleccions = idx_eleccions_0
            dades_fila = fila.find_all("td")

            if len(dades_fila) > 0:

                # Creem una fila temporal per assegurar que tots els valors del diccionari
                # s'omplen i no queda la taula final desequilibrada
                fila_dict = {clau: pd.NA for clau in dict_partits_governants.keys()}

                fila_dict["país"] = (dades_fila[idx_pais].get_text(strip=True)
                                     if idx_pais is not None else pd.NA)
                fila_dict["any"] = year

                # Les files que només contenen 3 dades no corresponen a països democràtics
                if len(dades_fila) == 3:
                    # Per tant, omplim els valors amb Nones o similar
                    fila_dict["sistema de partits"] = "Non-partisan"
                    fila_dict["partit governant"] = pd.NA

                    continue

                if format_taula_antic:
                    if len(dades_fila) == 4:
                        fila_dict["sistema de partits"] = (
                            dades_fila[idx_sistema].get_text(strip=True)
                            if idx_sistema is not None else pd.NA
                        )

                    else:
                        sistema_partits = None

                        # La forma de saber a quin sistema pertany cada país és
                        # identificant quina columna conté text, ja que cada columna
                        # pertany a un sistema de partits
                        for i in range(1, 5):
                            text_sistema = dades_fila[i].get_text(strip=True)

                            if text_sistema:
                                fila_dict["sistema de partits"] = [th.get_text(strip=True)
                                                                   .lower() for th in taula.find_all("th")[4:8:][i - 1]]

                                break

                        idx_govern = idx_govern_0 + 3
                        idx_eleccions = idx_eleccions_0 + 3

                    govern = dades_fila[idx_govern].get_text(strip=True)

                    # Extraiem les parelles (any, tipus d'elecció) de cada fila del format
                    # antic
                    anys_eleccions = re.findall(
                        r"(\d{4}(?:[–-]\d{2,4})?)\s+([a-zA-Z\s]+?)\s+election",
                        dades_fila[idx_eleccions].get_text(separator=" ", strip=True),
                        flags=re.IGNORECASE
                    )

                else:
                    fila_dict["sistema de partits"] = dades_fila[idx_sistema].get_text(
                        strip=True
                    )
                    govern = BeautifulSoup(dades_fila[idx_govern].decode_contents()
                                           .split("<hr")[0], "html.parser").get_text(strip=True)

                    # Extraiem les parelles (any, tipus d'elecció) de cada fila del format
                    # actual
                    anys_eleccions = re.findall(
                        r"(\d{4}(?:[–-]\d{2,4})?)\s*\(([^)]+)\)",
                        dades_fila[idx_eleccions].get_text(separator=" ", strip=True),
                        flags=re.IGNORECASE
                    )

                en_coalicio = bool(re.search(r"[,(]", govern))
                fila_dict["en coalició?"] = en_coalicio

                if not en_coalicio:
                    fila_dict["partit governant"] = govern
                else:
                    # En cas que el govern sigui una coalició de partits, només ens quedem
                    # amb el que té més representació
                    fila_dict["partit governant"] = re.split(
                        r"[,(]", govern, maxsplit=1
                    )[0].strip()

                for yr, tipus in anys_eleccions:
                    tipus_minuscules = tipus.lower()
                    if tipus_minuscules in dict_tipus_eleccions:
                        clau_dict = dict_tipus_eleccions[tipus_minuscules]
                        fila_dict[clau_dict] = yr

                for clau, _ in dict_partits_governants.items():
                    dict_partits_governants[clau].append(fila_dict[clau])
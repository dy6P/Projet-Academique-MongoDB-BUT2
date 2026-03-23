from SPARQLWrapper import SPARQLWrapper, JSON
import json

ENDPOINT = "https://query.wikidata.org/sparql"
sparql = SPARQLWrapper(ENDPOINT)
ACTEURS = ["Leonardo DiCaprio", "Brad Pitt", "Tom Hanks", "Meryl Streep"]

def recuperer_tout(nom_acteur):
    requete = f"""
    SELECT DISTINCT ?film ?filmLabel ?date ?genreLabel ?realisateur ?realisateurLabel ?realisateurNaissance ?membreCasting ?membreCastingLabel ?membreNaissance ?roleLabel
    WHERE {{
        ?acteur rdfs:label "{nom_acteur}"@en .
        {{ SELECT DISTINCT ?film WHERE {{
            ?acteur rdfs:label "{nom_acteur}"@en .
            ?film wdt:P161 ?acteur ;
                wdt:P166 [] .
        }} LIMIT 3 }}
        OPTIONAL {{ ?film wdt:P577 ?date }}
        OPTIONAL {{ ?film wdt:P136 ?genre }}
        OPTIONAL {{
            ?film wdt:P57 ?realisateur .
            OPTIONAL {{ ?realisateur wdt:P569 ?realisateurNaissance }}
        }}
        OPTIONAL {{
            ?film p:P161 ?declaration .
            ?declaration ps:P161 ?membreCasting .
            OPTIONAL {{ ?membreCasting wdt:P569 ?membreNaissance }}
            OPTIONAL {{ ?declaration pq:P453 ?role }}
            FILTER EXISTS {{ ?declaration pq:P453 ?role }}
        }}
        SERVICE wikibase:label {{ bd:serviceParam wikibase:language "fr,en". }}
    }}
    """
    sparql.setQuery(requete)
    sparql.setReturnFormat(JSON)
    return sparql.query().convert()["results"]["bindings"]


def construire_documents(lignes):
    films = {}
    for ligne in lignes:
        id_film = ligne["film"]["value"].split("/")[-1]
        if id_film not in films:
            films[id_film] = {
                "wikidata_id": id_film,
                "titre": ligne.get("filmLabel", {}).get("value", ""),
                "annee": ligne.get("date", {}).get("value", "")[:4],
                "genres": [],
                "realisateur": {},
                "casting": []
            }
            if ligne.get("realisateur"):
                films[id_film]["realisateur"] = {
                    "wikidata_id": ligne["realisateur"]["value"].split("/")[-1],
                    "nom": ligne.get("realisateurLabel", {}).get("value", ""),
                    "dateNaissance": ligne.get("realisateurNaissance", {}).get("value", "")[:10]
                }
        film = films[id_film]
        genre = ligne.get("genreLabel", {}).get("value")
        if genre and genre not in film["genres"]:
            film["genres"].append(genre)
        membre = ligne.get("membreCasting", {}).get("value")
        if membre:
            id_membre = membre.split("/")[-1]
            ids_casting = [m["wikidata_id"] for m in film["casting"]]
            if id_membre not in ids_casting:
                film["casting"].append({
                    "wikidata_id": id_membre,
                    "nom": ligne.get("membreCastingLabel", {}).get("value", ""),
                    "dateNaissance": ligne.get("membreNaissance", {}).get("value", "")[:10],
                    "role": ligne.get("roleLabel", {}).get("value", "")
                })
    return films


def main():
    tous_les_films = {}
    for acteur in ACTEURS:
        lignes = recuperer_tout(acteur)
        films = construire_documents(lignes)
        for id_film, doc in films.items():
            if id_film not in tous_les_films:
                tous_les_films[id_film] = doc
    with open("films.json", "w", encoding="utf-8") as f:
        json.dump(list(tous_les_films.values()), f, indent=True, ensure_ascii=False)


if __name__ == "__main__":
    main()
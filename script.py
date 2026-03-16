from SPARQLWrapper import SPARQLWrapper, JSON
import json

ENDPOINT = "https://query.wikidata.org/sparql"
sparql = SPARQLWrapper(ENDPOINT)

ACTORS = ["Leonardo DiCaprio", "Brad Pitt", "Tom Hanks"]

def actor_query(actor_name):
    return f"""
    SELECT ?film ?filmLabel ?date ?genreLabel ?director ?directorLabel
    WHERE {{
      ?actor rdfs:label "{actor_name}"@en .
      ?film wdt:P161 ?actor .

      OPTIONAL {{ ?film wdt:P577 ?date }}
      OPTIONAL {{ ?film wdt:P136 ?genre }}
      OPTIONAL {{ ?film wdt:P57 ?director }}

      SERVICE wikibase:label {{ bd:serviceParam wikibase:language "en". }}
    }}
    LIMIT 3
    """

def sparql_query(query):
    sparql.setQuery(query)
    sparql.setReturnFormat(JSON)
    return sparql.query().convert()

def main():
    films = []
    for actor in ACTORS:
        query = actor_query(actor)
        data = sparql_query(query)
        for film_data in data["results"]["bindings"]:
            film = {
                "wikidata_id": film_data["film"]["value"].split("/")[-1],
                "title": film_data.get("filmLabel", {}).get("value"),
                "year": film_data.get("date", {}).get("value", "")[:4],
                "genres": [
                    film_data.get("genreLabel", {}).get("value")
                ] if "genreLabel" in film_data else [],
                "director": {
                    "name": film_data.get("directorLabel", {}).get("value"),
                    "birthDate": "",
                    "wikidata_id": film_data["director"]["value"].split("/")[-1]
                    if "director" in film_data else ""
                },
                "cast": [
                    {
                        "name": actor,
                        "birthDate": "",
                        "role": "",
                        "wikidata_id": ""
                    }
                ]
            }
            films.append(film)
    with open("films.json", "w") as f:
        json.dump(films, f, indent=2)

if __name__ == "__main__":
    main()
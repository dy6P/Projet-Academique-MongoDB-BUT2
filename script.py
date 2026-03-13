import requests
import json

ENDPOINT = "https://query.wikidata.org/sparql"

ACTORS = [
    "Leonardo DiCaprio",
    "Brad Pitt",
    "Tom Hanks"
]

def sparql_query(query):
    response = requests.get(
        ENDPOINT,
        params = {"query": query, "format": "json"},
        headers = {"User-Agent": "AcademicProject/1.0"}
    )
    return response.json()

def actor_query(actor_name):
    return f"""
    SELECT ?id ?title ?date
           ?genre
           ?director
    WHERE {{
        ?actor rdfs:label "{actor_name}"@en .
        ?id wdt:P161 ?actor .
        ?id wdt:P166 ?award .
        OPTIONAL {{ ?id wdt:P577 ?date }}
        OPTIONAL {{ ?id wdt:P136 ?genre }}
        OPTIONAL {{ ?id wdt:P57 ?director }}
    }}
    LIMIT 3
    """


def main():
    films = []
    for actor in ACTORS:
        query = actor_query(actor)
        data = sparql_query(query)
        for film_data in data["results"]["bindings"]:
            film = {
                "wikidata_id": film_data["id"]["value"].split("/")[-1],
                "title": film_data.get("title", {}).get("value"),
                "year": film_data.get("date", {}).get("value", "")[:4],
                "genre": film_data.get("genre", {}).get("value"),
                "director": film_data.get("director", {}).get("value")
            }
            films.append(film)
    with open("films.json", "w") as f:
        json.dump(films, f, indent=True)

if __name__ == "__main__":
    main()
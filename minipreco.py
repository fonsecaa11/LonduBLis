import requests
import csv

def extrair_miniprecos_osm():
    """Extrai dados das lojas Minipreço do OSM e salva num ficheiro CSV."""

    overpass_url = "http://overpass-api.de/api/interpreter"
    overpass_query = """
    [out:json];
    area[name="Portugal"]->.a;
    area[name="Região Autónoma dos Açores"]->.b;
    area[name="Região Autónoma da Madeira"]->.c;
    (
      node["shop"="supermarket"]["name"="Minipreço"](area.a);
      way["shop"="supermarket"]["name"="Minipreço"](area.a);
      relation["shop"="supermarket"]["name"="Minipreço"](area.a);
      node["shop"="supermarket"]["name"="Minipreço"](area.b);
      way["shop"="supermarket"]["name"="Minipreço"](area.b);
      relation["shop"="supermarket"]["name"="Minipreço"](area.b);
      node["shop"="supermarket"]["name"="Minipreço"](area.c);
      way["shop"="supermarket"]["name"="Minipreço"](area.c);
      relation["shop"="supermarket"]["name"="Minipreço"](area.c);
    );
    out center;
    """

    response = requests.get(overpass_url, params={'data': overpass_query})
    data = response.json()

    miniprecos = []
    for element in data['elements']:
        if 'center' in element:
            lat = element['center']['lat']
            lon = element['center']['lon']
        else:
            lat = element['lat']
            lon = element['lon']

        nome = element['tags'].get('name', 'N/A')
        morada = element['tags'].get('addr:street', 'N/A') + ', ' + element['tags'].get('addr:housenumber', 'N/A') + ', ' + element['tags'].get('addr:city', 'N/A')

        miniprecos.append([nome, lat, lon, morada])

    with open('miniprecos.csv', 'w', newline='', encoding='utf-8-sig') as csvfile:
        writer = csv.writer(csvfile, delimiter=';')
        writer.writerow(['Nome', 'Latitude', 'Longitude', 'Morada'])  # Escreve o cabeçalho
        writer.writerows(miniprecos)

    print("Dados extraídos e salvos em miniprecos.csv")

if __name__ == "__main__":
    extrair_miniprecos_osm()
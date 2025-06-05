import time
import requests
import csv
from bs4 import BeautifulSoup

# URL principal do site
url_base = "https://www.apcc.pt"
url_principal = f"{url_base}/centros/"

# Nome do ficheiro CSV
csv_file = "centros_comerciais.csv"

# Criar e escrever o cabeçalho do CSV
with open(csv_file, "w", newline="", encoding="utf-8-sig") as f:
    writer = csv.writer(f, delimiter=";")
    writer.writerow(["Nome Centro", "Contacto", "Promotor", "Proprietário", "Gestor", "Área Bruta Locável(ABL)", "Nº Lojas", "Morada", "Código Postal", "Localidade", "Telefone", "Email", "Website"])

# Obter a página inicial
response = requests.get(url_principal)
soup = BeautifulSoup(response.text, "html.parser")

# Encontrar os centros comerciais
lojas = soup.select("article.c-centros__item")

for loja in lojas:
    try:
        # Obter link da loja
        link_loja = loja.get("data-href")
        if not link_loja:
            continue
        
        url_loja = url_base + link_loja
        response_loja = requests.get(url_loja)
        soup_loja = BeautifulSoup(response_loja.text, "html.parser")

        # Nome do centro comercial
        nome_centro = soup_loja.find("h1").get_text(strip=True)

        # Encontrar a tabela de informações
        tabela = soup_loja.select_one("table.c-centos__info_tbl")
        info = {
            "Nome Centro": nome_centro,
            "Contacto": "",
            "Promotor": "",
            "Proprietário": "",
            "Gestor": "",
            "Área Bruta Locável(ABL)": "",
            "Nº Lojas": "",
            "Morada": "",
            "Código Postal": "",
            "Localidade": "",
            "Telefone": "",
            "Email": "",
            "Website": ""
        }

        if tabela:
            for linha in tabela.find_all("tr"):
                colunas = linha.find_all("td")
                if len(colunas) == 2:
                    chave = colunas[0].get_text(strip=True).replace(":", "")
                    valor = colunas[1].get_text(strip=True)
                    info[chave] = valor
        
        # Guardar no CSV
        with open(csv_file, "a", newline="", encoding="utf-8-sig") as f:
            writer = csv.writer(f, delimiter=";")
            writer.writerow([
                info["Nome Centro"], info["Contacto"], info["Promotor"], info["Proprietário"],
                info["Gestor"], info["Área Bruta Locável(ABL)"], info["Nº Lojas"], info["Morada"],
                info["Código Postal"], info["Localidade"], info["Telefone"], info["Email"], info["Website"]
            ])

        print(f"✅ Extraído: {nome_centro}")

    except Exception as e:
        print(f"❌ Erro ao processar um centro comercial: {e}")

print(f"✅ Scraping concluído! Os dados foram guardados em '{csv_file}'.")

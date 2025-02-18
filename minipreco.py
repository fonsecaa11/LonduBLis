from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pandas as pd
import time

# Configuração do WebDriver
options = webdriver.ChromeOptions()
#options.add_argument("--headless")   Executar sem abrir o browser (remover se quiseres ver)
driver = webdriver.Chrome(options=options)

# Lista de localidades a partir do ficheiro
with open("data/txt/localidades.txt", "r", encoding="utf-8") as file:
    localidades = [line.strip() for line in file.readlines()]

# Lista para armazenar os dados
dados_lojas = []

for localidade in localidades:
    print(f"Processando {localidade}...")
    url_tiendeo = f"https://www.tiendeo.pt/Lojas/{localidade}/minipreco"
    driver.get(url_tiendeo)
    time.sleep(3)  # Espera para carregar

    # Encontrar todas as lojas
    try:
        lojas = WebDriverWait(driver, 5).until(
            EC.presence_of_all_elements_located((By.CSS_SELECTOR, '[data-testid="store_item"] a'))
        )
        links_lojas = [loja.get_attribute("href") for loja in lojas]
    except:
        print(f"Nenhuma loja encontrada em {localidade}.")
        continue

    for loja_url in links_lojas:
        driver.get(loja_url)
        time.sleep(2)

        # Obter o link do Google Maps
        try:
            mapa_link = WebDriverWait(driver, 5).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, '[data-testid="store_info_details_address"]'))
            ).get_attribute("href")
        except:
            print(f"Sem link de mapa para {loja_url}.")
            continue

        # Obter coordenadas a partir do link
        try:
            driver.get(mapa_link)
            time.sleep(3)

            # Nome e morada
            nome_loja = WebDriverWait(driver, 5).until(
                EC.presence_of_element_located((By.CLASS_NAME, "DUwDvf"))
            ).text

            endereco_loja = driver.find_element(By.CLASS_NAME, "Io6YTe").text

            # Extrair coordenadas do URL do Google Maps
            lat_long = mapa_link.split("/@")[1].split("z")[0]
            latitude, longitude = lat_long.split(",")[:2]

            # Guardar os dados
            dados_lojas.append([nome_loja, endereco_loja, latitude, longitude])
            print(f"✔ Dados extraídos: nome{nome_loja}, {endereco_loja}, {latitude}, {longitude}")

        except Exception as e:
            print(f"Erro ao obter dados do Google Maps: {e}")

# Criar DataFrame e guardar CSV
df = pd.DataFrame(dados_lojas, columns=["Nome", "Endereço", "Latitude", "Longitude"])
df.to_csv("minipreco_lojas.csv", index=False, encoding="utf-8-sig", sep=";", quoting=1)

print("✅ Processo concluído! Dados guardados em minipreco_lojas.csv")
driver.quit()

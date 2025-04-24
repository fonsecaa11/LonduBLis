from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import time
import re
import csv
import os

# Configuração do Selenium
driver = webdriver.Chrome()
driver.get("https://www.lidl.pt")
driver.maximize_window()
time.sleep(5)

# Aceitar cookies
try:
    botao_cookies = driver.find_element(By.ID, 'onetrust-accept-btn-handler')
    botao_cookies.click()
    time.sleep(5)
except Exception:
    print("Nenhum botão de cookies encontrado.")

# Clicar no botão para abrir a modal de seleção de lojas
try:
    select_store_button = driver.find_element(By.CSS_SELECTOR, '[data-ga-action="Storesearch"] a')
    select_store_button.click()
    time.sleep(3)
except:
    print("Botão de seleção de loja não encontrado!")
    driver.quit()
    exit()

# Ler localidades do ficheiro
with open("data/txt/localidades.txt", "r", encoding="utf-8") as file:
    localidades = [line.strip() for line in file.readlines()]

dados_lojas = []

# Nome do ficheiro CSV
csv_filename = "lojas_lidl.csv"

# Verificar se o ficheiro já existe para evitar duplicação de cabeçalhos
file_exists = os.path.isfile(csv_filename)

with open(csv_filename, "a", newline="", encoding="utf-8") as file:
    writer = csv.writer(file, delimiter=";")

    # Se o ficheiro não existir, escreve os cabeçalhos
    if not file_exists:
        writer.writerow(["Nome", "Endereço", "Código Postal", "Localidade"])

    for localidade in localidades:
        # Inserir a localidade no campo de pesquisa
        search_input = driver.find_element(By.CSS_SELECTOR, "input.nuc-m-map-search-menu__search-field-input")
        search_input.clear()
        search_input.send_keys(localidade)
        time.sleep(2)
        search_input.send_keys(Keys.RETURN)
        time.sleep(3)

        # Obter todas as lojas da pesquisa
        lojas = driver.find_elements(By.CLASS_NAME, "nuc-m-storesearch-result__button")

        for loja in lojas:
            loja.click()
            time.sleep(3)

            detalhe_lojas = driver.find_elements(By.CLASS_NAME, "nuc-m-storesearch-info__detail-page-link")

            for detalhe_loja in detalhe_lojas:
                detalhe_loja.click()
                time.sleep(3)

                # Extrair o nome da loja corretamente
                try:
                    nome_loja_element = driver.find_element(By.CLASS_NAME, "lirt-o-store-detail-card__headline")
                    nome_loja = nome_loja_element.text.strip()

                    # Usar regex para capturar apenas o nome antes da vírgula
                    match = re.match(r"^(Lidl\s[\w\s]+),", nome_loja)
                    if match:
                        nome_loja = match.group(1)
                except:
                    nome_loja = "Desconhecido"

                # Extrair endereço
                try:
                    endereco_elements = driver.find_elements(By.CLASS_NAME, "lirt-o-store-detail-card__address")
                    rua = endereco_elements[0].text.strip() if len(endereco_elements) > 0 else "Desconhecido"
                    cidade_codigo = endereco_elements[1].text.strip() if len(endereco_elements) > 1 else "Desconhecido"

                    # Separar código postal e localidade
                    match = re.match(r"(\d{4}-\d{3})\s(.+)", cidade_codigo)
                    if match:
                        codigo_postal = match.group(1)
                        localidade_extraida = match.group(2)
                    else:
                        codigo_postal = "Desconhecido"
                        localidade_extraida = cidade_codigo
                except:
                    rua, codigo_postal, localidade_extraida = "Desconhecido", "Desconhecido", "Desconhecido"

                # Guardar os dados
                writer.writerow([nome_loja, rua, codigo_postal, localidade_extraida])
                print(f"✔ Dados extraídos: {nome_loja}; {rua}; {codigo_postal}; {localidade_extraida}")

                # Voltar à lista de lojas
                driver.back()
                time.sleep(2)

            back_button = driver.find_element(By.CLASS_NAME, "nuc-m-map-search-menu__info-back")
            back_button.click()
            time.sleep(3)
        
        search_back_button = driver.find_element(By.CLASS_NAME, "nuc-m-map-search-menu__results-close-button")
        search_back_button.click()
        time.sleep(1)

# Fechar o navegador
driver.quit()

print(f"📂 Dados adicionados a {csv_filename} com sucesso!")
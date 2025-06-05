import re
import pandas as pd
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from urllib.parse import quote

# Caminho para o ficheiro de localidades
distritos_path = "C:\\Users\\gonca\\Desktop\\Projeto\\data\\txt\\distritos.txt"

# Função para aceitar cookies
def aceitar_cookies(driver):
    try:
        botao_cookies = driver.find_element(By.CSS_SELECTOR, '#third-btn')
        botao_cookies.click()
        time.sleep(2)
    except:
        pass

# Fazer scroll até o elemento da lista de lojas
def scroll_ate_lista(driver, css_selector):
    elemento = WebDriverWait(driver, 15).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, css_selector))
    )
    driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", elemento)


# Clicar no botão "Ver todos", se existir
def carregar_mais_lojas(driver):
    scrollable_div = driver.find_element(By.CSS_SELECTOR, 'ul.panelLateralResultadosLista')
    try:
        driver.execute_script("arguments[0].scrollTo(0, arguments[0].scrollHeight);", scrollable_div)
        botao_mais_lojas = driver.find_element(By.XPATH, "//button[contains(text(), 'Ver todos')]")
        botao_mais_lojas.click()
    except:
        pass


driver = webdriver.Chrome()
driver.maximize_window()

dados = []

with open(distritos_path, "r", encoding="ISO-8859-1") as file:
    distritos = [linha.strip() for linha in file.readlines() if linha.strip()]

for distrito in distritos:
    try:
        url = f"https://www.mercadona.pt/pt/supermercados-portugal?s={quote(distrito)}"
        driver.get(url)

        aceitar_cookies(driver)
        scroll_ate_lista(driver, '.panelLateralResultadosLista')
        carregar_mais_lojas(driver)

        lojas_links = driver.find_elements(By.CSS_SELECTOR, 'li.panelLateralResultadosElemento')
        time.sleep(2)

        for i in range(len(elementos_loja)):
            # Refazer a lista de elementos após cada click
            elementos_loja = driver.find_elements(By.CSS_SELECTOR, "li.panelLateralResultadosElemento")

            if not elementos_loja[i].find_elements(By.CSS_SELECTOR, ".supermercadoPais.pt"):
                continue

            elementos_loja[i].click()
            try:
                nome = driver.find_element(By.CSS_SELECTOR, '.panelDetalleTitulo').text.strip()
            except:
                nome = None

            try:
                morada = driver.find_element(By.CSS_SELECTOR, '.panelDetalleCalle').text.strip()
            except:
                morada = None
            
            try:
                cidade_raw = driver.find_element(By.CSS_SELECTOR, ".panelDetalleCiudad").text.strip()
                codigo_postal = localidade = ""

                match = re.match(r"(\d{4}-\d{3})\s+([^\(]+)", cidade_raw)
                if match:
                    codigo_postal = match.group(1).strip()
                    localidade = match.group(2).strip()
            except:
                codigo_postal, localidade = None, None

            try:
                link_mapa = driver.find_element(By.CSS_SELECTOR, '.green-border-transparent-button.supermercadoComoLlegar.otro').get_attribute('href')
                latitude, longitude = None, None

                if link_mapa:
                    coordenadas = re.search(r"dir//([-.\d]+),([-.\d]+)", link_mapa)
                    if coordenadas:
                        latitude, longitude = coordenadas.groups()
            except:
                latitude, longitude = None, None

            dados.append({
                "Nome": nome,
                "Morada": morada,
                "Codigo Postal": codigo_postal,
                "Localidade": localidade,
                "Latitude": latitude,
                "Longitude": longitude,
                "Distrito": distrito
            })

    except Exception as e:
        print(f"Erro ao processar loja no link {distrito}: {e}")

    # Guardar os dados no CSV
    df = pd.DataFrame(dados)
    df.to_csv("Mercadona.csv", index=False, sep=";", encoding="utf-8-sig")

driver.quit()
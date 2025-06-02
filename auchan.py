from selenium import webdriver
from selenium.webdriver.common.by import By
import time
import pandas as pd

# Configurar Selenium
driver = webdriver.Chrome()
driver.get('https://www.auchan.pt/pt/lojas')
driver.maximize_window()

try:
    botao_cookies = driver.find_element(By.XPATH, '//button[contains(text(), "Aceitar todos os cookies")]')
    botao_cookies.click()
    time.sleep(2)
except:
    pass

# Localizar todas as lojas pela classe 'list-item'
lojas_elements = driver.find_elements(By.CSS_SELECTOR, 'li.list-item')

# Ignora dados que contem a palavra Gasolineira
lojas_links = []
for loja in lojas_elements:
    link_element = loja.find_element(By.TAG_NAME, 'a')
    loja_titulo = link_element.get_attribute('title').lower()
    if 'gasolineira' not in loja_titulo:
        link = link_element.get_attribute('href')
        lojas_links.append(link)


# Recolha de dados de cada loja
dados = []
for loja_link in lojas_links:
    driver.get(loja_link)
    time.sleep(3)
    
    try:
        # Nome da loja
        nome = driver.find_element(By.CSS_SELECTOR, '.store-name').text.strip()
        
        # Endereço e localização
        endereco_raw = driver.find_element(By.XPATH, "//script[contains(text(),'streetAddress')]").get_attribute("innerHTML")
        endereco_completo = endereco_raw.split('"streetAddress":"')[1].split('","')[0]
        endereco = endereco_completo.split(',')[0]
        codigo_postal = endereco_raw.split('"postalCode":"')[1].split('","')[0]
        address_locality = endereco_raw.split('"addressLocality":"')[1].split('","')[0]
        
        # Coordenadas
        google_maps_link = driver.find_element(By.CSS_SELECTOR, '.auc-storeinfo--directions').get_attribute('href')
        lat, lon = google_maps_link.split('daddr=')[1].split(',')

        dados.append({
            "Nome": nome,
            "Morada": endereco,
            "Codigo Postal": codigo_postal,
            "Localidade": address_locality,
            "Latitude": lat,
            "Longitude": lon
        })

        print(f"{nome} add to csv")

    except Exception as e:
        print(f"Erro ao processar loja em {loja_link}: {e}")

df = pd.DataFrame(dados)
df.to_csv("Auchan.csv", index=False, sep=";", encoding="utf-8-sig")

driver.quit()


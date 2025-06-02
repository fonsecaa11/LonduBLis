from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import re
import pandas as pd
import time

# Configuração do Selenium
driver = webdriver.Chrome()
driver.maximize_window()
driver.get('https://www.aldi.pt/tools/lojas-e-horarios-de-funcionamento.html/l')

time.sleep(5)

dados = []

# Capturar todas as localidades
try:
    WebDriverWait(driver, 15).until(EC.presence_of_element_located((By.CSS_SELECTOR, 'li a.ubsf_sitemap-group-link')))
    localidades_links = driver.find_elements(By.CSS_SELECTOR, 'li a.ubsf_sitemap-group-link')
    localidades_urls = [localidade.get_attribute('href') for localidade in localidades_links]
except Exception as e:
    print(f"Erro ao carregar localidades: {e}")
    driver.quit()
    exit()

# Processar cada localidade
for localidade_url in localidades_urls:
    try:
        driver.get(localidade_url)
        WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.CSS_SELECTOR, 'a.ubsf_sitemap-location-link')))
        lojas_links = driver.find_elements(By.CSS_SELECTOR, 'a.ubsf_sitemap-location-link')
        lojas_urls = [loja.get_attribute('href') for loja in lojas_links]
    except Exception as e:
        print(f"Erro ao carregar lojas para {localidade_url}: {e}")
        continue

    # Processar cada loja
    for loja_url in lojas_urls:
        try:
            driver.get(loja_url)
            WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.CSS_SELECTOR, 'div.ubsf_card')))

            nome = driver.find_element(By.CSS_SELECTOR, '.ubsf_details-details-title').text.strip()
            enderecos = [e.text for e in driver.find_elements(By.CSS_SELECTOR, '.ubsf_details-address')]

            if enderecos:
                endereco_texto = " ".join(enderecos)
                match = re.search(r'(\d{4}-\d{3}\s[\w\s\-]+)', endereco_texto)
                if match:
                    endereco = endereco_texto[:match.start()].strip(", ")
                    codigo_postal_full = match.group(1)
                    codigo_postal_partes = re.match(r'(\d{4}-\d{3})\s(.+)', codigo_postal_full)
                    if codigo_postal_partes:
                        codigo_postal = codigo_postal_partes.group(1)
                        localidade = codigo_postal_partes.group(2)
                    else:
                        codigo_postal = None
                        localidade = None
                else:
                    endereco = None
            else:
                print("Endereço não encontrado.")

            try:
                map_url_element = driver.find_element(By.CSS_SELECTOR, 'div[data-testid="location-page-static-map"]')
                map_url_style = map_url_element.get_attribute("style")
                map_url_match = re.search(r'url\("([^"]+)"\)', map_url_style)

                if map_url_match:
                    map_url = map_url_match.group(1)
                    lat_long_match = re.search(r'/(-?\d+\.\d+),(-?\d+\.\d+),', map_url)
                    if lat_long_match:
                        longitude = lat_long_match.group(1)
                        latitude = lat_long_match.group(2)
                
            except:
                longitude, latitude = None, None

            dados.append({
                    "Nome": nome,
                    "Endereço": endereco,
                    "Código Postal": codigo_postal,
                    "Localidade": localidade,
                    "Latitude": latitude,
                    "Longitude": longitude
                })
            print(f"Loja {nome} guardada com sucesso.")

        except Exception as e:
            print(f"Erro ao processar loja em {loja_url}: {e}")

df = pd.DataFrame(dados)
df.to_csv("Aldi.csv", index=False, sep=";", encoding="utf-8-sig")

# Fechar o navegador
driver.quit()

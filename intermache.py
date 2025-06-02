from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import pandas as pd


# Configuração do Selenium
driver = webdriver.Chrome()
driver.maximize_window()
driver.get('https://www.intermarche.pt/lojas/')

time.sleep(5)

dados = []

# Aceitar cookies
try:
    botao_cookies = driver.find_element(By.ID, 'CybotCookiebotDialogBodyLevelButtonLevelOptinAllowAll')
    botao_cookies.click()
    time.sleep(2)
except:
    pass

# Aguardar até que os links das lojas estejam disponíveis
try:
    WebDriverWait(driver, 15).until(EC.presence_of_element_located((By.CSS_SELECTOR, '.district.accordion-content')))
    lojas_links = driver.find_elements(By.CSS_SELECTOR, '.district.accordion-content a')

    # Extrair todos os URLs
    urls = [loja.get_attribute('href') for loja in lojas_links]
except Exception as e:
    print(f"Erro ao carregar links das lojas: {e}")
    driver.quit()
    exit()

# Abrir cada link e processar os dados
for url in urls:
    try:
        driver.get(url)  # Abrir o link da loja
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, 'div#pos-data')))

        # Extrair informações da loja
        try:
            nome = driver.find_element(By.CSS_SELECTOR, 'h1[itemprop="name"]').text
        except:
            nome = None

        try:
            endereco = driver.find_element(By.CSS_SELECTOR, 'span[itemprop="streetAddress"]').text
        except:
            endereco = None

        try:
            codigo_postal_full = driver.find_element(By.CSS_SELECTOR, 'span[itemprop="postalCode"]').text
            codigo_postal, localidade = codigo_postal_full.split(' ', 1)
        except:
            codigo_postal, localidade = None, None
        
        try:
            latitude = driver.find_element(By.CSS_SELECTOR, 'div#pos-map').get_attribute('data-latitude')
            longitude = driver.find_element(By.CSS_SELECTOR, 'div#pos-map').get_attribute('data-longitude')
        except:
            latitude, longitude = None, None

        dados.append({
            "Nome": nome,
            "Morada": endereco,
            "Codigo Postal": codigo_postal,
            "Localidade": localidade,
            "Latitude": latitude,
            "Longitude": longitude
        })
        
        print(f"Loja {nome} inserida com sucesso.")
    except Exception as e:
        telefone = None
        print(f"Erro ao processar loja no link {url}: {e}")

df = pd.DataFrame(dados)
df.to_csv("Intermache.csv", index=False, sep=";", encoding="utf-8-sig")

driver.quit()

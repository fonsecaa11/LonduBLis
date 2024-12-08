from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import mysql.connector
import time

# Configurar Selenium
driver = webdriver.Chrome()
driver.get('https://www.auchan.pt/pt/lojas')
driver.maximize_window()

# Localizar todas as lojas pela classe 'list-item'
lojas_elements = driver.find_elements(By.CSS_SELECTOR, 'li.list-item')

lojas_links = []
for loja in lojas_elements:
    link_element = loja.find_element(By.TAG_NAME, 'a')
    loja_titulo = link_element.get_attribute('title').lower()
    if 'gasolineira' not in loja_titulo:
        link = link_element.get_attribute('href')
        lojas_links.append(link)
    else:
        print(f"Ignorando loja: {loja_titulo}") 

# Conectar á base de dados
conn = mysql.connector.connect(
    host="localhost", 
    user="root", 
    password="1234", 
    database="projeto"
)
cursor = conn.cursor()

# Loop para aceder a cada loja e extrair dados
for loja_link in lojas_links:
    driver.get(loja_link)
    time.sleep(3) 
    
    try:
        # Capturar o nome da loja
        nome = driver.find_element(By.CSS_SELECTOR, '.store-name').text.strip()
        
        # Capturar o endereço e código postal
        endereco_raw = driver.find_element(By.XPATH, "//script[contains(text(),'streetAddress')]").get_attribute("innerHTML")
        endereco_completo = endereco_raw.split('"streetAddress":"')[1].split('","')[0]
        endereco = endereco_completo.split(',')[0]
        codigo_postal = endereco_raw.split('"postalCode":"')[1].split('","')[0]
        address_locality = endereco_raw.split('"addressLocality":"')[1].split('","')[0]
        codigo_postal_completo = f"{codigo_postal} {address_locality}"
        
        # Capturar latitude e longitude
        google_maps_link = driver.find_element(By.CSS_SELECTOR, '.auc-storeinfo--directions').get_attribute('href')
        lat, lon = google_maps_link.split('daddr=')[1].split(',')

        # Inserir dados na base de dados
        cursor.execute("""
            INSERT INTO lojas_auchan (nome, endereco, codigo_postal, latitude, longitude)
            VALUES (%s, %s, %s, %s, %s)
        """, (nome, endereco, codigo_postal_completo, lat, lon))
        conn.commit()
        print(f"Loja {nome} inserida com sucesso.")

    except Exception as e:
        print(f"Erro ao processar loja em {loja_link}: {e}")

# Fechar conexão e driver
driver.quit()
cursor.close()
conn.close()

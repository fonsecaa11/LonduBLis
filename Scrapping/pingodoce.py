from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import mysql.connector
import re

# Configuração do Selenium
driver = webdriver.Chrome()
driver.get('https://www.pingodoce.pt/lojas/?tipo-loja=lojas')
driver.maximize_window()

# Aguardar até que os links das lojas estejam disponíveis
try:
    WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.CSS_SELECTOR, 'a.js-map-sidebar-card')))
    lojas_links = driver.find_elements(By.CSS_SELECTOR, 'a.js-map-sidebar-card')

    # Extrair todos os URLs
    urls = [loja.get_attribute('href') for loja in lojas_links]
except Exception as e:
    print(f"Erro ao carregar links das lojas: {e}")
    driver.quit()
    exit()

# Conectar á base de dados MySQL
conn = mysql.connector.connect(
    host="localhost", 
    user="root", 
    password="1234", 
    database="projeto"
)
cursor = conn.cursor()

# Inicializar o WebDriver e processar os dados
for url in urls:
    try:
        driver.get(url)  # Abrir o link da loja
        WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.CSS_SELECTOR, 'div.store-information')))

        nome = driver.find_element(By.CSS_SELECTOR, '.title').text.strip()

        endereco = driver.find_elements(By.CSS_SELECTOR, '.store-information-details .address-container p')
        endereco_completo = ' '.join([e.text for e in endereco]) if endereco else "Endereço não disponível"

        # Validar se há pelo menos um elemento na lista antes de acessar o último item
        codigo_postal = endereco[-1].text if endereco and len(endereco) > 0 else "Código postal não disponível"

        telemovel_element = driver.find_elements(By.CSS_SELECTOR, '.store-information-details .contents span')
        telemovel = telemovel_element[0].text if telemovel_element else "Telemóvel não disponível"

        iframe_src = driver.find_element(By.CSS_SELECTOR, 'iframe[title="Mapa da localização"]').get_attribute('src')
        latitude, longitude = re.search(r"center=([\d.-]+),([\d.-]+)", iframe_src).groups()

        # Inserir dados na base de dados
        cursor.execute("""
            INSERT INTO lojas_pingodoce (nome, endereco, codigo_postal, telemovel, latitude, longitude)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (nome, endereco_completo, codigo_postal, telemovel, latitude, longitude))
        conn.commit()
        print(f"Loja {nome} inserida com sucesso.")

    except Exception as e:
        print(f"Erro ao processar loja em {url}: {e}")

# Fechar conexões
cursor.close()
conn.close()
driver.quit()
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import mysql.connector

# Configuração do Selenium
driver = webdriver.Chrome()
driver.get('https://www.intermarche.pt/lojas/')
driver.maximize_window()

# Aceitar cookies
try:
    WebDriverWait(driver, 5).until(
        EC.element_to_be_clickable((By.CSS_SELECTOR, '#CybotCookiebotDialogBodyLevelButtonLevelOptinAllowAll'))
    ).click()
    print("Cookies aceites.")
except Exception as e:
    print(f"Erro ao aceitar cookies: {e}")

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

# Conectar á base de dados MySQL
conn = mysql.connector.connect(
    host="localhost", 
    user="root", 
    password="1234", 
    database="projeto"
)
cursor = conn.cursor()

# Abrir cada link e processar os dados
for url in urls:
    try:
        driver.get(url)  # Abrir o link da loja
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, 'div#pos-data')))

        # Extrair informações da loja
        nome = driver.find_element(By.CSS_SELECTOR, 'h1[itemprop="name"]').text
        endereco = driver.find_element(By.CSS_SELECTOR, 'span[itemprop="streetAddress"]').text
        codigo_postal = driver.find_element(By.CSS_SELECTOR, 'span[itemprop="postalCode"]').text
        telefone_elementos = driver.find_elements(By.CSS_SELECTOR, 'a[itemprop="telephone"]')
        telefone = telefone_elementos[0].text if telefone_elementos else None
        email = driver.find_element(By.CSS_SELECTOR, 'a[itemprop="email"]').text
        latitude = driver.find_element(By.CSS_SELECTOR, 'div#pos-map').get_attribute('data-latitude')
        longitude = driver.find_element(By.CSS_SELECTOR, 'div#pos-map').get_attribute('data-longitude')

        # Inserir dados no banco de dados
        cursor.execute("""
            INSERT INTO lojas_intermache (nome, endereco, codigo_postal, telefone, email, latitude, longitude)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """, (nome, endereco, codigo_postal, telefone, email, latitude, longitude))
        conn.commit()
        print(f"Loja {nome} inserida com sucesso.")
    except Exception as e:
        telefone = None
        print(f"Erro ao processar loja no link {url}: {e}")

# Fechar conexões
cursor.close()
conn.close()
driver.quit()

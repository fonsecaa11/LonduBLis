from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import mysql.connector
import re


# Função para aceitar cookies
def aceitar_cookies(driver):
    try:
        WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, 'button[data-testid="uc-accept-all-button"]'))
        )
        
        botao_cookies = driver.find_element(By.CSS_SELECTOR, 'button[data-testid="uc-accept-all-button"]')
        print(f"Botão encontrado: {botao_cookies.text}")  # Verificar se foi encontrado
        
        botao_cookies.click()
        print("Cookies aceites.")
    except Exception as e:
        print(f"Erro ao aceitar cookies: {e}")



# Configuração do Selenium
driver = webdriver.Chrome()
driver.get('https://www.aldi.pt/tools/lojas-e-horarios-de-funcionamento.html/l')
driver.maximize_window()


# Conectar à base de dados MySQL
conn = mysql.connector.connect(
    host="localhost", 
    user="root", 
    password="1234", 
    database="projeto"
)
cursor = conn.cursor()

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

            # Obter nome da loja
            nome = driver.find_element(By.CSS_SELECTOR, '.ubsf_details-details-title').text.strip()


            # Obter endereço da loja
            enderecos = [e.text for e in driver.find_elements(By.CSS_SELECTOR, '.ubsf_details-address')]

            if enderecos:
                endereco_texto = " ".join(enderecos)  # Junta os textos em uma única string
                match = re.search(r'(\d{4}-\d{3}\s[\w\s\-]+)', endereco_texto)  # Procura pelo padrão "1234-567 Localidade"

                if match:
                    endereco = endereco_texto[:match.start()].strip(", ")
                    codigo_postal = match.group(1)
                else:
                    print("Código postal e localidade não encontrados no endereço.")
            else:
                print("Endereço não encontrado.")

            # Obter coordenadas da loja
            map_url_element = driver.find_element(By.CSS_SELECTOR, 'div[data-testid="location-page-static-map"]')
            map_url_style = map_url_element.get_attribute("style")
            
            map_url_match = re.search(r'url\("([^"]+)"\)', map_url_style)
            
            if map_url_match:
                map_url = map_url_match.group(1)

                lat_long_match = re.search(r'/(-?\d+\.\d+),(-?\d+\.\d+),', map_url)
                if lat_long_match:
                    longitude = lat_long_match.group(1)
                    latitude = lat_long_match.group(2)
                else:
                    print("Latitude e longitude não encontradas na URL.")
            else:
                print("URL do mapa não encontrada.")

            # Inserir dados na base de dados
            cursor.execute("""
                INSERT INTO lojas_aldi (nome, endereco, codigo_postal, latitude, longitude)
                VALUES (%s, %s, %s, %s, %s)
            """, (nome, endereco, codigo_postal, latitude, longitude))
            conn.commit()

            print(f"Loja {nome} inserida com sucesso.")

        except Exception as e:
            print(f"Erro ao processar loja em {loja_url}: {e}")

# Fechar conexões
cursor.close()
conn.close()
driver.quit()

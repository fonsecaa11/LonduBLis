import re
import mysql.connector
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from urllib.parse import quote

# Caminho para o GeckoDriver
geckodriver_path = "C:\\Users\\gonca\\OneDrive\\Ambiente de Trabalho\\Projeto\\geckodriver.exe"

# Caminho para o ficheiro de localidades
localidades_path = "C:\\Users\\gonca\\OneDrive\\Ambiente de Trabalho\\Projeto\\localidades.txt"

# Configura o GeckoDriver
service = Service(executable_path=geckodriver_path)

# Conectar ao Banco de Dados
def conectar_banco():
    return mysql.connector.connect(
        host="localhost",  
        user="root",  
        password="1234",  
        database="projeto" 
    )

# Inserir loja no banco de dados
def inserir_loja(conn, codigo_postal, nome, endereco, telemovel):
    cursor = conn.cursor()
    query = """
        INSERT INTO lojas_pingodoce (codigo_postal_id, nome, endereco, telemovel)
        VALUES (%s, %s, %s, %s)
    """
    cursor.execute(query, (codigo_postal, nome, endereco, telemovel))
    conn.commit()
    cursor.close()

# Inicializar o WebDriver e processar os dados
def processar_localidades():
    driver = webdriver.Firefox(service=service)
    conn = conectar_banco()

    try:
        # Ler o ficheiro de localidades
        with open(localidades_path, "r", encoding="ISO-8859-1") as file:
            localidades = [linha.strip() for linha in file.readlines() if linha.strip()]

        for localidade in localidades:
            try:
                # Codificar o nome da localidade para URL
                url = f"https://www.pingodoce.pt/lojas/?l={quote(localidade)}"
                driver.get(url)

                # Verificar rapidamente se existem lojas na página
                lojas_links = WebDriverWait(driver, 3).until(
                    EC.presence_of_all_elements_located((By.CSS_SELECTOR, 'a.js-map-sidebar-card'))
                )

                # Processar cada loja
                for i in range(len(lojas_links)):
                    lojas_links = WebDriverWait(driver, 3).until(
                        EC.presence_of_all_elements_located((By.CSS_SELECTOR, 'a.js-map-sidebar-card'))
                    )

                    loja_link = lojas_links[i]
                    loja_url = loja_link.get_attribute('href')
                    driver.get(loja_url)

                    # Capturar os dados da loja
                    nome_loja = WebDriverWait(driver, 10).until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, '.title'))
                    ).text.strip()

                    endereco = driver.find_elements(By.CSS_SELECTOR, '.store-information-details .address-container p')
                    endereco_completo = ' '.join([e.text for e in endereco])

                    endereco_sem_cp = re.sub(r'\d{4}-\d{3}', '', endereco_completo).strip()
                    codigo_postal = endereco[-1].text
                    telemovel = driver.find_element(By.CSS_SELECTOR, '.store-information-details .contents span').text

                    # Inserir no banco de dados
                    inserir_loja(conn, codigo_postal, nome_loja, endereco_sem_cp, telemovel)

                    # Voltar para a lista de lojas
                    driver.back()

            except Exception as e:
                # Logar erros e continuar para o próximo concelho
                with open("erros.log", "a", encoding="utf-8") as log_file:
                    log_file.write(f"Erro ao processar o concelho '{localidade}': {str(e)}\n")
                continue

    finally:
        conn.close()
        driver.quit()

# Executar o script
if __name__ == "__main__":
    processar_localidades()

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
distritos_path = "C:\\Users\\gonca\\OneDrive\\Ambiente de Trabalho\\Projeto\\data\\txt\\distritos.txt"

# Configura o GeckoDriver
service = Service(geckodriver_path)

# Conectar á Base de Dados
def conectar_bd():
    return mysql.connector.connect(
        host="localhost",  
        user="root",  
        password="1234",  
        database="projeto" 
    )

# Inserir loja na base de dados
def inserir_loja(conn, nome, endereco, codigo_postal, telefone, latitude, longitude):
    cursor = conn.cursor()
    query = """
        INSERT INTO lojas_mercadona (nome, endereco, codigo_postal, telefone, latitude, longitude)
        VALUES (%s, %s, %s, %s, %s, %s)
    """
    cursor.execute(query, (nome, endereco, codigo_postal, telefone, latitude, longitude))
    conn.commit()
    cursor.close()


# Função para aceitar cookies
def aceitar_cookies(driver):
    try:
        # Aguarda até o botão de cookies estar visível e clica
        botao_cookies = WebDriverWait(driver, 5).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, '#third-btn'))  # Ajustar o seletor conforme necessário
        )
        botao_cookies.click()
        print("Cookies aceites.")
    except Exception as e:
        print(f"Erro ao aceitar cookies: {e}")


# Fazer scroll até o elemento da lista de lojas
def scroll_ate_lista(driver, css_selector):
    elemento = WebDriverWait(driver, 15).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, css_selector))
    )
    driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", elemento)



# Função para clicar no botão "Mais supermercados perto", se existir
def carregar_mais_lojas(driver):
    try:
        while True:
            # Procurar o botão pelo texto "Ver todos"
            botao_mais_lojas = WebDriverWait(driver, 3).until(
                EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Ver todos')]"))
            )
            botao_mais_lojas.click()
            print("Botão 'Ver todos' clicado.")
            
            # Esperar brevemente para carregar mais resultados
            WebDriverWait(driver, 2).until(
                EC.presence_of_all_elements_located((By.CSS_SELECTOR, 'li.panelLateralResultadosElemento'))
            )
    except Exception as e:
        print("Não há mais supermercados para carregar ou erro ao clicar no botão.")


# Inicializar o WebDriver e processar os dados
def processar_localidades():
    driver = webdriver.Firefox(service=service)
    driver.maximize_window()
    conn = conectar_bd()

    try:
        # Ler o ficheiro de localidades
        with open(distritos_path, "r", encoding="ISO-8859-1") as file:
            distritos = [linha.strip() for linha in file.readlines() if linha.strip()]

        for distrito in distritos:
            try:
                url = f"https://www.mercadona.pt/pt/supermercados-portugal?s={quote(distrito)}"
                driver.get(url)

                aceitar_cookies(driver)

                scroll_ate_lista(driver, '.panelLateralResultadosLista')

                carregar_mais_lojas(driver)

                # Verificar se existem lojas na página
                lojas_links = WebDriverWait(driver, 30).until(
                    EC.presence_of_all_elements_located((By.CSS_SELECTOR, 'li.panelLateralResultadosElemento'))
                )

                for loja in lojas_links:
                    # ** Verificar se a loja pertence a Portugal **
                    if not loja.find_elements(By.CSS_SELECTOR, '.supermercadoPais.pt'):
                        print(f"A loja em '{distrito}' não pertence a Portugal. Ignorada.")
                        continue

                    # Clicar na loja para obter detalhes
                    loja.click()

                    # Capturar os dados da loja
                    nome = WebDriverWait(driver, 20).until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, '.panelDetalleTitulo'))
                    ).text.strip()

                    endereco = driver.find_element(By.CSS_SELECTOR, '.panelDetalleCalle').text.strip()
                    codigo_postal = driver.find_element(By.CSS_SELECTOR, '.panelDetalleCiudad').text.strip()
                    telefone = driver.find_element(By.CSS_SELECTOR, '.supermercadoTelefono').text.strip()

                    # Extrair o link do mapa
                    link_mapa = driver.find_element(By.CSS_SELECTOR, '.green-border-transparent-button.supermercadoComoLlegar.otro').get_attribute('href')
                    latitude, longitude = None, None

                    if link_mapa:
                        coordenadas = re.search(r"dir//([-.\d]+),([-.\d]+)", link_mapa)
                        if coordenadas:
                            latitude, longitude = coordenadas.groups()

                    # Inserir no banco de dados
                    inserir_loja(conn, nome, endereco, codigo_postal, telefone, latitude, longitude)

                    # Voltar à lista de lojas
                    driver.back()

            except Exception as e:
                with open("erros.log", "a", encoding="utf-8") as log_file:
                    log_file.write(f"Erro ao processar '{distrito}': {str(e)}\n")

    finally:
        conn.close()
        driver.quit()

# Executar o script
if __name__ == "__main__":
    processar_localidades()

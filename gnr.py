from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import pandas as pd
import time
from selenium.webdriver.common.keys import Keys

# Configurar o Selenium
options = webdriver.ChromeOptions()
options.add_argument('--disable-blink-features=AutomationControlled')
driver = webdriver.Chrome(options=options)
driver.get("https://www.gnr.pt/contactos.aspx")

dados_postos = []


search_box = driver.find_element(By.ID, "ctl00_MenuLateral_TextBoxTextoPesq")
search_box.send_keys(f"Posto" + Keys.ENTER)
time.sleep(5)

def extrair_dados():
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    linhas = soup.select('tbody > tr')

    # Pular cabeçalho (se existir)
    if linhas and "background-color:#004A33" in str(linhas[0]):
        linhas = linhas[1:]

    for linha in linhas:
        try:
            nome_posto = linha.find('a', class_='gridviewVER').text.strip()
            endereco = linha.find('span', id=lambda x: x and '_Endereco' in x).text.strip()
            cp4 = linha.find('span', id=lambda x: x and '_CP4' in x).text.strip()
            cp3 = linha.find('span', id=lambda x: x and '_CP3' in x).text.strip()
            localidade = linha.find('span', id=lambda x: x and '_CPDesignacao' in x).text.strip()

            dados_postos.append({
                "Posto": nome_posto,
                "Endereço": endereco,
                "Código Postal": f"{cp4}-{cp3}",
                "Localidade": localidade
            })
            print(f"Extraído: {nome_posto}")
        except Exception as e:
            print(f"Erro na linha: {e}")
            continue

proxima_pagina = 1
try:
    while True:
        # Esperar tabela carregar
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "tbody > tr"))
        )
        
        # Extrair dados da página atual
        extrair_dados()

        # Paginação - tentar clicar no próximo número
        try:
            proxima_pagina = proxima_pagina + 1
            
            # Localizar o link da próxima página
            try:
                link = driver.find_element(By.XPATH, f"//td/a[contains(@href, 'Page${proxima_pagina}')]")
                driver.execute_script("arguments[0].click();", link)
            except:
                # Se não encontrar o link, usar __doPostBack diretamente
                driver.execute_script(f"__doPostBack('ctl00$Conteudo$ListaUnidades','Page${proxima_pagina}')")
            
            time.sleep(2)  # Espera para carregar
            print(f"Next page: ", {proxima_pagina})
        except Exception as e:
            print(f"Erro na paginação: {e}")
            print("Possível fim das páginas.")
            break

finally:
    driver.quit()

# Salvar dados
if dados_postos:
    df = pd.DataFrame(dados_postos)
    df.to_csv('postos_gnr.csv', index=False, encoding='utf-8-sig', sep=';')
    print(f"Arquivo salvo! Total de registros: {len(df)}")
else:
    print("Nenhum dado foi extraído.")
from selenium import webdriver
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
import pandas as pd
import re
import time

# Iniciar o navegador
driver = webdriver.Chrome()
driver.get('https://feed.continente.pt/lojas')
driver.maximize_window()

# Aceitar cookies (se aparecer)
try:
    botao_cookies = driver.find_element(By.XPATH, '//button[contains(text(), "Aceitar Todos")]')
    botao_cookies.click()
    time.sleep(2)
except:
    pass

# Esperar que a página carregue completamente
time.sleep(3)

# Obter o HTML da página depois de JS carregar
html = driver.page_source
soup = BeautifulSoup(html, 'html.parser')

# Fechar o navegador pois agora só usamos BeautifulSoup
driver.quit()

dados = []

lojas = soup.select('li.storeMapHeader__store')

for loja in lojas:
    nome = loja.get("data-name")
    latitude = loja.get("data-lat")
    longitude = loja.get("data-lng")

    endereco_node = loja.select_one('p.storeMapHeader__store-addres')
    endereco_completo = endereco_node.text.strip() if endereco_node else None

    if not endereco_completo:
        continue

    match = re.match(r'(.*?)(\d{4}-\d{3})(.*)', endereco_completo)
    if match:
        endereco = match.group(1).strip()
        cp = match.group(2)
        cidade = match.group(3).strip()
        codigo_postal = f"{cp} {cidade}"
    else:
        continue

    dados.append({
        "Nome": nome,
        "Morada": endereco,
        "Código Postal": cp,
        "Localidade": cidade,
        "Latitude": latitude,
        "Longitude": longitude
    })

# Guardar no CSV com separador ;
df = pd.DataFrame(dados)
df.to_csv("Continente.csv", index=False, sep=";", encoding="utf-8-sig")


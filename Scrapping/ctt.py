from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
import time
import pandas as pd
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support import expected_conditions as EC
import re

# Configuração do driver (mantida igual)
options = Options()
#options.add_argument("--headless")
options.add_argument("--start-maximized")
driver = webdriver.Chrome(options=options)
wait = WebDriverWait(driver, 10)

# Acessar o site e aceitar cookies (mantido igual)
url = "https://www.ctt.pt/feapl_2/app/open/stationSearch/stationSearch.jspx"
driver.get(url)
time.sleep(5)

try:
    driver.find_element(By.ID, "onetrust-accept-btn-handler").click()
    time.sleep(2)
except:
    pass

# Abrir lista de distritos
driver.find_element(By.ID, "districts1").click()
time.sleep(1)

# Obter todos os distritos disponíveis
distritos = driver.find_elements(By.CSS_SELECTOR, "#districts1 option")
distritos = [d for d in distritos if d.get_attribute("value")]

dados = []

# Iterar por cada distrito (SEM while True externo)
for distrito in distritos:
    nome_distrito = distrito.text
    print(f"📍 Processando distrito: {nome_distrito}")
    
    # Selecionar o distrito
    distrito.click()
    time.sleep(2)
    
    # Clicar em Procurar
    procurar_btn = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "input.button.primary[value='Procurar']")))
    driver.execute_script("arguments[0].scrollIntoView(true);", procurar_btn)
    time.sleep(0.5)
    procurar_btn.click()
    time.sleep(3)
    
    # Processar todas as páginas do distrito atual
    while True:
        # Obter todos os pontos da página atual
        pontos = wait.until(EC.presence_of_all_elements_located((By.CLASS_NAME, "entry-wrapper")))
        
        for ponto in pontos:
            try:
                # Seu código de extração mantido igual
                nome = ponto.find_element(By.TAG_NAME, "h3").text.strip()
                tipo = ponto.find_element(By.TAG_NAME, "p").text.strip()
                
                morada_div = ponto.find_element(By.CLASS_NAME, "posRelative")
                morada_texto = morada_div.text
                
                linhas = [linha.strip() for linha in morada_texto.split('\n') if linha.strip()]
                morada_linha1 = linhas[0].strip()
                if ',' in morada_linha1:
                    morada_linha1 = morada_linha1.split(',')[0].strip()
                
                cod_postal, localidade = "", ""
                for linha in morada_texto.split('\n'):
                    linha = linha.strip()
                    match = re.search(r'(\d{4}-\d{3}) ([A-ZÀ-Ú\s-]+)$', linha)
                    if match:
                        cod_postal = match.group(1)
                        localidade = match.group(2).strip()
                        break
                    
                try:
                    link = morada_div.find_element(By.PARTIAL_LINK_TEXT, "Ver no mapa").get_attribute("href")
                    coords = link.split("q=")[1].split("&")[0] if "q=" in link else ""
                    lat, lon = coords.split(",") if "," in coords else ("", "")
                except:
                    lat, lon = None, None
                
                dados.append({
                    "Nome": nome,
                    "Tipo": tipo,
                    "Morada": morada_linha1,
                    "Código Postal": cod_postal,
                    "Localidade": localidade,
                    "Latitude": lat,
                    "Longitude": lon
                })
                
            except Exception as e:
                print(f"Erro ao processar ponto: {nome, str(e)}")
                continue
        
        # Tentar paginar
        try:
            next_button = wait.until(
                EC.element_to_be_clickable((By.XPATH, '//a[contains(@onclick, "goToStationPage") and @title="Seguinte"]')))
            driver.execute_script("arguments[0].scrollIntoView();", next_button)
            time.sleep(1)
            next_button.click()
            time.sleep(3)  # Espera para carregar nova página
            
            # Verificar se a nova página carregou
            wait.until(EC.staleness_of(pontos[0]))
            
        except Exception as e:
            print(f"Fim das páginas para {nome_distrito}")
            break

    # Salvar os dados após processar cada distrito
    df = pd.DataFrame(dados)
    df.to_csv("pontos_ctt.csv", index=False, sep=";", encoding="utf-8-sig")

driver.quit()
print("✅ Dados guardados em pontos_ctt_completo.csv")
import time
import re
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException

def tentar_abrir_link(driver, link, tentativas=3):
    for tentativa in range(1, tentativas + 1):
        try:
            driver.set_page_load_timeout(30)  # Timeout de 30 segundos
            driver.get(link)
            time.sleep(5)
            return True  # Sucesso
        except Exception as e:
            print(f"⚠️ Tentativa {tentativa} falhou para {link}: {e}")
            if tentativa == tentativas:
                print(f"❌ Falhou após {tentativas} tentativas. A saltar este restaurante.")
                return False
            time.sleep(3)  # Pequena pausa antes da próxima tentativa



def scroll_google_maps(driver):
    scrollable_div = driver.find_element(By.CSS_SELECTOR, 'div.m6QErb.DxyBCb.kA9KIf.dS8AEf[role="feed"]')
    while True:
        driver.execute_script("arguments[0].scrollTo(0, arguments[0].scrollHeight);", scrollable_div)
        time.sleep(2)
        try:
            fim_lista = driver.find_element(By.XPATH, '//span[contains(text(), "Chegou ao fim da lista.")]')
            if fim_lista.is_displayed():
                break
        except:
            pass

def extract_coordinates(url):
    match = re.search(r'@(-?\d+\.\d+),(-?\d+\.\d+)', url)
    if match:
        return float(match.group(1)), float(match.group(2))
    return "-", "-"

def extrair_cp_localidade(morada):
    match = re.search(r'(\d{4}-\d{3})\s+(.+)', morada)
    if match:
        return match.group(1), match.group(2)
    return "-", "-"

# Lê os códigos postais do ficheiro cp.txt
with open("data/txt/freguesias.txt", "r", encoding="utf-8") as f:
    freguesias = [linha.strip() for linha in f if linha.strip()]

# Setup do Chrome
options = Options()
options.add_argument("--start-maximized")
driver = webdriver.Chrome(options=options)

# Abre o Google Maps
driver.get("https://www.google.com/maps")
time.sleep(3)

# Aceitar cookies
try:
    botao_cookies = driver.find_element(By.CSS_SELECTOR, 'button[aria-label="Aceitar tudo"]')
    botao_cookies.click()
    time.sleep(2)
except:
    pass

dados = []
latitudes_guardadas = set()

for freguesia in freguesias:
    print(f"\n🔍 A pesquisar Ginásios em: {freguesia}")
    search_box = driver.find_element(By.ID, "searchboxinput")
    search_box.clear()
    search_box.send_keys(f"Ginásios em {freguesia}" + Keys.ENTER)
    time.sleep(5)

    try:
        scroll_google_maps(driver)
    except:
        print("⚠️ Erro ao fazer scroll. A continuar para o próximo CP.")
        continue

    ginasios = driver.find_elements(By.CSS_SELECTOR, 'a.hfpxzc')
    links = list({r.get_attribute("href") for r in ginasios if r.get_attribute("href")})

    print(f"🔗 {len(links)} links encontrados para {freguesia}")

    for i, link in enumerate(links):
        if not tentar_abrir_link(driver, link):
            continue

        try:
            nome_ginasio = driver.find_element(By.CLASS_NAME, "DUwDvf").text
        except:
            nome_ginasio = "-"

        try:
            morada = driver.find_element(By.CLASS_NAME, "Io6YTe").text
        except:
            morada = "-"

        try:
            fechado = driver.find_element(By.CLASS_NAME, "aSftqf").text
        except:
            fechado = "-"

        lat, lng = extract_coordinates(driver.current_url)

        try:
            tipo_ginasio = driver.find_element(By.CLASS_NAME, "DkEaL").text
        except:
            tipo_ginasio = "-"

        # Evitar duplicados pela latitude
        if lat not in latitudes_guardadas:
            latitudes_guardadas.add(lat)
            dados.append({
                "Nome": nome_ginasio,
                "Morada": morada,
                "Tipo de Ginásio": tipo_ginasio,
                "Latitude": lat,
                "Longitude": lng,
                "Estado": fechado,
            })
            print(f"{i+1}: {nome_ginasio} (adicionado)")
        else:
            print(f"{i+1}: {nome_ginasio} (duplicado, ignorado)")


        if (len(dados)) % 10 == 0:
            df = pd.DataFrame(dados)
            df[['Código Postal', 'Localidade']] = df['Morada'].apply(lambda x: pd.Series(extrair_cp_localidade(str(x))))
            df['Morada'] = df['Morada'].str.replace(r'\s*\d{4}-\d{3}\s+.+$', '', regex=True).str.strip(", ")
            df.to_csv('ginasios.csv', sep=';', index=False, encoding="utf-8-sig")


# Salva no final
df = pd.DataFrame(dados)
df[['Código Postal', 'Localidade']] = df['Morada'].apply(lambda x: pd.Series(extrair_cp_localidade(str(x))))
df['Morada'] = df['Morada'].str.replace(r'\s*\d{4}-\d{3}\s+.+$', '', regex=True).str.strip(", ")
df.to_csv('ginasios.csv', sep=';', index=False, encoding="utf-8-sig")


driver.quit()
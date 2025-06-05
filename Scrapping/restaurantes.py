import time
import re
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options

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
with open("data/txt/concelhos.txt", "r", encoding="utf-8") as f:
    concelhos = [linha.strip() for linha in f if linha.strip()]

# Setup do Chrome
options = Options()
#options.add_argument("--headless")
#options.add_argument("--disable-gpu")
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

for concelho in concelhos:
    print(f"\n🔍 A pesquisar restaurantes em: {concelho}")
    search_box = driver.find_element(By.ID, "searchboxinput")
    search_box.clear()
    search_box.send_keys(f"Restaurantes em {concelho}" + Keys.ENTER)
    time.sleep(5)

    try:
        scroll_google_maps(driver)
    except:
        print("⚠️ Erro ao fazer scroll. A continuar para o próximo CP.")
        continue

    restaurantes = driver.find_elements(By.CSS_SELECTOR, 'a.hfpxzc')
    links = list({r.get_attribute("href") for r in restaurantes if r.get_attribute("href")})

    print(f"🔗 {len(links)} links encontrados para {concelho}")

    for i, link in enumerate(links):
        if not tentar_abrir_link(driver, link):
            continue

        try:
            nome_restaurante = driver.find_element(By.CLASS_NAME, "DUwDvf").text
        except:
            nome_restaurante = "-"

        try:
            rating_element = driver.find_element(By.CSS_SELECTOR, 'span.ceNzKf[aria-label$="estrelas "]')
            rating = rating_element.get_attribute("aria-label").split(" ")[0]
        except:
            rating = "-"

        try:
            avaliacoes_element = driver.find_element(By.XPATH, '//span[contains(@aria-label, "críticas")]')
            numero_avaliacoes = avaliacoes_element.get_attribute("aria-label").split(" ")[0].replace("\u202f", "").replace("\xa0", "")
        except:
            numero_avaliacoes = "-"

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
            tipo_restaurante = driver.find_element(By.CLASS_NAME, "DkEaL").text
        except:
            tipo_restaurante = "-"

        try:
            acerca = driver.find_element(By.XPATH, '//div[text()="Acerca de"]')
            acerca.click()
            time.sleep(2)  # Dá um tempinho para o conteúdo carregar
        except:
            print("⚠️ Não foi possível clicar em 'Acerca de'")

        # Dietas especiais
        entregas = "-"
        take_away = "-"
        opcao_vegetariana = "-"
        opcao_vegana = "-"

        try:
            dietas = driver.find_elements(By.CSS_SELECTOR, 'ul.ZQ6we li span[aria-label]')
            for dieta in dietas:
                texto = dieta.get_attribute("aria-label").strip()
                if "Faz entregas" in texto:
                    entregas = "Sim"
                if "Tem take away" in texto:
                    take_away = "Sim"
                if "Serve pratos vegetarianos" in texto:
                    opcao_vegetariana = "Sim"
                if "Serve pratos veganos" in texto:
                    opcao_vegana = "Sim"
        except:
            pass

        # Evitar duplicados pela latitude
        if lat not in latitudes_guardadas:
            latitudes_guardadas.add(lat)
            dados.append({
                "Nome": nome_restaurante,
                "Morada": morada,
                "Rating": rating,
                "Nº Avaliações": numero_avaliacoes,
                "Tipo de Restaurante": tipo_restaurante,
                "Latitude": lat,
                "Longitude": lng,
                "Estado": fechado,
                "Opções vegetarianas": opcao_vegetariana,
                "Opções veganas": opcao_vegana,
                "Entregas": entregas,
                "Take Away": take_away
            })
            print(f"{i+1}: {nome_restaurante} (adicionado)")
        else:
            print(f"{i+1}: {nome_restaurante} (duplicado, ignorado)")

    # Guarda após acabar um conceho
    df = pd.DataFrame(dados)
    df[['Código Postal', 'Localidade']] = df['Morada'].apply(lambda x: pd.Series(extrair_cp_localidade(str(x))))
    df['Morada'] = df['Morada'].str.replace(r'\s*\d{4}-\d{3}\s+.+$', '', regex=True).str.strip(", ")
    df.to_csv('restaurantes1.csv', sep=';', index=False, encoding="utf-8-sig")


driver.quit()
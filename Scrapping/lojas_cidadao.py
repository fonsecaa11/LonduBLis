from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import time
import csv

# Configuração do Selenium
driver = webdriver.Chrome()
driver.get("https://www2.gov.pt/locais-de-atendimento-de-servicos-publicos/-/pesquisa/search_stores?_searchresults_formDate=1728482816241&_searchresults_keywords=&_searchresults_keywords2=&_searchresults_portalCategoryTypesId=&_searchresults_LojasEspacos+238350=on&_searchresults_checkboxNames=LojasEspacos+47584870%2CLojasEspacos+47584871%2CLojasEspacos+47584867%2CLojasEspacos+238351%2CLojasEspacos+238352%2CLojasEspacos+47584869%2CLojasEspacos+47584872%2CLojasEspacos+238350%2CLojasEspacos+47584873%2CLojasEspacos+47584868%2CDistritos+238329%2CDistritos+238330%2CDistritos+238331%2CDistritos+238332%2CDistritos+238333%2CDistritos+238334%2CDistritos+238407%2CDistritos+238408%2CDistritos+238409%2CDistritos+238410%2CDistritos+238411%2CDistritos+238412%2CDistritos+238413%2CDistritos+238414%2CDistritos+238415%2CDistritos+238416%2CDistritos+238417%2CDistritos+238418%2CDistritos+238419%2CDistritos+238420%2CDistritos+238421%2CDistritos+238422%2CDistritos+238423%2CDistritos+238424%2CDistritos+238425%2CDistritos+238426%2CDistritos+238427%2CDistritos+238428%2CDistritos+238429%2CPaises+25290870%2CPaises+25290864%2CPaises+25290908%2CPaises+25291018%2CPaises+25291021&pageSequenceNumber=2")
driver.maximize_window()
time.sleep(5)

nomes_lojas = set() # Para evitar nomes duplicados
dados_lojas = []

# Clicar no botão "Mostrar mais" até carregar todas as lojas
while True:
    try:
        botao_mostrar_mais = driver.find_element(By.XPATH, "//button[contains(text(), 'Ver mais')]")
        botao_mostrar_mais.click()
        time.sleep(3)  # Aguardar carregamento
    except:
        break  # Se não encontrar o botão, sai do loop


# Obter todas as lojas da pesquisa
lojas = driver.find_elements(By.CLASS_NAME, "pl-3")
time.sleep(3)

for index, loja in enumerate(lojas, start=1):
    try:
        nome = loja.find_element(By.TAG_NAME, "a").text.strip()
        endereco_completo = loja.find_element(By.CLASS_NAME, "pb-3").text.strip()
        
        partes_endereco = endereco_completo.split("\n")
        endereco = " ".join(partes_endereco[:-1]).strip()
        codigo_postal = partes_endereco[-1].strip() if "-" in partes_endereco[-1] else ""
            
        
        if nome not in nomes_lojas:
            nomes_lojas.add(nome)
            dados_lojas.append([index, nome, endereco, codigo_postal])
            print(f"✔ Dados extraídos: {index}, {nome}, {endereco}, {codigo_postal}")
    except Exception as e:
        print(f"Erro ao processar uma loja: {e}")

# Fechar o navegador
driver.quit()

# Nome do ficheiro CSV
csv_filename = "csv_geral/lojas_cidadao.csv"

# Guardar os dados num ficheiro CSV
with open(csv_filename, "w", newline="", encoding="utf-8") as file:
    writer = csv.writer(file, delimiter=";")
    writer.writerow(["Id_loja_cidadao", "Nome", "Endereço", "Código Postal"])  # Cabeçalhos
    writer.writerows(dados_lojas)  # Escrever os dados

print(f"Dados salvos em {csv_filename}!")
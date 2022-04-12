from unicodedata import name
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from time import sleep
from selenium.webdriver.common.by import By
import pandas as pd

# clica nos botões ouro, prata, bronze
def click_button(driv, metal):
    try:
        driv.find_element(By.XPATH, f"//button[@class='checkbox -larger -{metal}']").click()
    except:
        driv.find_element(By.XPATH, "//button[@class='accordion__btn']").click()
        sleep(1)
        driv.find_element(By.XPATH, f"//button[@class='checkbox -larger -{metal}']").click()
        
    sleep(0.5)
    return True

# coleta os elementos na página (empresas e inventários) e armazena em listas
def list_elements(driver,metal,empresas_lista,inventarios_lista,num_invent,categoria):
    sleep(2)
    empresas = driver.find_elements(By.CLASS_NAME,"participant-box__title")
    inventarios = driver.find_elements(By.CLASS_NAME,"participant-box__stamps")
    sleep(1)

    for i in range(len(empresas)):
        if empresas[i].text not in empresas_lista:
            empresas_lista.append(empresas[i].text)
            inventarios_lista.append(inventarios[i].text)
            num_invent.append(inventarios[i].text.count(',')+1)
            categoria.append(metal)
    
    return [empresas_lista,inventarios_lista,num_invent,categoria]

def main():
    empresas_lista = []
    inventarios_lista = []
    num_invent = []
    categoria = []

    driver = webdriver.Chrome(ChromeDriverManager().install())
    url = "https://registropublicodeemissoes.com.br/participantes"
    driver.get(url)
    sleep(7)

    # pega empresas categoria inventário Ouro
    click_button(driver, "bronze")
    click_button(driver, "silver")
    [empresas_lista,inventarios_lista,num_invent,categoria] = list_elements(driver,"Ouro",empresas_lista,inventarios_lista,num_invent,categoria)

    # pega empresas categoria inventário Prata
    click_button(driver, "silver")
    click_button(driver, "gold")
    [empresas_lista,inventarios_lista,num_invent,categoria] = list_elements(driver,"Prata",empresas_lista,inventarios_lista,num_invent,categoria)

    # pega empresas categoria inventário Bronze
    click_button(driver, "bronze")
    click_button(driver, "silver")
    [empresas_lista,inventarios_lista,num_invent,categoria] = list_elements(driver,"Bronze",empresas_lista,inventarios_lista,num_invent,categoria)

    dic = {"Empresa": empresas_lista, "Número Invent.": num_invent, "Categoria":categoria, "Inventários": inventarios_lista }
    df = pd.DataFrame.from_dict(dic, orient='index')
    df = df.transpose()

    df.to_excel("empresas_registro_emissoes.xlsx",sheet_name="Registro Público de Emissões")

if __name__ == "__main__":
    main()
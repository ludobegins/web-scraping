# gets contact info from Brazilian sugarcane mills: name, city, website, emails, telephones
# info from novacana.com
# must have a login username and password in novacana.com to work
# info is saved in an Excel file

from typing import final
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.keys import Keys
import pandas as pd
from pandas import ExcelWriter
from time import sleep
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By

usuario_nova_cana = "insert_username"  # INSERT USERNAME HERE
senha_nova_cana = "insert_password"    # INSERT PASSWORD HERE
path = r"C:\path"  # INSERT FILE PATH HERE

estado_url_suffix = ["acre","bahia","goias","mato-grosso","minas-gerais","paraiba","rio-de-janeiro","rio-grande-do-sul","sao-paulo","alagoas","amazonas","ceara","espirito-santo","maranhao","mato-grosso-do-sul","para","parana","piaui","rio-grande-do-norte","rondonia","sergipe","tocantins"]
base_url = "https://www.novacana.com/usinas_brasil/estados/"

def nova_cana_login(url_suffix):
    driver = webdriver.Chrome(ChromeDriverManager().install())
    url = base_url + url_suffix
    driver.get(url)
    login_button = driver.find_elements_by_xpath('//a[@class="ncLogin dropdown-toggle"]')[0].click()
    username = driver.find_element_by_name("username")
    password = driver.find_element_by_name("password")
    username.send_keys(usuario_nova_cana)
    password.send_keys(senha_nova_cana)
    login_submit_button = driver.find_elements_by_xpath('//button[@class="btn btn-success submitLogin"]')[0].click()
    return(driver)

def lista_usinas(driv):
    usinas = driv.find_elements_by_tag_name('h1')
    usinas_lista = []
    for u in range(len(usinas)):
        usinas_lista.append(usinas[u].text)
    usinas_lista = [u for u in usinas_lista if u not in ("","Capacidade de moagem","Selos e autorizações","ASSINE","COMPARTILHAR")]
    del usinas_lista[0:2]
    return(usinas_lista)

def lista_cidades(driv):
    cidades = driv.find_elements_by_tag_name('h2')
    cidades_lista = []
    for c in range(len(cidades)):
        cidades_lista.append(cidades[c].text)
    cidades_lista = [c for c in cidades_lista if c not in ("")]
    return(cidades_lista)

def lista_contatos(driv):
    tipo_contatos = driver.find_elements_by_class_name("tab-nome")
    contatos = driver.find_elements_by_class_name("tab-cargo")      
    contatos_lista = []
    for i in range(len(contatos)):
        wait = WebDriverWait(driver, 10)
        #sleep(1)
        tipo_cont = wait.until(EC.presence_of_all_elements_located((By.CLASS_NAME,"tab-nome")))
        cont = wait.until(EC.presence_of_all_elements_located((By.CLASS_NAME,"tab-cargo")))       #element_to_be_clickable((By.ID, 'someid')))
        contatos_lista.append(tipo_cont[i].text + cont[i].text)
    return contatos_lista

def add_blank_contacts(cont_list):
    for i in range(0, len(cont_list)):
        if i % 3 == 0:
            if "Site" in cont_list[i]:
                pass
            else:
                cont_list.insert(i,"Site:")
        elif (i-1) % 3 == 0:
            if "Email" in cont_list[i]:
                pass
            else:
                cont_list.insert(i,"Email:")
        else:
            if "Tel" in cont_list[i]:
                pass
            else:
                cont_list.insert(i,"Telefone:")
    return cont_list

def split_contacts(cont_list):
    sites = []
    emails = []
    telefones = []
    for s in cont_list:
        if "Site" in s:
            sites.append(s)
        if "Email" in s:
            emails.append(s)
        if "Tel" in s:
            telefones.append(s)
    return sites, emails, telefones

def clean_cols(cid,sit,ema,tel):
    for i in range(len(cid)):
        try:
            cid[i] = cid[i].split(" -")[0]
        except:
            pass
        try:
            sit[i] = sit[i].split("Site:")[1]
        except:
            pass
        try:
            ema[i] = ema[i].split("Email:")[1]
        except:
            pass
        try:
            tel[i] = tel[i].split("Telefone:")[1]
        except:
            pass
    return cid, sit, ema, tel

def lists_to_df(usi,cid,sit,ema,tel):
    a = {'Usina':usi, 'Cidade':cid, 'Site':sit, 'Email':ema,'Telefone':tel }
    df = pd.DataFrame.from_dict(a, orient='index')
    df = df.transpose()
    return df

def save_xls(dict_dfs, xls_path):
    writer = ExcelWriter(xls_path)
    for key in dict_dfs:
        dict_dfs[key].to_excel(writer, key)
    writer.save()

def main():
    dict_usinas = {}

    for estado in estado_url_suffix:
        lista_dfs_usinas_estado = []
        driver = nova_cana_login(estado)
        sleep(5)
        usinas_lista = lista_usinas(driver)
        cidades_lista = lista_cidades(driver)
        contatos_lista = add_blank_contacts(lista_contatos(driver))
        (sites,emails,telefones) = split_contacts(contatos_lista)
        (cidades_lista,sites,emails,telefones) = clean_cols(cidades_lista,sites,emails,telefones)
        lista_dfs_usinas_estado.append(lists_to_df(usinas_lista,cidades_lista,sites,emails,telefones))

        if estado == "sao-paulo":
            lim_pag = 10
        else:
            lim_pag = 4

        for i in range(2,lim_pag):
            try:
                driver.get(base_url+estado+f"?page={i}")
                #driver = nova_cana_login(estado+f"?page={i}")
                sleep(5)
                usinas_lista = lista_usinas(driver)
                cidades_lista = lista_cidades(driver)
                contatos_lista = add_blank_contacts(lista_contatos(driver))
                (sites,emails,telefones) = split_contacts(contatos_lista)
                (cidades_lista,sites,emails,telefones) = clean_cols(cidades_lista,sites,emails,telefones)
                lista_dfs_usinas_estado.append(lists_to_df(usinas_lista,cidades_lista,sites,emails,telefones))
            except:
                pass
        
        df_usinas_estado = pd.concat(lista_dfs_usinas_estado)
        dict_usinas[estado] = df_usinas_estado
        #print(df_usinas_estado)
        save_xls(dict_usinas,path)

    driver.close()

if __name__ == "__main__":
    main()
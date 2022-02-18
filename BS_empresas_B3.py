from bs4 import BeautifulSoup
from urllib.request import urlopen
import pandas as pd

url = "https://www.infomoney.com.br/cotacoes/empresas-b3/"
page = urlopen(url)
html = page.read().decode("utf-8")
soup = BeautifulSoup(html,"html.parser")

text_v0 = soup.get_text() #.strip()#.replace("\n\n\n","")
start_text_v0 = text_v0.find("Mais sobre\n\nOnde Investir\n\n\n\n\n")+len("Mais sobre\n\nOnde Investir\n\n\n\n\n")
end_text_v0 = text_v0.find("Guias InfoMoney") - 23
text_v0 = text_v0[start_text_v0:end_text_v0]

delimit_categ = "\n\n\n\n\n\n\n\n\n"
text_categ = text_v0.split(delimit_categ)
#

delimit_categ_2 =  "keyboard_arrow_down\nkeyboard_arrow_up\n\n\n\n\n\nEmpresas\nAtivos\n\n\n\n\n"
for i in range(len(text_categ)):
    text_categ[i] = text_categ[i].split(delimit_categ_2)

#print(text_categ)

dict_categ = {}
for categ in text_categ:
    dict_categ[categ[0]] = categ[1].split("\n\n")
    dict_categ[categ[0]].remove("")

for key in dict_categ:
    key = key.strip()
    key.replace("\n","")

#print(dict_categ)

df = pd.DataFrame.from_dict(dict_categ, orient="index")
df = df.transpose()
#print(df)

xls = df.to_excel("empresas_b3.xlsx")



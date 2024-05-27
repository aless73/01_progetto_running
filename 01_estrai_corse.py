import bs4 as BeautifulSoup
import ssl
import numpy as np
from urllib.request import Request, urlopen
import pickle
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select


percorso='D:/alessandro2/04_altri_hobby/03_manuale python/01_progetto_running/'
gcontext = ssl.SSLContext()

radice='https://www.endu.net'
coda='/search/events?sport=running'

#URL='https://www.endu.net/search/events?sport=running'
URL=radice+coda

def scarica_pagina(URL):
    req = Request(URL, headers={'User-Agent': 'Mozilla/5.0'})
    webpage = urlopen(req, context=gcontext).read()
    soup = BeautifulSoup.BeautifulSoup(webpage, features="lxml")
    return soup

#trova all'interno dell'html le tabelle ma 
def pagina_giocatori(soup):
    table = soup.findAll("table", {"class": "items"})
    lista_righe=table[0].findAll("tr")
    lista_righe=lista_righe[1:]
    lista_link=table[0].findAll("a")
    lista_pulita=[a['href'] for a in lista_link if a['href']!='#']
    giocatori=[]
    indici=np.arange(0,len(lista_righe),3)
    giocatori=[]
    for c in indici:
        giocatore=list(lista_righe[c].strings)[2:6]
        giocatore.append(lista_pulita[c])
        giocatori.append(giocatore)
    return giocatori


path='C:\Program Files (x86)\chromedriver.exe'
capa = DesiredCapabilities.CHROME
capa["pageLoadStrategy"] = "none"
#QUANDO DA UN ERRORE SULLA VERSIONE DI CHROMEDRIVER, BISOGNA SCARICARE CHROMEDRIVER E CHROME NELLA STESSA VERSIONE E METTERE IL PRIMO IN PROGRAMFILES
#IL SECONDO NELLA DIRECTORY DOVE E' IL BROWSER CHROME (ATTENZIONE CANCELLA TUTTE LE PWD E I PREFERITI DELLA VECCHIA VERSIONE DI CHROME)
driver = webdriver.Chrome(desired_capabilities=capa,executable_path=path)

#recupero la lista che contiene le url che sono state già trattate
file_trattate='f_03_url_trattate.pickle'
url_trattate_grezze=pickle.load(open(percorso+file_trattate,'rb'))
#bisogna fare alcuni aggiustamenti:
    #la lista è nella forma [[1,url],[]..] la trasformo in [url, url,...]
    #devo togliere lo slash alla fine e it/ 
solo_url_trattate=list(map(lambda x: x[1],url_trattate_grezze))
combo_path='//*[@id="container"]/div/div/div[1]/div/div[3]/label/select'

#dalla pagina degli eventi trovo le relative url
#le confronto con quelle già trattate e se sono nuove le aggiungo alla lista gare_url
#la carico
print('carica')
driver.get(URL)
time.sleep(5)
#accetto i cookie
cookie=driver.find_element(By.XPATH, '//*[@id="iubenda-cs-banner"]/div/div/div/button')
print('trovato2')
cookie.click()
#seleziono solo gli eventi passati
combo = Select(driver.find_element(By.XPATH,combo_path))
combo.select_by_value('string:past')
#generazione dei numeri di pagine
#nella prima pagina le pagine da 1 a 7 hanno numeri da 3 a 9
#se numeri di pagine è 2 pagina corrente non devo cliccare su nessun elemento
numeri_pagine=[n for n in range(2,9)]
#successivamente ogni pagina ha numero 6 (ho generato 46 volte 6)
###per le volte successive evitare di arrivare fino a 46
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
numeri_pagine.extend([6 for n in range(0,46)])
pagina0='//*[@id="container"]/div/div/div[2]/div[21]/div/ul/li['
pagina1=']/a'
#generazione del numero di elementi in una pagina
numeri=np.arange(1,21,1)
prima_meta='//*[@id="container"]/div/div/div[2]/div['
seconda_meta=']/div/div/a'
#'//*[@id="container"]/div/div/div[2]/div[1]/div/div/a'
gare_url=[]
cont=1
for pag in numeri_pagine:
    if pag==2:
        print('prima pagina')
    else:
        ind_pagina=driver.find_element(By.XPATH, pagina0+str(pag)+pagina1)
        ind_pagina.click()
        print('pagina ',cont)
    time.sleep(4)
    for num in numeri:
        elemento=prima_meta+str(num)+seconda_meta
        evento=driver.find_element(By.XPATH, elemento)
        print('trovato')
        link_url = evento.get_attribute("href")
        if link_url not in solo_url_trattate:
            gare_url.append(link_url)
            print('aggiunta')
        else:
            print('gia trattata')
    cont+=1
#lista di url da aggiungere manualmente
aggiungi_maunale=['https://www.endu.net/events/mezza-maratona-della-concordia-citta-di-agrigento-2',
'https://www.endu.net/events/maratonina-della-befana-2',
'https://www.endu.net/events/maratonina-dei-magi',
'https://www.endu.net/events/mezza-maratona-sul-brembo',
'https://www.endu.net/events/agropoli-paestum-half-marathon']
#aggiungi_manuale=['https://www.endu.net/events/run-for-autism']
#gare_url.extend(aggiungi_manuale)

pickle.dump(gare_url,open(percorso+'f_01_gare_url.pickle','wb'),protocol=4)
import bs4 as BeautifulSoup
import ssl
import numpy as np
from urllib.request import Request, urlopen
import pickle
import time
import glob
import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import WebDriverException
import shutil

folder_scarico='C:/Users/unieuro/Downloads/'
folder_risultati='01_file_risultati/'
percorso='D:/alessandro2/04_altri_hobby/03_manuale python/01_progetto_running/'
infile='f_01_gare_url.pickle'
infile_db_gare='f_02_db_gare.pickle'
infile_trattate='f_03_url_trattate.pickle'
infile_scartate='f_04_url_scartate.pickle'
gcontext = ssl.SSLContext()

radice='https://www.endu.net'
coda='/results'
uuu='alessandrovolpetti@gmail.com'
ppp='iron42195'
mail_path='/html/body/div[1]/div[3]/form[1]/div[1]/div/input'
pwd_path='/html/body/div[1]/div[3]/form[1]/div[2]/div/input[3]'

path='C:\Program Files (x86)\chromedriver.exe'
capa = DesiredCapabilities.CHROME
capa["pageLoadStrategy"] = "none"
#QUANDO DA UN ERRORE SULLA VERSIONE DI CHROMEDRIVER, BISOGNA SCARICARE CHROMEDRIVER E CHROME NELLA STESSA VERSIONE E METTERE IL PRIMO IN PROGRAMFILES
#IL SECONDO NELLA DIRECTORY DOVE E' IL BROWSER CHROME (ATTENZIONE CANCELLA TUTTE LE PWD E I PREFERITI DELLA VECCHIA VERSIONE DI CHROME)
driver = webdriver.Chrome(desired_capabilities=capa,executable_path=path)

def scarica_pagina(URL):
    req = Request(URL, headers={'User-Agent': 'Mozilla/5.0'})
    webpage = urlopen(req, context=gcontext).read()
    soup = BeautifulSoup.BeautifulSoup(webpage, features="lxml")
    return soup

#estrae le informazioni della gara 
def info_gara(zuppa, posizione):
    car='·'
    blob1=zuppa.find_all('div', class_='titavatar')[0].get_text()
    titolo=blob1.replace('\n','').replace('\xa0',' ').replace('/','_').replace('-','_').strip()
    titolo=titolo.split('  ')[0]
    blob2=zuppa.find_all('div', class_='descavatar')[0].get_text()
    info=blob2.replace('\n','').replace('\xa0',' ').replace('/','_').replace('-','_').strip().split(car)
    info=[a.strip() for a in info]
    info.insert(0,titolo)
    info.append(gara)
    info.insert(0,posizione)
    return info
#riempe il form del login
def log_in(user,pwd,mail_path,pwd_path):
    log=driver.find_element(By.XPATH,mail_path)
    print('trovata mail')
    log.clear()
    log.send_keys(user)
    print('scritta email')
    pp=driver.find_element(By.XPATH,pwd_path)
    print('trovata pwd')
    pp.clear()
    pp.send_keys(pwd)
    print('scritta pwd')
    pp.submit()

def rinomina_file(gara,distanza,downloads_folder):
    files = glob.glob(os.path.join(downloads_folder, "*"))
    files.sort(key=os.path.getmtime)
    files.reverse()
    file=files[0]
    nuovo_nome=gara.replace(' ','_').replace('-','').replace(':','_').replace(',','_').replace('.','_').replace("\'", '').replace('"','')+'_'+distanza.replace(' ','_').replace('/','_').replace(':','_').replace(',','_').replace('.','_').replace('"','')+'.xls'
    shutil.copyfile(file, percorso+folder_risultati+nuovo_nome)
#trova un elemento sulla base del testo ad esso collegato con un match parziale    
def trova_by_text(testo,testo_no):
    check=0
    try:
        obiettivo=driver.find_element(By.XPATH,f"//*[contains(text(), '{testo}')]")
        check=1
        print('trovato testo')
    except NoSuchElementException:
        try:
            nores=driver.find_element(By.XPATH,f"//*[contains(text(), '{testo_no}')]")
            check=0
            print('trovato no res', check)
            obiettivo='no res'
        except NoSuchElementException:
            obiettivo='no res'
            print('trovato nulla')
    return obiettivo,check
#trova un elemento sulla base del testo ad esso collegato con un match esatto
#non l'ho usato perchè una volta che trovo l'elemento poi non mi risulta cliccabile
def trova_by_text_esatto(testo,testo_no):
    check=0
    try:
        obiettivo=driver.find_element(By.XPATH,f"//*[text()=, '{testo}')]")
        check=1
        print('trovato testo')
    except NoSuchElementException:
        try:
            nores=driver.find_element(By.XPATH,f"//*[contains(text(), '{testo_no}')]")
            check=0
            print('trovato no res', check)
            obiettivo='no res'
        except NoSuchElementException:
            obiettivo='no res'
            print('trovato nulla')
    return obiettivo,check

#trova il pulsante per scaricare i risultati in una lista di possibili Xpath
#trova anche se i risultati non sono disponibili 
#restituisce l'oggetto da cliccare e la variabile check a 1 se trovati e a 0 se non trovati
def trova_risultati(possibili):
    check=0
    for passo in possibili:
        try:
            risultati_xls=driver.find_element(By.XPATH, passo)
            check=1
            print('trovato',check)
            break    
        except NoSuchElementException:
            try:
                nores=driver.find_element(By.XPATH,'//*[@id="contenitore"]/div[1]/div[1]/div[1]/div/div[10]/p/span')
                check=0
                print('trovato no res', check)
                risultati_xls='no res'
                break
            except NoSuchElementException:
                risultati_xls='no res'
                print('proviamo altro')
    return risultati_xls, check
#trova un elemento ricercandolo tra una lista di possibili Xpath
#variabile semplificata del precedente non restituisce il check e non verifica la presenza
#della stringa no res
def trova_possibili(possibili):
    for passo in possibili:
        try:
            oggetto=driver.find_element(By.XPATH, passo)
            print('trovato possibile')
            break    
        except NoSuchElementException:
            oggetto='nores'
            print('proviamo altro')
    return oggetto
#trova una combo fra una lista di possibili xpath
def trova_possibili_combo(possibili):
    for combi in possibili:
        try:
            combo = Select(driver.find_element(By.XPATH,combi))
            break
        except NoSuchElementException:
            print('provo secondo')
    return combo

def tratta_url(driver,URL):
    print('carico zuppa')
    zuppa=scarica_pagina(URL)
    print('carica')
    driver.get(URL)
    time.sleep(5)
    if posizione==1:
        #accetto i cookie solo la prima volta che accedo
        cookie=driver.find_element(By.XPATH, '//*[@id="iubenda-cs-banner"]/div/div/div/button')
        print('cookie')
        cookie.click()
    #cerco il bottone dei risultati
    risultati_xls,check=trova_by_text(spia_xls,spia_nores)
    #risultati_xls,check=trova_risultati(possibili_xls)
    if check==1:
        #i risultati esistono; intanto scarico le informazioni della gara
        info=info_gara(zuppa,posizione)
        #se non ho ancora fatto il login
        if fatto_log==0:
            fatto_log=1
            print('devo fare il login')
            #poi faccio click
            risultati_xls.click()
            time.sleep(2)
            #compare il pop up per il login
            #accedi,check=trova_by_text_esatto(spia_acc,spia_noacc)
            accedi=trova_possibili(possibili_acce)
            accedi.click()
            time.sleep(3)
            #riempo il form e lo invio
            log_in(uuu,ppp,mail_path,pwd_path)
            time.sleep(6)
        else:
            print('login già fatto')
        #seleziono la combo con le distanze della gara (potrebbero essere più di una)
        combo=trova_possibili_combo(possibili_combo)
        options = combo.options
        values_list = [option.get_attribute("value") for option in options]
        label_list = [option.get_attribute("label") for option in options]
        ####limitare le liste a tre
        itera=min(3,len(values_list))
        info.append(len(label_list[:itera]))
        info.append(label_list[:itera])
        #itero rispetto ai valori della gara per scaricare il file di ogni gara
        distanze=[]
        for vv in range(itera):
            combo.select_by_value(values_list[vv])
            time.sleep(3)
            #clicco di nuovo sui risultati: devo cercarli nuovamente perchè l'oggetto contiene un'informazione di sessione
            risultati_xls,check=trova_risultati(possibili_xls)
            if risultati_xls.text=='PDF':
                print('solo pdf')
                break
            elif risultati_xls.text=='Altre classifiche':
                print('altre classifiche')
                break
            else:
                risultati_xls.click()
            time.sleep(3)
            #appare il disclaimer
            disclaimer=trova_possibili(possibili_discl)
            disclaimer.click()
            time.sleep(8)
            #rinomino il file
            rinomina_file(info[1],label_list[vv],folder_scarico)
            #devo cercare la distanza e clicco quindi sul primo
            primo=trova_possibili(possibili_primo)
            #per alcune selezioni della combo non c'è alcun risultato
            if primo!='nores':
                primo.click()
                time.sleep(4)
                dista=trova_possibili(possibili_dista)
                if type(dista)!=str:
                    distanze.append(dista.text)
                driver.back()
            else:
                print('niente primo')
        info.append(distanze)
        db_gare.append(info)
    else:
        print('risultati non disponibili')
        scartate.append([posizione,gara])
        print('scritto')


#caricol il file che contiene le url delle gare
gare_url=pickle.load(open(percorso+infile,'rb'))
db_gare=pickle.load(open(percorso+infile_db_gare,'rb'))
url_trattate_grezze=pickle.load(open(percorso+infile_trattate,'rb'))
#bisogna fare alcuni aggiustamenti:
    #la lista è nella forma [[1,url],[]..] la trasformo in [url, url,...]
    #devo togliere lo slash alla fine e it/ 
solo_url_trattate=list(map(lambda x: x[1].replace('it/',''),url_trattate_grezze))

#questi sono i possibili xpath relativi a scarica dati su excel
possibili_xls=['//*[@id="contenitore"]/div[1]/div[1]/div[1]/div[15]/div[2]/a[2]/div',
               '//*[@id="contenitore"]/div[1]/div[1]/div[1]/div[14]/div[2]/a[2]/div',
               '//*[@id="contenitore"]/div[1]/div[1]/div[1]/div[15]/div[2]/a/div']

possibili_combo=['/html/body/center/div/div/div[2]/div[1]/div[1]/div[1]/div[8]/div[1]/select',
                '/html/body/center/div/div/div[2]/div[1]/div[1]/div[1]/div[7]/div[1]/select',
                '//*[@id="contenitore"]/div[1]/div[1]/div[1]/div[7]/div[1]/select',
                '//*[@id="contenitore"]/div[1]/div[1]/div[1]/div[8]/div[1]/select']

possibili_primo=['/html/body/center/div/div/div[2]/div[1]/div[1]/div[1]/div[13]/div[1]/div[2]/div[2]/table/tbody/tr[1]/td[3]/a',
                 '//*[@id="ranksTable"]/tbody/tr[1]/td[3]/a']


possibili_dista=['//*[@id="dx1"]/div[2]/div[1]/div[9]/div[3]/div[19]/div/div[2]/span[2]/span[2]',
                 '//*[@id="dx1"]/div[2]/div[1]/div[9]/div[3]/div[9]/div/div[2]/span[2]/span[2]',
                 '//*[@id="dx1"]/div[2]/div[1]/div[9]/div[3]/div[7]/div/div[2]/span[2]/span[2]',
                 '//*[@id="dx1"]/div[2]/div[1]/div[9]/div[3]/div[3]/div/div[2]/span[2]/span[2]',
                 '//*[@id="dx1"]/div[2]/div[1]/div[9]/div[3]/div[2]/div/div[2]/span[2]/span[2]']

possibili_discl=['/html/body/div[9]/div/div/div[3]/a/span',
                 '/html/body/div[10]/div/div/div[3]/a/span',
                 '/html/body/div[12]/div/div/div[3]/a/span',
                 '/html/body/div[11]/div/div/div[3]/a/span']

possibili_acce=['/html/body/div[9]/div/div/div[2]/button[1]/span',
                '/html/body/div[10]/div/div/div[2]/button[1]/span',
                '/html/body/div[12]/div/div/div[2]/button[1]/span',
                '/html/body/div[11]/div/div/div[2]/button[1]/span']


spia_xls='XLS'
spia_nores='Risultati non disponibili'
spia_acc='ACCEDI'
spia_noacc='no'
spia_cookie='Continua senza accettare'

#accedo alla pagina dei risultati
#controllo se ci sono risultati disponibili
    #se no metto la url in una lista scartate e passo oltre
    #in caso contrario faccio click

scartate=pickle.load(open(percorso+infile_scartate,'rb'))

posizione=1
check=0
fatto_log=0
inizio=time.time()
for gara in gare_url[:]:
    if gara not in solo_url_trattate:
        URL=gara+coda
        try:
            tratta_url(driver,URL)
        except WebDriverException as e:
            # Handle WebDriver exceptions (e.g., network issues)
            print("WebDriverException:", e)
            print("Resuming after the last successful URL...")
            # Log the error, sleep for a while, or take other actions as needed
            time.sleep(10)  # Example: Wait for 10 seconds before resuming
            continue
        except Exception as e:
            # Handle other types of exceptions
            print("Other Exception:", e)
            # Log the error, sleep for a while, or take other actions as needed
            time.sleep(10)  # Example: Wait for 10 seconds before resuming
            continue
        else:
            # If no exception occurred, continue with the next URL
            print("Webpage scraped successfully:", URL)
        url_trattate_grezze.append([posizione,gara])
        pickle.dump(db_gare,open(percorso+'f_02_db_gare.pickle','wb'),protocol=4)
        pickle.dump(url_trattate_grezze,open(percorso+'f_03_url_trattate.pickle','wb'),protocol=4)
        pickle.dump(scartate,open(percorso+infile_scartate,'wb'),protocol=4)
        posizione+=1
    else:
        print('gia trattata')
driver.quit()
fine=time.time()
print('tempo trascorso {:.2f} secondi'.format(fine-inizio))
    

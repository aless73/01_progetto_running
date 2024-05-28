import numpy as np
import pickle
import time
import glob
import os
import pandas as pd

folder_risultati='01_file_risultati/'
percorso='D:/alessandro2/04_altri_hobby/03_manuale python/01_progetto_running/'
infile='f_01_gare_url.pickle'
infile_db_gare='f_02_db_gare.pickle'
infile_trattate='f_03_url_trattate.pickle'
infile_scartate='f_04_url_scartate.pickle'

#caricol il file che contiene le url delle gare
gare_url=pickle.load(open(percorso+infile,'rb'))
db_gare=pickle.load(open(percorso+infile_db_gare,'rb'))
url_trattate_grezze=pickle.load(open(percorso+infile_trattate,'rb'))
scartate=pickle.load(open(percorso+infile_scartate,'rb'))
#bisogna fare alcuni aggiustamenti:
    #la lista è nella forma [[1,url],[]..] la trasformo in [url, url,...]
    #devo togliere lo slash alla fine e it/ 
solo_url_trattate=list(map(lambda x: x[1],url_trattate_grezze))

nome_gare=list(map(lambda x: x[1],db_gare))
#può capitare che il numero di distanze [lista -1] sia inferiore al numero
#di competizioni diverse presenti nella lista +2
for ddd in db_gare:
    differenza=len(ddd[-2])-len(ddd[-1])
    if differenza>0:
        for _ in range(differenza):
            ddd[-1].append('nd')
            print('aggiunto distanza non disponibile') 

#####DA PULIRE LE DATE
#genero i nomi dei mesi in inglese e li combino con i numeri
import calendar
import locale
locale.setlocale(locale.LC_TIME, 'en_US.UTF-8')
month_names = calendar.month_name[1:]
month_numbers = ['{:02d}'.format(i) for i in range(1, 13)]
month_numbers=['-'+m+'-' for m in month_numbers]
nomi_numeri=dict(zip(month_names,month_numbers))
#faccio la stessa cosa per l'italiano
locale.setlocale(locale.LC_TIME, 'it_IT.UTF-8')
italian_month_names = calendar.month_name[1:]
nomi_numeri_italiano=dict(zip(italian_month_names,month_numbers))
#stringa da togliere
via=' (Date to be confirmed)'
#isolo le date
date_raw=list(map(lambda x: x[2],db_gare))
date_raw=list(map(lambda x: x.replace(via,'').replace('  ',''),date_raw))
#tolgo tutta la parte dall'inizio fino al carattere _ dove presente
date_raw = [s.split('_ ', 1)[-1] if '_' in s else s for s in date_raw]
for mm in range(len(month_names)):
    date_raw=list(map(lambda x: x.replace(month_names[mm],nomi_numeri[month_names[mm]]).replace(italian_month_names[mm],nomi_numeri_italiano[italian_month_names[mm]]), date_raw))
date_pulite=[m.replace(' ','') for m in date_raw]
#tratto due casi specifici di errori di data
date_pulite=[m.replace('2023','27-05-2023') if m=='2023'else m for m in date_pulite ]
###PER QUALCHE RAGIONE IGNOTA QUESTA ASSEGNAZIONE NON FUNZIONA
#date_pulite[date_pulite.index('2023')]='27-05-2023' a.replace('2023','27-05-2023')
#ci sono alcune date che hanno 2024 invece di 2023
#per trovarle seleziono quelle che hanno la data maggiore a 30-03-2024
date_ok = pd.to_datetime(date_pulite, format='%d-%m-%Y')
filtered_dates = date_ok[date_ok > '2024-03-30']
anomale=filtered_dates.strftime('%d-%m-%Y')
#per queste sostituisco 2024 con 2023
for ana in anomale:
    posizione=date_pulite.index(ana)
    date_pulite[posizione]=date_pulite[posizione].replace('2024','2023')
#rifaccio la trasformazione a datetime e riverifico che non ci siano più
date_ok = pd.to_datetime(date_pulite, format='%d-%m-%Y')
filtered_dates = date_ok[date_ok > '2024-03-30']

    
#bisogna isolare citta e provincia per ogni gara
luoghi_raw=list(map(lambda x: x[3],db_gare))
sigla_pr_raw=list(map(lambda x: x[-2:] if len(x)>2 and x[-3]==' ' or len(x)==2 else '' ,luoghi_raw))
comune_raw=list(map(lambda x: x[:-3] if len(x)>2 and x[-3]==' ' else '' ,luoghi_raw))
#tipi gara, url, e numero di distanse per gara
tipo=list(map(lambda x: x[4],db_gare))
url=list(map(lambda x: x[5],db_gare))
n_distanze=list(map(lambda x: x[6],db_gare))

###devo pensare ad un'altra procedura per la fase di aggiornamento
### che carica il df e aggiunge i dati
df_gare=pd.DataFrame({'nome':nome_gare,'luogo':luoghi_raw,'comune':comune_raw,
                      'provincia':sigla_pr_raw,'data':date_ok,'tipo':tipo,
                      'url':url,'n_distanze':n_distanze})

###forse è meglio farla dal dataframe in modo che quando faccio l'aggiornamento
##non devo unire due liste
##questo serve per ottenere l'anagrafica dei posti
luoghi_unici=sorted(list(set(luoghi_raw)))
luoghi_unici=[a for a in luoghi_unici if a!='']
sigla_pr_unici=sorted(list(set(sigla_pr_raw)))
comuni_unici=sorted(list(set(comune_raw)))
date_uniche=np.unique(date_ok)
#list(filter(lambda x: len(x)>2 and x[-3]!=' ',luoghi_unici))
#sigla_pr=list(map(lambda x: x[-2:] if len(x)>2 and x[-3]==' ' else '' ,luoghi_unici))
tipo_ana=list(set(tipo))


##salvo il db gare come gare trattate e lo azzero in modo che al passo successivo
## non vado a ritrattare le stesse gare
pickle.dump(db_gare,open(percorso+'f_05_db_gare_trattate.pickle','wb'),protocol=4)

def genera_nome(gara,distanza):        
    nuovo_nome=gara.replace(' ','_').replace('-','').replace(':','_').replace(',','_').replace('.','_').replace("\\", '').replace('|','').replace('"','').replace("\'", '')+'_'+distanza.replace(' ','_').replace('/','_').replace(':','_').replace(',','_').replace('.','_').replace("\\", '').replace('|','').replace('"','')+'.xls'
    return nuovo_nome

def genera_nome_bis(gara,distanza):
    #in questo non tolgo ' nel nome della gara        
    nuovo_nome_bis=gara.replace(' ','_').replace('-','').replace(':','_').replace(',','_').replace('.','_').replace("\\", '').replace('|','').replace('"','')+'_'+distanza.replace(' ','_').replace('/','_').replace(':','_').replace(',','_').replace('.','_').replace("\\", '').replace('|','').replace('"','')+'.xls'
    return nuovo_nome_bis

#devo creare un identificativo univoco unendo nome della gara e data 
# al riferimento del file che serve per caricare il file relativo
# metto quindi in testa:
    #(data+nomefile),(nomefile),(nomegara),(distanza),(risultati)

colonne_risultati=['id', 'nome_gara', 'distanza','POS_ASSOLUTA', 'PETTORALE', 'COGNOME', 'NOME', 'TEAM',
       'NAZIONALITA', 'CATEGORIA', 'POS_CAT', 'POS_SESSO',
       'TEMPO_UFFICIALE', 'percentile','tempo_vs_1']
df_risultati_gare=pd.DataFrame(columns=colonne_risultati)
dummy_date = '1970-01-01 '
cont=0
lista_file=glob.glob(percorso+folder_risultati+'*')
lista_file=[a.replace('D:/alessandro2/04_altri_hobby/03_manuale python/01_progetto_running/01_file_risultati\\','') for a in lista_file]
file_trattati=[]
file_scartati=[]
for gg in range(len(db_gare[:])):
    #gg=144
    gara=db_gare[gg][1]
    for dd in range(len(db_gare[gg][-2]))[:]:
        cont+=1
        nome_file=genera_nome(gara,db_gare[gg][-2][dd])
        #per alcuni file è stata tenuta la ' nel nome in queto caso genero un nuovo nome con la '
        if nome_file not in lista_file:
            nome_file=genera_nome_bis(gara,db_gare[gg][-2][dd])
        print(cont, nome_file)
        identificativo=date_pulite[gg]+nome_file
        distanza=db_gare[gg][-1][dd]
        print(identificativo)
        print(distanza)
        try:
            transito=pd.read_excel(percorso+folder_risultati+nome_file)
            #togliere colonna pt e DISTACCO e inserire POS_CAT se non presente
            if len(transito)==0:
                print('zero valori')
                continue
            cole=transito.columns.values
            if 'DISTACCO' in cole:
                del transito['DISTACCO']
            if 'pt' in cole:
                del transito['pt']
            if 'POS_CAT' not in cole:
                transito['POS_CAT']=pd.Series([0]*len(transito))
            if 'CATEGORIA' not in cole:
                transito['CATEGORIA']=pd.Series(['']*len(transito))
            if 'POS_SESSO' not in cole:
                transito['POS_SESSO']=pd.Series([0]*len(transito))
            #siccome in molti casi la posizione assoluta non considera gli atleti tesserati
            #per una squadra straniera la sostituisco con l'index. In alcuni casi non c'è proprio
            transito['POS_ASSOLUTA']=transito.index+1
            #nei casi in cui c'è 0h o 1h lo sostituisco con 00
            transito.TEMPO_UFFICIALE=transito.TEMPO_UFFICIALE.astype(str)
            transito.TEMPO_UFFICIALE=transito.TEMPO_UFFICIALE.map(lambda x: x.replace('0h','00').replace('1h','01').replace('2h','02').replace('3h','03').replace('4h','04').replace('5h','05').replace('6h','06').replace('(+1d) ','1970-01-02 ').replace('(+2d) ','1970-01-03 ').replace('(+3d) ','1970-01-04 ').replace('(+4d) ','1970-01-05 ').replace('(+45228d) ','').replace('nan','00:00:00'))
            transito.TEMPO_UFFICIALE=transito.TEMPO_UFFICIALE.map(lambda x: x.split('.')[0])
            transito.TEMPO_UFFICIALE=transito.TEMPO_UFFICIALE.map(lambda x: '00:'+x if len(x)==5 else x)
            transito.TEMPO_UFFICIALE=transito.TEMPO_UFFICIALE.map(lambda x: '0'+x if len(x)==7 else x)
            transito.TEMPO_UFFICIALE = transito.TEMPO_UFFICIALE.map(lambda x: dummy_date+x if len(x)==8 else x)
            transito.TEMPO_UFFICIALE = pd.to_datetime(transito.TEMPO_UFFICIALE, format='%Y-%m-%d %H:%M:%S')
            transito['percentile']=(transito.index+1)/len(transito)*100
            valore=pd.to_datetime('1970-01-01 00:00:00',format='%Y-%m-%d %H:%M:%S')
            numeratore=(transito.TEMPO_UFFICIALE-valore).dt.total_seconds()
            transito['tempo_vs_1']=numeratore/min(numeratore)
            transito['id']=pd.Series([identificativo]*len(transito))
            transito['nome_gara']=pd.Series([gara]*len(transito))
            transito['distanza']=pd.Series([distanza]*len(transito))
            transito=transito[colonne_risultati]
            df_risultati_gare=pd.concat([df_risultati_gare,transito])
            file_trattati.append(nome_file)
        except FileNotFoundError:
            file_scartati.append(nome_file)
            print('risultati non disponibili per ', nome_file)

tutti=file_trattati.copy()
tutti.extend(file_scartati)

mancanti=[a for a in lista_file if a not in tutti]
df_nome_gara=pd.DataFrame({'nome_gara':nome_gare})
df_mancanti=pd.DataFrame({'mancante':mancanti})
df_tutti=pd.DataFrame({'url':tutti})

#df_nome_gara.to_excel('nome_gare.xls')
#df_mancanti.to_excel('mancanti.xls')
#df_tutti.to_excel('tutti.xls')
#df_risultati_gare.to_excel('prova.xls')
####elementi da salvare alla fine dell'elaborazione
#anagrafiche
anagrafiche={'luoghi':luoghi_unici,'sigla_pr':sigla_pr_unici,'comuni':comuni_unici,
             'date':date_uniche,'tipi_gare':tipo_ana,'nome_gare':nome_gare}
pickle.dump(anagrafiche,open(percorso+'f_06_anagrafiche.pickle','wb'),protocol=4)
#df_gare
pickle.dump(df_gare,open(percorso+'f_07_df_gare.pickle','wb'),protocol=4)
#df_risultati_gare
pickle.dump(df_risultati_gare,open(percorso+'f_08_df_risultati_gare.pickle','wb'),protocol=4)

#####RICORDARSI QUESTO
#azzero il db_gare in modo che al giro successivo non vado a trattare le stesse gare
db_gare=[]
pickle.dump(db_gare,open(percorso+'f_02_db_gare.pickle','wb'),protocol=4)


####PASSI SUCCESSIVI DA FARE
#URL da reinserire nel prossimo giro di aggiornamento
nnn='https://www.endu.net/events/scarpa-doro-half-marathon-2'
#scrivere una nuova procedura per la generazione del nome dei file 
#deve prendere solo la parte alfanumerica delle stringhe dei nomi delle gare e delle distanze
#creare un'altro file che tratta solo il nuovo db_gare e aggiorna i df esistenti


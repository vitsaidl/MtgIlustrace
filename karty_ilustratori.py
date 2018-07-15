# -*- coding: utf-8 -*-
"""
Created on Wed Apr 11 16:25:00 2018

@author: VS
"""
from bs4 import BeautifulSoup
import requests
import pandas as pd
from PIL import Image, ImageTk as PIIIL
from tkinter import *
from tkinter import ttk
from tkinter import filedialog


def nactiStranku(jmeno, poradCislo):
    stranka1 = "http://gatherer.wizards.com/Pages/Search/Default.aspx?page="
    stranka2 = "&action=advanced&artist=+[\""
    stranka3 = "\"]"
    strankaKomplet = stranka1 + poradCislo+stranka2+ jmeno + stranka3
    dataStrany = requests.get(strankaKomplet)
    soup = BeautifulSoup(dataStrany.content)
    return soup
    
#http://gatherer.wizards.com/Pages/Search/Default.aspx?action=advanced&artist=+["Rebecca Guay"]

def vytvorTabulkuKaret(jmeno):
    tabulka = pd.DataFrame(columns = ("Nazev karty", "Edice", "Odkaz"))
    celkovaDelka = 0   #aby se tabulka rozsirovala a ne prepisovala
    cisloPage = 0
    jmenoPrvniKarty = "Bugbug, the problem maker"#na ukonceni nekonecne smycky
    while(True):
        polevka = nactiStranku(jmeno,str(cisloPage))
        souborJmen = polevka.find_all("span", class_="cardTitle") #vezme vše v tazích span, které mají class atribut rovný "cardTitle"
        souborEdic = polevka.find_all("td", class_="rightCol setVersions")
        souborOdkazuObrazku = polevka.find_all("td", class_="leftCol")
        
        delka = 0   #sem se uklada delka aktualni stranky
        delka = len(souborJmen)
        print(delka)
        cisloPage = cisloPage +1
        if delka ==0: break  #pro ilustrátory mající méně než 100 karet; tehdy totiž další stránka není kopií předchozí, ale je prázdná
        if jmenoPrvniKarty==(souborJmen[0].get_text()).lstrip(): break
        jmenoPrvniKarty = (souborJmen[0].get_text()).lstrip()
        
        for i in range(0,delka):
            jmenoKarty = (souborJmen[i].get_text()).lstrip()  #vytahá text tagem sevřený, lstrip vyhodí prázdné znaky na začátku strinku (zde /n)
            jmenoEdice = souborEdic[i].img["alt"] #v td tagu najde tag img a z něj vytáhne hodnotu atributu "alt"
            jmenoEdice = jmenoEdice.replace("(Common)","")      #nahrazení rarity bílým místem
            jmenoEdice = jmenoEdice.replace("(Uncommon)","")
            jmenoEdice = jmenoEdice.replace("(Rare)","")
            jmenoEdice = jmenoEdice.replace("(Mythic Rare)","")
            jmenoEdice = jmenoEdice.replace("(Land)","")
            odkaz = souborOdkazuObrazku[i].img["src"]
            odkaz = odkaz.replace("../../","http://gatherer.wizards.com/")
            #print(jmenoKarty)
            tabulka.loc[celkovaDelka + i] = [jmenoKarty, jmenoEdice, odkaz]
            
        celkovaDelka = celkovaDelka + delka
       
    return tabulka

#handlery eventů
def vybranaKarta(*args):    #bez buďto paraetru self, nebo *args to hází errory
    global seznamKaret    #aby se nevytvořila lokální proměnná
    indexVybraneKarty = seznamKaret.current()
    popisekEdice.config(text = tabulkaKaret["Edice"].values.tolist()[indexVybraneKarty])
    novaUrl = tabulkaKaret["Odkaz"].values.tolist()[indexVybraneKarty]
    newObrazekPIL = PIIIL.Image.open(requests.get(novaUrl, stream=True).raw)
    newObrazek2 = PIIIL.PhotoImage(newObrazekPIL) 
    prvek_s_obr.config(image =newObrazek2 )
    prvek_s_obr.image =  newObrazek2 #nechápu, ale bez tohodle by se starý obrázek asi správně nevyhodil (garbage collection) a nový by se nezobrazil, viz https://stackoverflow.com/questions/37270359/image-not-displaying-in-python-tkinter-in-ui
    tlacitkoUloz.config(state ="normal") #odblokování ukládacího tlačítka

def vybranyIlustrator(*args):
    global seznamIlustratoru
    global tabulkaKaret
    global seznamKaret
    jmeno = seznamIlustratoru.get()
    tabulkaKaret = vytvorTabulkuKaret(jmeno)
    seznamKaret["values"]=tabulkaKaret["Nazev karty"].values.tolist()
    tlacitkoUloz.config(state =DISABLED) #zablokování ukládacího tlačítka
    
def ulozObrazek(*args):
    global seznamKaret
    indexVybraneKarty = seznamKaret.current()
    novaUrl = tabulkaKaret["Odkaz"].values.tolist()[indexVybraneKarty]
    newObrazekPIL = PIIIL.Image.open(requests.get(novaUrl, stream=True).raw)
    jmenoSouboru = filedialog.asksaveasfilename(defaultextension = "png",filetypes= [("png",".png")],  initialfile = tabulkaKaret["Nazev karty"].values.tolist()[indexVybraneKarty])
    if jmenoSouboru != "" : newObrazekPIL.save(jmenoSouboru)  #při zmáčknutí Cancel totiž dialog vrátí ""



tabulkaKaret = vytvorTabulkuKaret("Rebecca Guay")
root = Tk()     #vytvoření základního okna, jelikož ale v tomhle nemůžou být specializované widgety, musí se udělat mainframe jako dítě rootu
root.title("Kolekce ilustrací")  #název okna

mainframe = ttk.Frame(root, padding=(3, 3, 12, 12))
mainframe.grid(column=0, row=0, sticky=(N, W, E, S))
mainframe.columnconfigure(0, weight=1)
mainframe.rowconfigure(0, weight=1)

seznamIlustratoru =  ttk.Combobox(mainframe, values=("Rebecca Guay","Terese Nielsen", "John Avon", "Johannes Voss"), state = "readonly", width = 30)
seznamIlustratoru.grid(column=0, row=0)
seznamIlustratoru.bind("<<ComboboxSelected>>", vybranyIlustrator )
seznamIlustratoru.set("Rebecca Guay")

seznamKaret = ttk.Combobox(mainframe, values=tabulkaKaret["Nazev karty"].values.tolist(), state = "readonly", width = 30)
seznamKaret.grid(column=0, row=11)
seznamKaret.bind("<<ComboboxSelected>>", vybranaKarta )
seznamKaret.set("Název karty")

popisekEdice = ttk.Label(mainframe, text="Popisek edice")
popisekEdice.grid(column=0, row=12)

#obrazek = PhotoImage(file='C:\\vs\\slunicko.gif') #takhle pomocí interních metok tkinteru to jde ale jen pro gify...
obrazekPIL = PIIIL.Image.open("default.jpg")  #obrázek se otevře pomocí PILu
obrazek2 = PIIIL.PhotoImage(obrazekPIL)         #a zkonvertuje se do něčeho, s čím si už tkinter poradí
prvek_s_obr = ttk.Label(mainframe, image = obrazek2)
prvek_s_obr.grid(column=0, row=1, rowspan = 10)

tlacitkoUloz = ttk.Button(mainframe, text = "Ulož obrázek",command = ulozObrazek, state = DISABLED)
tlacitkoUloz.grid(column = 0, row = 13)

root.mainloop()   
  


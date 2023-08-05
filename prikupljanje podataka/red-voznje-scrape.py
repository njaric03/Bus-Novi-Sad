import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.common.exceptions import WebDriverException
import time
import re

url = "http://www.gspns.rs/red-voznje/{}"

oblasti = {"gradski": 1, "prigradski": 2}
dani = {"radni dan" : 1, "subota" : 2, "nedelja" : 3}

df = pd.DataFrame(columns=["ID linije", "Smer", "Lista polazaka", "Dan"])

driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
driver.maximize_window()
driver.get(url.format("gradski"))

#menjanje dana
def promeni_dan(dan):
    try:
        driver.find_element(By.CSS_SELECTOR, '#dan > option:nth-child({})'.format(dani[dan])).click()
    except:
        pass


#otvori sve linije
def otvori_sve_linije():
    br_linija = len(driver.find_elements(By.CSS_SELECTOR, '#linija > option'))
    for linija in range(1, br_linija + 1):
        try:
            driver.find_element(By.CSS_SELECTOR, '#linija > option:nth-child({})'.format(linija)).click()
        except WebDriverException:
            pass
    try:
        driver.find_element(By.CSS_SELECTOR, '#rvform > button').click()
    except WebDriverException:
        pass

#menjanje oblasti
def promeni_oblast(oblast):
    try:
        driver.find_element(By.CSS_SELECTOR, '#rv > option:nth-child({})'.format(oblast)).click()
    except WebDriverException:
        pass

#svi polasci za dati dan i liniju
def get_polasci_oblast(dan, oblast):
    promeni_oblast(oblasti[oblast])
    time.sleep(0.5)
    promeni_dan(dani[dan])
    time.sleep(0.5)
    otvori_sve_linije()
    time.sleep(0.5)
    imena_linija = [element.text.split('\n') for element in driver.find_elements(By.CSS_SELECTOR, '#ispis-polazaka > div')]
    linije = []
    for linija in imena_linija:
        linije.append(linija[0])
        linije.append(linija[0])
    smerovi = ['Smer A' if i % 2 == 0 else 'Smer B' for i in range(len(linije))]
    lista_listi_polazaka = []
    for i in range(int(len(linije) / 2)):
        svi_elementi = driver.find_elements(By.CSS_SELECTOR, '#ispis-polazaka > table')[0].text.split("\n")
        polasci = [element for element in svi_elementi if element and element[0].isdigit()] 
        polasci_sredjeno = []
        for polazak in polasci:
            polazak = re.sub("[^0-9]", "", polazak)
            sat = polazak[0:2]
            for i in range(2, len(polazak), 2):
                polasci_sredjeno.append(sat + ":" + polazak[i:i+2])
        polasci_a = []
        polasci_b = []
        promeni_smer = False
        for p in range(1, len(polasci_sredjeno)):
            if (polasci_sredjeno[p - 1] > '12:00' or polasci_sredjeno[p - 1] < '03:00') and (polasci_sredjeno[p] > '03:00' or polasci_sredjeno[p] < '12:00'):
                promeni_smer = True            
            if not promeni_smer:
                polasci_a.append(polasci_sredjeno[p])
            else:
                polasci_b.append(polasci_sredjeno[p])
        lista_listi_polazaka.append(polasci_a)
        lista_listi_polazaka.append(polasci_b)
    print(len(linije), len(smerovi), len(lista_listi_polazaka))
    df = pd.DataFrame({"ID linije": linije, "Smer": smerovi, "Lista polazaka": lista_listi_polazaka})
    df['Dan'] = dan
    df.to_csv("raspored.csv", mode='a', index=False)

def get_polasci(dan):
    get_polasci_oblast(dan, "gradski")
    get_polasci_oblast(dan, "prigradski")

#svi polasci za sve dane i linije
def get_raspored():
    for dan in dani:
        get_polasci(dan)

get_raspored()
driver.quit()
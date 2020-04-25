from bs4 import BeautifulSoup
import csv
import io
import pandas as pd
import re
from datetime import date
from datetime import datetime
import requests
from colorama import Back, Fore, Style

# With this function I make the webscrapping I need to extract the data from the tarifaluzahora website
def scrapping (tarifa, day = str(date.today())):
    
    # Web to scrap
    url = 'https://tarifaluzhora.es/?tarifa=' + tarifa
    page = requests.get(url)
    soup = BeautifulSoup(page.text, "html.parser")
    
    # Web scraping to price & description
    price_ = soup.findAll("span", {"itemprop": "price"})
    hours_ = soup.findAll("span", {"itemprop": "description"})
    
    # Get the values of price & hours with a for loop
    price_hour_ = [price.get_text() for price in price_]
    schedule_ = [time.get_text() for time in hours_]
    
    # I've created a dataframe, its name is DF and it has two columns at the moment
    df = pd.DataFrame.from_dict({'precio':price_hour_,'horario':schedule_})
    
    # I have created two more columns, Time contains the 2nd digit of the time column, 
    # to be able to operate with the hours if necessary.
    # ‘Fare' contains the chosen fare
    df['hora'] = [int(x[:2]) for x in df['horario']]
    df['tarifa'] = tarifa
    df['minimo'] = df['precio'].min()
    df['precio'] =  [re.sub(r'/[k][W][h]','', str(x)) for x in df['precio']]
    #df['precio'] =  [re.sub(r'\€\/[k][W][h]','', str(x)) for x in df['precio']]
    df['horario'] =  [re.sub(r'[:]','', str(x)) for x in df['horario']]
    #df['minimo'] =  [re.sub(r'\€\/[k][W][h]','', str(x)) for x in df['minimo']]
    
    return df

def main():
    print("¿Sobre qué tarifa quieres saber el precio más económico?")
    choice = input(Fore.CYAN + "Puedes elegir entre: coche_electrico, normal, discriminacion ")
    #choice = input(Fore.WHITE + "¿De qué tarifa quieres saber el precio? ")

    #if choice == "coche_electrico":
    df = scrapping(choice)
    df = df.filter(items = ['tarifa', 'precio','hora'])
    df = df.groupby("precio").min().reset_index()

    if df['hora'][0] <= 12: 
        print(Fore.GREEN + f"El precio más barato para la tarifa {choice} es de, {df.precio[0]} y la hora a la {df.hora[0]} am.")
        print(Style.RESET_ALL)
    else:
        print(Fore.GREEN + f"El precio más barato para la tarifa {choice} es de, {df.precio[0]} y la hora a las {df.hora[0]} pm.")
        print(Style.RESET_ALL)

if __name__ == "__main__":
    main()
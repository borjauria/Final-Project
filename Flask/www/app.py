import pandas as pd
import re
import requests
from datetime import date
from flask import request
from flask import Flask, render_template, redirect
from datetime import datetime
from bs4 import BeautifulSoup

app = Flask(__name__)

@app.route('/')
@app.route('/home', methods=['GET','POST'])
def scrapping():
    global df, coche_electrico_choice, normal_choice, discriminacion_choice
    coche_electrico_choice = None
    normal_choice = None
    discriminacion_choice = None
    if request.form.get('coche_electrico'):
        coche_electrico_choice = request.form['coche_electrico']
        url = 'https://tarifaluzhora.es/?tarifa=' + coche_electrico_choice
        page = requests.get(url)
        soup = BeautifulSoup(page.text, "html.parser")
        price_ = soup.findAll("span", {"itemprop": "price"})
        hours_ = soup.findAll("span", {"itemprop": "description"})
        price_hour_ = [price.get_text() for price in price_]
        schedule_ = [time.get_text() for time in hours_]
        df = pd.DataFrame.from_dict({'precio':price_hour_,'horario':schedule_})
        df['hora'] = [int(x[:2]) for x in df['horario']]
        df['tarifa'] = coche_electrico_choice
        df['precio'] =  [re.sub(r'/[k][W][h]','', str(x)) for x in df['precio']]
        df['horario'] =  [re.sub(r'[:]','', str(x)) for x in df['horario']]
        df = df.filter(items = ['tarifa', 'precio','hora'])
        df = df.groupby("precio").min().reset_index()
        return redirect('/tarifas')

    elif request.form.get('normal'):
        normal_choice = request.form['normal']
        url = 'https://tarifaluzhora.es/?tarifa=' + normal_choice
        page = requests.get(url)
        soup = BeautifulSoup(page.text, "html.parser")
        price_ = soup.findAll("span", {"itemprop": "price"})
        hours_ = soup.findAll("span", {"itemprop": "description"})
        price_hour_ = [price.get_text() for price in price_]
        schedule_ = [time.get_text() for time in hours_]
        df = pd.DataFrame.from_dict({'precio':price_hour_,'horario':schedule_})
        df['hora'] = [int(x[:2]) for x in df['horario']]
        df['tarifa'] = normal_choice
        df['precio'] =  [re.sub(r'/[k][W][h]','', str(x)) for x in df['precio']]
        df['horario'] =  [re.sub(r'[:]','', str(x)) for x in df['horario']]
        df = df.filter(items = ['tarifa', 'precio','hora'])
        df = df.groupby("precio").min().reset_index()
        return redirect('/tarifas')


    elif request.form.get('discriminacion'):
        discriminacion_choice = request.form['discriminacion']
        url = 'https://tarifaluzhora.es/?tarifa=' + discriminacion_choice
        page = requests.get(url)
        soup = BeautifulSoup(page.text, "html.parser")
        price_ = soup.findAll("span", {"itemprop": "price"})
        hours_ = soup.findAll("span", {"itemprop": "description"})
        price_hour_ = [price.get_text() for price in price_]
        schedule_ = [time.get_text() for time in hours_]
        df = pd.DataFrame.from_dict({'precio':price_hour_,'horario':schedule_})
        df['hora'] = [int(x[:2]) for x in df['horario']]
        df['tarifa'] = discriminacion_choice
        df['precio'] =  [re.sub(r'/[k][W][h]','', str(x)) for x in df['precio']]
        df['horario'] =  [re.sub(r'[:]','', str(x)) for x in df['horario']]
        df = df.filter(items = ['tarifa', 'precio','hora'])
        df = df.groupby("precio").min().reset_index()
        return redirect('/tarifas')
    else:
        return render_template('home.html')

@app.route("/tarifas")
def tarifas():
    if coche_electrico_choice != None:
        return render_template('tarifas.html', choice=coche_electrico_choice, precio=df['precio'], hora=df['hora'])
    elif normal_choice != None:
        return render_template('tarifas.html', choice=normal_choice, precio=df['precio'], hora=df['hora'])
    elif discriminacion_choice != None:
        return render_template('tarifas.html', choice=discriminacion_choice, precio=df['precio'], hora=df['hora'])

if __name__ == '__main__':
    app.run()
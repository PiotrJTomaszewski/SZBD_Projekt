from flask import Flask, render_template, request, flash, redirect, url_for
import mysql.connector as db
import data_generators.create_workers as creator

from pages_show import show
from pages_show_info import show_info
from pages_add import add
from pages_edit import edit
from pages_assign import assign

# Register blueprints
app = Flask(__name__)
app.register_blueprint(show)
app.register_blueprint(show_info)
app.register_blueprint(add)
app.register_blueprint(edit)
app.register_blueprint(assign)

conn_args = {'host': 'localhost', 'database': 'sbdbazadanych', 'user': 'db_projekt', 'password': 'db_projekt'}

app.secret_key = 'Super secret key. Please don\'t look at it :)'

workers = creator.gen_workers_dict(10)

dane = {
    'oddzialy': [{'adres': 'Marcelińska', 'nazwa': 'Oddział Główny'},
                 {'adres': 'Rybaki', 'nazwa': 'Oddział Komunikacyjny'}],
    'budynki': [
        {'adres': 'Marcelińska 5', 'nazwa': 'Budynek A', 'liczba_pieter': 1, 'oddzial': {'adres': 'Konopnickiej'}},
        {'adres': 'Marcelińska 6', 'nazwa': 'Budynek B', 'liczba_pieter': 2, 'oddzial': {'adres': 'JeszczeJedna'}},
        {'adres': 'Rybaki 14', 'nazwa': 'Call-center', 'liczba_pieter': 4, 'oddzial': {'adres': 'Testowa'}}],
    'magazyny': [{'numer': 1, 'oddzial': {'adres': 'Marcelińska'}, 'pojemnosc': 3},
                 {'numer': 2, 'oddzial': {'adres': 'Marcelińska'}, 'pojemnosc': 20},
                 {'numer': 3, 'oddzial': {'adres': 'Rybaki'}, 'pojemnosc': 12},
                 {'numer': 4, 'oddzial': {'adres': 'Rybaki'}, 'pojemnosc': 30}],
    'dzialy': [{'nazwa': 'Human Relations', 'skrot': 'HR', 'oddzial': {'adres': 'Testowa'}},
               {'nazwa': 'Information Technology', 'skrot': 'IT', 'oddzial': {'adres': 'NieTestowa'}}],
    'biura': [{'numer': 1, 'budynek': {'adres': 'Marcelińska 5'}, 'liczba_stanowisk': 23, 'pietro': 31},
              {'numer': 12, 'budynek': {'adres': 'Rybaki 14'}, 'liczba_stanowisk': 512, 'pietro': 777}],
    'sprzety': [
        {'numer': 1, 'typ': 'laptop', 'nazwa': 'Testowa nazwa', 'producent': 'Testowy producent',
         'data_zakupu': '01/12/2019',
         'numer_magazynu': 1, 'data_przyznania': '11/12/2019'},
        {'numer': 4, 'typ': 'telefon', 'nazwa': 'Lorem Impsum', 'producent': 'Lorem Impsum',
         'data_zakupu': '03/12/2019',
         'numer_magazynu': 2, 'data_przyznania': '01/11/2016'}]
}


# TODO: Dodać wyświetlanie listy sprzętu i oprogramowania

def read_from_database(what):
    conn = db.connect(**conn_args)
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM ' + what)
    cols = [i[0].upper() for i in cursor.description]
    rows = cursor.fetchall()
    conn.close()
    return cols, rows


@app.route('/')
def tmp_root():
    strony = ['dodaj_oddzial', 'dodaj_magazyn', 'dodaj_sprzet', 'dodaj_oprogramowanie', 'dodaj_pracownika',
              'dodaj_budynek', 'dodaj_dzial']
    return render_template('tmp/tymczasowy_index.html', strony=strony)


if __name__ == '__main__':
    app.run(debug=True)

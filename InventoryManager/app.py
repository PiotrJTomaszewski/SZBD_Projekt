from flask import Flask, render_template
import mysql.connector as db
import data_generators.create_workers as creator

app = Flask(__name__)

conn_args = {'host': 'localhost', 'database': 'sbdbazadanych', 'user': 'db_projekt', 'password': 'db_projekt'}

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


@app.route('/pracownicy')
def pracownicy():
    # col_names, rows = read_from_database('pracownik')
    pracownicy = workers
    for i in range(len(pracownicy)):
        if pracownicy[i]['czy_nadal_pracuje'] == '1':
            pracownicy[i]['czy_nadal_pracuje'] = 'Tak'
        else:
            pracownicy[i]['czy_nadal_pracuje'] = 'Nie'
    return render_template('show/pokaz_pracownicy.html', pracownicy=pracownicy)


@app.route('/biura')
def biura():
    biura = [{'numer': i['numer'], 'budynek': i['budynek'],
              'pietro': 3, 'liczba_stanowisk': 12} for i in dane['biura']]
    return render_template('show/pokaz_biura.html', biura=biura)


@app.route('/oddzialy')
def oddzialy():
    oddzialy = dane['oddzialy']
    # col_names, rows = read_from_database('oddzial')
    return render_template('show/pokaz_oddzialy.html', oddzialy=oddzialy)


@app.route('/dzialy')
def dzialy():
    dzialy = dane['dzialy']
    return render_template('show/pokaz_dzialy.html', dzialy=dzialy)


@app.route('/budynki')
def budynki():
    budynki = dane['budynki']
    return render_template('show/pokaz_budynki.html', budynki=budynki)


@app.route('/magazyny')
def magazyny():
    magazyny = dane['magazyny']
    return render_template('show/pokaz_magazyny.html', magazyny=magazyny)


@app.route('/')
def hello_world():
    strony = ['dodaj_oddzial', 'dodaj_magazyn', 'dodaj_sprzet', 'dodaj_oprogramowanie', 'dodaj_pracownika',
              'dodaj_budynek', 'dodaj_dzial']
    return render_template('tmp/tymczasowy_index.html', strony=strony)


@app.route('/dodaj_oddzial')
def dodaj_oddzial():
    return render_template('add_modify/dodaj_oddzial.html')


@app.route('/dodaj_magazyn')
def dodaj_magazyn():
    oddzialy = ['Testowa', 'Kwiatowa', 'Krótka']
    return render_template('add_modify/dodaj_magazyn.html', oddzialy=oddzialy)


@app.route('/dodaj_sprzet')
def dodaj_sprzet():
    domyslne = {'numer_ewidencyjny': 15, 'data_zakupu': '2019-12-16'}
    magazyny = dane['magazyny']
    typy = {'laptop', 'telefon'}
    return render_template('add_modify/dodaj_sprzet.html', magazyny=magazyny, domyslne=domyslne, typy=typy)


@app.route('/dodaj_oprogramowanie')
def dodaj_oprogramowanie():
    domyslne = {'numer_ewidencyjny': 15, 'data_zakupu': '2019-12-16'}
    return render_template('add_modify/dodaj_oprogramowanie.html', domyslne=domyslne)


@app.route('/dodaj_pracownika')
def dodaj_pracownika():
    dzialy = dane['dzialy']
    biura = dane['biura']
    return render_template('add_modify/dodaj_pracownika.html', biura=biura, dzialy=dzialy)


@app.route('/dodaj_budynek')
def dodaj_budynek():
    oddzialy = [i[0] for i in dane['oddzialy']]
    return render_template('add_modify/dodaj_budynek.html', oddzialy=oddzialy)


@app.route('/dodaj_dzial')
def dodaj_dzial():
    oddzialy = [i[0] for i in dane['oddzialy']]
    return render_template('add_modify/dodaj_dzial.html', oddzialy=oddzialy)


@app.route('/dodaj_biuro')
def dodaj_biuro():
    pass


@app.route('/pokaz_pracownik_info/<pesel>')
def pokaz_pracownik_info(pesel):
    pracownik = workers[0]
    pracownik['czy_nadal_pracuje'] = 'Tak'
    sprzety = dane['sprzety']
    karty_dostepu = [
        {'id': 123, 'data_przyznania': '12/11/2019', 'prawa_dostepu': [
            {'data_przyznania': '04/12/2019', 'data_wygasniecia': '04/12/2020', 'biuro': {'numer': 23},
             'budynek': {'adres': dane['budynki'][0]['adres']}},
            {'data_przyznania': '04/12/2019', 'data_wygasniecia': '04/12/2020', 'biuro': {'numer': 33},
             'budynek': {'adres': dane['budynki'][1]['adres']}}]}
    ]
    return render_template('show_info/pokaz_pracownik_info.html', sprzety=sprzety, pracownik=pracownik,
                           karty_dostepu=karty_dostepu)


@app.route('/pokaz_sprzet_info/<numer_ewidencyjny>')
def pokaz_sprzet_info(numer_ewidencyjny):
    oprogramowania = [{'numer': 51, 'nazwa': 'Office 2012', 'producent': 'Microsoft', 'data_zakupu': '01/02/2013',
                       'data_wygasniecia': '05/06/2020'},
                      {'numer': 64, 'nazwa': 'Windows 10', 'producent': 'Microsoft', 'data_zakupu': '04/02/2019',
                       'data_wygasniecia': '01/06/2025'}]
    sprzet = {'numer': numer_ewidencyjny, 'typ': 'laptop', 'nazwa': 'Latitude 6231', 'producent': 'DELL',
              'data_zakupu': '03/02/2012',
              'stan': {'gdzie': 'pracownik', 'id': '4312351234', 'text': 'Paweł Testowy (4312351234)'},
              'uwagi': 'Uszkodzony'}

    return render_template('show_info/pokaz_sprzet_info.html', sprzet=sprzet, oprogramowania=oprogramowania)


@app.route('/pokaz_oprogramowanie_info/<numer_ewidencyjny>')
def pokaz_oprogramowanie_info(numer_ewidencyjny):
    oprogramowanie = {'numer': 51, 'nazwa': 'Office 2012', 'producent': 'Microsoft', 'data_zakupu': '01/02/2013',
                      'data_wygasniecia': '05/06/2020', 'liczba_licencji': 'Nieograniczona', 'uwagi': 'Brak'}
    sprzety = dane['sprzety']
    return render_template('/show_info/pokaz_oprogramowanie_info.html', oprogramowanie=oprogramowanie, sprzety=sprzety)


@app.route('/pokaz_biuro_info/<numer_biura>')
def pokaz_biuro_info(numer_biura):
    biuro = {'numer': numer_biura, 'budynek': {'nazwa': 'ASD', 'adres': 'Testowa 8'}, 'pietro': 4,
             'liczba_stanowisk': 3,
             'oddzial': {'nazwa': 'asd', 'adres': 'Testowa'}}
    pracownicy = [{'pesel': '328648918623', 'imie': 'Pawel', 'nazwisko': 'Pawlowski', 'dzial': {'nazwa': 'IT'},
                   'numer_telefonu': '4123124124', 'adres_email': 'asdasf@awe.com'},
                  {'pesel': '328648918623', 'imie': 'Pawel', 'nazwisko': 'Pawlowski', 'dzial': {'nazwa': 'IT'},
                   'numer_telefonu': '4123124124', 'adres_email': 'asdasf@awe.com'}]
    dostepy = [{'karta': {'numer': 13, 'data_przyznania': '02/02/2013'}, 'data_przyznania': '01/12/2019',
                'data_wygasniecia': '12/12/2019',
                'pracownik': {'pesel': 21352134, 'imie': 'Łukasz', 'nazwisko': 'Cezary'}}]
    sprzety = dane['sprzety']
    return render_template('show_info/pokaz_biuro_info.html', biuro=biuro, pracownicy=pracownicy, dostepy=dostepy,
                           sprzety=sprzety)


@app.route('/pokaz_oddzial_info/<adres>')
def pokaz_oddzial_info(adres):
    oddzial = dane['oddzialy'][0]
    return render_template('show_info/pokaz_oddzial_info.html', oddzial=oddzial, dzialy=dane['dzialy'],
                           magazyny=dane['magazyny'], budynki=dane['budynki'])


@app.route('/pokaz_dzial_info/<nazwa>')
def pokaz_dzial_info(nazwa):
    dzial = {'nazwa': 'Information Technology', 'skrot': 'IT',
             'oddzial': {'nazwa': 'Testowa', 'adres': 'Lokacja też testowa'}}
    pracownicy = [{'pesel': '328648918623', 'imie': 'Pawel', 'nazwisko': 'Pawlowski', 'dzial': {'nazwa': 'IT'},
                   'numer_telefonu': '4123124124', 'adres_email': 'asdasf@awe.com'},
                  {'pesel': '328648918623', 'imie': 'Pawel', 'nazwisko': 'Pawlowski', 'dzial': {'nazwa': 'IT'},
                   'numer_telefonu': '4123124124', 'adres_email': 'asdasf@awe.com'}]
    return render_template('show_info/pokaz_dzial_info.html', dzial=dzial, pracownicy=pracownicy)


@app.route('/pokaz_magazyn_info/<numer>')
def pokaz_magazyn_info(numer):
    magazyn = dane['magazyny'][0]
    magazyn['zajete_miejsce'] = 12
    magazyn['wolne_miejsce'] = 3
    sprzety = dane['sprzety']
    magazyn['oddzial'] = {}
    magazyn['oddzial']['nazwa'] = 'Testowy'
    magazyn['oddzial']['adres'] = 'Kwiatowa'
    return render_template('show_info/pokaz_magazyn_info.html', magazyn=magazyn, sprzety=sprzety)


@app.route('/pokaz_budynek_info/<adres>')
def pokaz_budynek_info(adres):
    budynek = dane['budynki'][0]
    budynek['oddzial'] = {'adres': 'Testowa'}
    dostepy = [{'karta': {'numer': 13, 'data_przyznania': '02/02/2013'}, 'data_przyznania': '01/12/2019',
                'data_wygasniecia': '12/12/2019',
                'pracownik': {'pesel': 21352134, 'imie': 'Łukasz', 'nazwisko': 'Cezary'},
                'biuro': {'numer': 20}}]
    biura = dane['biura']
    return render_template('show_info/pokaz_budynek_info.html', budynek=budynek, dostepy=dostepy, biura=biura)


@app.route('/pokaz_karta_dostepu_info/<id_karty>')
def pokaz_karta_dostepu_info(id_karty):
    return id_karty


@app.route('/przypisz_sprzet/<pesel>')
def przypisz_sprzet(pesel):
    pracownik = {"pesel": pesel, 'imie': 'Karol', 'nazwisko': 'Testowy'}
    przypisania = [{'id': 1, 'data_przydzialu': '11/12/2019'}, {'id': 4, 'data_przydzialu': '01/01/2019'}]
    sprzety = dane['sprzety']
    return render_template('add_modify/przypisz_sprzet.html', pracownik=pracownik, przypisania=przypisania,
                           sprzety=sprzety)


if __name__ == '__main__':
    app.run()

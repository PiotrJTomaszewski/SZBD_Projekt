from flask import Flask, render_template
import mysql.connector as db
import data_generators.create_workers as creator

app = Flask(__name__)

conn_args = {'host': 'localhost', 'database': 'sbdbazadanych', 'user': 'db_projekt', 'password': 'db_projekt'}

workers = creator.gen_workers_list(10, 'data_generators/FakeNameGenerator.com_43849084.csv')

dane = {
    'oddzialy': [['Marcelińska', 'Oddział Główny'], ['Rybaki', 'Oddział Komunikacyjny']],
    'budynki': [['Marcelińska 5', 'Budynek A', 1], ['Marcelińska 6', 'Budynek B', 2], ['Rybaki 14', 'Call-center', 4]],
    'magazyny': [{'numer': 1, 'oddzial': 'Marcelińska'}, {'numer': 2, 'oddzial': 'Marcelińska'},
                 {'numer': 3, 'oddzial': 'Rybaki'}, {'numer': 4, 'oddzial': 'Rybaki'}],
    'dzialy': ['Human Relations', 'Information Technology', 'Public Relations'],
    'biura': [{'numer': 1, 'budynek': 'Marcelińska 5'}, {'numer': 12, 'budynek': 'Rybaki 14'}],
    'sprzety': [
        {'numer': 1, 'typ': 'laptop', 'nazwa': 'Testowa nazwa', 'producent': 'Testowy producent',
         'data_zakupu': '01/12/2019',
         'numer_magazynu': 1, 'data_przyznania': '11/12/2019'},
        {'numer': 4, 'typ': 'telefon', 'nazwa': 'Lorem Impsum', 'producent': 'Lorem Impsum',
         'data_zakupu': '03/12/2019',
         'numer_magazynu': 2, 'data_przyznania': '01/11/2016'}]
}


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
    site_data = {'title': 'Pracownicy', 'goto_site': '/pokaz_pracownik_info',
                 'add_new_button_text': 'Dodaj nowego pracownika',
                 'add_new_button_link': '/dodaj_pracownika'}
    col_names = ['Pesel', 'Imię', 'Nazwisko', 'Numer telefonu', 'Czy nadal pracuje', 'Adres email', 'Dział', 'Biuro']
    return render_template('show/show.html', col_names=col_names, rows=workers, site_data=site_data)


@app.route('/pracownicy/biuro/<nr_biura>')
def pracownicy_w_biurze(nr_biura):
    # col_names, rows = read_from_database('pracownik')
    site_data = {'title': 'Pracownicy w biurze {}'.format(nr_biura), 'goto_site': '/pokaz_pracownik_info',
                 'add_new_button_text': 'Dodaj nowego pracownika',
                 'add_new_button_link': '/dodaj_pracownika'}
    col_names = ['Pesel', 'Imię', 'Nazwisko', 'Numer telefonu', 'Czy nadal pracuje', 'Adres email', 'Dział', 'Biuro']
    return render_template('show/show.html', col_names=col_names, rows=workers, site_data=site_data)


@app.route('/pracownicy/dzial/<nazwa_dzialu>')
def pracownicy_w_dziale(nazwa_dzialu):
    # col_names, rows = read_from_database('pracownik')
    site_data = {'title': 'Pracownicy w dziale {}'.format(nazwa_dzialu), 'goto_site': '/pokaz_pracownik_info',
                 'add_new_button_text': 'Dodaj nowego pracownika',
                 'add_new_button_link': '/dodaj_pracownika'}
    col_names = ['Pesel', 'Imię', 'Nazwisko', 'Numer telefonu', 'Czy nadal pracuje', 'Adres email', 'Dział', 'Biuro']
    return render_template('show/show.html', col_names=col_names, rows=workers, site_data=site_data)


@app.route('/biura')
def biura():
    # col_names, rows = read_from_database('biuro')
    site_data = {'title': 'Biura', 'goto_site': '/pracownicy/biuro/23',
                 'add_new_button_text': 'Dodaj nowe biuro',
                 'add_new_button_link': '/dodaj_biuro'}
    col_names = ['Numer', 'Budynek', 'Piętro', 'Liczba stanowisk']
    rows = [[i['numer'], i['budynek'], 3, 12] for i in dane['biura']]
    return render_template('show/show.html', col_names=col_names, rows=rows, site_data=site_data)


@app.route('/biura/<adres_budynku>')
def biura_w_budynku(adres_budynku):
    # col_names, rows = read_from_database('biuro')
    site_data = {'title': 'Biura w budynku {}'.format(adres_budynku), 'goto_site': '/pracownicy/biuro/23',
                 'add_new_button_text': 'Dodaj nowe biuro',
                 'add_new_button_link': '/dodaj_biuro'}
    col_names = ['Numer', 'Piętro', 'Liczba stanowisk']
    rows = [[i['numer'], 3, 5] for i in dane['biura']]
    return render_template('show/show.html', col_names=col_names, rows=rows, site_data=site_data)


@app.route('/oddzialy')
def oddzialy():
    site_data = {'title': 'Oddziały', 'goto_site': '/budynki/Kwiecinska',
                 'add_new_button_text': 'Dodaj nowy oddział',
                 'add_new_button_link': '/dodaj_oddzial'
                 }
    col_names = ['Adres', 'Nazwa']
    rows = dane['oddzialy']
    # col_names, rows = read_from_database('oddzial')
    return render_template('show/show.html', col_names=col_names, rows=rows, site_data=site_data)


@app.route('/dzialy')
def dzialy():
    site_data = {'title': 'Działy', 'goto_site': '/pracownicy/dzial/IT',
                 'add_new_button_text': 'Dodaj nowy dział',
                 'add_new_button_link': '/dodaj_dzial'
                 }
    col_names = ['Nazwa', 'Skrócona nazwa', 'Oddział']
    rows = [['Human Relations', 'HR', 'Kwiecinska 1'],
            ['Public Relations', 'PR', 'Kwiecinska 1'],
            ['Information Technology', 'IT', 'Kwiecinska 1']]
    # col_names, rows = read_from_database('oddzial')
    return render_template('show/show.html', col_names=col_names, rows=rows, site_data=site_data)


@app.route('/budynki')
def budynki():
    # col_names, rows = read_from_database('budynek')
    site_data = {'title': 'Budynki', 'goto_site': '/biura/Testowa%203',
                 'add_new_button_text': 'Dodaj nowy budynek',
                 'add_new_button_link': '/dodaj_budynek'
                 }
    col_names = ["Adres", "Nazwa", "Ilość pięter"]
    rows = dane['budynki']
    return render_template('show/show.html', col_names=col_names, rows=rows, site_data=site_data)


@app.route('/budynki/<adres_oddzialu>')
def budynki_w_oddziale(adres_oddzialu):
    # col_names, rows = read_from_database('budynek')
    site_data = {'title': 'Budynki w oddziale {}'.format(adres_oddzialu), 'goto_site': '/biura/Testowa%203',
                 'add_new_button_text': 'Dodaj nowy budynek',
                 'add_new_button_link': '/dodaj_budynek'
                 }
    col_names = ["Adres", "Nazwa", "Ilość pięter"]
    rows = dane['budynki']
    return render_template('show/show.html', col_names=col_names, rows=rows, site_data=site_data)


@app.route('/magazyny')
def magazyny():
    pass


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


@app.route('/pokaz_pracownik_info/<nr>')
def pokaz_pracownik_info(nr):
    nr = int(nr)
    dane_osobowe = {'imie': workers[nr][1], 'nazwisko': workers[nr][2], 'pesel': workers[nr][0],
                    'numer_telefonu': workers[nr][3],
                    'czy_nadal_pracuje': workers[nr][4], 'adres_email': workers[nr][5], 'dzial': workers[nr][6],
                    'biuro': workers[nr][7]}
    sprzety = dane['sprzety']
    karty_dostepu = [
        [123, '12/11/2019', [{'data_przyznania': '04/12/2019', 'data_wygasniecia': '04/12/2020', 'numer_biura': 23,
                              'budynek': dane['budynki'][0][0]},
                             {'data_przyznania': '04/12/2019', 'data_wygasniecia': '04/12/2020', 'numer_biura': 33,
                              'budynek': dane['budynki'][1][0]}]]
    ]
    return render_template('show/pokaz_pracownik_info.html', sprzety=sprzety, dane_osobowe=dane_osobowe,
                           karty_dostepu=karty_dostepu)


@app.route('/pokaz_sprzet_info/<nr>')
def pokaz_sprzet_info(nr):
    nr = int(nr)
    softwares = [{'numer': 51, 'nazwa': 'Office 2012', 'producent': 'Microsoft', 'data_zakupu': '01/02/2013',
                  'data_wygasniecia': '05/06/2020'},
                 {'numer': 64, 'nazwa': 'Windows 10', 'producent': 'Microsoft', 'data_zakupu': '04/02/2019',
                  'data_wygasniecia': '01/06/2025'}]
    dane = {'numer_ewidencyjny': 23, 'typ': 'laptop', 'nazwa': 'Latitude 6231', 'producent': 'DELL',
            'data_zakupu': '03/02/2012', 'stan': 'Paweł Testowy (91234123)', 'uwagi': 'Uszkodzony'}

    return render_template('show/pokaz_sprzet_info.html', dane=dane, softwares=softwares)


@app.route('/przypisz_sprzet')
def przypisz_sprzet():
    przypisania = [{'id': 1, 'data_przydzialu': '11/12/2019'}, {'id': 4, 'data_przydzialu': '01/01/2019'}]
    sprzety = dane['sprzety']
    return render_template('add_modify/przypisz_sprzet.html', przypisania=przypisania, sprzety=sprzety)


if __name__ == '__main__':
    app.run()

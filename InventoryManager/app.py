from flask import Flask, render_template
import mysql.connector as db
import data_generators.create_workers as creator

app = Flask(__name__)

conn_args = {'host': 'localhost', 'database': 'sbdbazadanych', 'user': 'db_projekt', 'password': 'db_projekt'}

workers = creator.gen_workers_list(10, 'data_generators/FakeNameGenerator.com_43849084.csv')


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
                 'add_new_button_link': 'dodaj_pracownika'}
    col_names = ['Pesel', 'Imię', 'Nazwisko', 'Numer telefonu', 'Czy nadal pracuje', 'Adres email', 'Dział', 'Biuro']
    return render_template('show/show.html', col_names=col_names, rows=workers, site_data=site_data)


@app.route('/biura')
def biura():
    col_names, rows = read_from_database('biuro')
    return render_template('show/show.html', col_names=col_names, rows=rows)


@app.route('/oddzialy')
def oddzialy():
    site_data = {'title': 'Oddziały', 'goto_site': '/budynki',
                 'add_new_button_text': 'Dodaj nowy oddział',
                 'add_new_button_link': 'dodaj_oddzial'
                 }
    col_names = ['Adres', 'Nazwa']
    rows = [['test', 'test'], ['test2', 'test2']]
    # col_names, rows = read_from_database('oddzial')
    return render_template('show/show.html', col_names=col_names, rows=rows, site_data=site_data)


@app.route('/budynki')
def budynki():
    # col_names, rows = read_from_database('budynek')
    site_data = {'title': 'Budynki', 'goto_site': '/',
                 'add_new_button_text': 'Dodaj nowy budynek',
                 'add_new_button_link': 'dodaj_budynek'
                 }
    col_names = ["Adres", "Nazwa", "Ilość pięter"]
    rows = [['budynekTest', 'test', 1], ['budynekTest2', 'test2', 3]]
    return render_template('show/show.html', col_names=col_names, rows=rows, site_data=site_data)


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
    oddzialy = ['Testowa 1', 'Kwiatowa 33', 'Krótka 5']
    return render_template('add_modify/dodaj_magazyn.html', oddzialy=oddzialy)


@app.route('/dodaj_sprzet')
def dodaj_sprzet():
    domyslne = {'numer_ewidencyjny': 15, 'data_zakupu': '2019-12-16'}
    magazyny = [{'numer': 1, 'oddzial': 'Testowa 1'}, {'numer': 2, 'oddzial': 'Testowa 1'},
                {'numer': 3, 'oddzial': 'Kwiatowa 33'}, {'numer': 4, 'oddzial': 'Krótka 5'}]
    typy = {'laptop', 'telefon'}
    return render_template('add_modify/dodaj_sprzet.html', magazyny=magazyny, domyslne=domyslne, typy=typy)


@app.route('/dodaj_oprogramowanie')
def dodaj_oprogramowanie():
    domyslne = {'numer_ewidencyjny': 15, 'data_zakupu': '2019-12-16'}
    return render_template('add_modify/dodaj_oprogramowanie.html', domyslne=domyslne)


@app.route('/dodaj_pracownika')
def dodaj_pracownika():
    dzialy = ['HR', 'IT', 'PR']
    biura = [{'numer': 1, 'budynek': 'Kwiatowa 1/9'}, {'numer': 12, 'budynek': 'Testowa 6/2'}]
    return render_template('add_modify/dodaj_pracownika.html', biura=biura, dzialy=dzialy)


@app.route('/dodaj_budynek')
def dodaj_budynek():
    oddzialy = ['Testowa 1', 'Kwiatowa 33', 'Krótka 5']
    return render_template('add_modify/dodaj_budynek.html', oddzialy=oddzialy)


@app.route('/dodaj_dzial')
def dodaj_dzial():
    oddzialy = ['Testowa 1', 'Kwiatowa 33', 'Krótka 5']
    return render_template('add_modify/dodaj_dzial.html', oddzialy=oddzialy)


@app.route('/pokaz_pracownik_info')
def pokaz_pracownik_info():
    dane_osobowe = {'imie': 'Karol', 'nazwisko': 'Testowy', 'pesel': '91042301234', 'numer_telefonu': '991234123',
                    'czy_nadal_pracuje': 'Tak', 'adres_email': 'asd@test.com', 'dzial': 'IT', 'biuro': '123'}
    sprzety = [
        {'numer': 1, 'nazwa': 'Testowa nazwa', 'producent': 'Testowy producent', 'data_przyznania': '01/12/2019',
         'typ': 'laptop'},
        {'numer': 4, 'nazwa': 'Lorem Impsum', 'producent': 'Lorem Impsum', 'data_przyznania': '03/12/2019',
         'typ': 'telefonid'}]
    karty_dostepu = [
        [123, '12/11/2019', [{'data_przyznania': '04/12/2019', 'data_wygasniecia': '04/12/2020', 'numer_biura': 23,
                              'budynek': 'Kosowa 2/1'},
                             {'data_przyznania': '04/12/2019', 'data_wygasniecia': '04/12/2020', 'numer_biura': 33,
                              'budynek': 'Testowa 1/1'}]]
    ]
    return render_template('show/pokaz_pracownik_info.html', sprzety=sprzety, dane_osobowe=dane_osobowe,
                           karty_dostepu=karty_dostepu)


@app.route('/przypisz_sprzet')
def przypisz_sprzet():
    przypisania = [{'id': 1, 'data_przydzialu': '11/12/2019'}, {'id': 4, 'data_przydzialu': '01/01/2019'}]
    sprzety = [
        {'numer': 1, 'typ': 'laptop', 'nazwa': 'Testowa nazwa', 'producent': 'Testowy producent',
         'data_zakupu': '01/12/2019',
         'numer_magazynu': 2},
        {'numer': 4, 'typ': 'telefon', 'nazwa': 'Lorem Impsum', 'producent': 'Lorem Impsum',
         'data_zakupu': '03/12/2019',
         'numer_magazynu': 3}]
    return render_template('add_modify/przypisz_sprzet.html', przypisania=przypisania, sprzety=sprzety)


if __name__ == '__main__':
    app.run()

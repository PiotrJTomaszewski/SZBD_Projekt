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
    col_names, rows = read_from_database('pracownik')
    return render_template('show/show.html', col_names=col_names, rows=workers)


@app.route('/biura')
def biura():
    col_names, rows = read_from_database('biuro')
    return render_template('show/show.html', col_names=col_names, rows=rows)


@app.route('/oddzialy')
def oddzialy():
    col_names, rows = read_from_database('oddzial')
    return render_template('show/show.html', col_names=col_names, rows=rows)


@app.route('/budynki')
def budynki():
    col_names, rows = read_from_database('budynek')
    return render_template('show/show.html', col_names=col_names, rows=rows)


@app.route('/')
def hello_world():
    strony = ['dodaj_oddzial', 'dodaj_magazyn', 'dodaj_sprzet']
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
    return render_template('add_modify/dodaj_sprzet.html', magazyny=magazyny, domyslne=domyslne)


if __name__ == '__main__':
    app.run()

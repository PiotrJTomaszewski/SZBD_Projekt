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
    return render_template('index.html', col_names=col_names, rows=workers)


@app.route('/biura')
def biura():
    col_names, rows = read_from_database('biuro')
    return render_template('index.html', col_names=col_names, rows=rows)


@app.route('/oddzialy')
def oddzialy():
    col_names, rows = read_from_database('oddzial')
    return render_template('index.html', col_names=col_names, rows=rows)


@app.route('/budynki')
def budynki():
    col_names, rows = read_from_database('budynek')
    return render_template('index.html', col_names=col_names, rows=rows)

@app.route('/')
def index():
    return render_template('index.html')


if __name__ == '__main__':
    app.run()

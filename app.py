from flask import Flask, render_template
import mysql.connector as db

app = Flask(__name__)

conn_args = {'host': 'localhost', 'database': 'db_projekt', 'user': 'db_projekt', 'password': 'db_projekt'}


@app.route('/')
def index():
    conn = db.connect(**conn_args)
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM WORKERS')
    rows = cursor.fetchall()
    conn.close()
    col_names = ('Id', 'Imię', 'Nazwisko', 'Płeć', 'Email', 'Pesel', 'Data urodzenia', 'Numer telefonu')
    return render_template('index.html', col_names=col_names, rows=rows)


if __name__ == '__main__':
    app.run()

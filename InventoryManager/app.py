from flask import Flask, render_template

app = Flask(__name__)


@app.route('/')
def hello_world():
    return 'Hello World!'


@app.route('/dodaj_oddzial.html')
def dodaj_oddzial():
    return render_template('add_modify/dodaj_oddzial.html')


@app.route('/dodaj_magazyn.html')
def dodaj_magazyn():
    oddzialy = ['Testowa 1', 'Kwiatowa 33', 'Krótka 5']
    return render_template('add_modify/dodaj_magazyn.html', oddzialy=oddzialy)


if __name__ == '__main__':
    app.run()

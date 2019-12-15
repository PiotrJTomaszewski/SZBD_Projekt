from flask import Flask, render_template

app = Flask(__name__)


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

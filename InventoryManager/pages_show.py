from flask import Flask, render_template, request, flash, redirect, url_for, Blueprint
import data_generators.create_workers as creator

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

show = Blueprint('show', __name__)


@show.route('/pracownicy')
def pracownicy():
    # col_names, rows = read_from_database('pracownik')
    pracownicy = workers
    for i in range(len(pracownicy)):
        if pracownicy[i]['czy_nadal_pracuje'] == '1':
            pracownicy[i]['czy_nadal_pracuje'] = 'Tak'
        else:
            pracownicy[i]['czy_nadal_pracuje'] = 'Nie'
    return render_template('show/pokaz_pracownicy.html', pracownicy=pracownicy)


@show.route('/biura')
def biura():
    biura = [{'numer': i['numer'], 'budynek': i['budynek'],
              'pietro': 3, 'liczba_stanowisk': 12} for i in dane['biura']]
    return render_template('show/pokaz_biura.html', biura=biura)


@show.route('/oddzialy')
def oddzialy():
    oddzialy = dane['oddzialy']
    # col_names, rows = read_from_database('oddzial')
    return render_template('show/pokaz_oddzialy.html', oddzialy=oddzialy)


@show.route('/dzialy')
def dzialy():
    dzialy = dane['dzialy']
    return render_template('show/pokaz_dzialy.html', dzialy=dzialy)


@show.route('/budynki')
def budynki():
    budynki = dane['budynki']
    return render_template('show/pokaz_budynki.html', budynki=budynki)


@show.route('/magazyny')
def magazyny():
    magazyny = dane['magazyny']
    return render_template('show/pokaz_magazyny.html', magazyny=magazyny)

from flask import Flask, render_template, request, flash, redirect, url_for, Blueprint
import data_generators.create_workers as creator
from database_connector import DatabaseConnector as DBC
from helpers import make_dictionaries_list

# TODO: Dodać wyświetlanie listy sprzętu i oprogramowania

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


@show.route('/pokaz/oddzialy')
def oddzialy():
    branches, error = DBC().get_instance().execute_query_fetch(
        """SELECT adres, nazwa FROM Oddzial ORDER BY adres""")
    if error is not None:
        flash('Wystąpił błąd!<br/>{}'.format(error.msg))
    branches_data = make_dictionaries_list(['adres', 'nazwa'], branches)
    return render_template('show/pokaz_oddzialy.html', oddzialy=branches_data)


@show.route('/pokaz/budynki')
def budynki():
    buildings, error = DBC().get_instance().execute_query_fetch(
        """SELECT adres, nazwa, ilosc_pieter, oddzial_adres FROM Budynek ORDER BY adres"""
    )
    if error is not None:
        flash('Wystąpił błąd!<br/>{}'.format(error.msg))
    buildings_data = make_dictionaries_list(['adres', 'nazwa', 'liczba_pieter', 'oddzial_adres'], buildings)
    return render_template('show/pokaz_budynki.html', budynki=buildings_data)


@show.route('/pokaz/biura')
def biura():
    offices, error = DBC().get_instance().execute_query_fetch(
        """SELECT numer, liczba_stanowisk, pietro, budynek_adres from Biuro ORDER BY numer"""
    )
    if error is not None:
        flash('Wystąpił błąd!<br/>{}'.format(error.msg))
    offices_data = make_dictionaries_list(['numer', 'liczba_stanowisk', 'pietro', 'budynek_adres'], offices)
    return render_template('show/pokaz_biura.html', biura=offices_data)


@show.route('/pokaz/dzialy')
def dzialy():
    depts, error = DBC().get_instance().execute_query_fetch(
        """SELECT nazwa, skrot, oddzial_adres from Dzial ORDER BY nazwa"""
    )
    if error is not None:
        flash('Wystąpił błąd!<br/>{}'.format(error.msg))
    # if depts is None or len(depts) == 0:
    #     flash('Nie znaleziono działów!')
    #     return render_template('show/pokaz_dzialy.html', dzialy=[])
    depts_data = make_dictionaries_list(['nazwa', 'skrot', 'oddzial_adres'], depts)
    return render_template('show/pokaz_dzialy.html', dzialy=depts_data)


@show.route('/pokaz/pracownicy')
def pracownicy():
    workers, error = DBC().get_instance().execute_query_fetch(
        """SELECT p.pesel, p.imie, p.nazwisko, p.numer_telefonu, p.czy_nadal_pracuje, p.adres_email, p.dzial_nazwa, 
        p.biuro_numer, d.skrot 
        FROM Pracownik p JOIN Dzial d on p.dzial_nazwa = d.nazwa
        WHERE czy_nadal_pracuje = 1
        ORDER BY pesel"""
    )
    if error is not None:
        flash('Wystąpił błąd!<br/>{}'.format(error.msg))
    workers_data = make_dictionaries_list(
        ['pesel', 'imie', 'nazwisko', 'numer_telefonu', 'czy_nadal_pracuje', 'adres_email', 'dzial_nazwa',
         'biuro_numer', 'dzial_skrot'], workers)
    print(workers_data)
    return render_template('show/pokaz_pracownicy.html', pracownicy=workers_data)


@show.route('/pokaz/magazyny')
def magazyny():
    magazyny_dane = dane['magazyny']
    return render_template('show/pokaz_magazyny.html', magazyny=magazyny_dane)


@show.route('/pokaz/sprzet')
def sprzet():
    pass


@show.route('/pokaz/oprogramowanie')
def oprogramowanie():
    pass

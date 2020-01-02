from flask import Flask, render_template, request, flash, redirect, url_for, Blueprint
import data_generators.create_workers as creator
from forms import *

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

assign = Blueprint('assign', __name__)


@assign.route('/przypisz_sprzet/<pesel>')
def przypisz_sprzet(pesel):
    pracownik = {"pesel": pesel, 'imie': 'Karol', 'nazwisko': 'Testowy'}
    przypisania = [{'id': 1, 'data_przydzialu': '11/12/2019'}, {'id': 4, 'data_przydzialu': '01/01/2019'}]
    sprzety = dane['sprzety']
    return render_template('add_modify/przypisz_sprzet.html', pracownik=pracownik, przypisania=przypisania,
                           sprzety=sprzety)

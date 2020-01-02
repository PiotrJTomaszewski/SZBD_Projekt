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

add = Blueprint('add', __name__)


@add.route('/dodaj_oddzial')
def dodaj_oddzial():
    return render_template('add_modify/dodaj_oddzial.html')


@add.route('/dodaj_magazyn')
def dodaj_magazyn():
    oddzialy = ['Testowa', 'Kwiatowa', 'Krótka']
    return render_template('add_modify/dodaj_magazyn.html', oddzialy=oddzialy)


@add.route('/dodaj_sprzet')
def dodaj_sprzet():
    domyslne = {'numer_ewidencyjny': 15, 'data_zakupu': '2019-12-16'}
    magazyny = dane['magazyny']
    typy = {'laptop', 'telefon'}
    return render_template('add_modify/dodaj_sprzet.html', magazyny=magazyny, domyslne=domyslne, typy=typy)


@add.route('/dodaj_oprogramowanie')
def dodaj_oprogramowanie():
    domyslne = {'numer_ewidencyjny': 15, 'data_zakupu': '2019-12-16'}
    return render_template('add_modify/dodaj_oprogramowanie.html', domyslne=domyslne)


@add.route('/dodaj_pracownika', methods=['GET', 'POST'])
def dodaj_pracownika():
    offices = [[biuro['numer'], 'Biuro {} w budynku {}'.format(biuro['numer'], biuro['budynek']['adres'])] for biuro in
               dane['biura']]
    depts = [[dzial['nazwa'], 'Dział {} ({})'.format(dzial['nazwa'], dzial['skrot'])] for dzial in
             dane['dzialy']]

    title = 'Dodaj pracownika'

    form = AddEditWorkerForm()
    form.office_number.choices = offices
    form.dept_name.choices = depts
    if request.method == 'POST':
        if form.validate():
            return redirect(url_for('show_info.pokaz_pracownik_info', pesel=form.pesel.value))
        else:
            flash('Proszę upewnić się czy wszystkie pola zostały poprawnie wypełnione!')
            return render_template('add_modify/dodaj_edytuj_pracownika.html', form=form, title=title)
    else:
        return render_template('add_modify/dodaj_edytuj_pracownika.html', form=form, title=title)


@add.route('/dodaj_budynek')
def dodaj_budynek():
    oddzialy = [i[0] for i in dane['oddzialy']]
    return render_template('add_modify/dodaj_budynek.html', oddzialy=oddzialy)


@add.route('/dodaj_dzial')
def dodaj_dzial():
    oddzialy = [i[0] for i in dane['oddzialy']]
    return render_template('add_modify/dodaj_dzial.html', oddzialy=oddzialy)


@add.route('/dodaj_biuro')
def dodaj_biuro():
    pass

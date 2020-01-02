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

edit = Blueprint('edit', __name__)


@edit.route('/edytuj_pracownika/<pesel>', methods=['GET', 'POST'])
def edytuj_pracownika(pesel):
    offices = [[biuro['numer'], 'Biuro {} w budynku {}'.format(biuro['numer'], biuro['budynek']['adres'])] for biuro in
               dane['biura']]
    depts = [[dzial['nazwa'], 'Dział {} ({})'.format(dzial['nazwa'], dzial['skrot'])] for dzial in
             dane['dzialy']]

    title = 'Edytuj pracownika'

    form = AddEditWorkerForm()
    form.office_number.choices = offices
    form.dept_name.choices = depts

    worker = workers[0]
    form.pesel.default = pesel
    form.name.default = 'Anita'
    form.surname.default = 'Testowa'
    form.phone_number.default = worker.get(667123321)
    form.is_still_working.default = True
    form.process()
    if request.method == 'POST':
        if form.validate():
            return redirect(url_for('show_info.pokaz_pracownik_info', pesel=form.pesel.value))
        else:
            flash('Proszę upewnić się czy wszystkie pola zostały poprawnie wypełnione!')
            return render_template('add_modify/dodaj_edytuj_pracownika.html', form=form, title=title)
    else:
        return render_template('add_modify/dodaj_edytuj_pracownika.html', form=form, title=title)

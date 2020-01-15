from flask import Flask, render_template, request, flash, redirect, url_for, Blueprint
import data_generators.create_workers as creator
from forms import *
from database_connector import DatabaseConnector as DBC
from mysql.connector import errorcode

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


@edit.route('/edytuj/oddzial/<adres>', methods=['GET', 'POST'])
def edytuj_oddzial(adres):
    form = AddEditBranchForm()
    if request.method == 'GET':
        current_data, error = DBC().get_instance().execute_query_fetch(
            """SELECT (adres, nazwa) FROM Oddzial WHERE adres = %s""", [adres])
        if error is None and current_data is not None and len(current_data) == 1:
            form.name.default = current_data[1]
            form.address.default = current_data[0]
            form.process()
        else:
            flash('Wystąpił błąd!<br/>{}'.format(error.msg))
        return render_template('edit/edytuj_oddzial.html', form=form, adres=adres)
    if request.method == 'POST':
        if form.validate():
            new_address = form.address.data
            new_name = form.name.data
            error = DBC().get_instance().execute_query_add_edit_delete(
                """UPDATE Oddzial
                SET nazwa=%s, adres=%s
                WHERE adres=%s""", [new_name, new_address, adres]
            )
            if error is None:
                return redirect(url_for('show_info.pokaz_oddzial_info', adres=new_address))
            else:
                # Translate errors to Polish
                if error.errno in (errorcode.ER_ROW_IS_REFERENCED, errorcode.ER_ROW_IS_REFERENCED_2):
                    error.msg = 'Nie można zmienić adresu, jeśli oddział posiada podrzędny dział, magazyn lub budynek!'
                flash('Wystąpił błąd!<br/>{}'.format(error.msg))
                return render_template('edit/edytuj_oddzial.html', form=form, adres=adres)
        else:
            flash('Proszę upewnić się czy wszystkie pola zostały poprawnie wypełnione!')
            return render_template('edit/edytuj_oddzial.html', form=form, adres=adres)


@edit.route('/edytuj/budynek/<adres>', methods=['GET', 'POST'])
def edytuj_budynek(adres):
    oddzialy = [(oddzial['adres'], '{} ({})'.format(oddzial['nazwa'], oddzial['adres'])) for oddzial in
                dane['oddzialy']]

    form = AddEditBuildingForm()
    form.branch_address.choices = oddzialy
    form.process()

    if request.method == 'POST':
        if form.validate():
            return redirect(url_for('show_info.pokaz_budynek_info', adres='TODO'))
        else:
            flash('Proszę upewnić się czy wszystkie pola zostały poprawnie wypełnione!')
            return render_template('edit/edytuj_budynek.html', form=form, adres=adres)
    else:
        return render_template('edit/edytuj_budynek.html', form=form, adres=adres)


@edit.route('/edytuj/biuro/<numer>', methods=['GET', 'POST'])
def edytuj_biuro(numer):
    form = AddEditOfficeForm()

    if request.method == 'POST':
        if form.validate():
            return redirect(url_for('show_info.pokaz_biuro_info', numer='TODO'))
        else:
            flash('Proszę upewnić się czy wszystkie pola zostały poprawnie wypełnione!')
            return render_template('edit/edytuj_biuro.html', form=form, numer=numer)
    else:
        return render_template('edit/edytuj_biuro.html', form=form, numer=numer)


@edit.route('/edytuj/dzial/<nazwa>', methods=['GET', 'POST'])
def edytuj_dzial(nazwa):
    oddzialy = [(oddzial['adres'], '{} ({})'.format(oddzial['nazwa'], oddzial['adres'])) for oddzial in
                dane['oddzialy']]

    form = AddEditDepForm()
    form.branch_address.choices = oddzialy

    if request.method == 'POST':
        if form.validate():
            return redirect(url_for('show_info.pokaz_dzial_info', nazwa='TODO'))
        else:
            flash('Proszę upewnić się czy wszystkie pola zostały poprawnie wypełnione!')
            return render_template('edit/edytuj_dzial.html', form=form, nazwa=nazwa)
    else:
        return render_template('edit/edytuj_dzial.html', form=form, nazwa=nazwa)


@edit.route('/edytuj/pracownik/<pesel>', methods=['GET', 'POST'])
def edytuj_pracownika(pesel):
    offices = [[biuro['numer'], 'Biuro {} w budynku {}'.format(biuro['numer'], biuro['budynek']['adres'])] for biuro in
               dane['biura']]
    depts = [[dzial['nazwa'], 'Dział {} ({})'.format(dzial['nazwa'], dzial['skrot'])] for dzial in
             dane['dzialy']]

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
            return render_template('edit/edytuj_pracownika.html', form=form, pesel=pesel)
    else:
        return render_template('edit/edytuj_pracownika.html', form=form, pesel=pesel)


@edit.route('/edytuj/magazyn/<numer>', methods=['GET', 'POST'])
def edytuj_magazyn(numer):
    oddzialy = [(oddzial['adres'], '{} ({})'.format(oddzial['nazwa'], oddzial['adres'])) for oddzial in
                dane['oddzialy']]
    form = AddEditMagazineForm()
    form.branch_address.choices = oddzialy

    if request.method == 'POST':
        if form.validate():
            return redirect(url_for('show_info.pokaz_magazyn_info', numer='TODO'))
        else:
            flash('Proszę upewnić się czy wszystkie pola zostały poprawnie wypełnione!')
            return render_template('add/dodaj_magazyn.html', form=form, numer=numer)
    else:
        return render_template('add/dodaj_magazyn.html', form=form, numer=numer)


@edit.route('/edytuj/sprzet/<numer_ewidencyjny>', methods=['GET', 'POST'])
def edytuj_sprzet(numer_ewidencyjny):
    typy = {['laptop', 'laptop'], ['telefon', 'telefon']}
    form = AddEditHardwareForm()
    form.existing_type.choices = typy

    if request.method == 'POST':
        if form.validate():
            return redirect(url_for('show_info.pokaz_sprzet_info', numer_ewidencyjny='TODO'))
        else:
            flash('Proszę upewnić się czy wszystkie pola zostały poprawnie wypełnione!')
            return render_template('edit/edytuj_sprzet.html', form=form, numer_ewidencyjny=numer_ewidencyjny)
    else:
        return render_template('edit/edytuj_sprzet.html', form=form, numer_ewidencyjny=numer_ewidencyjny)

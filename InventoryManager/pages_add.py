from flask import Flask, render_template, request, flash, redirect, url_for, Blueprint
import data_generators.create_workers as creator
from forms import *
from database_connector import DatabaseConnector as DBC

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


@add.route('/dodaj/oddzial', methods=['GET', 'POST'])
def dodaj_oddzial():
    form = AddEditBranchForm()

    if request.method == 'POST':
        if form.validate():  # Input ok
            adres = form.address.data
            nazwa = form.name.data
            result = DBC().get_instance().add_branch(adres, nazwa)
            if result is None:  # If there was no error
                return redirect(url_for('show_info.pokaz_oddzial_info', adres=adres))
            else:
                flash('Wystąpił błąd podczas dodawania oddziału!<br/> {}'.format(result.msg))
                return render_template('add/dodaj_oddzial.html', form=form)
        else:
            flash('Proszę upewnić się czy wszystkie pola zostały poprawnie wypełnione!')
            return render_template('add/dodaj_oddzial.html', form=form)
    else:
        return render_template('add/dodaj_oddzial.html', form=form)


@add.route('/dodaj/budynek', methods=['GET', 'POST'])
def dodaj_budynek():
    oddzialy = [(oddzial['adres'], '{} ({})'.format(oddzial['nazwa'], oddzial['adres'])) for oddzial in
                dane['oddzialy']]

    form = AddEditBuildingForm()
    form.branch_address.choices = oddzialy

    if request.method == 'POST':
        if form.validate():
            return redirect(url_for('show_info.pokaz_budynek_info', adres='TODO'))
        else:
            flash('Proszę upewnić się czy wszystkie pola zostały poprawnie wypełnione!')
            return render_template('add/dodaj_budynek.html', form=form)
    else:
        return render_template('add/dodaj_budynek.html', form=form)


@add.route('/dodaj/biuro', methods=['GET', 'POST'])
def dodaj_biuro():
    form = AddEditOfficeForm()
    form.building_address.choices = [[0,0]]
    if request.method == 'POST':
        if form.validate():
            return redirect(url_for('show_info.pokaz_biuro_info', numer='TODO'))
        else:
            flash('Proszę upewnić się czy wszystkie pola zostały poprawnie wypełnione!')
            return render_template('add/dodaj_biuro.html', form=form)
    else:
        return render_template('add/dodaj_biuro.html', form=form)


@add.route('/dodaj/dzial', methods=['GET', 'POST'])
def dodaj_dzial():
    oddzialy = [(oddzial['adres'], '{} ({})'.format(oddzial['nazwa'], oddzial['adres'])) for oddzial in
                dane['oddzialy']]

    form = AddEditDepForm()
    form.branch_address.choices = oddzialy

    if request.method == 'POST':
        if form.validate():
            return redirect(url_for('show_info.pokaz_dzial_info', nazwa='TODO'))
        else:
            flash('Proszę upewnić się czy wszystkie pola zostały poprawnie wypełnione!')
            return render_template('add/dodaj_dzial.html', form=form)
    else:
        return render_template('add/dodaj_dzial.html', form=form)


@add.route('/dodaj/pracownik', methods=['GET', 'POST'])
def dodaj_pracownika():
    offices = [[biuro['numer'], 'Biuro {} w budynku {}'.format(biuro['numer'], biuro['budynek']['adres'])] for biuro in
               dane['biura']]
    depts = [[dzial['nazwa'], 'Dział {} ({})'.format(dzial['nazwa'], dzial['skrot'])] for dzial in
             dane['dzialy']]

    form = AddEditWorkerForm()
    form.office_number.choices = offices
    form.dept_name.choices = depts

    if request.method == 'POST':
        if form.validate():
            return redirect(url_for('show_info.pokaz_pracownik_info', pesel='TODO'))
        else:
            flash('Proszę upewnić się czy wszystkie pola zostały poprawnie wypełnione!')
            return render_template('add/dodaj_pracownika.html', form=form)
    else:
        return render_template('add/dodaj_pracownika.html', form=form)


@add.route('/dodaj/magazyn', methods=['GET', 'POST'])
def dodaj_magazyn():
    oddzialy = [(oddzial['adres'], '{} ({})'.format(oddzial['nazwa'], oddzial['adres'])) for oddzial in
                dane['oddzialy']]
    form = AddEditMagazineForm()
    form.branch_address.choices = oddzialy

    if request.method == 'POST':
        if form.validate():
            return redirect(url_for('show_info.pokaz_magazyn_info', numer='TODO'))
        else:
            flash('Proszę upewnić się czy wszystkie pola zostały poprawnie wypełnione!')
            return render_template('add/dodaj_magazyn.html', form=form)
    else:
        return render_template('add/dodaj_magazyn.html', form=form)


@add.route('/dodaj/sprzet', methods=['GET', 'POST'])
def dodaj_sprzet():
    typy = [['laptop', 'laptop'], ['telefon', 'telefon']]
    form = AddEditHardwareForm()
    form.existing_type.choices = typy

    if request.method == 'POST':
        if form.validate():
            return redirect(url_for('show_info.pokaz_sprzet_info', numer_ewidencyjny='TODO'))
        else:
            flash('Proszę upewnić się czy wszystkie pola zostały poprawnie wypełnione!')
            return render_template('add/dodaj_sprzet.html', form=form)
    else:
        return render_template('add/dodaj_sprzet.html', form=form)


@add.route('/dodaj/oprogramowanie')
def dodaj_oprogramowanie():
    domyslne = {'numer_ewidencyjny': 15, 'data_zakupu': '2019-12-16'}
    return render_template('add/dodaj_oprogramowanie.html', domyslne=domyslne)

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

add = Blueprint('add', __name__)


@add.route('/dodaj/oddzial', methods=['GET', 'POST'])
def dodaj_oddzial():
    form = AddEditBranchForm()

    if request.method == 'POST':
        if form.validate():  # Input ok
            adres = form.address.data
            nazwa = form.name.data
            query = """INSERT INTO Oddzial (adres, nazwa) VALUES (%s, %s)"""
            error = DBC().get_instance().execute_query_add_edit_delete(query, (adres, nazwa))
            if error is None:  # If there was no error
                flash('Oddział został pomyślnie dodany')
                return redirect(url_for('show_info.pokaz_oddzial_info', adres=adres))
            else:
                # Translate errors
                if error.errno == errorcode.ER_DUP_ENTRY:  # Duplicate entry
                    error.msg = 'Oddział o podanym adresie już istnieje!'

                flash('Wystąpił błąd podczas dodawania oddziału!<br/>{}'.format(error.msg))
                return render_template('add/dodaj_oddzial.html', form=form)
        else:
            flash('Proszę upewnić się czy wszystkie pola zostały poprawnie wypełnione!')
            return render_template('add/dodaj_oddzial.html', form=form)
    else:
        return render_template('add/dodaj_oddzial.html', form=form)


@add.route('/dodaj/budynek', methods=['GET', 'POST'])
def dodaj_budynek():
    branches, error = DBC().get_instance().execute_query_fetch("""SELECT adres, nazwa FROM Oddzial""")
    if error is not None:
        flash('Wystąpił błąd podczas pobierania dostępnych oddziałów!<br/>{}'.format(error.msg))
    branches_choices = [(branch[0], ('{} ({})'.format(branch[1], branch[0]))) for branch in branches]
    form = AddEditBuildingForm()
    form.branch_address.choices = branches_choices

    if request.method == 'POST':
        if form.validate():  # Input ok
            address = form.address.data
            name = form.name.data
            number_of_floors = form.number_of_floors.data
            branch_address = form.branch_address.data
            error = DBC().get_instance().execute_query_add_edit_delete(
                """INSERT INTO Budynek (adres, nazwa, ilosc_pieter, oddzial_adres)
                VALUES(%s, %s, %s, %s)""", (address, name, number_of_floors, branch_address)
            )
            if error is None:  # If there was no error
                flash('Budynek został pomyślnie dodany')
                return redirect(url_for('show_info.pokaz_budynek_info', adres=address))
            else:
                # Translate errors
                if error.errno == errorcode.ER_DUP_ENTRY:  # Duplicate entry
                    error.msg = 'Budynek o podanym adresie już istnieje!'

                flash('Wystąpił błąd podczas dodawania budynku!<br/>{}'.format(error.msg))
                return render_template('add/dodaj_budynek.html', form=form)
        else:
            flash('Proszę upewnić się czy wszystkie pola zostały poprawnie wypełnione!')
            return render_template('add/dodaj_budynek.html', form=form)
    else:
        return render_template('add/dodaj_budynek.html', form=form)


@add.route('/dodaj/biuro', methods=['GET', 'POST'])
def dodaj_biuro():
    buildings, error = DBC().get_instance().execute_query_fetch("""SELECT adres, nazwa FROM Budynek ORDER BY nazwa""")
    if error is not None:
        flash('Wystąpił błąd podczas pobierania dostępnych budynków!<br/>{}'.format(error.msg))
    buildings_choices = [(building[0], ('{} ({})'.format(building[1], building[0]))) for building in buildings]
    form = AddEditOfficeForm()
    form.building_address.choices = buildings_choices

    if request.method == 'POST':
        if form.validate():  # Input ok
            number = form.number.data
            number_of_posts = form.number_of_posts.data
            floor = form.floor.data
            building_address = form.building_address.data

            result, error = DBC().get_instance().execute_query_add_edit_delete_with_fetch(
                """SELECT DodajBiuro(%s, %s, %s, %s) FROM dual""",
                (number, number_of_posts, floor, building_address)
            )
            if error is None:  # If there was no error
                print(result[0][0])
                if result[0][0] == 0:  # Result code
                    # ok
                    flash('Biuro zostało pomyślnie dodane')
                    return redirect(url_for('show_info.pokaz_biuro_info', numer_biura=number))
                else:
                    if result[0][0] == 1:
                        flash('Wystąpił błąd podczas dodawania biura!<br/>Nieprawidłowe piętro!')
                    else:
                        flash('Wystąpił błąd podczas dodawania biura!<br/>\
                        Upewnij się czy inne biuro nie używa już tego numeru!')
                    return render_template('add/dodaj_biuro.html', form=form)
            else:
                # Translate errors
                if error.errno == errorcode.ER_DUP_ENTRY:  # Duplicate entry
                    error.msg = 'Biuro o podanym numerze już istnieje!'
                flash('Wystąpił błąd podczas dodawania biura!<br/>{}'.format(error.msg))
                return render_template('add/dodaj_biuro.html', form=form)
        else:
            flash('Proszę upewnić się czy wszystkie pola zostały poprawnie wypełnione!')
            return render_template('add/dodaj_biuro.html', form=form)
    else:
        return render_template('add/dodaj_biuro.html', form=form)


@add.route('/dodaj/dzial', methods=['GET', 'POST'])
def dodaj_dzial():
    goto = 'add/dodaj_dzial.html'
    branches, error = DBC().get_instance().execute_query_fetch("""SELECT adres, nazwa FROM Oddzial""")
    if error is not None:
        flash('Wystąpił błąd podczas pobierania dostępnych oddziałów!<br/>{}'.format(error.msg))
    branches_choices = [(branch[0], ('{} ({})'.format(branch[1], branch[0]))) for branch in branches]
    form = AddEditDepForm()
    form.branch_address.choices = branches_choices

    if request.method == 'POST':
        if form.validate():  # Input ok
            name = form.name.data
            name_short = form.short_name.data
            branch_address = form.branch_address.data
            error = DBC().get_instance().execute_query_add_edit_delete(
                """INSERT INTO Dzial (nazwa, skrot, oddzial_adres)
                VALUES(%s, %s, %s)""", (name, name_short, branch_address)
            )
            if error is None:  # If there was no error
                flash('Dział został pomyślnie dodany')
                return redirect(url_for('show_info.pokaz_dzial_info', nazwa=name))
            else:
                # Translate errors
                if error.errno == errorcode.ER_DUP_ENTRY:  # Duplicate entry
                    error.msg = 'Dział o podanej nazwie już istnieje!'

                flash('Wystąpił błąd podczas dodawania działu!<br/>{}'.format(error.msg))
                return render_template(goto, form=form)
        else:
            flash('Proszę upewnić się czy wszystkie pola zostały poprawnie wypełnione!')
            return render_template(goto, form=form)
    else:
        return render_template(goto, form=form)


@add.route('/dodaj/pracownik', methods=['GET', 'POST'])
def dodaj_pracownika():
    goto = 'add/dodaj_pracownika.html'
    offices, error = DBC().get_instance().execute_query_fetch("""SELECT B.numer, B.budynek_adres, B.pietro, B2.oddzial_adres, IleWolnychMiejscBiuro(B.numer)
     FROM Biuro B JOIN Budynek B2 on B.budynek_adres = B2.adres
    WHERE IleWolnychMiejscBiuro(B.numer) > 0
    ORDER BY numer""")
    if error is not None:
        flash('Wystąpił błąd podczas pobierania dostępnych biur!<br/>{}'.format(error.msg))
    offices_choices = [(office[0], '{} w {}, piętro {}, oddział {} - wolne miejsce {}'.format(
        office[0], office[1], office[2], office[3], office[4]))
                       for office in offices]
    depts, error = DBC().get_instance().execute_query_fetch("""SELECT nazwa, skrot,  oddzial_adres
     FROM Dzial ORDER BY nazwa""")
    if error is not None:
        flash('Wystąpił błąd podczas pobierania dostępnych działów!<br/>{}'.format(error.msg))
    depts_choices = [(dept[0], ('{} ({}) oddział {}'.format(dept[0], dept[1], dept[2]))) for dept in depts]

    form = AddEditWorkerForm()
    form.office_number.choices = offices_choices
    form.dept_name.choices = depts_choices

    if request.method == 'POST':
        if form.validate():  # Input ok
            pesel = form.pesel.data
            name = form.name.data
            surname = form.surname.data
            phone_number = form.phone_number.data
            if form.is_still_working:
                is_still_working = '1'
            else:
                is_still_working = '0'
            email = form.email_address.data
            dept_name = form.dept_name.data
            office_number = form.office_number.data
            # Check if office and departament are in the same branch
            office_branch = ''
            for o in offices:
                if o[0] == office_number:
                    office_branch = o[3]
                    break
            dept_branch = ''
            for d in depts:
                if d[0] == dept_name:
                    dept_branch = d[2]
                    break
            if office_branch != dept_branch:
                flash('Wystąpił błąd podczas dodawania pracownika!<br/>\
                      Biuro i dział muszą należeć do tego samego oddziału!')
                return render_template(goto, form=form)
            error = DBC().get_instance().execute_query_add_edit_delete(
                """INSERT INTO Pracownik (pesel, imie, nazwisko, numer_telefonu, czy_nadal_pracuje, 
                adres_email, dzial_nazwa, biuro_numer)
                VALUES(%s, %s, %s, %s, %s, %s, %s, %s)""", (pesel, name, surname, phone_number, is_still_working,
                                                            email, dept_name, office_number)
            )
            if error is None:  # If there was no error
                flash('Pracownik został pomyślnie dodany')
                return redirect(url_for('show_info.pokaz_pracownik_info', pesel=pesel))
            else:
                # Translate errors
                if error.errno == errorcode.ER_DUP_ENTRY:  # Duplicate entry
                    error.msg = 'Pracownik o podanym numerze PESEL już istnieje!'

                flash('Wystąpił błąd podczas dodawania pracownika!<br/>{}'.format(error.msg))
                return render_template(goto, form=form)
        else:
            flash('Proszę upewnić się czy wszystkie pola zostały poprawnie wypełnione!')
            return render_template(goto, form=form)
    else:
        return render_template(goto, form=form)


@add.route('/dodaj/magazyn', methods=['GET', 'POST'])
def dodaj_magazyn():
    goto = 'add/dodaj_magazyn.html'
    branches, error = DBC().get_instance().execute_query_fetch("""SELECT adres, nazwa FROM Oddzial""")
    if error is not None:
        flash('Wystąpił błąd podczas pobierania dostępnych oddziałów!<br/>{}'.format(error.msg))
    branches_choices = [(branch[0], ('{} ({})'.format(branch[1], branch[0]))) for branch in branches]
    form = AddEditMagazineForm()
    form.branch_address.choices = branches_choices

    if request.method == 'POST':
        if form.validate():  # Input ok
            number = form.number.data
            branch_address = form.branch_address.data
            capacity = form.capacity.data
            error = DBC().get_instance().execute_query_add_edit_delete(
                """INSERT INTO Magazyn (numer, pojemnosc, oddzial_adres)
                VALUES(%s, %s, %s)""", (number, capacity, branch_address)
            )
            if error is None:  # If there was no error
                flash('Magazyn został pomyślnie dodany')
                return redirect(url_for('show_info.pokaz_magazyn_info', numer=number))
            else:
                # Translate errors
                if error.errno == errorcode.ER_DUP_ENTRY:  # Duplicate entry
                    error.msg = 'Magazyn o podanym numerze już istnieje!'

                flash('Wystąpił błąd podczas dodawania magazynu!<br/>{}'.format(error.msg))
                return render_template(goto, form=form)
        else:
            flash('Proszę upewnić się czy wszystkie pola zostały poprawnie wypełnione!')
            return render_template(goto, form=form)
    else:
        return render_template(goto, form=form)


@add.route('/dodaj/sprzet', methods=['GET', 'POST'])
def dodaj_sprzet():
    goto = 'add/dodaj_sprzet.html'
    types, error = DBC().get_instance().execute_query_fetch("""SELECT DISTINCT typ FROM Sprzet""")
    if error is not None:
        flash('Wystąpił błąd podczas pobierania dostępnych typów sprzętu!<br/>{}'.format(error.msg))
    form = AddEditHardwareForm()
    # types_choices = [('0', '0')]
    # if types is not None and len(types) > 0:
    types_choices = [(t[0], t[0]) for t in types]
    form.existing_type.choices = types_choices

    # Get some available evidence number
    available_number = DBC().get_instance().execute_query_fetch("""SELECT max(numer_ewidencyjny)+1 FROM Sprzet""")
    if available_number is None or len(available_number) == 0:
        available_number = 0
    elif available_number[0][0][0] is None:
        available_number = 0
    else:
        available_number = available_number[0][0][0]
    form.number.default = available_number
    form.process()
    magazines, error = DBC().get_instance().execute_query_fetch(
        """SELECT numer, WolnaPojemnoscMagazynu(numer), oddzial_adres from Magazyn
        WHERE WolnaPojemnoscMagazynu(numer) > 0""")
    magazines_choices = [(str(m[0]), '{} w oddziale {} - wolne miejsce {}'.format(m[0], m[2], m[1])) for m in magazines]
    form.magazine_number.choices = magazines_choices
    print(form.magazine_number.choices)
    if request.method == 'POST':
        print(form.magazine_number.data)
        if form.validate():  # Input ok
            number = form.number.data
            purchase_date = form.purchase_date.data
            name = form.name.data
            define_new_type = form.new_or_existing_switch.data
            if define_new_type is None or define_new_type == 0 or define_new_type == '0':
                # Use existing type
                hw_type = form.existing_type.data
            else:
                hw_type = form.new_type.data
            manufacturer = form.brand.data
            notes = form.notes.data
            magazine_number = form.magazine_number.data
            if notes is None or notes == '':
                error = DBC().get_instance().execute_query_add_edit_delete(
                    """INSERT INTO Sprzet (numer_ewidencyjny, data_zakupu, nazwa, typ, producent, magazyn_numer) 
                    VALUES (%s, %s, %s, %s, %s, %s)""", (number, purchase_date, name, hw_type, manufacturer, magazine_number)
                )
            else:
                error = DBC().get_instance().execute_query_add_edit_delete(
                    """INSERT INTO Sprzet (numer_ewidencyjny, data_zakupu, nazwa, typ, producent, uwagi, magazyn_numer)
                    VALUES(%s, %s, %s, %s, %s, %s, %s)""",
                    (number, purchase_date, name, hw_type, manufacturer, notes, magazine_number)
                )
            if error is None:  # If there was no error
                flash('Sprzet został pomyślnie dodany')
                return redirect(url_for('show_info.pokaz_sprzet_info', numer_ewidencyjny=number))
            else:
                # Translate errors
                if error.errno == errorcode.ER_DUP_ENTRY:  # Duplicate entry
                    error.msg = 'Magazyn o podanym numerze już istnieje!'

            flash('Wystąpił błąd podczas dodawania magazynu!<br/>{}'.format(error.msg))
            return render_template(goto, form=form)
        else:
            flash('Proszę upewnić się czy wszystkie pola zostały poprawnie wypełnione!')
            return render_template(goto, form=form)
    else:
        return render_template(goto, form=form)


@add.route('/dodaj/oprogramowanie')
def dodaj_oprogramowanie():
    domyslne = {'numer_ewidencyjny': 15, 'data_zakupu': '2019-12-16'}
    return render_template('add/dodaj_oprogramowanie.html', domyslne=domyslne)

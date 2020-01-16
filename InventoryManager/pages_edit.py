from flask import Flask, render_template, request, flash, redirect, url_for, Blueprint, session
from forms import *
from database_connector import DatabaseConnector as DBC
from mysql.connector import errorcode

edit = Blueprint('edit', __name__)


@edit.route('/edytuj/oddzial/<adres>', methods=['GET', 'POST'])
def edytuj_oddzial(adres):
    form = AddEditBranchForm()
    if request.method == 'GET':
        current_data, error = DBC().get_instance().execute_query_fetch(
            """SELECT adres, nazwa FROM Oddzial WHERE adres = %s""", [adres])
        if error is None and current_data is not None and len(current_data) == 1:
            form = AddEditBranchForm(address=current_data[0][0], name=current_data[0][1])
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
                flash('Pomyślnie zedytowano oddział')
                session['wybrany_oddzial_adres'] = new_address
                session['wybrany_oddzial_nazwa'] = new_name
                return redirect(url_for('show_info.pokaz_oddzial_info', adres=new_address))
            else:
                # Translate errors to Polish
                if error.errno == errorcode.ER_DUP_ENTRY:
                    error.msg = 'Istnieje już oddział o podanym adresie!'
                elif error.errno in (errorcode.ER_ROW_IS_REFERENCED, errorcode.ER_ROW_IS_REFERENCED_2):
                    error.msg = 'Nie można zmienić adresu jeśli oddział posiada podrzędny dział, magazyn lub budynek!'
                flash('Wystąpił błąd!<br/>{}'.format(error.msg))
                return render_template('edit/edytuj_oddzial.html', form=form, adres=adres)
        else:
            flash('Proszę upewnić się czy wszystkie pola zostały poprawnie wypełnione!')
            return render_template('edit/edytuj_oddzial.html', form=form, adres=adres)


@edit.route('/edytuj/budynek/<adres>', methods=['GET', 'POST'])
def edytuj_budynek(adres):
    goto = 'edit/edytuj_budynek.html'
    form = AddEditBuildingForm()
    # form.branch_address.choices = branches_choices
    if request.method == 'GET':
        current_data, error = DBC().get_instance().execute_query_fetch(
            """SELECT adres, nazwa, ilosc_pieter
            FROM Budynek
            WHERE adres = %s""", [adres]
        )
        if error is None and len(current_data) == 1:
            form = AddEditBuildingForm(address=current_data[0][0],
                                       name=current_data[0][1],
                                       number_of_floors=current_data[0][2])
        else:
            flash('Wystąpił błąd!<br/>{}'.format(error.msg))
        return render_template(goto, form=form, adres=adres)
    if request.method == 'POST':
        if form.validate():  # Input ok
            new_address = form.address.data
            new_name = form.name.data
            new_number_of_floors = form.number_of_floors.data
            # branch_address = form.branch_address.data
            error = DBC().get_instance().execute_query_add_edit_delete(
                """UPDATE Budynek
                SET adres=%s, nazwa=%s, ilosc_pieter=%s
                WHERE adres = %s""", (new_address, new_name, new_number_of_floors, adres)
            )
            if error is None:  # If there was no error
                flash('Budynek został pomyślnie zedytowany')
                return redirect(url_for('show_info.pokaz_budynek_info', adres=adres))
            else:
                # Translate errors
                if error.errno == errorcode.ER_DUP_ENTRY:  # Duplicate entry
                    error.msg = 'Budynek o podanym adresie już istnieje!'
                elif error.errno in (errorcode.ER_ROW_IS_REFERENCED, errorcode.ER_ROW_IS_REFERENCED_2):
                    error.msg = 'Nie można zmienić adresu jeśli budynek posiada podrzędne obiekty!'

                flash('Wystąpił błąd podczas edycji budynku!<br/>{}'.format(error.msg))
                return render_template(goto, form=form, adres=adres)
        else:
            flash('Proszę upewnić się czy wszystkie pola zostały poprawnie wypełnione!')
            return render_template(goto, form=form, adres=adres)
    else:
        return render_template(goto, form=form, adres=adres)


@edit.route('/edytuj/biuro/<numer>', methods=['GET', 'POST'])
def edytuj_biuro(numer):
    goto = 'edit/edytuj_biuro.html'
    form = AddEditOfficeForm()
    buildings, error = DBC().get_instance().execute_query_fetch("""
        SELECT adres, nazwa 
        FROM Budynek 
        WHERE oddzial_adres = %s
        ORDER BY nazwa""", [session['wybrany_oddzial_adres']])
    if error is not None:
        flash('Wystąpił błąd podczas pobierania dostępnych budynków!<br/>{}'.format(error.msg))
    buildings_choices = [(building[0], ('{} ({})'.format(building[1], building[0]))) for building in buildings]
    form.building_address.choices = buildings_choices

    if request.method == 'GET':
        current_data, error = DBC().get_instance().execute_query_fetch(
            """SELECT numer, liczba_stanowisk, pietro, budynek_adres
             FROM Biuro 
             WHERE numer = %s""", [numer])
        if error is None and current_data is not None and len(current_data) == 1:
            form = AddEditOfficeForm(number=current_data[0][0],
                                     number_of_posts=current_data[0][1],
                                     floor=current_data[0][2],
                                     building_address=current_data[0][3])
            form.building_address.choices = buildings_choices
        else:
            flash('Wystąpił błąd!<br/>{}'.format(error.msg))
        return render_template(goto, form=form, numer=numer)

    if request.method == 'POST':
        if form.validate():  # Input ok
            new_number = form.number.data
            new_number_of_posts = form.number_of_posts.data
            new_floor = form.floor.data
            new_building_address = form.building_address.data
            # TODO: Sprawdzanie poprawności

            error = DBC().get_instance().execute_query_add_edit_delete(
                """UPDATE Biuro
                SET numer=%s, liczba_stanowisk=%s, pietro=%s, budynek_adres=%s
                WHERE numer=%s""",
                (new_number, new_number_of_posts, new_floor, new_building_address, numer)
            )
            if error is None:  # If there was no error
                # ok
                flash('Biuro zostało pomyślnie zaktualizowane')
                return redirect(url_for('show_info.pokaz_biuro_info', numer_biura=new_number))
            else:
                # Translate errors
                if error.errno == errorcode.ER_DUP_ENTRY:  # Duplicate entry
                    error.msg = 'Biuro o podanym numerze już istnieje!'
                elif error.errno in (errorcode.ER_ROW_IS_REFERENCED, errorcode.ER_ROW_IS_REFERENCED_2):
                    error.msg = 'Nie można zmienić numeru biura jeśli istnieją podlegli pracownicy lub przypisany sprzęt'
                else:
                    flash('Wystąpił błąd podczas edycji biura!<br/>{}'.format(error.msg))
                return render_template(goto, form=form, numer=numer)
        else:
            flash('Proszę upewnić się czy wszystkie pola zostały poprawnie wypełnione!')
            return render_template(goto, form=form, numer=numer)
    else:
        return render_template(goto, form=form, numer=numer)


@edit.route('/edytuj/dzial/<nazwa>', methods=['GET', 'POST'])
def edytuj_dzial(nazwa):
    goto = 'edit/edytuj_dzial.html'
    form = AddEditDepForm()

    if request.method == 'GET':
        current_data, error = DBC().get_instance().execute_query_fetch(
            """SELECT nazwa, skrot
            FROM Dzial
            WHERE nazwa = %s""", [nazwa])
        if error is None and current_data is not None and len(current_data) == 1:
            form = AddEditDepForm(name=current_data[0][0],
                                  name_short=current_data[0][1])
        else:
            flash('Wystąpił błąd!<br/>{}'.format(error.msg))
        return render_template(goto, form=form, nazwa=nazwa)

    if request.method == 'POST':
        if form.validate():  # Input ok
            new_name = form.name.data
            new_name_short = form.short_name.data
            # branch_address = form.branch_address.data
            error = DBC().get_instance().execute_query_add_edit_delete(
                """UPDATE Dzial
                SET nazwa=%s, skrot=%s
                WHERE nazwa = %s""", (new_name, new_name_short, nazwa)
            )
            if error is None:  # If there was no error
                flash('Dział został pomyślnie zedytowany')
                return redirect(url_for('show_info.pokaz_dzial_info', nazwa=nazwa))
            else:
                # Translate errors
                if error.errno == errorcode.ER_DUP_ENTRY:  # Duplicate entry
                    error.msg = 'Dział o podanej nazwie już istnieje!'
                elif error.errno in (errorcode.ER_ROW_IS_REFERENCED, errorcode.ER_ROW_IS_REFERENCED_2):
                    error.msg = 'Nie można zmienić nazwy działu jeśli istnieją zatrudnieni w nim pracownicy'
                flash('Wystąpił błąd podczas edycji działu!<br/>{}'.format(error.msg))
                return render_template(goto, form=form, nazwa=nazwa)
        else:
            flash('Proszę upewnić się czy wszystkie pola zostały poprawnie wypełnione!')
            return render_template(goto, form=form, nazwa=nazwa)
    else:
        return render_template(goto, form=form, nazwa=nazwa)


@edit.route('/edytuj/pracownik/<pesel>', methods=['GET', 'POST'])
def edytuj_pracownika(pesel):
    goto = 'edit/edytuj_pracownika.html'
    offices, error = DBC().get_instance().execute_query_fetch("""
        SELECT B.numer, B.budynek_adres, B.pietro, IleWolnychMiejscBiuro(B.numer)
        FROM Biuro B JOIN Budynek B2 on B.budynek_adres = B2.adres
        WHERE IleWolnychMiejscBiuro(B.numer) > 0
         AND B2.oddzial_adres = %s
        ORDER BY numer""", [session['wybrany_oddzial_adres']])
    if error is not None:
        flash('Wystąpił błąd podczas pobierania dostępnych biur!<br/>{}'.format(error.msg))
    offices_choices = [(office[0], '{} w {}, piętro {}, wolne miejsce {}'.format(
        office[0], office[1], office[2], office[3]))
                       for office in offices]
    depts, error = DBC().get_instance().execute_query_fetch("""
        SELECT nazwa, skrot
        FROM Dzial
        WHERE oddzial_adres = %s
        ORDER BY nazwa""", [session['wybrany_oddzial_adres']])
    if error is not None:
        flash('Wystąpił błąd podczas pobierania dostępnych działów!<br/>{}'.format(error.msg))
    depts_choices = [(dept[0], ('{} ({})'.format(dept[0], dept[1]))) for dept in depts]

    form = AddEditWorkerForm()
    form.office_number.choices = offices_choices
    form.dept_name.choices = depts_choices

    if request.method == 'GET':
        current_data, error = DBC().get_instance().execute_query_fetch(
            """SELECT pesel, imie, nazwisko, numer_telefonu,
            czy_nadal_pracuje, adres_email, dzial_nazwa, biuro_numer
            FROM Pracownik
            WHERE pesel = %s""", [pesel])
        if error is None and current_data is not None and len(current_data) == 1:
            if current_data[0][4] == 1 or current_data[0][4] == '1':
                is_still_working = 1
            else:
                is_still_working = None
            form = AddEditWorkerForm(pesel=current_data[0][0],
                                     name=current_data[0][1],
                                     surname=current_data[0][2],
                                     phone_number=current_data[0][3],
                                     is_still_working=is_still_working,
                                     email_address=current_data[0][5],
                                     dept_name=current_data[0][6],
                                     office_number=current_data[0][7])
            form.office_number.choices = offices_choices
            form.dept_name.choices = depts_choices
        else:
            flash('Wystąpił błąd!<br/>{}'.format(error.msg))
        return render_template(goto, form=form, pesel=pesel)

    if request.method == 'POST':
        if form.validate():  # Input ok
            new_pesel = form.pesel.data
            new_name = form.name.data
            new_surname = form.surname.data
            new_phone_number = form.phone_number.data
            if form.is_still_working.data:
                new_is_still_working = '1'
            else:
                new_is_still_working = '0'
            new_email = form.email_address.data
            new_dept_name = form.dept_name.data
            new_office_number = form.office_number.data

            error = DBC().get_instance().execute_query_add_edit_delete(
                """UPDATE Pracownik
                SET pesel=%s, imie=%s, nazwisko=%s, numer_telefonu=%s,
                czy_nadal_pracuje=%s, adres_email=%s, dzial_nazwa=%s, biuro_numer=%s
                WHERE pesel=%s""",
                [new_pesel, new_name, new_surname, new_phone_number, new_is_still_working,
                 new_email, new_dept_name, new_office_number, pesel]
            )
            if error is None:  # If there was no error
                flash('Pracownik został pomyślnie zedytowany')
                return redirect(url_for('show_info.pokaz_pracownik_info', pesel=pesel))
            else:
                # Translate errors
                if error.errno == errorcode.ER_DUP_ENTRY:  # Duplicate entry
                    error.msg = 'Pracownik o podanym numerze PESEL już istnieje!'
                elif error.errno in (errorcode.ER_ROW_IS_REFERENCED, errorcode.ER_ROW_IS_REFERENCED_2):
                    error.msg = 'Nie można zmienić numeru PESEL jeśli istnieją podrzędne obiekty (na przykład karta dostępu)'

                flash('Wystąpił błąd podczas edycji pracownika!<br/>{}'.format(error.msg))
                return render_template(goto, form=form, pesel=pesel)
        else:
            flash('Proszę upewnić się czy wszystkie pola zostały poprawnie wypełnione!')
            return render_template(goto, form=form, pesel=pesel)
    else:
        return render_template(goto, form=form, pesel=pesel)


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

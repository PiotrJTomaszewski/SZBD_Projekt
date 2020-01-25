from flask import Flask, render_template, request, flash, redirect, url_for, Blueprint, session
from forms import *
from database_connector import DatabaseConnector as DBC
from mysql.connector import errorcode
from helpers import *

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
    form = AddEditBuildingForm(address=session['wybrany_oddzial_adres'] + ' ')

    if request.method == 'POST':
        if form.validate():  # Input ok
            address = form.address.data
            name = form.name.data
            number_of_floors = form.number_of_floors.data
            # branch_address = form.branch_address.data
            error = DBC().get_instance().execute_query_add_edit_delete(
                """INSERT INTO Budynek (adres, nazwa, ilosc_pieter, oddzial_adres)
                VALUES(%s, %s, %s, %s)""", (address, name, number_of_floors, session['wybrany_oddzial_adres'])
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
    buildings, error = DBC().get_instance().execute_query_fetch("""
    SELECT adres, nazwa, ilosc_pieter 
    FROM Budynek 
    WHERE oddzial_adres = %s
    ORDER BY nazwa""", [session['wybrany_oddzial_adres']])
    if error is not None:
        flash('Wystąpił błąd podczas pobierania dostępnych budynków!<br/>{}'.format(error.msg))
    buildings_choices = [(building[0], ('{} ({}) - {} pięter'.format(building[1], building[0], building[2]))) for building in buildings]
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
    form = AddEditDepForm()

    if request.method == 'POST':
        if form.validate():  # Input ok
            name = form.name.data
            name_short = form.short_name.data
            # branch_address = form.branch_address.data
            error = DBC().get_instance().execute_query_add_edit_delete(
                """INSERT INTO Dzial (nazwa, skrot, oddzial_adres)
                VALUES(%s, %s, %s)""", (name, name_short, session['wybrany_oddzial_adres'])
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

    if request.method == 'POST':
        if form.validate():  # Input ok
            pesel = form.pesel.data
            name = form.name.data
            surname = form.surname.data
            phone_number = form.phone_number.data
            if form.is_still_working.data:
                is_still_working = '1'
            else:
                is_still_working = '0'
            email = form.email_address.data
            dept_name = form.dept_name.data
            office_number = form.office_number.data
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

    next_available_number, error = DBC().get_instance().execute_query_fetch("""SELECT MAX(numer)+1
    FROM Magazyn""")
    if error is not None:
        flash('Wystąpił błąd podczas pobierania sugerowanego numeru magazynu')
    if next_available_number is None or len(next_available_number) == 0:
        next_available_number = 0
    else:
        next_available_number = next_available_number[0][0]
    form = AddEditWarehouseForm(number=next_available_number)

    if request.method == 'POST':
        if form.validate():  # Input ok
            number = form.number.data
            capacity = form.capacity.data
            error = DBC().get_instance().execute_query_add_edit_delete(
                """INSERT INTO Magazyn (numer, pojemnosc, oddzial_adres)
                VALUES(%s, %s, %s)""", (number, capacity, session['wybrany_oddzial_adres'])
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
    types, error = DBC().get_instance().execute_query_fetch("""SELECT DISTINCT typ FROM Sprzet ORDER BY typ""")
    if error is not None:
        flash('Wystąpił błąd podczas pobierania dostępnych typów sprzętu!<br/>{}'.format(error.msg))

    # Get some available evidence number
    available_number = DBC().get_instance().execute_query_fetch("""SELECT max(numer_ewidencyjny)+1 FROM Sprzet""")
    if available_number is None or len(available_number) == 0:
        available_number = 0
    elif available_number[0][0][0] is None:
        available_number = 0
    else:
        available_number = available_number[0][0][0]

    form = AddEditHardwareForm(number=available_number)

    types_choices = [(t[0], t[0]) for t in types]
    form.existing_type.choices = types_choices

    warehouses, error = DBC().get_instance().execute_query_fetch(
        """SELECT numer, WolnaPojemnoscMagazynu(numer) from Magazyn
        WHERE WolnaPojemnoscMagazynu(numer) > 0
         AND oddzial_adres = %s""", [session['wybrany_oddzial_adres']])
    warehouses_choices = [(m[0], '{} - wolne miejsce {}'.format(m[0], m[1])) for m in warehouses]
    form.warehouse_number.choices = warehouses_choices

    if request.method == 'POST':
        if form.validate_on_submit():  # Input ok
            number = form.number.data  # TODO: Make this not necessary
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
            warehouse_number = form.warehouse_number.data
            error = DBC().get_instance().execute_query_add_edit_delete(
                """INSERT INTO Sprzet (numer_ewidencyjny, data_zakupu, nazwa, typ, producent, uwagi, magazyn_numer)
                VALUES(%s, %s, %s, %s, %s, %s, %s)""",
                (number, purchase_date, name, hw_type, manufacturer, notes, warehouse_number)
            )
            if error is None:  # If there was no error
                flash('Sprzet został pomyślnie dodany')
                return redirect(url_for('show_info.pokaz_sprzet_info', numer_ewidencyjny=number))
            else:
                # Translate errors
                if error.errno == errorcode.ER_DUP_ENTRY:  # Duplicate entry
                    error.msg = 'Sprzęt o podanym numerze ewidencyjnym już istnieje!'

            flash('Wystąpił błąd podczas dodawania sprzętu!<br/>{}'.format(error.msg))
            return render_template(goto, form=form)
        else:
            flash('Proszę upewnić się czy wszystkie pola zostały poprawnie wypełnione!')
            return render_template(goto, form=form)
    else:
        return render_template(goto, form=form)


@add.route('/dodaj/oprogramowanie', methods=['GET', 'POST'])
def dodaj_oprogramowanie():
    goto = 'add/dodaj_oprogramowanie.html'

    # Get some available evidence number
    available_number = DBC().get_instance().execute_query_fetch(
        """SELECT max(numer_ewidencyjny)+1 FROM Oprogramowanie""")
    if available_number is None or len(available_number) == 0:
        available_number = 0
    elif available_number[0][0][0] is None:
        available_number = 0
    else:
        available_number = available_number[0][0][0]

    form = AddEditSoftware(number=available_number)

    if request.method == 'POST':
        if form.validate_on_submit():  # Input ok
            number = form.number.data  # TODO: Make this not necessary
            name = form.name.data
            manufacturer = form.brand.data
            purchase_date = form.purchase_date.data
            expiration_date = form.expiration_date.data
            licence_count = form.number_of_licences.data
            notes = form.notes.data

            if expiration_date and expiration_date < purchase_date:
                flash('Błąd. Licencja nie może wygasać przed zakupem')
                return render_template(goto, form=form)

            error = DBC().get_instance().execute_query_add_edit_delete(
                """INSERT INTO Oprogramowanie (numer_ewidencyjny, nazwa, producent, data_zakupu,
                 data_wygasniecia, ilosc_licencji, uwagi)
                VALUES (%s, %s, %s, %s, %s, %s, %s)""",
                (number, name, manufacturer, purchase_date, expiration_date, licence_count, notes)
            )

            if error is None:  # If there was no error
                flash('Oprogramowanie zostało pomyślnie dodane')
                return redirect(url_for('show_info.pokaz_oprogramowanie_info', numer_ewidencyjny=number))
            else:
                # Translate errors
                if error.errno == errorcode.ER_DUP_ENTRY:  # Duplicate entry
                    error.msg = 'Oprogramowanie o podanym numerze ewidencyjnym już istnieje!'
                elif error.errno == 4025:  # Constraint CHK_data failed
                    error.msg = 'Licencja nie może wygasać przed zakupem!'

            flash('Wystąpił błąd podczas dodawania oprogramowania!<br/>{}'.format(error.msg))
            return render_template(goto, form=form)
        else:
            flash('Proszę upewnić się czy wszystkie pola zostały poprawnie wypełnione!')
            return render_template(goto, form=form)
    else:
        return render_template(goto, form=form)


@add.route('/dodaj/karta/pracownik/<pesel>')
def dodaj_karta(pesel):
    worker, error = DBC().get_instance().execute_query_fetch("""
    SELECT pesel, imie, nazwisko, biuro_numer, dzial_nazwa
    FROM Pracownik
    WHERE pesel = %s""", [pesel])
    if error or not worker:
        flash('Wystąpił błąd podczas pobierania informacji o pracowniku')
        return redirect(url_for('show.pracownicy'))
    worker_data = make_dictionary(['pesel', 'imie', 'nazwisko', 'biuro_numer', 'dzial_nazwa'], worker[0])

    offices, error = DBC().get_instance().execute_query_fetch("""
    SELECT BI.numer, BI.pietro, BI.budynek_adres
    FROM Biuro BI
    JOIN Budynek BU on BI.budynek_adres = BU.adres
    WHERE BU.oddzial_adres = %s
    ORDER BY BI.numer""", [session['wybrany_oddzial_adres']])
    if error:
        flash('Wystąpił błąd podczas pobierania dostępnych biur')
        return redirect(url_for('show_info.pokaz_pracownik_info', pesel=pesel))
    if not offices:
        flash('W oddziale nie znajdują się żadne biura')
        return redirect(url_for('show_info.pokaz_pracownik_info', pesel=pesel))
    offices_data = make_dictionaries_list(['numer', 'pietro', 'budynek_adres'], offices)

    return render_template('add/dodaj_karte.html', pracownik=worker_data, biura=offices_data)


@add.route('/wykonaj/dodaj/karta/pracownik/<pesel>', methods=['GET', 'POST'])
def wykonaj_dodaj_karta(pesel):
    if request.method == 'GET':
        return redirect(url_for('dodaj_karta', pesel=pesel))
    if request.method == 'POST':
        selected_offices = request.form.getlist('selected_offices')
        if not selected_offices:
            flash('Proszę wybrać biuro')
            return redirect(url_for('add.dodaj_karta', pesel=pesel))
        selected_offices = [int(x) for x in selected_offices]
        assignment_date = request.form.get('card_assignment_date')
        expiration_date = request.form.get('access_expiration_date')

        assignment_date = string_to_date(assignment_date)
        if expiration_date and expiration_date != '':
            expiration_date = string_to_date(expiration_date)
        else:
            expiration_date = None

        if expiration_date and expiration_date < assignment_date:
            flash('Data wygaśnięcia prawa nie może być wcześniejsza niż data przyznania karty')
            return redirect(url_for('add.dodaj_karta', pesel=pesel))

        # Create new card
        card_id, error = DBC().get_instance().execute_query_add_edit_delete_with_fetch_last_id("""
        INSERT INTO KartaDostepu
        (data_przyznania, pracownik_pesel)
        VALUES (%s, %s)""", [assignment_date, pesel])
        if error or not card_id:
            flash('Wystąpił błąd podczas dodawania nowej karty')
            return redirect(url_for('add.dodaj_karta', pesel=pesel))
        card_id = card_id[0][0]

        if request.form.get('add_access'):
            for office_number in selected_offices:
                # Assign access to the card
                error = DBC().get_instance().execute_query_add_edit_delete("""
                INSERT INTO PrawoDostepu (data_przyznania, data_wygasniecia, kartadostepu_id_karty, biuro_numer)
                VALUES (%s, %s, %s, %s)""", [assignment_date, expiration_date, card_id, office_number])
                if error:
                    flash('Wystąpił błąd podczas przypisywania do karty prawa dostępu')
                    return redirect(url_for('show_info.pokaz_pracownik_info', pesel=pesel))
        flash('Karta została pomyślnie dodana')
        return redirect(url_for('show_info.pokaz_pracownik_info', pesel=pesel))

from flask import Flask, render_template, request, flash, redirect, url_for, Blueprint, session
from forms import *
from database_connector import DatabaseConnector as DBC
from mysql.connector import errorcode
from helpers import *

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
            flash('Wystąpił błąd podczas pobierania informacji o oddziale')
            return redirect(url_for('strona_glowna'))
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
            max_floor_office, _ = DBC().get_instance().execute_query_fetch("""
            SELECT MAX(pietro)
            FROM Biuro
            WHERE budynek_adres = %s""", [adres])
            if max_floor_office and max_floor_office[0][0] >= new_number_of_floors:
                flash('Wystąpił błąd podczas edycji budynku!<br/>'
                      'W budynku istnieje biuro na piętrze {}, więc liczba pięter w budynku musi być większa'.format(
                    max_floor_office[0][0]))
                return render_template(goto, form=form, adres=adres)

            error = DBC().get_instance().execute_query_add_edit_delete(
                """UPDATE Budynek
                SET adres=%s, nazwa=%s, ilosc_pieter=%s
                WHERE adres = %s""", (new_address, new_name, new_number_of_floors, adres)
            )
            if error is None:  # If there was no error
                flash('Budynek został pomyślnie zedytowany')
                return redirect(url_for('show_info.pokaz_budynek_info', adres=new_address))
            else:
                # Translate errors
                if error.errno == errorcode.ER_DUP_ENTRY:  # Duplicate entry
                    error.msg = 'Budynek o podanym adresie już istnieje!'
                elif error.errno in (errorcode.ER_ROW_IS_REFERENCED, errorcode.ER_ROW_IS_REFERENCED_2):
                    error.msg = 'Nie można zmienić adresu jeśli w budynku znajdują się biura!'

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
        SELECT adres, nazwa, ilosc_pieter
        FROM Budynek 
        WHERE oddzial_adres = %s
        ORDER BY nazwa""", [session['wybrany_oddzial_adres']])
    if error is not None:
        flash('Wystąpił błąd podczas pobierania dostępnych budynków!<br/>{}'.format(error.msg))
    buildings_choices = [(building[0], ('{} ({}) - {} pięter'.format(building[1], building[0], building[2]))) for
                         building in buildings]
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

            floors_in_building, _ = DBC().get_instance().execute_query_fetch("""
            SELECT ilosc_pieter
            FROM Budynek
            WHERE adres = %s""", [new_building_address])
            if floors_in_building and new_floor >= floors_in_building[0][0]:
                flash(
                    'Wystąpił błąd podczas edycji biura! <br/> Nieprawidłowe piętro, w budynku {} jest {} pięter'.format(
                        new_building_address, floors_in_building[0][0]))
                return render_template(goto, form=form, numer=numer)

            workers_in_building, _ = DBC().get_instance().execute_query_fetch("""
            SELECT COUNT(*)
            FROM Pracownik
            WHERE biuro_numer = %s
            AND czy_nadal_pracuje = '1'""", [numer])
            if workers_in_building and workers_in_building[0][0] > new_number_of_posts:
                flash('Wystąpił błąd podczas edycji biura! <br/> '
                      'Liczba stanowisk nie może być mniejsza, niż liczba osób pracujących w biurze ({})!'.format(
                    workers_in_building[0][0]))
                return render_template(goto, form=form, numer=numer)

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
                                  short_name=current_data[0][1])
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
                return redirect(url_for('show_info.pokaz_dzial_info', nazwa=new_name))
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
            flash('Wystąpił błąd!<br/>Nie znaleziono pracownika')
            return redirect(url_for('show.pracownicy'))
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
                return redirect(url_for('show_info.pokaz_pracownik_info', pesel=new_pesel))
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
    goto = 'edit/edytuj_magazyn.html'
    current_capacity, error = DBC().get_instance().execute_query_fetch("""
    SELECT pojemnosc
    FROM Magazyn
    WHERE numer = %s""", [numer])
    if not current_capacity or error:
        flash('Wystąpił błąd!<br/>Nie znaleziono magazynu')
        return redirect(url_for('show.magazyny'))
    form = AddEditWarehouseForm(number=numer, capacity=current_capacity[0][0])

    if request.method == 'POST':
        if form.validate():  # Input ok
            new_number = form.number.data
            new_capacity = form.capacity.data
            capacity_taken, error = DBC().get_instance().execute_query_fetch("""
            SELECT COUNT(*)
            FROM Sprzet
            WHERE magazyn_numer = %s""", [numer])
            if capacity_taken and not error:
                if capacity_taken[0][0] > new_capacity:
                    flash("""Nowa pojemność magazynu nie może być mniejsza od zajętej pojemności ({})""".format(
                        capacity_taken[0][0]))
                    return render_template(goto, form=form, numer=numer)

            error = DBC().get_instance().execute_query_add_edit_delete("""
            UPDATE Magazyn
            SET numer=%s, pojemnosc=%s
            WHERE numer=%s""", [new_number, new_capacity, numer])
            if error is None:  # If there was no error
                flash('Magazyn został pomyślnie zedytowany')
                return redirect(url_for('show_info.pokaz_magazyn_info', numer=new_number))
            else:
                # Translate errors
                if error.errno == errorcode.ER_DUP_ENTRY:  # Duplicate entry
                    error.msg = 'Magazyn o podanym numerze już istnieje!'
                elif error.errno in (errorcode.ER_ROW_IS_REFERENCED, errorcode.ER_ROW_IS_REFERENCED_2):
                    error.msg = 'Nie można zmienić numeru jeśli w magazynie znajduje się sprzęt'
                flash('Wystąpił błąd podczas edycji magazynu!<br/>{}'.format(error.msg))
                return render_template(goto, form=form, numer=numer)
        else:
            flash('Proszę upewnić się czy wszystkie pola zostały poprawnie wypełnione!')
            return render_template(goto, form=form, numer=numer)
    else:
        return render_template(goto, form=form, numer=numer)


@edit.route('/edytuj/sprzet/<numer_ewidencyjny>', methods=['GET', 'POST'])
def edytuj_sprzet(numer_ewidencyjny):
    goto = 'edit/edytuj_sprzet.html'

    current_data, error = DBC().get_instance().execute_query_fetch("""
    SELECT numer_ewidencyjny, data_zakupu, nazwa, typ, producent, uwagi, magazyn_numer
    FROM Sprzet
    WHERE numer_ewidencyjny = %s""", [numer_ewidencyjny])
    if error or not current_data:
        flash('Nie udało się pobrać informacji o sprzęcie')
        return redirect(url_for('show.sprzet_w_magazynach'))
    current_data = make_dictionary(
        ['numer_ewidencyjny', 'data_zakupu', 'nazwa', 'typ', 'producent', 'uwagi', 'magazyn_numer'], current_data[0])

    types, error = DBC().get_instance().execute_query_fetch("""SELECT DISTINCT typ FROM Sprzet ORDER BY typ""")
    if error is not None:
        flash('Wystąpił błąd podczas pobierania dostępnych typów sprzętu!')

    form = AddEditHardwareForm(number=current_data['numer_ewidencyjny'],
                               purchase_date=current_data['data_zakupu'],
                               name=current_data['nazwa'],
                               existing_type=current_data['typ'],
                               brand=current_data['producent'],
                               warehouse=current_data['magazyn_numer'],
                               notes=current_data['uwagi']
                               )

    types_choices = [(t[0], t[0]) for t in types]
    form.existing_type.choices = types_choices
    warehouses, error = DBC().get_instance().execute_query_fetch(
        """SELECT DISTINCT numer, WolnaPojemnoscMagazynu(numer)
        FROM Magazyn LEFT JOIN Sprzet S on Magazyn.numer = S.magazyn_numer
        WHERE (WolnaPojemnoscMagazynu(numer) > 0
         OR S.numer_ewidencyjny = %s)
         AND oddzial_adres = %s
        ORDER BY numer""", [numer_ewidencyjny, session['wybrany_oddzial_adres']])
    warehouses_choices = []
    for m in warehouses:
        if m[0] == current_data['magazyn_numer']:
            warehouses_choices.append([m[0], '{} - obecny magazyn'.format(m[0])])
        else:
            warehouses_choices.append([m[0], '{} - wolne miejsce {}'.format(m[0], m[1])])
    form.warehouse_number.choices = warehouses_choices

    if request.method == 'POST':
        if not current_data['magazyn_numer']:  # If the hardware is not in a warehouse ignore this field
            form.warehouse_number.validators.clear()
            form.warehouse_number.validators.append(validators.Optional())
        if form.validate_on_submit():  # Input ok
            new_number = form.number.data
            new_purchase_date = form.purchase_date.data
            new_name = form.name.data
            new_define_new_type = form.new_or_existing_switch.data
            if new_define_new_type is None or new_define_new_type == 0 or new_define_new_type == '0':
                # Use existing type
                new_hw_type = form.existing_type.data
            else:
                new_hw_type = form.new_type.data
            new_manufacturer = form.brand.data
            new_notes = form.notes.data
            if current_data['magazyn_numer']:  # Only if already in any warehouse
                new_warehouse_number = form.warehouse_number.data
            else:
                new_warehouse_number = None
            error = DBC().get_instance().execute_query_add_edit_delete(
                """UPDATE Sprzet
                SET numer_ewidencyjny=%s, data_zakupu=%s, nazwa=%s, typ=%s, producent=%s, uwagi=%s, magazyn_numer=%s
                WHERE numer_ewidencyjny = %s""",
                [new_number, new_purchase_date, new_name, new_hw_type, new_manufacturer, new_notes,
                 new_warehouse_number,
                 numer_ewidencyjny]
            )
            if error is None:  # If there was no error
                flash('Sprzet został pomyślnie zedytowany')
                return redirect(url_for('show_info.pokaz_sprzet_info', numer_ewidencyjny=new_number))
            else:
                # Translate errors
                if error.errno == errorcode.ER_DUP_ENTRY:  # Duplicate entry
                    error.msg = 'Sprzęt o podanym numerze ewidencyjnym już istnieje!'
                elif error.errno in (errorcode.ER_ROW_IS_REFERENCED, errorcode.ER_ROW_IS_REFERENCED_2):
                    error.msg = 'Nie można zmienić numeru ewidencyjnego, jeśli sprzęt znajduje się w jakimś przypisaniu!'
            flash('Wystąpił błąd podczas dodawania sprzętu!<br/>{}'.format(error.msg))
            return render_template(goto, form=form, sprzet=current_data)
        else:
            flash('Proszę upewnić się czy wszystkie pola zostały poprawnie wypełnione!')
            return render_template(goto, form=form, sprzet=current_data)
    else:
        return render_template(goto, form=form, sprzet=current_data)


@edit.route('/edytuj/oprogramowanie/<numer_ewidencyjny>', methods=['GET', 'POST'])
def edytuj_oprogramowanie(numer_ewidencyjny):
    goto = 'edit/edytuj_oprogramowanie.html'
    # Get current data
    current_data, error = DBC().get_instance().execute_query_fetch("""
    SELECT numer_ewidencyjny, nazwa, producent, data_zakupu, data_wygasniecia, ilosc_licencji, uwagi
    FROM Oprogramowanie
    WHERE numer_ewidencyjny = %s""", [numer_ewidencyjny])
    if error or not current_data:
        print(error)
        flash('Nie znaleziono oprogramowania')
        return redirect(url_for('show.oprogramowanie'))
    current_data = make_dictionary(
        ['numer_ewidencyjny', 'nazwa', 'producent', 'data_zakupu', 'data_wygasniecia', 'liczba_licencji', 'uwagi'],
        current_data[0])

    form = AddEditSoftware(number=current_data['numer_ewidencyjny'],
                           name=current_data['nazwa'],
                           brand=current_data['producent'],
                           purchase_date=current_data['data_zakupu'],
                           expiration_date=current_data['data_wygasniecia'],
                           number_of_licences=current_data['liczba_licencji'],
                           notes=current_data['uwagi']
                           )

    if request.method == 'POST':
        if form.validate_on_submit():  # Input ok
            new_number = form.number.data
            new_name = form.name.data
            new_manufacturer = form.brand.data
            new_purchase_date = form.purchase_date.data
            new_expiration_date = form.expiration_date.data
            new_licence_count = form.number_of_licences.data
            new_notes = form.notes.data

            if new_expiration_date and new_expiration_date < new_purchase_date:
                flash('Wystąpił błąd. Licencja nie może wygasać przed zakupem')
                return render_template(goto, form=form, numer_ewidencyjny=numer_ewidencyjny)

            # Check if used licence count doesn't exceed new total licence count
            if new_licence_count:  # Only if there are finite licence copies
                used_licences, error = DBC().get_instance().execute_query_fetch("""
                SELECT COUNT(*) FROM OprogramowanieNaSprzecie
                WHERE oprogramowanie_numer=%s""", [numer_ewidencyjny])
                if error:
                    print(error)
                if used_licences and new_licence_count < used_licences[0][0]:
                    flash("""Wystąpił błąd. Liczba używanych obecnie kopii tego oprogramowania ({}) 
                    nie może przewyższać liczby dostępnych licencji.""".format(used_licences[0][0]))
                    return render_template(goto, form=form, numer_ewidencyjny=numer_ewidencyjny)

            error = DBC().get_instance().execute_query_add_edit_delete(
                """UPDATE Oprogramowanie
                 SET numer_ewidencyjny=%s, nazwa=%s, producent=%s, data_zakupu=%s,
                 data_wygasniecia=%s, ilosc_licencji=%s, uwagi=%s
                 WHERE numer_ewidencyjny=%s""",
                [new_number, new_name, new_manufacturer, new_purchase_date, new_expiration_date, new_licence_count,
                 new_notes, numer_ewidencyjny]
            )

            if error is None:  # If there was no error
                flash('Oprogramowanie zostało pomyślnie zedytowane')
                return redirect(url_for('show_info.pokaz_oprogramowanie_info', numer_ewidencyjny=new_number))
            else:
                # Translate errors
                if error.errno == errorcode.ER_DUP_ENTRY:  # Duplicate entry
                    error.msg = 'Oprogramowanie o podanym numerze ewidencyjnym już istnieje!'
                elif error.errno == 4025:  # Constraint CHK_data failed
                    error.msg = 'Licencja nie może wygasać przed zakupem!'
                elif error.errno in (errorcode.ER_ROW_IS_REFERENCED, errorcode.ER_ROW_IS_REFERENCED_2):
                    error.msg = 'Nie można zmienić numeru ewidencyjnego, jeśli oprogramowanie jest zainstalowane na jakimś sprzęcie!'
            flash('Wystąpił błąd podczas dodawania oprogramowania!<br/>{}'.format(error.msg))
            return render_template(goto, form=form, numer_ewidencyjny=numer_ewidencyjny)
        else:
            flash('Proszę upewnić się czy wszystkie pola zostały poprawnie wypełnione!')
            return render_template(goto, form=form, numer_ewidencyjny=numer_ewidencyjny)
    else:
        return render_template(goto, form=form, numer_ewidencyjny=numer_ewidencyjny)

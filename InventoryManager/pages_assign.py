from flask import Flask, render_template, request, flash, redirect, url_for, Blueprint, session
from database_connector import DatabaseConnector as DBC
from helpers import *

assign = Blueprint('assign', __name__)


@assign.route('/przypisz/sprzet/pracownik/<pesel>')
def przypisz_sprzet_pracownik(pesel):
    worker_data, error = DBC().get_instance().execute_query_fetch("""
    SELECT pesel, imie, nazwisko, skrot, oddzial_adres, biuro_numer
    FROM Pracownik P
    JOIN Dzial D on P.dzial_nazwa = D.nazwa
    WHERE pesel = %s""", [pesel])
    if not worker_data or error:
        print(error)
        flash('Nie udało się pobrać danych pracownika')
        return redirect(url_for("show.pracownicy"))
    worker = make_dictionary(['pesel', 'imie', 'nazwisko', 'dzial_skrot', 'oddzial_adres', 'biuro_numer'],
                             worker_data[0])

    title = 'Przypisz sprzęt do pracownika {imie} {nazwisko}, dział {dzial}, biuro {biuro}'.format(
        imie=worker['imie'], nazwisko=worker['nazwisko'], dzial=worker['dzial_skrot'],
        biuro=worker['biuro_numer']
    )
    post_address = url_for('assign._przypisz_sprzet_pracownik_post', pesel=pesel)

    available_hardware_data, error = DBC().get_instance().execute_query_fetch("""
    SELECT numer_ewidencyjny, typ, nazwa, producent, data_zakupu, magazyn_numer
    FROM Sprzet
    JOIN Magazyn M on Sprzet.magazyn_numer = M.numer
    WHERE oddzial_adres = %s
    ORDER BY numer_ewidencyjny""", [worker['oddzial_adres']])
    if error:
        print(error)
        flash('Nie udało się pobrać dostępnego sprzętu')
        return redirect(url_for("show.pracownicy"))

    available_hardware = make_dictionaries_list(['numer', 'typ', 'nazwa', 'producent', 'data_zakupu', 'numer_magazynu'],
                                                available_hardware_data)
    if not available_hardware:
        flash('Nie ma wolnego sprzętu w magazynach')
        return redirect(url_for('show_info.pokaz_pracownik_info', pesel=pesel))

    current_assignments_data, error = DBC().get_instance().execute_query_fetch("""
    SELECT id_przydzialu, DATE_FORMAT(data_przydzialu, '%d.%m.%Y')
    FROM Przypisanie
    WHERE pracownik_pesel = %s
    AND data_zwrotu IS NULL;""", [worker['pesel']])
    if error:
        print(error)
        flash('Nie udało się pobrać obecnie istniejących przypisań')
        return redirect(url_for("show.pracownicy"))

    current_assignments = make_dictionaries_list(['id', 'data_przydzialu'], current_assignments_data)

    return render_template('assign/przypisz_sprzet.html', tytul=title, przypisania=current_assignments,
                           sprzety=available_hardware, post_adres=post_address)


@assign.route('/wykonaj/przypisz/sprzet/pracownik/<pesel>', methods=['POST', 'GET'])
def _przypisz_sprzet_pracownik_post(pesel):
    if request.method == 'GET':
        return redirect(url_for('assign.przypisz_sprzet_pracownik', pesel=pesel))
    if request.method == 'POST':
        worker_data, error = DBC().get_instance().execute_query_fetch("""
            SELECT pesel, imie, nazwisko, skrot, oddzial_adres
            FROM Pracownik P
            JOIN Dzial D on P.dzial_nazwa = D.nazwa
            WHERE pesel = %s""", [pesel])
        if not worker_data or error:
            print(error)
            flash('Nie udało się pobrać danych pracownika')
            return redirect(url_for("show.pracownicy"))
        worker = make_dictionary(['pesel', 'imie', 'nazwisko', 'dzial_skrot', 'oddzial_adres'], worker_data[0])

        list_of_hardware = request.form.getlist('hardware')
        if len(list_of_hardware) == 0:
            flash('Nie wybrano żadnego sprzętu')
            return redirect(url_for('assign.przypisz_sprzet_pracownik', pesel=pesel))

        assignment_date = request.form.get('assignment_date_box')
        if request.form.get('assignment_date_box') != '':
            assignment_id, error = DBC().get_instance().execute_query_add_edit_delete_with_fetch_last_id("""
            INSERT INTO Przypisanie
            (data_przydzialu, pracownik_pesel)
            VALUES (%s, %s)""", [assignment_date, worker['pesel']])
            if error:
                print(error)
                flash('Wystąpił bład podczas dodawania nowego przypisania')
                return redirect(url_for('assign.przypisz_sprzet_pracownik', pesel=pesel))
            assignment_id = assignment_id[0][0]
        else:  # New assignment date box empty
            flash('Data przypisania nie może być pusta')
            return redirect(url_for('assign.przypisz_sprzet_pracownik', pesel=pesel))

        # Assign hardware
        for hardware in list_of_hardware:
            error_code, error = DBC().get_instance().execute_query_add_edit_delete_with_fetch("""
            SELECT PrzypiszSprzet(%s, %s) FROM dual""", [hardware, assignment_id])
            if error or error_code[0][0] != 0:
                if not error:
                    if error_code[0][0] == 1:
                        msg = 'Wybrany sprzęt nie znajduje się w magazynie'
                        flash('Wystąpił błąd podczas przypisywania sprzętu ' + msg)
                    elif error_code[0][0] == 2:
                        msg = 'Podaczas przypisywania sprzętu wystąpił wyjątek'
                        flash('Wystąpił błąd podczas przypisywania sprzętu ' + msg)
                else:
                    flash('Wystąpił błąd podczas przypisywania sprzętu ' + error.msg)
                return redirect(url_for('assign.przypisz_sprzet_pracownik', pesel=pesel))
        flash('Sprzęt został przypisany pomyślnie')
    return redirect(url_for('show_info.pokaz_pracownik_info', pesel=pesel))


@assign.route('/przypisz/sprzet/biuro/<numer_biura>')
def przypisz_sprzet_biuro(numer_biura):
    office_data, error = DBC().get_instance().execute_query_fetch("""
    SELECT numer, pietro, budynek_adres, oddzial_adres
    FROM Biuro
    JOIN Budynek B on Biuro.budynek_adres = B.adres
    WHERE numer = %s""", [numer_biura])
    if not office_data or error:
        print(error)
        flash('Nie udało się pobrać danych biura')
        return redirect(url_for("show.biura"))
    office = make_dictionary(['numer', 'pietro', 'budynek_adres', 'oddzial_adres'], office_data[0])

    title = 'Przypisz sprzęt do biura numer {numer} w {budynek}, piętro {pietro}'.format(
        numer=office['numer'], budynek=office['budynek_adres'], pietro=office['pietro']
    )
    post_address = url_for('assign._przypisz_sprzet_biuro_post', numer_biura=numer_biura)

    available_hardware_data, error = DBC().get_instance().execute_query_fetch("""
    SELECT numer_ewidencyjny, typ, nazwa, producent, data_zakupu, magazyn_numer
    FROM Sprzet
    JOIN Magazyn M on Sprzet.magazyn_numer = M.numer
    WHERE oddzial_adres = %s
    ORDER BY numer_ewidencyjny""", [office['oddzial_adres']])
    if error:
        print(error)
        flash('Nie udało się pobrać dostępnego sprzętu')
        return redirect(url_for('show.biura'))

    available_hardware = make_dictionaries_list(['numer', 'typ', 'nazwa', 'producent', 'data_zakupu', 'numer_magazynu'],
                                                available_hardware_data)
    if not available_hardware:
        flash('Nie ma wolnego sprzętu w magazynach')
        return redirect(url_for("show_info.pokaz_biuro_info", numer_biura=numer_biura))

    current_assignments_data, error = DBC().get_instance().execute_query_fetch("""
    SELECT id_przydzialu, DATE_FORMAT(data_przydzialu, '%d.%m.%Y')
    FROM Przypisanie
    WHERE biuro_numer = %s
    AND data_zwrotu IS NULL;""", [office['numer']])
    if error:
        print(error)
        flash('Nie udało się pobrać obecnie istniejących przypisań')
        return redirect(url_for("show.biura"))

    current_assignments = make_dictionaries_list(['id', 'data_przydzialu'], current_assignments_data)

    return render_template('assign/przypisz_sprzet.html', tytul=title, przypisania=current_assignments,
                           sprzety=available_hardware, post_adres=post_address)


@assign.route('/wykonaj/przypisz/sprzet/biuro/<numer_biura>', methods=['POST', 'GET'])
def _przypisz_sprzet_biuro_post(numer_biura):
    if request.method == 'GET':
        return redirect(url_for('assign.przypisz_sprzet_biuro', numer_biura=numer_biura))
    if request.method == 'POST':
        office_data, error = DBC().get_instance().execute_query_fetch("""
        SELECT numer, pietro, budynek_adres, oddzial_adres
        FROM Biuro
        JOIN Budynek B on Biuro.budynek_adres = B.adres
        WHERE numer = %s""", [numer_biura])
        if not office_data or error:
            print(error)
            flash('Nie udało się pobrać danych biura')
            return redirect(url_for("show.biura"))
        office = make_dictionary(['numer', 'pietro', 'budynek_adres', 'oddzial_adres'], office_data[0])

        list_of_hardware = request.form.getlist('hardware')
        if len(list_of_hardware) == 0:
            flash('Nie wybrano żadnego sprzętu')
            return redirect(url_for('assign.przypisz_sprzet_biuro', numer_biura=numer_biura))

        assignment_date = request.form.get('assignment_date_box')
        if request.form.get('assignment_date_box') != '':
            assignment_id, error = DBC().get_instance().execute_query_add_edit_delete_with_fetch_last_id("""
            INSERT INTO Przypisanie
            (data_przydzialu, biuro_numer)
            VALUES (%s, %s)""", [assignment_date, office['numer']])
            if error:
                print(error)
                flash('Wystąpił bład podczas dodawania nowego przypisania')
                return redirect(url_for('assign.przypisz_sprzet_biuro', numer_biura=numer_biura))
            assignment_id = assignment_id[0][0]
        else:  # New assignment date box empty
            flash('Data przypisania nie może być pusta')
            return redirect(url_for('assign.przypisz_sprzet_biuro', numer_biura=numer_biura))

        # Assign hardware
        for hardware in list_of_hardware:
            error_code, error = DBC().get_instance().execute_query_add_edit_delete_with_fetch("""
            SELECT PrzypiszSprzet(%s, %s) FROM dual""", [hardware, assignment_id])
            if error or error_code[0][0] != 0:
                if not error:
                    if error_code[0][0] == 1:
                        msg = 'Wybrany sprzęt nie znajduje się w magazynie'
                        flash('Wystąpił błąd podczas przypisywania sprzętu ' + msg)
                    elif error_code[0][0] == 2:
                        msg = 'Podaczas przypisywania sprzętu wystąpił wyjątek'
                        flash('Wystąpił błąd podczas przypisywania sprzętu ' + msg)
                else:
                    flash('Wystąpił błąd podczas przypisywania sprzętu ' + error.msg)
                return redirect(url_for('assign.przypisz_sprzet_biuro', numer_biura=numer_biura))
        flash('Sprzęt został pomyślnie przypisany')
    return redirect(url_for('show_info.pokaz_biuro_info', numer_biura=numer_biura))


@assign.route('/przypisz/oprogramowanie/sprzet/<numer_ewidencyjny>')
def przypisz_oprogramowanie(numer_ewidencyjny):
    hardware, error = DBC().get_instance().execute_query_fetch("""
    SELECT S.numer_ewidencyjny, S.typ, S.nazwa, S.producent, S.data_zakupu, S.magazyn_numer, P.pracownik_pesel, P.biuro_numer
     FROM Sprzet S
     LEFT OUTER JOIN SprzetWPrzypisaniu S2 on S.numer_ewidencyjny = S2.sprzet_numer_ewidencyjny
     LEFT OUTER JOIN Przypisanie P on S2.przypisanie_id_przydzialu = P.id_przydzialu
     WHERE S.numer_ewidencyjny = %s""", [numer_ewidencyjny])
    if error or not hardware:
        flash('Wystąpił błąd! Nie znaleziono sprzętu')
        return redirect(url_for('show_info.pokaz_sprzet_info', numer_ewidencyjny=numer_ewidencyjny))
    hardware_data = make_dictionary(
        ['numer', 'typ', 'nazwa', 'producent', 'data_zakupu', 'magazyn_numer', 'pracownik_pesel', 'biuro_numer'],
        hardware[0])
    if hardware_data.get('pracownik_pesel'):
        hardware_data['stan'] = 'Przypiany do pracownika {}'.format(hardware_data['pracownik_pesel'])
    elif hardware_data.get('biuro_numer'):
        hardware_data['stan'] = 'Przypisany do biura {}'.format(hardware_data['biuro_numer'])
    else:
        hardware_data['stan'] = 'W magazynie {}'.format(hardware_data['magazyn_numer'])

    available_software, error = DBC().get_instance().execute_query_fetch("""
    SELECT numer_ewidencyjny, nazwa, producent, DATE_FORMAT(data_zakupu, '%d.%m.%Y'), 
    DATE_FORMAT(data_wygasniecia, '%d.%m.%Y'), ilosc_licencji
    FROM Oprogramowanie
    WHERE (ilosc_licencji IS NULL
    OR IleWolnychLicencji(numer_ewidencyjny) > 0)
    AND (data_wygasniecia IS NULL
    OR data_wygasniecia > CURRENT_DATE)""")
    if error:
        flash('Wystąpił błąd podczas pobierania dostępnego oprogramowania')
        return redirect(url_for('show_info.pokaz_sprzet_info', numer_ewidencyjny=numer_ewidencyjny))
    if not available_software:
        flash('Nie znaleziono żadnej dostępnej kopii oprogramowania')
        return redirect(url_for('show_info.pokaz_sprzet_info', numer_ewidencyjny=numer_ewidencyjny))
    available_software_data = make_dictionaries_list(
        ['numer', 'nazwa', 'producent', 'data_zakupu', 'data_wygasniecia', 'liczba_licencji'], available_software)

    for i in range(len(available_software_data)):
        if not available_software_data[i].get('data_wygasniecia'):
            available_software_data[i]['data_wygasniecia'] = 'Nie wygasa'
        if not available_software_data[i].get('liczba_licencji'):
            available_software_data[i]['liczba_licencji'] = 'Nieograniczona'
    return render_template('assign/przypisz_oprogramowanie.html', sprzet=hardware_data,
                           dostepne_oprogramowanie=available_software_data)


@assign.route('/wykonaj/przypisz/oprogramowanie/sprzet/<numer_ewidencyjny>', methods=['GET', 'POST'])
def wykonaj_przypisz_oprogramowanie(numer_ewidencyjny):
    if request.method == 'GET':
        return redirect(url_for('assign.przypisz_oprogramowanie', numer_ewidencyjny=numer_ewidencyjny))
    if request.method == 'POST':
        if not request.form.get('chosen_software'):
            flash('Proszę wybrać oprogramowanie')
            return redirect(url_for('assign.przypisz_oprogramowanie', numer_ewidencyjny=numer_ewidencyjny))
        chosen_software = request.form.getlist('chosen_software')
        chosen_software = [int(x) for x in chosen_software]
        for software in chosen_software:
            result, error = DBC().get_instance().execute_query_add_edit_delete_with_fetch("""
            SELECT ZainstalujOprogramowanie(%s, %s) FROM dual""", [numer_ewidencyjny, software])
            if error:
                flash('Wystąpił błąd podczas przypisywania oprogramowania do sprzętu')
                return redirect(url_for('show_info.pokaz_sprzet_info', numer_ewidencyjny=numer_ewidencyjny))
            if result[0][0] == 1:
                flash('Wystąpił błąd, oprogramowanie {} nie posiada wystarczającej liczby licencji'.format(software))
                return redirect(url_for('assign.przypisz_oprogramowanie', numer_ewidencyjny=numer_ewidencyjny))
            if result[0][0] == 2:
                flash(
                    'Wystąpił błąd, upewnij się czy oprogramowanie {} nie było już zainstalowane na tym sprzęcie'.format(
                        software))
                return redirect(url_for('assign.przypisz_oprogramowanie', numer_ewidencyjny=numer_ewidencyjny))
        flash('Oprogramowanie zostało przypisane pomyślnie')
    return redirect(url_for('show_info.pokaz_sprzet_info', numer_ewidencyjny=numer_ewidencyjny))


@assign.route('/przypisz/prawo_dostepu/pracownik/<pesel>/karta/<id_karty>')
def przypisz_prawo_dostepu_karta(pesel, id_karty):
    worker, error = DBC().get_instance().execute_query_fetch("""
    SELECT pesel, imie, nazwisko, dzial_nazwa, biuro_numer
    FROM Pracownik
    WHERE pesel = %s""", [pesel])
    if error:
        flash('Wystąpił błąd podczas pobierania informacji o pracowniku')
        return redirect(url_for('show.pracownicy'))
    if not worker:
        flash('Nie znaleziono pracownika')
        return redirect(url_for('show.pracownicy'))
    worker_data = make_dictionary(['pesel', 'imie', 'nazwisko', 'dzial_nazwa', 'biuro_numer'], worker[0])

    card, error = DBC().get_instance().execute_query_fetch("""
    SELECT id_karty, data_przyznania, pracownik_pesel
    FROM KartaDostepu
    WHERE id_karty = %s""", [id_karty])
    if error:
        flash('Wystąpił błąd podczas pobierania informacji o karcie')
        return redirect(url_for('show_info.pokaz_pracownik_info', pesel=pesel))
    if not card:
        flash('Nie znaleziono karty')
        return redirect(url_for('show_info.pokaz_pracownik_info', pesel=pesel))

    card_data = make_dictionary(['id', 'data_przyznania', 'pracownik_pesel'], card[0])

    if worker_data['pesel'] != card_data['pracownik_pesel']:
        flash('Błąd! Wybrana karta nie należy do wskazanego pracownika')
        return redirect(url_for('show_info.pokaz_pracownik_info', pesel=pesel))

    current_assignments, error = DBC().get_instance().execute_query_fetch("""
    SELECT PD.data_przyznania, PD.data_wygasniecia, PD.biuro_numer, B.budynek_adres, B.pietro
    FROM PrawoDostepu PD
    JOIN Biuro B on PD.biuro_numer = B.numer
    WHERE PD.kartadostepu_id_karty = %s
    AND (PD.data_wygasniecia IS NULL OR PD.data_wygasniecia >= CURRENT_DATE)
    ORDER BY PD.data_przyznania DESC, PD.data_wygasniecia DESC, B.numer ASC""", [id_karty])
    if error:
        flash('Wystąpił błąd podczas pobierania listy obecnych praw dostępu')
        return redirect(url_for('show_info.pokaz_pracownik_info', pesel=pesel))
    current_assignments_data = make_dictionaries_list(
        ['dostep_data_przyznania', 'dostep_data_wygasniecia', 'numer', 'budynek_adres', 'pietro'], current_assignments)
    for i in range(len(current_assignments_data)):
        if not current_assignments_data[i]['dostep_data_wygasniecia']:  # If it never expires
            current_assignments_data[i]['dostep_data_wygasniecia'] = 'Nie wygasa'

    available_offices, error = DBC().get_instance().execute_query_fetch("""
    SELECT numer, budynek_adres, pietro
    FROM Biuro
    JOIN Budynek B on Biuro.budynek_adres = B.adres
    WHERE B.oddzial_adres = %s
    ORDER BY numer""", [session['wybrany_oddzial_adres']])
    if error:
        flash('Wystąpił błąd podczas pobierania dostępnych biur')
        return redirect(url_for('show_info.pokaz_pracownik_info', pesel=pesel))
    if not available_offices:
        flash('W oddziale nie ma żadnych biur, do których można by przyznać dostęp')
        return redirect(url_for('show_info.pokaz_pracownik_info', pesel=pesel))
    available_offices_data = make_dictionaries_list(['numer', 'budynek_adres', 'pietro'], available_offices)

    # Exclude those offices that worker already has access to
    current_assignments_office_numbers = [x['numer'] for x in current_assignments_data]
    available_offices_data = [x for x in available_offices_data if x['numer'] not in current_assignments_office_numbers]
    if not available_offices_data:  # Check once again3
        flash('W oddziale nie ma żadnych biur, do których można by przyznać dostęp')
        return redirect(url_for('show_info.pokaz_pracownik_info', pesel=pesel))
    return render_template('assign/przypisz_dostep_karta.html', karta=card_data, pracownik=worker_data,
                           obecne_biura=current_assignments_data, dostepne_biura=available_offices_data)


@assign.route('/wykonaj/przypisz/prawo_dostepu/pracownik/<pesel>/karta/<id_karty>', methods=['GET', 'POST'])
def wykonaj_przypisz_prawo_dostepu_karta(pesel, id_karty):
    if request.method == 'GET':
        return redirect(url_for('assign.przypisz_prawo_dostepu_karta', pesel=pesel, id_karty=id_karty))
    if request.method == 'POST':
        print(request.form)
        if not request.form.get('selected_offices'):
            flash('Prosze wybrać biura')
            return redirect(url_for('assign.przypisz_prawo_dostepu_karta', pesel=pesel, id_karty=id_karty))
        expiration_date = request.form.get('access_expiration_date')
        if expiration_date and expiration_date != '':
            expiration_date = string_to_date(expiration_date)
        else:
            expiration_date = None
        assign_date = request.form.get('access_assign_date')
        assign_date = string_to_date(assign_date)
        if expiration_date and expiration_date < assign_date:
            flash('Data wygasnięcia prawa nie może być wcześniejsza niż data wygaśnięcia')
            return redirect(url_for('assign.przypisz_prawo_dostepu_karta', pesel=pesel, id_karty=id_karty))
        # Get card assign date
        card_assign_date, error = DBC().get_instance().execute_query_fetch("""
        SELECT data_przyznania
        FROM KartaDostepu
        WHERE id_karty = %s""", [id_karty])
        if error or not card_assign_date:
            flash('Wystąpił błąd podczas pobierania informacji o karcie')
            return redirect(url_for('show_info.pokaz_pracownicy_info', pesel=pesel))
        card_assign_date = card_assign_date[0][0]
        if card_assign_date < assign_date:
            flash('Data przyznania prawa nie może być wcześniejsza niż data przyznania karty dostępu')
            return redirect(url_for('assign.przypisz_prawo_dostepu_karta', pesel=pesel, id_karty=id_karty))

        selected_offices = request.form.getlist('selected_offices')
        for office_number in selected_offices:
            # Assign access to the card
            error = DBC().get_instance().execute_query_add_edit_delete("""
                   INSERT INTO PrawoDostepu (data_przyznania, data_wygasniecia, kartadostepu_id_karty, biuro_numer)
                   VALUES (%s, %s, %s, %s)""", [assign_date, expiration_date, id_karty, office_number])
            if error:
                print(error)
                flash('Wystąpił błąd podczas przypisywania do karty prawa dostępu')
                return redirect(url_for('show_info.pokaz_pracownik_info', pesel=pesel))
    flash('Prawo dostępu zostało pomyślnie przypisane do karty')
    return redirect(url_for('show_info.pokaz_pracownik_info', pesel=pesel))

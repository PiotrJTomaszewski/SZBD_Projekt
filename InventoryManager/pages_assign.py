from flask import Flask, render_template, request, flash, redirect, url_for, Blueprint
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

    title = 'Przypisz sprzęt do pracownika {imie} {nazwisko}, numer PESEL {pesel}, dział {dzial}, biuro {biuro}'.format(
        imie=worker['imie'], nazwisko=worker['nazwisko'], pesel=worker['pesel'], dzial=worker['dzial_skrot'],
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
        flash('Sprzęt został przypisany pomyślnie')
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
        if not request.form:
            flash('Proszę wybrać oprogramowanie')
            return redirect(url_for('assign.przypisz_oprogramowanie', numer_ewidencyjny=numer_ewidencyjny))
        chosen_software = request.form.getlist('chosen_software')
        chosen_software = [int(x) for x in chosen_software]
        for software in chosen_software:
            result, error = DBC().get_instance().execute_query_add_edit_delete_with_fetch("""
            SELECT ZainstalujOprogramowanie(%s, %s) FROM dual""", [numer_ewidencyjny, software])
            if error:
                flash('Wystąpił błąd podczas przypisywania opgoramowania do sprzętu')
                return redirect(url_for('show_info.pokaz_sprzet_info', numer_ewidencyjny=numer_ewidencyjny))
            if result[0][0] == 1:
                flash('Wystąpił błąd, oprogramowanie {} nie posiada wystarczającej liczby licencji'.format(software))
                return redirect(url_for('assign.przypisz_oprogramowanie', numer_ewidencyjny=numer_ewidencyjny))
            if result[0][0] == 2:
                flash('Wystąpił błąd, upewnij się czy oprogramowanie {} nie było już zainstalowane na wybranym sprzęcie'.format(software))
                return redirect(url_for('assign.przypisz_oprogramowanie', numer_ewidencyjny=numer_ewidencyjny))
        flash('Oprogramowanie zostało przypisane pomyślnie')
    return redirect(url_for('show_info.pokaz_sprzet_info', numer_ewidencyjny=numer_ewidencyjny))

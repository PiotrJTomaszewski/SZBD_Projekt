from flask import Flask, render_template, request, flash, redirect, url_for, Blueprint
from database_connector import DatabaseConnector as DBC
from helpers import *

assign = Blueprint('assign', __name__)


@assign.route('/przypisz_sprzet/pracownik/<pesel>')
def przypisz_sprzet_pracownik(pesel):
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

    title = 'Przypisz sprzęt do pracownika {imie} {nazwisko}, numer PESEL {pesel}, dział {dzial}'.format(
        imie=worker['imie'], nazwisko=worker['nazwisko'], pesel=worker['pesel'], dzial=worker['dzial_skrot']
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


@assign.route('/post/przypisz_sprzet/pracownik/<pesel>', methods=['POST', 'GET'])
def _przypisz_sprzet_pracownik_post(pesel):
    if request.method == 'GET':
        redirect(url_for('assign.przypisz_sprzet_pracownik', pesel=pesel))
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

        create_new_assignment = (request.form.get('new_assignment_checkbox') is not None)
        if create_new_assignment:
            assignment_date = request.form.get('assignment_date_box')
            if request.form.get('assignment_date_box') != '':
                assignment_id, error = DBC().get_instance().execute_query_add_edit_delete_with_fetch_last_id("""
                INSERT INTO Przypisanie
                (data_przydzialu, pracownik_pesel)
                VALUES (%s, %s)""", [assignment_date, worker['pesel']])
                if error:
                    print(error)
                    flash('Wystąpił bład podczas dodawania nowego przypisania')
                    redirect(url_for('assign.przypisz_sprzet_pracownik', pesel=pesel))
                assignment_id = assignment_id[0][0]
            else:  # New assignment date box empty
                flash('Wybrano stworzenie nowego przypisania, więc data przypisania nie może być pusta')
                redirect(url_for('assign.przypisz_sprzet_pracownik', pesel=pesel))
        else:  # Use existing assignment
            assignment_id = request.form.get('old_assignment_box')
        list_of_hardware = request.form.getlist('hardware')
        if len(list_of_hardware) == 0:
            flash('Nie wybrano żadnego sprzętu')
            redirect(url_for('assign.przypisz_sprzet_pracownik', pesel=pesel))
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
                redirect(url_for('assign.przypisz_sprzet_pracownik', pesel=pesel))
    return redirect(url_for('show_info.pokaz_pracownik_info', pesel=pesel))


@assign.route('/przypisz_sprzet/biuro/<numer_biura>')
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
        return redirect(url_for("show.biura"))

    available_hardware = make_dictionaries_list(['numer', 'typ', 'nazwa', 'producent', 'data_zakupu', 'numer_magazynu'],
                                                available_hardware_data)
    if not available_hardware:
        flash('Nie ma wolnego sprzętu w magazynach')

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


@assign.route('/post/przypisz_sprzet/biuro/<numer_biura>', methods=['POST', 'GET'])
def _przypisz_sprzet_biuro_post(numer_biura):
    if request.method == 'GET':
        redirect(url_for('assign.przypisz_sprzet_biuro', numer_biura=numer_biura))
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

        create_new_assignment = (request.form.get('new_assignment_checkbox') is not None)
        if create_new_assignment:
            assignment_date = request.form.get('assignment_date_box')
            if request.form.get('assignment_date_box') != '':
                assignment_id, error = DBC().get_instance().execute_query_add_edit_delete_with_fetch_last_id("""
                INSERT INTO Przypisanie
                (data_przydzialu, biuro_numer)
                VALUES (%s, %s)""", [assignment_date, office['numer']])
                if error:
                    print(error)
                    flash('Wystąpił bład podczas dodawania nowego przypisania')
                    redirect(url_for('assign.przypisz_sprzet_biuro', numer_biura=numer_biura))
                assignment_id = assignment_id[0][0]
            else:  # New assignment date box empty
                flash('Wybrano stworzenie nowego przypisania, więc data przypisania nie może być pusta')
                redirect(url_for('assign.przypisz_sprzet_biuro', numer_biura=numer_biura))
        else:  # Use existing assignment
            assignment_id = request.form.get('old_assignment_box')
        list_of_hardware = request.form.getlist('hardware')
        if len(list_of_hardware) == 0:
            flash('Nie wybrano żadnego sprzętu')
            redirect(url_for('assign.przypisz_sprzet_biuro', numer_biura=numer_biura))
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
                redirect(url_for('assign.przypisz_sprzet_biuro', numer_biura=numer_biura))
    return redirect(url_for('show_info.pokaz_biuro_info', numer_biura=numer_biura))

from flask import Flask, render_template, request, flash, redirect, url_for, Blueprint
from database_connector import DatabaseConnector as DBC
from helpers import *

assign = Blueprint('assign', __name__)


@assign.route('/przypisz_sprzet/<pesel>', methods=['POST', 'GET'])
def przypisz_sprzet(pesel):
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

    if request.method == 'GET':
        return render_template('assign/przypisz_sprzet.html', pracownik=worker, przypisania=current_assignments,
                               sprzety=available_hardware)
    elif request.method == 'POST':
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
                    return render_template('assign/przypisz_sprzet.html', pracownik=worker,
                                           przypisania=current_assignments, sprzety=available_hardware)
                assignment_id = assignment_id[0][0]
            else:  # New assignment date box empty
                flash('Wybrano stworzenie nowego przypisania, więc data przypisania nie może być pusta')
                return render_template('assign/przypisz_sprzet.html', pracownik=worker, przypisania=current_assignments,
                                       sprzety=available_hardware)
        else:  # Use existing assignment
            assignment_id = request.form.get('old_assignment_box')
        list_of_hardware = request.form.getlist('hardware')
        if len(list_of_hardware) == 0:
            flash('Nie wybrano żadnego sprzętu')
            return render_template('assign/przypisz_sprzet.html', pracownik=worker, przypisania=current_assignments,
                                   sprzety=available_hardware)
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
                return render_template('assign/przypisz_sprzet.html', pracownik=worker, przypisania=current_assignments,
                                       sprzety=available_hardware)
        return redirect(url_for('show_info.pokaz_pracownik_info', pesel=pesel))

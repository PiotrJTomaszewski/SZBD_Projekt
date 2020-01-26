from flask import Flask, render_template, request, flash, redirect, url_for, Blueprint
from database_connector import DatabaseConnector as DBC
from mysql.connector import errorcode

delete = Blueprint('delete', __name__)


@delete.route('/usun/oddzial/<adres>')
def usun_oddzial(adres):
    error = DBC().get_instance().execute_query_add_edit_delete("""
    DELETE FROM Oddzial
    WHERE adres = %s""", [adres])
    if error:
        print(error)
        flash('Wystąpił błąd podczas usuwania oddziału!<br/>')
        if error.errno in (errorcode.ER_ROW_IS_REFERENCED, errorcode.ER_ROW_IS_REFERENCED_2):
            flash('Nie można usunąc oddziału, jeśli znajduje się w nim dział, budynek albo magazyn.')
    else:
        flash('Oddział został pomyślnie usunięty')
    return redirect(url_for('strona_glowna'))


@delete.route('/usun/budynek/<adres>')
def usun_budynek(adres):
    error = DBC().get_instance().execute_query_add_edit_delete("""
    DELETE FROM Budynek
    WHERE adres = %s""", [adres])
    if error:
        flash('Wystąpił błąd podczas usuwania budynku!<br/>')
        print(error)
        if error.errno in (errorcode.ER_ROW_IS_REFERENCED, errorcode.ER_ROW_IS_REFERENCED_2):
            flash('Nie można usunąc budynku, jeśli znajdują się w nim biura.')

    else:
        flash('Budynek został pomyślnie usunięty')
    return redirect(url_for('show.budynki'))


@delete.route('/usun/biuro/<numer>')
def usun_biuro(numer):
    # Check if it has any current assignment
    assignments, _ = DBC().get_instance().execute_query_fetch("""
    SELECT COUNT(*)
    FROM Przypisanie
    WHERE biuro_numer = %s
    AND data_zwrotu IS NULL""", [numer])
    print(assignments)
    if assignments and assignments[0][0] > 0:
        flash("""Nie można usunąć biura, które ma aktualnie przypisany sprzęt. 
                  Zwróć wszystkie przypisania ({}) i spróbuj ponownie.""".format(assignments[0][0]))
    else:
        error = DBC().get_instance().execute_query_add_edit_delete("""
        DELETE FROM Biuro
        WHERE numer = %s""", [numer])
        if error:
            flash('Wystąpił błąd podczas usuwania biura!<br/>')
            print(error)
            if error.errno in (errorcode.ER_ROW_IS_REFERENCED, errorcode.ER_ROW_IS_REFERENCED_2):
                flash('Nie można usunąc biura, w którym ktoś pracuje.')

        else:
            flash('Biuro zostało pomyślnie usunięte')
    return redirect(url_for('show.biura'))


@delete.route('/usun/dzial/<nazwa>')
def usun_dzial(nazwa):
    error = DBC().get_instance().execute_query_add_edit_delete("""
    DELETE FROM Dzial
    WHERE nazwa = %s""", [nazwa])
    if error:
        flash('Wystąpił błąd podczas usuwania działu!<br/>')
        print(error)
        if error.errno in (errorcode.ER_ROW_IS_REFERENCED, errorcode.ER_ROW_IS_REFERENCED_2):
            flash('Nie można usunąc działu, w którym ktoś jest zatrudniony.')
    else:
        flash('Dział został pomyślnie usunięty')
    return redirect(url_for('show.dzialy'))


@delete.route('/usun/pracownik/<pesel>')
def usun_pracownika(pesel):
    # Check if the worker has any current hardware assignments
    assignments, _ = DBC().get_instance().execute_query_fetch("""
    SELECT COUNT(*)
    FROM Przypisanie
    WHERE pracownik_pesel = %s
    AND data_zwrotu IS NULL""", [pesel])
    if assignments and assignments[0][0] > 0:
        flash("""Nie można usunąć pracownika, który ma aktualnie przypisany sprzęt. 
              Zwróć wszystkie przypisania ({}) i spróbuj ponownie.""".format(assignments[0][0]))
    else:
        error = DBC().get_instance().execute_query_add_edit_delete("""
        DELETE FROM Pracownik
        WHERE pesel = %s""", [pesel])
        if error:
            flash('Wystąpił błąd podczas usuwania pracownika!')
            print(error)
        else:
            flash('Pracownik został pomyślnie usunięty')
    return redirect(url_for('show.pracownicy'))


@delete.route('/pracownik/<pesel>/usun/karta/<id_karty>')
def usun_karte_dostepu(pesel, id_karty):
    error = DBC().get_instance().execute_query_add_edit_delete("""
    DELETE FROM KartaDostepu
    WHERE id_karty = %s""", [id_karty])
    if error:
        flash('Wystąpił błąd podczas usuwania karty dostępu!')
        print(error)
    else:
        flash('Karta dostępu została pomyślnie usunięta')
    return redirect(url_for('show_info.pokaz_pracownik_info', pesel=pesel))


# @delete.route('/usun/prawo_dostepu/<id_karty>/<numer_biura>')
# def usun_prawo_dostepu(id_karty, numer_biura):
#     error = DBC().get_instance().execute_query_add_edit_delete("""
#     DELETE FROM PrawoDostepu
#     WHERE  = %s""", [adres])
#     if error:
#         flash('Wystąpił błąd podczas usuwania budynku!')
#         print(error)
#     else:
#         flash('Budynek został pomyślnie usunięty')
#     return redirect(url_for('show.budynki'))


@delete.route('/usun/magazyn/<numer>')
def usun_magazyn(numer):
    error = DBC().get_instance().execute_query_add_edit_delete("""
    DELETE FROM Magazyn
    WHERE numer = %s""", [numer])
    if error:
        flash('Wystąpił błąd podczas usuwania magazynu!<br/>')
        print(error)
        if error.errno in (errorcode.ER_ROW_IS_REFERENCED, errorcode.ER_ROW_IS_REFERENCED_2):
            flash('Nie można usunąc magazynu, w którym znajduje się sprzęt.')
    else:
        flash('Magazyn został pomyślnie usunięty')
    return redirect(url_for('show.magazyny'))


# @delete.route('/biuro/<numer>/usun/przypisanie/<id_przydzialu>')
# def usun_przypisanie_biuro(numer, id_przydzialu):
#     pass
#
#
# @delete.route('/pracownik/<pesel>/usun/przypisanie/<id_przydzialu>')
# def usun_przypisanie_pracownik(pesel, id_przydzialu):
#     pass


@delete.route('/usun/sprzet/<numer_ewidencyjny>')
def usun_sprzet(numer_ewidencyjny):
    error = DBC().get_instance().execute_query_add_edit_delete("""
    DELETE FROM Sprzet
    WHERE numer_ewidencyjny = %s""", [numer_ewidencyjny])
    if error:
        flash('Wystąpił błąd podczas usuwania sprzętu!')
        print(error)
    else:
        flash('Sprzęt został pomyślnie usunięty')
    # return redirect(url_for('show.budynki'))
    return redirect(url_for('show.sprzet_w_magazynach'))


# @delete.route('/usun/sprzet_w_przypisaniu/<numer_ewidencyjny>/<id_przydzialu>')
# def usun_sprzet_w_przypisaniu(numer_ewidencyjny, id_przydzialu):
#


@delete.route('/usun/oprogramowanie/<numer_ewidencyjny>')
def usun_oprogramowanie(numer_ewidencyjny):
    error = DBC().get_instance().execute_query_add_edit_delete("""
    DELETE FROM Oprogramowanie
    WHERE numer_ewidencyjny = %s""", [numer_ewidencyjny])
    if error:
        flash('Wystąpił błąd podczas usuwania oprogramowania!')
        print(error)
    else:
        flash('Oprogramowanie zostało pomyślnie usunięte')
    return redirect(url_for('show.oprogramowanie'))

# @delete.route('/usun/oprogramowanie_na_sprzecie/<sprzet_numer>/<oprogramowanie_numer>')
# def usun_oprogramowanie_na_sprzecie(sprzet_numer, oprogramowanie_numer):
#     pass

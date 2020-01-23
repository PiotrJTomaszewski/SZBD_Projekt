from flask import Flask, render_template, request, flash, redirect, url_for, Blueprint, session
from database_connector import DatabaseConnector as DBC
from datetime import date
from helpers import *

deassign = Blueprint('deassign', __name__)


@deassign.route('/zwroc/sprzet/<id_przydzialu>')
def zwroc_sprzet(id_przydzialu):
    assignment, error = DBC().get_instance().execute_query_fetch("""
    SELECT id_przydzialu, DATE_FORMAT(data_przydzialu, '%d.%m.%Y'), pracownik_pesel, biuro_numer, data_zwrotu
    FROM Przypisanie
    WHERE id_przydzialu = %s""", [id_przydzialu])
    if error or not assignment:
        flash('Wystąpił błąd podczas pobierania informacji o przydziale')
        return redirect(url_for('show.historia_przypisan'))
    assignment_data = make_dictionary(['id', 'data_przyznania', 'pracownik_pesel', 'biuro_numer', 'data_zwrotu'],
                                      assignment[0])
    if assignment_data['data_zwrotu']:
        flash('Wybrane przypisanie zostało już zwrócone')
        return redirect(url_for('show.historia_przypisan'))

    if assignment_data.get('pracownik_pesel'):
        owner, error = DBC().get_instance().execute_query_fetch("""
        SELECT P.pesel, P.imie, P.nazwisko, P.czy_nadal_pracuje, D.skrot, P.biuro_numer
        FROM Pracownik P
        JOIN Dzial D on P.dzial_nazwa = D.nazwa
        WHERE P.pesel = %s""", [assignment_data['pracownik_pesel']])
        if error or not owner:
            flash('Wystąpił błąd podczas pobierania informacji o właścicielu')
            return redirect(url_for('show.historia_przypisan'))
        owner = list(owner[0])
        if owner[3] == '1':
            owner[3] = 'Tak'
        else:
            owner[3] = 'Nie'
        owner_data = {'naglowki': ['PESEL', 'Imię', 'Nazwisko', 'Czy nadal pracuje', 'Dział', 'Numer biura'],
                      'dane': owner, 'typ': 'Pracownik'}
    else:
        owner, error = DBC().get_instance().execute_query_fetch("""
        SELECT numer, budynek_adres, pietro
        FROM Biuro
        WHERE numer = %s""", [assignment_data['biuro_numer']])
        if error or not owner:
            flash('Wystąpił błąd podczas pobierania informacji o właścicielu')
            return redirect(url_for('show.historia_przypisan'))
        owner_data = {'naglowki': ['Numer', 'Adres budynku', 'Piętro'], 'dane': owner[0], 'typ': 'Biuro'}

    hardware, error = DBC().get_instance().execute_query_fetch("""
    SELECT S.numer_ewidencyjny, S.typ, S.nazwa, S.producent, DATE_FORMAT(S.data_zakupu, '%d.%m.%Y')
    FROM SprzetWPrzypisaniu SWP
    JOIN Sprzet S on SWP.sprzet_numer_ewidencyjny = S.numer_ewidencyjny
    WHERE SWP.przypisanie_id_przydzialu = %s""", [assignment_data['id']])
    if error:
        flash('Wystąpił błąd podczas pobierania dostępnego sprzętu')
        return redirect(url_for('show.historia_przypisan'))
    if not hardware:
        flash('Wybrane przypisanie nie zawiera żadnego sprzętu')
    hardware_data = make_dictionaries_list(['numer', 'typ', 'nazwa', 'producent', 'data_zakupu'], hardware)

    magazines, error = DBC().get_instance().execute_query_fetch("""
    SELECT numer, pojemnosc, WolnaPojemnoscMagazynu(numer)
    FROM Magazyn
    WHERE oddzial_adres = %s
    AND WolnaPojemnoscMagazynu(numer) >= %s""", [session['wybrany_oddzial_adres'], len(hardware)])
    if error is not None:
        flash('Wystąpił błąd podczas pobierania listy magazynów')
    if not magazines:
        flash('W oddziale nie ma wolnych magazynów')
        return redirect(url_for('show.historia_przypisan'))
    magazines_data = make_dictionaries_list(['numer', 'pojemnosc', 'wolna_pojemnosc'], magazines)

    return render_template('deassign/zwroc_sprzet.html', przypisanie=assignment_data, wlasciciel=owner_data,
                           sprzety=hardware_data, magazyny=magazines_data)


@deassign.route('/wykonaj/zwroc/sprzet/<id_przydzialu>', methods=['GET', 'POST'])
def wykonaj_zwroc_sprzet(id_przydzialu):
    if request.method == 'GET':
        return redirect(url_for('deassign.zwroc_sprzet', id_przydzialu=id_przydzialu))
    if request.method == 'POST':
        return_date = request.form.get('return_date')
        if not return_date:
            flash('')
        return_date = date(int(return_date[:4]), int(return_date[5:7]), int(return_date[8:10]))
        result, error = DBC().get_instance().execute_query_fetch("""
        SELECT data_przydzialu, data_zwrotu
        FROM Przypisanie
        WHERE id_przydzialu = %s""", [id_przydzialu])
        if not result or error:
            flash('Wystąpił błąd podczas pobierania przydziału')
            return redirect(url_for('show.historia_przypisan'))
        if result[0][1]:
            flash('Błąd! Wybrane przypisanie zostało już zwrócone')
            return redirect(url_for('show.historia_przypisan'))
        assign_date = result[0][0]
        if return_date < assign_date:
            flash('Data zwrotu musi być późniejsza, niż data przypisania')
            return redirect(url_for('deassign.zwroc_sprzet', id_przydzialu=id_przydzialu))
        hardware_numbers, error = DBC().get_instance().execute_query_fetch("""
        SELECT S.numer_ewidencyjny
        FROM SprzetWPrzypisaniu SWP
        JOIN Sprzet S on SWP.sprzet_numer_ewidencyjny = S.numer_ewidencyjny
        WHERE SWP.przypisanie_id_przydzialu = %s""", [id_przydzialu])
        if error:
            flash('Wystąpił błąd podczas pobierania listy sprzętu w przypisaniu')
            return redirect(url_for('show.historia_przypisan'))
        selected_magazine = request.form.get('magazine_number')
        for hardware_number in hardware_numbers:
            hardware_number = hardware_number[0]
            result, error = DBC().get_instance().execute_query_add_edit_delete_with_fetch("""
            SELECT ZwrocSprzet(%s, %s, %s, %s) FROM dual""", [hardware_number, id_przydzialu, selected_magazine,
                                                              return_date])
            if error:
                flash('Wystąpił błąd podczas zwracania sprzętu')
                return redirect(url_for('show.historia_przypisan'))
            if result[0][0] == 1:
                print('Wybrany magazyn jest pełen!')
                return redirect(url_for('show_historia_przypisania'))
        return redirect(url_for('show.historia_przypisan'))


@deassign.route('/zwroc/oprogramowanie/sprzet/<numer_ewidencyjny>')
def zwroc_oprogramowanie(numer_ewidencyjny):
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

    assigned_software, error = DBC().get_instance().execute_query_fetch("""
        SELECT numer_ewidencyjny, nazwa, producent, DATE_FORMAT(data_zakupu, '%d.%m.%Y'), 
        DATE_FORMAT(data_wygasniecia, '%d.%m.%Y'), ilosc_licencji
        FROM Oprogramowanie
        JOIN OprogramowanieNaSprzecie ONS on Oprogramowanie.numer_ewidencyjny = ONS.oprogramowanie_numer
        WHERE ONS.sprzet_numer = %s""", [hardware_data['numer']])
    if error:
        flash('Wystąpił błąd podczas pobierania dostępnego oprogramowania')
        return redirect(url_for('show_info.pokaz_sprzet_info', numer_ewidencyjny=numer_ewidencyjny))
    if not assigned_software:
        flash('Wybrany sprzęt nie posiada przypisanego oprogramowania')
        return redirect(url_for('show_info.pokaz_sprzet_info', numer_ewidencyjny=numer_ewidencyjny))

    assigned_software_data = make_dictionaries_list(
        ['numer', 'nazwa', 'producent', 'data_zakupu', 'data_wygasniecia', 'liczba_licencji'], assigned_software)

    for i in range(len(assigned_software_data)):
        if not assigned_software_data[i].get('data_wygasniecia'):
            assigned_software_data[i]['data_wygasniecia'] = 'Nie wygasa'
        if not assigned_software_data[i].get('liczba_licencji'):
            assigned_software_data[i]['liczba_licencji'] = 'Nieograniczona'

    return render_template('deassign/zwroc_oprogramowanie.html', sprzet=hardware_data,
                           przypisane_oprogramowanie=assigned_software_data)


@deassign.route('/wykonaj/zwroc/oprogramowanie/sprzet/<numer_ewidencyjny>', methods=['GET', 'POST'])
def wykonaj_zwroc_oprogramowanie(numer_ewidencyjny):
    if request.method == 'GET':
        return redirect(url_for('deassign.zwroc_oprogramowanie', numer_ewidencyjny=numer_ewidencyjny))
    if request.method == 'POST':
        if not request.form:
            flash('Proszę wybrać oprogramowanie')
            return redirect(url_for('deassign.zwroc_oprogramowanie', numer_ewidencyjny=numer_ewidencyjny))
        chosen_software = request.form.getlist('chosen_software')
        chosen_software = [int(x) for x in chosen_software]
        for software in chosen_software:
            error = DBC().get_instance().execute_query_add_edit_delete("""
                DELETE FROM OprogramowanieNaSprzecie
                WHERE sprzet_numer = %s
                AND oprogramowanie_numer = %s""", [numer_ewidencyjny, software])
            if error:
                flash('Wystąpił błąd podczas przypisywania opgoramowania do sprzętu')
                return redirect(url_for('show_info.pokaz_sprzet_info', numer_ewidencyjny=numer_ewidencyjny))
        flash('Oprogramowanie zostało przypisane pomyślnie')
    return redirect(url_for('show_info.pokaz_sprzet_info', numer_ewidencyjny=numer_ewidencyjny))

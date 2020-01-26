from flask import Flask, render_template, request, flash, redirect, url_for, Blueprint, session
import data_generators.create_workers as creator
from database_connector import DatabaseConnector as DBC
from helpers import make_dictionaries_list

show = Blueprint('show', __name__)


@show.route('/pokaz/budynki')
def budynki():
    buildings, error = DBC().get_instance().execute_query_fetch(
        """SELECT adres, nazwa, ilosc_pieter, oddzial_adres
        FROM Budynek WHERE oddzial_adres = %s
        ORDER BY adres""",
        [session['wybrany_oddzial_adres']]
    )
    if error is not None:
        flash('Wystąpił błąd!<br/>{}'.format(error.msg))
    buildings_data = make_dictionaries_list(['adres', 'nazwa', 'liczba_pieter', 'oddzial_adres'], buildings)
    return render_template('show/pokaz_budynki.html', budynki=buildings_data)


@show.route('/pokaz/biura')
def biura():
    offices, error = DBC().get_instance().execute_query_fetch(
        """SELECT B.numer, B.liczba_stanowisk, B.pietro, B.budynek_adres, B2.oddzial_adres
        FROM Biuro B JOIN Budynek B2 on B.budynek_adres = B2.adres
        WHERE B2.oddzial_adres = %s
        ORDER BY numer""", [session['wybrany_oddzial_adres']]
    )
    if error is not None:
        flash('Wystąpił błąd!<br/>{}'.format(error.msg))
    offices_data = make_dictionaries_list(['numer', 'liczba_stanowisk', 'pietro', 'budynek_adres'], offices)
    return render_template('show/pokaz_biura.html', biura=offices_data)


@show.route('/pokaz/dzialy')
def dzialy():
    depts, error = DBC().get_instance().execute_query_fetch(
        """SELECT nazwa, skrot, oddzial_adres
        FROM Dzial
        WHERE oddzial_adres = %s
        ORDER BY nazwa""", [session['wybrany_oddzial_adres']]
    )
    if error is not None:
        flash('Wystąpił błąd!<br/>{}'.format(error.msg))
    # if depts is None or len(depts) == 0:
    #     flash('Nie znaleziono działów!')
    #     return render_template('show/pokaz_dzialy.html', dzialy=[])
    depts_data = make_dictionaries_list(['nazwa', 'skrot', 'oddzial_adres'], depts)
    return render_template('show/pokaz_dzialy.html', dzialy=depts_data)


@show.route('/pokaz/pracownicy')
def pracownicy():
    workers, error = DBC().get_instance().execute_query_fetch(
        """SELECT p.pesel, p.imie, p.nazwisko, p.numer_telefonu, p.czy_nadal_pracuje, p.adres_email, p.dzial_nazwa, 
        p.biuro_numer, d.skrot, d.oddzial_adres 
        FROM Pracownik p JOIN Dzial d on p.dzial_nazwa = d.nazwa
        WHERE d.oddzial_adres = %s
        ORDER BY pesel""", [session['wybrany_oddzial_adres']]
    )
    if error is not None:
        flash('Wystąpił błąd!<br/>{}'.format(error.msg))
    workers_data = make_dictionaries_list(
        ['pesel', 'imie', 'nazwisko', 'numer_telefonu', 'czy_nadal_pracuje', 'adres_email', 'dzial_nazwa',
         'biuro_numer', 'dzial_skrot'], workers)
    for worker in workers_data:
        if worker['czy_nadal_pracuje'] == '1':
            worker['czy_nadal_pracuje'] = 'Tak'
        else:
            worker['czy_nadal_pracuje'] = 'Nie'
    return render_template('show/pokaz_pracownicy.html', pracownicy=workers_data)


@show.route('/pokaz/magazyny')
def magazyny():
    warehouses, error = DBC().get_instance().execute_query_fetch(
        """SELECT numer, pojemnosc, oddzial_adres
        FROM Magazyn
        WHERE oddzial_adres = %s""", [session['wybrany_oddzial_adres']]
    )
    if error is not None:
        flash('Wystąpił błąd!<br/>{}'.format(error.msg))
    warehouses_data = make_dictionaries_list(['numer', 'pojemnosc', 'oddzial_adres'], warehouses)
    return render_template('show/pokaz_magazyny.html', magazyny=warehouses_data)


@show.route('/pokaz/sprzet_w_magazynach')
def sprzet_w_magazynach():
    hardware_in_warehouses, error = DBC().get_instance().execute_query_fetch(
        """SELECT S.numer_ewidencyjny, S.data_zakupu, S.nazwa, S.typ, S.producent, S.magazyn_numer
        FROM Sprzet S
        WHERE (SELECT oddzial_adres FROM Magazyn M WHERE M.numer = S.magazyn_numer) = %s""",
        [session['wybrany_oddzial_adres']]
    )
    if error is not None:
        print(error)
        flash('Wystąpił błąd!<br/>Nie można pobrać dostępnego sprzętu')
    hardware_data = make_dictionaries_list(
        ['numer_ewidencyjny', 'data_zakupu', 'nazwa', 'typ', 'producent', 'numer_magazynu'], hardware_in_warehouses)

    return render_template('show/pokaz_sprzet_w_magazynach.html', sprzety=hardware_data)


@show.route('/pokaz/oprogramowanie')
def oprogramowania():
    software, error = DBC().get_instance().execute_query_fetch(
        """SELECT numer_ewidencyjny, nazwa, producent, data_zakupu, data_wygasniecia, 
        coalesce(ilosc_licencji, 'Nielimitowane') FROM oprogramowanie""")
    if error is not None:
        print(error)
        flash('Wystąpił błąd!<br/>Nie można pobrać dostępnego sprzętu')
    software_data = make_dictionaries_list(
        ['numer_ewidencyjny', 'nazwa', 'producent', 'data_zakupu', 'data_wygasniecia', 'ilosc_licencji'], software)

    return render_template('show/pokaz_oprogramowania.html', oprogramowania=software_data)


@show.route('/pokaz/historia_przypisan')
def historia_przypisan():
    history, error = DBC().get_instance().execute_query_fetch(
        """SELECT P.id_przydzialu, P.data_przydzialu, P.data_zwrotu, P.pracownik_pesel, P.biuro_numer,
         SWP.sprzet_numer_ewidencyjny, S.typ, S.nazwa
        FROM Przypisanie P JOIN SprzetWPrzypisaniu SWP on P.id_przydzialu = SWP.przypisanie_id_przydzialu
        JOIN Sprzet S on SWP.sprzet_numer_ewidencyjny = S.numer_ewidencyjny
        WHERE (P.pracownik_pesel IS NOT NULL AND (
            SELECT D.oddzial_adres FROM Pracownik P2 JOIN Dzial D on P2.dzial_nazwa = D.nazwa
            WHERE P2.pesel = P.pracownik_pesel) = %s)
            OR
            (P.biuro_numer IS NOT NULL AND (
                SELECT B2.oddzial_adres FROM Biuro B JOIN Budynek B2 on B.budynek_adres = B2.adres
                WHERE P.biuro_numer = B.numer) = %s)
        ORDER BY P.data_przydzialu DESC, P.data_zwrotu DESC, P.id_przydzialu DESC
        """, [session['wybrany_oddzial_adres'], session['wybrany_oddzial_adres']])
    history_data = make_dictionaries_list(['id_przydzialu', 'data_przydzialu', 'data_zwrotu', 'pracownik_pesel',
                                           'biuro_numer', 'sprzet_numer_ewidencyjny', 'sprzet_typ', 'sprzet_nazwa'],
                                          history)
    return render_template('show/pokaz_historia_przypisan.html', wpisy=history_data)

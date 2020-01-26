from flask import Flask, render_template, request, flash, redirect, url_for, Blueprint
import data_generators.create_workers as creator
from database_connector import DatabaseConnector as DBC
from helpers import make_dictionaries_list, make_dictionary


show_info = Blueprint('show_info', __name__)


@show_info.route('/pokaz_info/oddzial/<adres>')
def pokaz_oddzial_info(adres):
    branch, error = DBC().get_instance().execute_query_fetch(
        """SELECT adres, nazwa from Oddzial
        WHERE adres = %s""", [adres]
    )
    if error is not None:
        flash('Wystąpił błąd!<br/>{}'.format(error.msg))
    branch_data = make_dictionary(['adres', 'nazwa'], branch[0])
    depts, error = DBC().get_instance().execute_query_fetch(
        """SELECT nazwa, skrot FROM Dzial
        WHERE oddzial_adres = %s""", [adres]
    )
    if error is not None:
        flash('Wystąpił błąd<br/>{}'.format(error.msg))
    depts_data = make_dictionaries_list(['nazwa', 'skrot'], depts)

    warehouses, error = DBC().get_instance().execute_query_fetch(
        """SELECT numer, pojemnosc, WolnaPojemnoscMagazynu(numer)
        FROM Magazyn
        WHERE oddzial_adres = %s""", [adres]
    )
    if error is not None:
        flash('Wystąpił błąd!<br/>{}'.format(error.msg))
    warehouses_data = make_dictionaries_list(['numer', 'pojemnosc', 'wolna_przestrzen'], warehouses)

    buildings, error = DBC().get_instance().execute_query_fetch(
        """SELECT adres, nazwa, ilosc_pieter FROM Budynek
        WHERE oddzial_adres = %s""", [adres]
    )
    if error is not None:
        flash('Wystąpił błąd!<br/>{}')
    buildings_data = make_dictionaries_list(['adres', 'nazwa', 'liczba_pieter'], buildings)

    return render_template('show_info/pokaz_oddzial_info.html', oddzial=branch_data, dzialy=depts_data,
                           magazyny=warehouses_data, budynki=buildings_data)


@show_info.route('/pokaz_info/budynek/<adres>')
def pokaz_budynek_info(adres):
    basic, error = DBC().get_instance().execute_query_fetch(
        """SELECT adres, nazwa, ilosc_pieter, oddzial_adres  from Budynek
        WHERE adres = %s""", [adres]
    )
    if error is not None:
        flash('Wystąpił błąd!<br/>{}'.format(error.msg))
    basic_data = make_dictionary(['adres', 'nazwa', 'ilosc_pieter', 'oddzial_adres'], basic[0])

    branch, error = DBC().get_instance().execute_query_fetch(
        """SELECT o.adres, o.nazwa from Oddzial o
        WHERE o.adres = (select b.oddzial_adres from Budynek b where b.adres = %s)""", [adres]
    )
    if error is not None:
        flash('Wystąpił błąd!<br/>{}'.format(error.msg))
    branch_data = make_dictionary(['adres', 'nazwa'], branch[0])

    offices, error = DBC().get_instance().execute_query_fetch(
        """SELECT numer, pietro, liczba_stanowisk FROM Biuro
        WHERE budynek_adres = %s ORDER BY pietro""", [adres]
    )
    if error is not None:
        flash('Wystąpił błąd<br/>{}'.format(error.msg))
    offices_data = make_dictionaries_list(['numer', 'pietro', 'liczba_stanowisk'], offices)

    workers, error = DBC().get_instance().execute_query_fetch(
        """SELECT p.pesel, p.nazwisko, p.imie, p.numer_telefonu, p.biuro_numer
        FROM Pracownik p
        WHERE p.biuro_numer in (SELECT b.numer FROM Biuro b WHERE b.budynek_adres = %s)""", [adres]
    )
    if error is not None:
        flash('Wystąpił błąd!<br/>{}'.format(error.msg))
    workers_data = make_dictionaries_list(['pesel', 'nazwisko', 'imie', 'numer_telefonu', 'biuro_numer'], workers)

    return render_template('show_info/pokaz_budynek_info.html', budynek=basic_data, oddzial=branch_data,
                           biura=offices_data, pracownicy=workers_data)


@show_info.route('/pokaz_info/pracownik/<pesel>')
def pokaz_pracownik_info(pesel):
    basic, error = DBC().get_instance().execute_query_fetch(
        """SELECT pesel, imie, nazwisko, numer_telefonu, czy_nadal_pracuje, adres_email, dzial_nazwa, biuro_numer from Pracownik
        WHERE pesel = %s""", [pesel]
    )
    if error is not None:
        flash('Wystąpił błąd!<br/>{}'.format(error.msg))
    basic_data = make_dictionary(['pesel', 'imie', 'nazwisko', 'numer_telefonu', 'czy_nadal_pracuje', 'adres_email',
                                  'dzial_nazwa', 'biuro_numer'], basic[0])

    branch, error = DBC().get_instance().execute_query_fetch(
        """SELECT o.adres, o.nazwa from Oddzial o
        WHERE o.adres = (select d.oddzial_adres from Dzial d where 
        d.nazwa = (select p.dzial_nazwa from  Pracownik p where pesel = %s))""", [pesel]
    )
    if error is not None:
        flash('Wystąpił błąd!<br/>{}'.format(error.msg))
    branch_data = make_dictionary(['adres', 'nazwa'], branch[0])

    hardware, error = DBC().get_instance().execute_query_fetch(
        """SELECT s.numer_ewidencyjny, s.nazwa, s.producent, s.typ FROM Sprzet s 
        where s.numer_ewidencyjny in (select swp.sprzet_numer_ewidencyjny from SprzetWPrzypisaniu swp
        where swp.przypisanie_id_przydzialu in (select p.id_przydzialu from Przypisanie p 
        where p.pracownik_pesel = %s and p.data_zwrotu is null)) """, [pesel]
    )
    if error is not None:
        flash('Wystąpił błąd<br/>{}'.format(error.msg))
    hardware_data = make_dictionaries_list(['numer_ewidencyjny', 'nazwa', 'producent', 'typ'], hardware)

    permissions, error = DBC().get_instance().execute_query_fetch(
        """SELECT b.budynek_adres, b.pietro, b.numer
        FROM Biuro b
        WHERE b.numer in (select pd.biuro_numer from PrawoDostepu pd
        where pd.kartadostepu_id_karty in (select kd.id_karty from KartaDostepu kd
        where kd.pracownik_pesel = %s))""", [pesel]
    )
    if error is not None:
        flash('Wystąpił błąd!<br/>{}'.format(error.msg))
    permissions_data = make_dictionaries_list(['budynek_adres', 'pietro', 'numer'], permissions)

    cards, error = DBC().get_instance().execute_query_fetch(
        """SELECT id_karty, data_przyznania from KartaDostepu 
        where pracownik_pesel = %s""", [pesel]
    )
    if error is not None:
        flash('Wystąpił błąd!<br/>{}'.format(error.msg))
    cards_data = make_dictionaries_list(['id_karty', 'data_przyznania'], cards)

    software, error = DBC().get_instance().execute_query_fetch(
        """SELECT o.numer_ewidencyjny, o.nazwa, o.producent from Oprogramowanie o
         where o.numer_ewidencyjny in (select onp.oprogramowanie_numer from OprogramowanieNaSprzecie onp 
         where onp.sprzet_numer in (SELECT s.numer_ewidencyjny FROM sprzet s 
        where s.numer_ewidencyjny in (select swp.sprzet_numer_ewidencyjny from SprzetWPrzypisaniu swp
        where swp.przypisanie_id_przydzialu in (select p.id_przydzialu from Przypisanie p 
        where p.pracownik_pesel = %s and p.data_zwrotu is null))))""", [pesel]
    )
    if error is not None:
        flash('Wystąpił błąd!<br/>{}'.format(error.msg))
    software_data = make_dictionaries_list(['numer_ewidencyjny', 'nazwa', 'producent'], software)

    return render_template('show_info/pokaz_pracownik_info.html', pracownik=basic_data, oddzial=branch_data,
                           karty=cards_data, dostepne_biura=permissions_data, oprogramowania=software_data,
                           sprzety=hardware_data)


@show_info.route('/pokaz_info/sprzet/<numer_ewidencyjny>')
def pokaz_sprzet_info(numer_ewidencyjny):
    basic, error = DBC().get_instance().execute_query_fetch(
        """SELECT numer_ewidencyjny, data_zakupu, nazwa, typ, producent, uwagi, magazyn_numer from Sprzet
        WHERE numer_ewidencyjny = %s""", [numer_ewidencyjny]
    )
    if error is not None:
        flash('Wystąpił błąd!<br/>{}'.format(error.msg))
    basic_data = make_dictionary(['numer_ewidencyjny', 'data_zakupu', 'nazwa', 'typ', 'producent', 'uwagi', 'magazyn_numer'], basic[0])

    history, error = DBC().get_instance().execute_query_fetch(
        """SELECT p.id_przydzialu, p.data_przydzialu, coalesce(p.data_zwrotu, 'Nie zwrócono'), p2.pesel, p2.nazwisko,
         p2.imie, p.biuro_numer 
        from Przypisanie p join Pracownik p2 on p.pracownik_pesel = p2.pesel
        where p.id_przydzialu in (select swp.przypisanie_id_przydzialu from SprzetWPrzypisaniu swp
        where swp.sprzet_numer_ewidencyjny = %s)
        UNION ALL
        SELECT p.id_przydzialu, p.data_przydzialu, coalesce(p.data_zwrotu, 'Nie zwrócono'), null, null, null, b.numer 
        from Przypisanie p join Biuro b on p.biuro_numer = b.numer
        where p.id_przydzialu in (select swp.przypisanie_id_przydzialu from SprzetWPrzypisaniu swp
        where swp.sprzet_numer_ewidencyjny = %s) order by data_przydzialu desc""", [numer_ewidencyjny, numer_ewidencyjny]
    )
    if error is not None:
        flash('Wystąpił błąd!<br/>{}'.format(error.msg))
    history_data = make_dictionaries_list(['id_przydzialu', 'data_przydzialu', 'data_zwrotu', 'pracownik_pesel',
                                    'pracownik_nazwisko', 'pracownik_imie', 'biuro_numer'], history)

    software, error = DBC().get_instance().execute_query_fetch(
        """SELECT o.numer_ewidencyjny, o.nazwa, o.producent from Oprogramowanie o
         where o.numer_ewidencyjny in (select onp.oprogramowanie_numer from OprogramowanieNaSprzecie onp 
         where onp.sprzet_numer = %s)""", [numer_ewidencyjny]
    )
    if error is not None:
        flash('Wystąpił błąd!<br/>{}'.format(error.msg))
    software_data = make_dictionaries_list(['numer_ewidencyjny', 'nazwa', 'producent'], software)

    return render_template('show_info/pokaz_sprzet_info.html', sprzet=basic_data, przypisania=history_data,
                           oprogramowania=software_data)


@show_info.route('/pokaz_info/oprogramowanie/<numer_ewidencyjny>')
def pokaz_oprogramowanie_info(numer_ewidencyjny):
    basic, error = DBC().get_instance().execute_query_fetch(
        """SELECT numer_ewidencyjny, nazwa, producent, data_zakupu, data_wygasniecia, ilosc_licencji, uwagi from Oprogramowanie
        WHERE numer_ewidencyjny = %s""", [numer_ewidencyjny]
    )
    if error is not None:
        flash('Wystąpił błąd!<br/>{}'.format(error.msg))
    basic_data = make_dictionary(['numer_ewidencyjny', 'nazwa', 'producent', 'data_zakupu', 'data_wygasniecia',
                                  'ilosc_licencji', 'uwagi'], basic[0])

    hardware, error = DBC().get_instance().execute_query_fetch(
        """SELECT s.nazwa, s.producent, s.typ, s.numer_ewidencyjny from Sprzet s
        WHERE s.numer_ewidencyjny in (select ons.sprzet_numer from OprogramowanieNaSprzecie ons
        where ons.oprogramowanie_numer = %s)""", [numer_ewidencyjny]
    )
    if error is not None:
        flash('Wystąpił błąd!<br/>{}'.format(error.msg))

    hardware_data = make_dictionaries_list(['nazwa', 'producent', 'typ', 'numer_ewidencyjny'], hardware)

    return render_template('show_info/pokaz_oprogramowanie_info.html', oprogramowanie=basic_data, sprzety=hardware_data)


@show_info.route('/pokaz_info/biuro/<numer_biura>')
def pokaz_biuro_info(numer_biura):
    basic, error = DBC().get_instance().execute_query_fetch(
        """SELECT numer, liczba_stanowisk, pietro, budynek_adres from Biuro
        WHERE numer = %s""", [numer_biura]
    )
    if error is not None:
        flash('Wystąpił błąd!<br/>{}'.format(error.msg))
    basic_data = make_dictionary(['numer', 'liczba_stanowisk', 'pietro', 'budynek_adres'], basic[0])

    building, error = DBC().get_instance().execute_query_fetch(
        """SELECT b.adres from Budynek b
        WHERE b.adres = (select budynek_adres from Biuro where numer = %s)""", [numer_biura]
    )
    if error is not None:
        flash('Wystąpił błąd!<br/>{}'.format(error.msg))
    building_data = make_dictionary(['adres'], building[0])

    workers, error = DBC().get_instance().execute_query_fetch(
        """SELECT pesel, imie, nazwisko, numer_telefonu, czy_nadal_pracuje, adres_email, dzial_nazwa, biuro_numer
        FROM Pracownik 
        WHERE biuro_numer = %s""", [numer_biura]
    )
    if error is not None:
        flash('Wystąpił błąd!<br/>{}'.format(error.msg))
    workers_data = make_dictionaries_list(['pesel', 'imie', 'nazwisko', 'numer_telefonu', 'czy_nadal_pracuje',
                                           'adres_email', 'dzial_nazwa', 'biuro_numer'], workers)

    hardware, error = DBC().get_instance().execute_query_fetch(
        """SELECT s.numer_ewidencyjny, s.nazwa, s.producent, s.typ FROM Sprzet s 
        where s.numer_ewidencyjny in (select swp.sprzet_numer_ewidencyjny from SprzetWPrzypisaniu swp
        where swp.przypisanie_id_przydzialu in (select p.id_przydzialu from Przypisanie p 
        where p.biuro_numer = %s and p.data_zwrotu is null)) """, [numer_biura]
    )
    if error is not None:
        flash('Wystąpił błąd<br/>{}'.format(error.msg))
    hardware_data = make_dictionaries_list(['numer_ewidencyjny', 'nazwa', 'producent', 'typ'], hardware)

    cards, error = DBC().get_instance().execute_query_fetch(
        """SELECT kd.id_karty, kd.data_przyznania, p.pesel, p.nazwisko, p.imie from KartaDostepu kd join Pracownik p 
        on kd.pracownik_pesel = p.pesel
        where kd.id_karty in (select pd.kartadostepu_id_karty from PrawoDostepu pd
        where pd.biuro_numer = %s)""", [numer_biura]
    )
    if error is not None:
        flash('Wystąpił błąd!<br/>{}'.format(error.msg))
    cards_data = make_dictionaries_list(['id_karty', 'data_przyznania', 'pracownik_pesel', 'pracownik_nazwisko', 'pracownik_imie'], cards)

    return render_template('show_info/pokaz_biuro_info.html', biuro=basic_data, budynek=building_data,
                           pracownicy=workers_data, sprzety=hardware_data, karty=cards_data)


@show_info.route('/pokaz_info/dzial/<nazwa>')
def pokaz_dzial_info(nazwa):
    basic, error = DBC().get_instance().execute_query_fetch(
        """SELECT nazwa, skrot, oddzial_adres from Dzial
        WHERE nazwa = %s""", [nazwa]
    )
    if error is not None:
        flash('Wystąpił błąd!<br/>{}'.format(error.msg))
    basic_data = make_dictionary(['nazwa', 'skrot', 'oddzial_adres'], basic[0])

    branch, error = DBC().get_instance().execute_query_fetch(
        """SELECT o.adres, o.nazwa from Oddzial o
        WHERE o.adres = (select d.oddzial_adres from Dzial d where 
        d.nazwa = %s)""", [nazwa]
    )
    if error is not None:
        flash('Wystąpił błąd!<br/>{}'.format(error.msg))
    branch_data = make_dictionary(['adres', 'nazwa'], branch[0])

    workers, error = DBC().get_instance().execute_query_fetch(
        """SELECT pesel, imie, nazwisko, numer_telefonu, czy_nadal_pracuje, adres_email, dzial_nazwa, biuro_numer
        FROM Pracownik 
        WHERE dzial_nazwa = %s""", [nazwa]
        )
    if error is not None:
        flash('Wystąpił błąd!<br/>{}'.format(error.msg))
    workers_data = make_dictionaries_list(['pesel', 'imie', 'nazwisko', 'numer_telefonu', 'czy_nadal_pracuje',
                                          'adres_email', 'dzial_nazwa', 'biuro_numer'], workers)

    return render_template('show_info/pokaz_dzial_info.html', dzial=basic_data, oddzial=branch_data,
                           pracownicy=workers_data)


@show_info.route('/pokaz_info/magazyn/<numer>')
def pokaz_magazyn_info(numer):
    basic, error = DBC().get_instance().execute_query_fetch(
        """SELECT numer, pojemnosc, oddzial_adres, WolnaPojemnoscMagazynu(numer) from Magazyn
        WHERE numer = %s""", [numer]
    )
    if error is not None:
        flash('Wystąpił błąd!<br/>{}'.format(error.msg))
    basic_data = make_dictionary(['numer', 'pojemnosc', 'oddzial_adres', 'wolne_miejsce'], basic[0])

    hardware, error = DBC().get_instance().execute_query_fetch(
        """SELECT s.nazwa, s.producent, s.typ, s.numer_ewidencyjny from Sprzet s
        WHERE s.magazyn_numer =  %s""", [numer]
    )
    if error is not None:
        flash('Wystąpił błąd!<br/>{}'.format(error.msg))

    hardware_data = make_dictionaries_list(['nazwa', 'producent', 'typ', 'numer_ewidencyjny'], hardware)

    return render_template('show_info/pokaz_magazyn_info.html', magazyn=basic_data, sprzety=hardware_data)


@show_info.route('/pokaz_info/karta_dostepu/<id_karty>')
def pokaz_karta_dostepu_info(id_karty):
    basic, error = DBC().get_instance().execute_query_fetch(
        """SELECT id_karty, data_przyznania, pracownik_pesel from KartaDostepu
        WHERE id_karty = %s""", [id_karty]
    )
    if error is not None:
        flash('Wystąpił błąd!<br/>{}'.format(error.msg))
    basic_data = make_dictionary(['id_karty', 'data_przyznania', 'pracownik_pesel'], basic[0])

    offices, error = DBC().get_instance().execute_query_fetch(
        """SELECT b.numer, b.budynek_adres, b.pietro from Biuro b
        WHERE b.numer in (select pd.biuro_numer from PrawoDostepu pd
        where pd.kartadostepu_id_karty = %s)""", [id_karty]
    )
    if error is not None:
        flash('Wystąpił błąd!<br/>{}'.format(error.msg))

    offices_data = make_dictionaries_list(['numer', 'budynek_adres', 'pietro'], offices)

    return render_template('show_info/pokaz_karta_dostepu_info.html', karta=basic_data, biura=offices_data)


# Redirects you to any other show info page (needed on the search page)
@show_info.route('/pokaz_info_dowolne/<typ>/<klucz>')
def pokaz_dowolne_info(typ, klucz):
    # Not finished yet and probably won't ever be
    if typ == 'oddzial':
        return redirect(url_for('show_info.pokaz_oddzial_info', adres=klucz))
    elif typ == 'budynek':
        return redirect(url_for('show_info.pokaz_budynek_info', adres=klucz))
    elif typ == 'biuro':
        return redirect(url_for('show_info.pokaz_biuro_info', numer_biura=klucz))
    elif typ == 'dzial':
        return redirect(url_for('show_info.pokaz_dzial_info', nazwa=klucz))
    elif typ == 'pracownik':
        return redirect(url_for('show_info.pokaz_pracownik_info', pesel=klucz))
    elif typ == 'magazyn':
        return redirect(url_for('show_info.pokaz_magazyn_info', numer=klucz))
    elif typ == 'sprzet':
        return redirect(url_for('show_info.pokaz_sprzet_info', numer_ewidencyjny=klucz))
    elif typ == 'oprogramowanie':
        return redirect(url_for('show_info.pokaz_oprogramowanie_info', numer_ewidencyjny=klucz))
    else:
        return redirect(url_for('niew_znaleziono'))

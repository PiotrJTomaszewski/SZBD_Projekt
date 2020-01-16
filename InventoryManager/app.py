from flask import Flask, render_template, request, flash, redirect, url_for, session
import data_generators.create_workers as creator
from database_connector import DatabaseConnector as DBC
from helpers import make_dictionaries_list

from pages_show import show
from pages_show_info import show_info
from pages_add import add
from pages_edit import edit
from pages_assign import assign
from pages_delete import delete

# Register blueprints
app = Flask(__name__)
app.register_blueprint(show)
app.register_blueprint(show_info)
app.register_blueprint(add)
app.register_blueprint(edit)
app.register_blueprint(assign)
app.register_blueprint(delete)

app.secret_key = 'Super secret key. Please don\'t look at it :)'


@app.route('/')
def strona_glowna():
    branches, error = DBC().get_instance().execute_query_fetch(
        """SELECT adres, nazwa FROM Oddzial ORDER BY adres""")
    if error is not None:
        flash('Wystąpił błąd!<br/>{}'.format(error.msg))
    branches_data = make_dictionaries_list(['adres', 'nazwa'], branches)
    return render_template('show/pokaz_oddzialy.html', oddzialy=branches_data)


@app.errorhandler(404)
def nie_znaleziono(error_code):
    return render_template('404.html')


@app.route('/wybierz_oddzial/<adres>')
def wybierz_oddzial(adres):
    session['wybrany_oddzial_adres'] = adres
    result, error = DBC().get_instance().execute_query_fetch("""SELECT nazwa FROM Oddzial WHERE adres = %s""", [adres])
    session['wybrany_oddzial_nazwa'] = result[0][0]
    return redirect(url_for('show_info.pokaz_oddzial_info', adres=adres))


@app.route('/wyszukaj', methods=['GET', 'POST'])
def wyszukaj():
    if request.method == 'GET':
        return render_template('search/wyszukaj.html')
    if request.method == 'POST':
        selected_object = request.form['object_select']
        selected_field = request.form['field_select']
        if request.form.get('search_only_here'):
            only_in_current_branch = True
        else:
            only_in_current_branch = False
        search_value = request.form['search_value']

        # Translate selected operand
        selected_operand = request.form['value_is']
        operand = ''
        text_operand = ''
        if selected_operand == 'value_is_equal':
            operand = '='
            text_operand = '='
        elif selected_operand == 'value_is_less':
            operand = '<'
            text_operand = '<'
        elif selected_operand == 'value_is_less_equal':
            operand = '<='
            text_operand = '≤'
        elif selected_operand == 'value_is_greater':
            operand = '>'
            text_operand = '>'
        elif selected_operand == 'value_is_greater_equal':
            operand = '>='
            text_operand = '≥'
        elif selected_operand == 'value_use_pattern':
            operand = 'LIKE'
            text_operand = 'pasuje do wzorca'

        if selected_object == 'object_building':
            # Create parts of the text to display
            text_object = 'Budynki'
            if selected_field == 'adres':
                text_field = 'adres budynku'
            elif selected_field == 'nazwa':
                text_field = 'nazwa budynku'
            elif selected_field == 'ilosc_pieter':
                text_field = 'liczba pięter'
            elif selected_field == 'oddzial_adres':
                text_field = 'adres oddziału'
            else:
                text_field = ''

            query = """
            SELECT adres, nazwa, ilosc_pieter, oddzial_adres
            FROM Budynek
            WHERE {field} {operand} %s""".format(field=selected_field, operand=operand)
            if only_in_current_branch:
                query += " AND oddzial_adres = '{}'".format(session['wybrany_oddzial_adres'])
            headers = ['Adres', 'Nazwa', 'Liczba pięter', 'Adres oddziału']
            goto_type = 'budynek'

        elif selected_object == 'object_office':
            # Create parts of the text to display
            text_object = 'Biura'
            if selected_field == 'adres':
                text_field = 'adres biura'
            elif selected_field == 'liczba_stanowisk':
                text_field = 'liczba stanowisk'
            elif selected_field == 'pietro':
                text_field = 'piętro'
            elif selected_field == 'budynek_adres':
                text_field = 'adres budynku'
            else:
                text_field = ''

            query = """
            SELECT numer, liczba_stanowisk, pietro, budynek_adres
            FROM Biuro
            WHERE {field} {operand} %s""".format(field=selected_field, operand=operand)
            if only_in_current_branch:
                query += " AND (SELECT oddzial_adres FROM Budynek WHERE adres=budynek_adres) = '{}'".format(
                    session['wybrany_oddzial_adres'])
            headers = ['Numer biura', 'Liczba stanowisk', 'Numer piętra', 'Adres budynku']
            goto_type = 'biuro'

        elif selected_object == 'object_dept':
            # Create parts of the text to display
            text_object = 'Działy'
            if selected_field == 'nazwa':
                text_field = 'nazwa działu'
            elif selected_field == 'skrot':
                text_field = 'skrót nazwy'
            elif selected_field == 'oddzial_adres':
                text_field = 'adres oddziału'
            else:
                text_field = ''

            query = """
                        SELECT nazwa, skrot, oddzial_adres
                        FROM Dzial
                        WHERE {field} {operand} %s""".format(field=selected_field, operand=operand)
            if only_in_current_branch:
                query += " AND oddzial_adres = '{}'".format(session['wybrany_oddzial_adres'])
            headers = ['Nazwa działu', 'Skrót nazwy', 'Adres oddziału']
            goto_type = 'dzial'

        elif selected_object == 'object_worker':
            if selected_field == 'czy_nadal_pracuje':
                if search_value.upper() == 'TAK':
                    search_value = '1'
                elif search_value.upper() == 'NIE':
                    search_value = '0'
            # Create parts of the text to display
            text_object = 'Pracownicy'
            if selected_field == 'pesel':
                text_field = 'numer PESEL'
            elif selected_field == 'imie':
                text_field = 'imię pracownika'
            elif selected_field == 'nazwisko':
                text_field = 'nazwisko pracownika'
            elif selected_field == 'numer_telefonu':
                text_field = 'numer telefonu'
            elif selected_field == 'czy_nadal_pracuje':
                text_field = 'czy nadal pracuje'
            elif selected_field == 'adres_email':
                text_field = 'adres email'
            elif selected_field == 'dzial_nazwa':
                text_field = 'nazwa działu'
            elif selected_field == 'biuro_numer':
                text_field = 'numer biura'
            else:
                text_field = ''

            query = """
                        SELECT pesel, imie, nazwisko, numer_telefonu, czy_nadal_pracuje, adres_email, dzial_nazwa, biuro_numer
                        FROM Pracownik
                        WHERE {field} {operand} %s""".format(field=selected_field, operand=operand)
            if only_in_current_branch:
                query += " AND (SELECT oddzial_adres FROM Dzial WHERE nazwa=dzial_nazwa) = '{}'".format(
                    session['wybrany_oddzial_adres'])
            headers = ['Numer PESEL', 'Imię', 'Nazwisko', 'Numer telefonu', 'Czy nadal pracuje', 'Adres email',
                       'Nazwa działu', 'Numer biura']
            goto_type = 'pracownik'

        elif selected_object == 'object_magazine':
            # Create parts of the text to display
            text_object = 'Magazyny'
            if selected_field == 'numer':
                text_field = 'numer magazynu'
            elif selected_field == 'pojemnosc':
                text_field = 'pojemność magazynu'
            elif selected_field == 'oddzial_adres':
                text_field = 'adres oddziału'
            else:
                text_field = ''

            query = """
                SELECT numer, pojemnosc, oddzial_adres
                FROM Magazyn
                WHERE {field} {operand} %s""".format(field=selected_field, operand=operand)
            if only_in_current_branch:
                query += " AND oddzial_adres = '{}'".format(session['wybrany_oddzial_adres'])
            headers = ['Numer magazynu', 'Pojemność', 'Adres oddziału']
            goto_type = 'magazyn'

        else:
            query = ''
            headers = []
            text_object = ''
            text_field = ''
            goto_type = ''
            flash('Wystąpił błąd!')
        result_rows, error = DBC().get_instance().execute_query_fetch(query, [search_value])
        if error is not None:
            flash('Wstąpił błąd podczas wyszukiwania!')
            print(error)

        result = {'headers': headers, 'rows': result_rows}

        if selected_object == 'object_worker':
            if search_value == '1':
                search_value = 'Tak'
            elif search_value == '0':
                search_value = 'Nie'

        if only_in_current_branch:
            result['text'] = '{object} w bieżącym oddziale gdzie {field} {operand} {value}'.format(
                object=text_object, field=text_field, operand=text_operand, value=search_value)
        else:
            result['text'] = '{object} gdzie {field} {operand} {value}'.format(
                object=text_object, field=text_field, operand=text_operand, value=search_value)
        # Replace 0 and 1 in is still working if workers were selected
        if selected_object == 'object_worker':
            for i in range(len(result['rows'])):
                result['rows'][i] = list(result['rows'][i])
                if result['rows'][i][4] == '1':
                    result['rows'][i][4] = 'Tak'
                else:
                    result['rows'][i][4] = 'Nie'

        # If the lookup took place in the current branch show go to info buttons
        if only_in_current_branch:
            result['goto_type'] = goto_type

        return render_template('search/wyszukaj.html', result=result)


if __name__ == '__main__':
    app.run(debug=True)

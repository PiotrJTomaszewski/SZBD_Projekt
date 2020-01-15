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


@app.route('/wybierz_oddzial/<adres>')
def wybierz_oddzial(adres):
    session['wybrany_oddzial_adres'] = adres
    result, error = DBC().get_instance().execute_query_fetch("""SELECT nazwa FROM Oddzial WHERE adres = %s""", [adres])
    session['wybrany_oddzial_nazwa'] = result[0][0]
    return redirect(url_for('show_info.pokaz_oddzial_info', adres=adres))


if __name__ == '__main__':
    app.run(debug=True)

from flask import Flask, render_template, request, flash, redirect, url_for, Blueprint
import data_generators.create_workers as creator
from forms import *

delete = Blueprint('delete', __name__)


@delete.route('/usun/oddzial/<adres>')
def usun_oddzial(adres):
    pass


@delete.route('/usun/budynek/<adres>')
def usun_budynek(adres):
    pass


@delete.route('/usun/biuro/<numer>')
def usun_biuro(numer):
    pass


@delete.route('/usun/dzial/<nazwa>')
def usun_dzial(nazwa):
    pass


@delete.route('/usun/pracownik/<pesel>')
def usun_pracownika(pesel):
    pass


@delete.route('/usun/karta_dostepu/<id_karty>')
def usun_karte_dostepu(id_karty):
    pass


@delete.route('/usun/prawo_dostepu/<id_karty>/<numer_biura>')
def usun_prawo_dostepu(id_karty, numer_biura):
    pass


@delete.route('/usun/magazyn/<numer>')
def usun_magazyn(numer):
    pass


@delete.route('/usun/przypisanie/<id_przydzialu>')
def usun_przypisanie(id_przydzialu):
    pass


@delete.route('/usun/sprzet/<numer_ewidencyjny>')
def usun_sprzet(numer_ewidencyjny):
    pass


@delete.route('/usun/sprzet_w_przypisaniu/<numer_ewidencyjny>/<id_przydzialu>')
def usun_sprzet_w_przypisaniu(numer_ewidencyjny, id_przydzialu):
    pass


@delete.route('/usun/oprogramowanie/<numer_ewidencyjny>')
def usun_oprogramowanie(numer_ewidencyjny):
    pass


@delete.route('/usun/oprogramowanie_na_sprzecie/<sprzet_numer>/<oprogramowanie_numer>')
def usun_oprogramowanie_na_sprzecie(sprzet_numer, oprogramowanie_numer):
    pass

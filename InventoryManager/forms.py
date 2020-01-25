from flask_wtf import FlaskForm
from wtforms import TextField, SubmitField, SelectField, BooleanField, IntegerField, \
    SelectMultipleField, validators, Field
from wtforms.fields.html5 import DateField
from wtforms.widgets import CheckboxInput, ListWidget


# TODO: Translate errors to Polish (enable existing translation)

class AddEditBranchForm(FlaskForm):
    address = TextField('Adres', [
        validators.InputRequired('Proszę podać adres'),
        validators.Length(max=30, message='Adres nie może być dłuższy niż 30 znaków')
    ])
    name = TextField('Nazwa', [
        validators.InputRequired('Proszę podać nazwę'),
        validators.Length(max=30, message='Nazwa nie może być dłuższa niż 30 znaków')
    ])
    submit = SubmitField('Zatwierdź')


class AddEditBuildingForm(FlaskForm):
    address = TextField('Adres', [
        validators.InputRequired('Proszę podać adres'),
        validators.Length(max=30, message='Adres nie może być dłuższy niż 30 znaków')
    ])
    name = TextField('Nazwa', [
        validators.InputRequired('Proszę podać nazwę'),
        validators.Length(max=30, message='Nazwa nie może być dłuższa niż 30 znaków')
    ])
    number_of_floors = IntegerField('Liczba pięter', [
        validators.InputRequired('Proszę podać liczę pięter'),
        validators.NumberRange(min=1, message='Liczba pięter musi być większa od 0'),
    ])
    # branch_address = SelectField('Oddział', [
    #     validators.InputRequired('Proszę wybrać oddział')
    # ], coerce=str)
    submit = SubmitField('Zatwierdź')


class AddEditOfficeForm(FlaskForm):
    number = IntegerField('Numer biura', [
        validators.InputRequired('Proszę podać numer biura'),
        validators.NumberRange(min=0, message='Numer biura nie może być mniejszy od 0')
    ])
    number_of_posts = IntegerField('Liczba stanowisk', [
        validators.InputRequired('Proszę podać liczbę stanowisk'),
        validators.NumberRange(min=1, message='Liczba stanowisk musi być większa od 0')
    ])
    building_address = SelectField('Budynek', [
        validators.InputRequired('Proszę wybrać budynek')
    ])
    floor = IntegerField('Piętro, na którym znajduje się biuro', [
        validators.InputRequired('Proszę podać piętro'),
        validators.NumberRange(min=0, message='Numer piętra nie może być mniejszy od 0')
    ])
    submit = SubmitField('Zatwierdź')


class AddEditDepForm(FlaskForm):
    name = TextField('Nazwa', [
        validators.InputRequired('Proszę podać nazwę'),
        validators.Length(max=30, message='Nazwa nie może być dłuższa niż 30 znaków')
    ])
    short_name = TextField('Skrót', [
        validators.InputRequired('Proszę podać skrót nazwy'),
        validators.Length(max=5, message='Skrót nazwy nie może być dłuższy niż 5 znaków')
    ])
    # branch_address = SelectField('Oddział', [
    #     validators.InputRequired('Proszę wybrać oddział')
    # ], coerce=str)
    submit = SubmitField('Zatwierdź')


class AddEditWorkerForm(FlaskForm):
    pesel = TextField('PESEL', [
        validators.InputRequired('Proszę podać numer PESEL'),
        validators.Regexp('^[0-9]{11}$', message='Numer PESEL musi składać się z 11 cyfr')
    ])
    name = TextField('Imię', [
        validators.InputRequired('Proszę podać imię'),
        validators.Length(max=30, message='Imię nie może być dłuższe niż 30 znaków')
    ])
    surname = TextField('Nazwisko', [
        validators.InputRequired('Proszę podać nazwisko'),
        validators.Length(max=30, message='Nazwisko nie może być dłuższe niż 30 znaków')
    ])
    phone_number = TextField('Numer telefonu', [
        validators.InputRequired('Proszę podać numer telefonu'),
        validators.Regexp('^[0-9]{9}$', message='Numer telefonu musi składać się z 9 cyfr')
    ])
    is_still_working = BooleanField('Czy nadal pracuje?', default=True)
    email_address = TextField('Adres email', [
        validators.InputRequired('Proszę podać adres email'),
        validators.Email('Proszę podać prawidłowy adres email'),
        validators.Length(max=50, message='Adres email nie może być dłuższy niż 50 znaków')
    ])
    dept_name = SelectField('Dział', [
        validators.InputRequired('Proszę wybrać dział')
    ], coerce=str)
    office_number = SelectField('Biuro', [
        validators.InputRequired('Proszę wybrać biuro')
    ], coerce=int)
    submit = SubmitField('Zatwierdź')


class AddEditAccessCardForm(FlaskForm):
    assign_date = DateField('Data przyznania', [
        validators.InputRequired('Proszę podać datę przyznania')
    ])
    worker_pesel = SelectField('Pracownik', [
        validators.InputRequired('Proszę wybrać pracownika'),
    ], coerce=str)
    submit = SubmitField('Zatwierdź')


class AddEditMagazineForm(FlaskForm):
    number = IntegerField('Numer magazynu', [
        validators.InputRequired('Proszę podać numer magazynu'),
        validators.NumberRange(min=0, message='Numer magazynu nie może być mniejszy od 0')
    ])
    capacity = IntegerField('Pojemność magazynu', [
        validators.InputRequired('Proszę podać pojemność magazynu'),
        validators.NumberRange(min=1, message='Pojemność magazynu nie może być mniejsza od 1')
    ])
    # branch_address = SelectField('Oddział', [
    #     validators.InputRequired('Proszę wybrać oddział')
    # ], coerce=str)
    submit = SubmitField('Zatwierdź')


# class AddEditAssignmentForm(FlaskForm):

# class MultiCheckboxField(SelectMultipleField):
#     widget = ListWidget(prefix_label=False)
#     option_widget = CheckboxInput()

class CheckboxField(Field):
    widget = CheckboxInput()
    _value = lambda x: 1


class AddEditHardwareForm(FlaskForm):
    number = IntegerField('Numer ewidencyjny', [
        validators.InputRequired('Proszę podać numer ewidencyjny'),
        validators.NumberRange(min=0, message='Numer ewidencyjny nie może być mniejszy od 0')
    ])
    purchase_date = DateField('Data zakupu', [
        validators.InputRequired('Proszę podać datę zakupu')
    ])
    name = TextField('Nazwa', [
        validators.InputRequired('Proszę podać nazwę'),
        validators.Length(max=30, message='Nazwa nie może być dłuższa niż 30 znaków')
    ])
    new_or_existing_switch = CheckboxField('Zdefiniować nowy typ?')
    existing_type = SelectField('Istniejący typ', [
        validators.Optional()
    ])
    new_type = TextField('Nowy typ', [
        validators.Optional(),
        validators.Length(max=30, message='Typ nie może być dłuższy niż 30 znaków')
    ])
    brand = TextField('Producent', [
        validators.InputRequired('Proszę podać nazwę producenta'),
        validators.Length(max=30, message='Nazwa producenta nie może być dłuższa niż 30 znaków')
    ])
    # magazine_number = SelectField('Magazyn (opcjonalne)', [
    #     validators.Optional()
    # ])
    magazine_number = SelectField('Magazyn', [
        validators.InputRequired('Proszę wybrać magazyn')
    ], coerce=int)
    notes = TextField('Uwagi (opcjonalne)', [
        validators.Length(max=150, message='Uwagi nie mogą być dłuższe niż 150 znaków')
    ])
    submit = SubmitField('Zatwierdź')


class AddEditSoftware(FlaskForm):
    number = IntegerField('Numer ewidencyjny', [
        validators.InputRequired('Proszę podać numer ewidencyjny'),
        validators.NumberRange(min=0, message='Numer ewidencyjny nie może być mniejszy od 0')
    ])
    name = TextField('Nazwa', [
        validators.InputRequired('Proszę podać nazwę'),
        validators.Length(max=30, message='Nazwa nie może być dłuższa niż 30 znaków')
    ])
    brand = TextField('Producent', [
        validators.InputRequired('Proszę podać nazwę producenta'),
        validators.Length(max=30, message='Nazwa producenta nie może być dłuższa niż 30 znaków')
    ])
    purchase_date = DateField('Data zakupu', [
        validators.InputRequired('Proszę podać datę zakupu')
    ])
    expiration_date = DateField('Data wygaśnięcia (opcjonalne)', [
        validators.Optional(),
    ])
    number_of_licences = IntegerField('Liczba licencji (opcjonalne)', [
        validators.Optional(),
        validators.NumberRange(min=1, message='Liczba licencji nie może być mniejsza od 1')
    ])
    notes = TextField('Uwagi (opcjonalne)', [
        validators.Length(max=150, message='Uwagi nie mogą być dłuższe niż 150 znaków')
    ])
    submit = SubmitField('Zatwierdź')

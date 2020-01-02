from flask_wtf import FlaskForm
from wtforms import TextField, SubmitField, SelectField, BooleanField, validators


class AddEditWorkerForm(FlaskForm):
    pesel = TextField('PESEL', [
        validators.InputRequired('Proszę podać numer PESEL!'),
        validators.Regexp('^[0-9]{11}$', message='Numer PESEL musi składać się z 11 cyfr!')])
    name = TextField('Imię', [
        validators.InputRequired('Proszę podać imię!'),
        validators.Length(max=30, message='Imię nie może być dłuższe niż 30 znaków!'), ])
    surname = TextField('Nazwisko', [
        validators.InputRequired('Proszę podać nazwisko!'),
        validators.Length(max=30, message='Nazwisko nie może być dłuższe niż 30 znaków!')])
    phone_number = TextField('Numer telefonu', [
        validators.InputRequired('Proszę podać numer telefonu!'),
        validators.Regexp('^[0-9]{9}$', message='Numer telefonu musi składać się z 9 cyfr!')])
    is_still_working = BooleanField('Czy nadal pracuje?', default=True)
    email_address = TextField('Adres email', [
        validators.InputRequired('Proszę podać adres email!'),
        validators.Email('Proszę podać prawidłowy adres email!'),
        validators.Length(max=50, message='Adres email nie może być dłuższy niż 50 znaków!')])
    dept_name = SelectField('Nazwa działu', [
        validators.InputRequired('Proszę wybrać dział!')])
    office_number = SelectField('Numer biura', [
        validators.InputRequired('Proszę wybrać biuro!')], coerce=int)
    submit = SubmitField('Zatwierdź')

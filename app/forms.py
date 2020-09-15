# Imports
 
from flask_wtf import FlaskForm

from wtforms import StringField, PasswordField, TextAreaField, SubmitField, SelectField, HiddenField, BooleanField
from wtforms.fields.html5 import DateField, TimeField, DateTimeLocalField

from wtforms.validators import ValidationError, DataRequired, EqualTo
from flask_wtf.file import FileField, FileRequired, FileAllowed

from app.models import User

# Forms

class LoginForm(FlaskForm):
    medzdravaid = StringField('medzdrava ID', validators=[DataRequired()])
    phonenumber = StringField('Номер телефона', validators=[DataRequired()])
    password = PasswordField('Пароль')

    submit = SubmitField('Войти')

# Registration form
class RegistrationForm(FlaskForm):
    # id выдаётся пользователю автоматически
    role = SelectField(
        "Тип тользователя",
        choices=[
            (1, 'Пациент'),
            (2, 'Врач'),
            (3, 'Администратор')
        ],
        validate_choice = False
    )
    first_name = StringField('Имя', validators=[DataRequired()])
    second_name = StringField('Фамилия', validators=[DataRequired()])
    middle_name = StringField('Отчество', validators=[DataRequired()])
    email = StringField('Email')
    sex = SelectField(
        "Пол",
        choices = [
            (1, 'женский'),
            (2, 'мужской')
        ],
        validate_choice = False
    )
    birthdate = DateField('Дата рождения', format='%Y-%m-%d', validators = [DataRequired()])
    address = StringField('Адрес', validators=[DataRequired()])
    phonenumber = StringField('Номер телефона', validators = [DataRequired()])
    password = PasswordField('Пароль')
    password2 = PasswordField('Повторите пароль', validators = [EqualTo('password')])
    submit = SubmitField('Зарегистрировать')


class EditProfileForm(FlaskForm):
    first_name = StringField('Имя', validators = [DataRequired()])
    second_name = StringField('Фамилия', validators = [DataRequired()])
    middle_name = StringField('Отчество', validators = [DataRequired()])
    birthdate = DateField('Дата рождения', format='%Y-%m-%d', validators = [DataRequired()])
    phonenumber = StringField('Номер телефона', validators = [DataRequired()])
    address = StringField('Адрес', validators = [DataRequired()])
    email = StringField('Email')
    submit = SubmitField('Подтвердить изменения')




# Creation of a new Event
class NewEventCreatorForm(FlaskForm):
    vrachi = User.query.filter(User.role == 2).order_by(User.second_name).all()
    choices_list = []
    for vrach in vrachi:
        name = vrach.second_name + " " + vrach.first_name + " " + vrach.middle_name
        a = (vrach.id, name)
        choices_list.append(a)
    id_vrach = SelectField(
        "Ответственный врач",
        choices = choices_list,
        validate_choice = False,
        )
    datetime = DateTimeLocalField('Дата и время события', format='%Y-%m-%dT%H:%M')
    event_name = StringField('Название события', validators=[DataRequired()])
    zacklucheniye = TextAreaField('Заключение')
    submit = SubmitField('Сохранить')
    
    def set_selectfield(self, id_vrach):
        self.id_vrach.data = id_vrach

    def validate_id_vrach(self, id_vrach):
        exists = User.query.filter_by(id = int(id_vrach.data)).scalar()
        if not exists:
            raise ValidationError('Такого врача нет')


# Creations of new allergen and diagnoses
class NewAllergen(FlaskForm):
    allergen = StringField('Аллерген', validators=[DataRequired()])
    submit = SubmitField('Создать')

class NewDiagnoz(FlaskForm):
    diagnoz = StringField('Диагноз', validators=[DataRequired()])
    submit = SubmitField('Создать')

class UploadAvatarForm(FlaskForm):
    image = FileField('Выберите файл', validators = [
        FileRequired("Нужно выбрать файл."),
        FileAllowed(['jpg', 'png'], 'Формат файла должен быть .png или .jpg.')
    ])
    submit = SubmitField('Загрузить')

class CropAvatarForm(FlaskForm):
    x = HiddenField()
    y = HiddenField()
    w = HiddenField()
    h = HiddenField()
    submit = SubmitField('Обрезать')

class GetEventsForm(FlaskForm):
    eventdate = DateField('Дата', format='%Y-%m-%d', validators=[DataRequired()])
    submit = SubmitField('Узнать')

class NewPostForm(FlaskForm):
    title = StringField('Заголовок статьи', validators = [DataRequired()])
    main_text = TextAreaField("Пост:", validators = [DataRequired()])
    main_image = FileField('Основное изображение', validators = [
        FileAllowed(['jpg', 'png'], 'Формат файла должен быть .png или .jpg')
        ])
    is_in_slider = BooleanField('Отображать на Главной')
    submit = SubmitField('Опубликовать')

class UserSearchForm(FlaskForm):
    search = StringField('Введите пользователя', validators = [DataRequired()])
    submit = SubmitField('Поиск')


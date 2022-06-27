from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, URLField
from wtforms.validators import DataRequired, Email


class LoginForm(FlaskForm):
    email = StringField("Email", validators=[DataRequired(), Email()])
    password = PasswordField("Password", validators=[DataRequired(), ])
    submit = SubmitField("submit", )


class PostForm(FlaskForm):
    family = StringField("Family", )
    genus = StringField("Genus")
    species = StringField("Species")
    authority = StringField("Authority")
    local_name = StringField("Local Name")
    language = StringField("Language")
    size_of_file = StringField("Size of file (PDF) for example 10. Don't include KB")
    size_tiff = StringField("Size of file (tiff) for example 10. Don't include KB")
    country = StringField("Country")
    submit = SubmitField("Submit")


class RegisterForm(FlaskForm):
    first_name = StringField("First Name", validators=[DataRequired(), ])
    second_name = StringField("Second Name", validators=[DataRequired()])
    email = StringField("Email", validators=[DataRequired(), ])
    password = PasswordField("Password", validators=[DataRequired(), ])
    submit = SubmitField("Submit")


class UrlForm(FlaskForm):
    url = URLField("Url", validators=[DataRequired(), ])
    submit = SubmitField("Submit")

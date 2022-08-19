from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, TextAreaField
from wtforms.validators import DataRequired, Email, Length, URL


# custom validator
def EmailOrNone(form, field):
    """
    Return without error if field has no input or if field is valid Email address
    """
    if len(field.data) == 0:
        return
    else:
        return Email()(form, field)

# custom validator
def UrlOrNone(form, field):
    """
    Return without error if field has no input or if field is valid url
    """
    if len(field.data) == 0:
        return
    else:
        return URL()(form, field)

class MessageForm(FlaskForm):
    """Form for adding/editing messages."""

    text = TextAreaField('text', validators=[DataRequired()])


class UserAddForm(FlaskForm):
    """Form for adding users."""

    username = StringField('Username', validators=[DataRequired()])
    email = StringField('E-mail', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[Length(min=6)])
    image_url = StringField('(Optional) Image URL')


        
class UserEditForm(FlaskForm):
    """Form for adding users."""

    username = StringField("Username")
    email = StringField("Email", validators=[ EmailOrNone ])
    image_url = StringField("(Optional) Image URL", validators=[ UrlOrNone ])
    header_image_url = StringField("(Optional) Header Image URL", validators=[ UrlOrNone ])
    bio = StringField("(Optional) Bio")
    password = PasswordField('Password')


class LoginForm(FlaskForm):
    """Login form."""

    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[Length(min=6)])

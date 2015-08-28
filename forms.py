from flask_wtf import Form
from wtforms import TextAreaField
from wtforms.validators import DataRequired


class PostForm(Form):
    content = TextAreaField("Type address in NYC: Empire State Building,  8th ave, NYC  "
                            "or  69 Bay 17th Street, Brooklyn",
                            validators=[DataRequired(),])

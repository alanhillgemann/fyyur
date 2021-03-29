from datetime import datetime
from enum import Enum
from flask_wtf import FlaskForm
from wtforms import BooleanField, DateTimeField, IntegerField, SelectField, SelectMultipleField, StringField
from wtforms.validators import DataRequired, NumberRange, Optional, Regexp, URL


class Genre(Enum):
    Alternative = 'Alternative'
    Blues = 'Blues'
    Classical = 'Classical'
    Country = 'Country'
    Electronic = 'Electronic'
    Folk = 'Folk'
    Funk = 'Funk'
    Heavy_Metal = 'Heavy Metal'
    Hip_Hop = 'Hip-Hop'
    Instrumental = 'Instrumental'
    Jazz = 'Jazz'
    Musical_Theatre = 'Musical Theatre'
    Pop = 'Pop'
    Punk = 'Punk'
    R_B = 'R&B'
    Reggae = 'Reggae'
    Rock_n_Roll = 'Rock n Roll'
    Soul = 'Soul'
    Other = 'Other'

    @classmethod
    def list(cls):
        return [(c.value, c.value) for c in cls]


class State(Enum):
    AK = 'AK'
    AL = 'AL'
    AR = 'AR'
    AZ = 'AZ'
    CA = 'CA'
    CO = 'CO'
    CT = 'CT'
    DC = 'DC'
    DE = 'DE'
    FL = 'FL'
    GA = 'GA'
    HI = 'HI'
    IA = 'IA'
    ID = 'ID'
    IL = 'IL'
    IN = 'IN'
    KS = 'KS'
    KY = 'KY'
    LA = 'LA'
    MA = 'MA'
    MD = 'MD'
    ME = 'ME'
    MI = 'MI'
    MN = 'MN'
    MO = 'MO'
    MS = 'MS'
    MT = 'MT'
    NC = 'NC'
    ND = 'ND'
    NE = 'NE'
    NH = 'NH'
    NJ = 'NJ'
    NM = 'NM'
    NV = 'NV'
    NY = 'NY'
    OH = 'OH'
    OK = 'OK'
    OR = 'OR'
    PA = 'PA'
    RI = 'RI'
    SC = 'SC'
    SD = 'SD'
    TN = 'TN'
    TX = 'TX'
    UT = 'UT'
    VA = 'VA'
    VT = 'VT'
    WA = 'WA'
    WI = 'WI'
    WV = 'WV'
    WY = 'WY'

    @classmethod
    def list(cls):
        return [(c.value, c.value) for c in cls]


class ShowForm(FlaskForm):
    artist_id = IntegerField('artist_id', validators=[DataRequired(), NumberRange(min=0, max=999999999999)])
    venue_id = IntegerField('venue_id', validators=[DataRequired(), NumberRange(min=0, max=999999999999)])
    start_time = DateTimeField('start_time', validators=[DataRequired()], format="%Y-%m-%d %H:%M", default=datetime.today)


class VenueForm(FlaskForm):
    name = StringField('name', validators=[DataRequired()])
    city = StringField('city', validators=[DataRequired()])
    state = SelectField('state', validators=[DataRequired()], choices=State.list())
    address = StringField('address', validators=[DataRequired()])
    phone = StringField('phone', validators=[DataRequired(), Regexp(r'^\d{3}-\d{3}-\d{4}$')])
    image_link = StringField('image_link', validators=[DataRequired(), URL()])
    genres = SelectMultipleField('genres', validators=[DataRequired()], choices=Genre.list())
    facebook_link = StringField('facebook_link', validators=[Optional(), URL()])
    website_link = StringField('website_link', validators=[Optional(), URL()])
    seeking_talent = BooleanField('seeking_talent')
    seeking_description = StringField('seeking_description')


class ArtistForm(FlaskForm):
    name = StringField('name', validators=[DataRequired()])
    city = StringField('city', validators=[DataRequired()])
    state = SelectField('state', validators=[DataRequired()], choices=State.list())
    phone = StringField('phone', validators=[DataRequired(), Regexp(r'^\d{3}-\d{3}-\d{4}$')])
    image_link = StringField('image_link', validators=[DataRequired(), URL()])
    genres = SelectMultipleField('genres', validators=[DataRequired()], choices=Genre.list())
    facebook_link = StringField('facebook_link', validators=[Optional(), URL()])
    website_link = StringField('website_link', validators=[Optional(), URL()])
    seeking_venue = BooleanField('seeking_venue')
    seeking_description = StringField('seeking_description')

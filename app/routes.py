# Standard Library imports

# Core Flask imports
from flask import Blueprint, render_template

# Third-party imports

# App imports
from flask import redirect, url_for
from app import db_manager
from app import login_manager
from .views import (
    error_views,
    account_management_views,
    static_views,
)
from .models import User,Uzivatele,PocetDeti

bp = Blueprint('routes', __name__)

# alias
db = db_manager.session
from flask_wtf import FlaskForm, RecaptchaField
from wtforms import StringField, PasswordField, BooleanField, SubmitField,DateField, IntegerField
from wtforms.validators import DataRequired, Email, EqualTo, Length,InputRequired, ValidationError
import re

class PocetDetiForm(FlaskForm):
    def validate_name(form, field):
        if not re.match("^[A-Za-z]*$", field.data):
            raise ValidationError("Name must contain only letters without special characters")

    def validate_pocet_deti(form, field):
        if not field.data.isdigit() or int(field.data) < 0:
            raise ValidationError("Pocet deti must be a positive integer")

    name = StringField('Name', validators=[InputRequired(message="You can't leave this empty"), validate_name])
    pocet_deti = StringField('Pocet Deti', validators=[InputRequired(message="You can't leave this empty"), validate_pocet_deti])


@bp.route("/smazat/<int:id>", methods=["POST"])
def smazat(id):
    # Vyhledání záznamu podle ID
    zaznam = db.query(PocetDeti).get(id)
    if zaznam:
        db.delete(zaznam)
        db.commit()
    return redirect(url_for("routes.vypis"))



@bp.route("/pocet_deti", methods=["GET", "POST"])
def pocet_deti():
    form=PocetDetiForm()
    if form.validate_on_submit():
        new_entry = PocetDeti(jmeno=form.name.data, pocet_deti=int(form.pocet_deti.data))
        db.add(new_entry)
        db.commit()
        return redirect(url_for("routes.vypis"))  # Přesměrování na /vypis
    return render_template("pocet_deti.html",form=form)

class FormFormular(FlaskForm):
    def validate_characters(form, field):
        if not re.match("^[A-Za-z]*$", field.data):
            raise ValidationError("Field must contain only letters without special characters")

    name = StringField('Name', validators=[InputRequired(message="You can't leave this empty"), validate_characters])
    surename = StringField('Surename', validators=[InputRequired(message="You can't leave this empty"), validate_characters])


@bp.route("/vypis", methods=["GET"])
def vypis():
    # Načtení všech záznamů z databáze
    zaznamy = db.query(PocetDeti).all()
    return render_template("vypis.html", zaznamy=zaznamy)


@bp.route("/formular", methods=["GET", "POST"])
def formular():
    form=FormFormular()
    if form.validate_on_submit():
        print(form.name.data)
        new_user = Uzivatele(name=form.name.data, surename=form.surename.data)
        db.add(new_user)
        db.commit()
        return "Formular submitted"
    return render_template("formular.html",form=form)
# Request management
@bp.before_app_request
def before_request():
    db()

@bp.teardown_app_request
def shutdown_session(response_or_exc):
    db.remove()

@login_manager.user_loader
def load_user(user_id):
    """Load user by ID."""
    if user_id and user_id != "None":
        return User.query.filter_by(user_id=user_id).first()

# Error views
bp.register_error_handler(404, error_views.not_found_error)

bp.register_error_handler(500, error_views.internal_error)

# Public views
bp.add_url_rule("/", view_func=static_views.index)

bp.add_url_rule("/register", view_func=static_views.register)

bp.add_url_rule("/login", view_func=static_views.login)

# Login required views
bp.add_url_rule("/settings", view_func=static_views.settings)

# Public API
bp.add_url_rule(
   "/api/login", view_func=account_management_views.login_account, methods=["POST"]
)

bp.add_url_rule("/logout", view_func=account_management_views.logout_account)

bp.add_url_rule(
   "/api/register",
   view_func=account_management_views.register_account,
   methods=["POST"],
)

# Login Required API
bp.add_url_rule("/api/user", view_func=account_management_views.user)

bp.add_url_rule(
   "/api/email", view_func=account_management_views.email, methods=["POST"]
)

# Admin required
bp.add_url_rule("/admin", view_func=static_views.admin)

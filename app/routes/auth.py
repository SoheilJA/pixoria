from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, current_user
from app import db, limiter
from app.models import User
from app.forms import LoginForm
from datetime import datetime

bp = Blueprint("auth", __name__)


@bp.route("/login", methods=["GET", "POST"])
@limiter.limit("5 per minute")
def login():
    if current_user.is_authenticated:
        return redirect(url_for("admin.dashboard"))

    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()

        if user is None or not user.check_password(form.password.data):
            flash("نام کاربری یا رمز عبور اشتباه است.", "danger")
            return redirect(url_for("auth.login"))

        if not user.is_active:
            flash("حساب کاربری شما غیرفعال است.", "warning")
            return redirect(url_for("auth.login"))

        login_user(user, remember=form.remember_me.data)
        user.last_login = datetime.utcnow()
        db.session.commit()

        next_page = request.args.get("next")
        if not next_page or not next_page.startswith("/"):
            next_page = url_for("admin.dashboard")

        flash(f"خوش آمدید {user.full_name or user.username}!", "success")
        return redirect(next_page)

    return render_template("auth/login.html", form=form)


@bp.route("/logout")
def logout():
    logout_user()
    flash("با موفقیت خارج شدید.", "info")
    return redirect(url_for("main.index"))

# auth.py
import os
from functools import wraps
from flask import session, redirect, url_for, request, render_template

def handle_login():
    """Maneja la lógica de login con password desde .env."""
    error = None
    if request.method == "POST":
        password = request.form.get("password", "")
        admin_password = os.getenv("ADMIN_PASSWORD", "admin123")
        if password == admin_password:
            session["authenticated"] = True
            next_url = request.args.get("next")
            return redirect(next_url or url_for("main.dashboard"))
        error = "Contraseña incorrecta"
    return render_template("login.html", error=error)
def login_required(f):
    """Decorator que protege rutas que requieren autenticación."""
    @wraps(f)
    def decorated(*args, **kwargs):
        if not session.get("authenticated"):
            return redirect(url_for("main.login", next=request.url))
        
        
        return f(*args, **kwargs)
    return decorated

def handle_login():
    """Maneja la lógica de login con password desde .env."""
    error = None
    if request.method == "POST":
        password = request.form.get("password", "")
        admin_password = os.getenv("ADMIN_PASSWORD", "admin123")
        if password == admin_password:
            session["authenticated"] = True
            next_url = request.args.get("next")
            return redirect(next_url or url_for("main.dashboard"))
        error = "Contraseña incorrecta"
    return render_template("login.html", error=error)

def handle_logout():
    """Cierra la sesión del usuario."""
    session.pop("authenticated", None)
    return redirect(url_for("main.login"))
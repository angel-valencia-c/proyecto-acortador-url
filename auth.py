# auth.py
import os
from functools import wraps
from flask import session, redirect, url_for, request, render_template_string

LOGIN_TEMPLATE = """
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <title>Login - URL Tracker</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: 'Segoe UI', sans-serif;
            background: #0f172a;
            display: flex;
            align-items: center;
            justify-content: center;
            min-height: 100vh;
        }
        .card {
            background: #1e293b;
            padding: 2.5rem;
            border-radius: 12px;
            width: 360px;
            box-shadow: 0 25px 50px rgba(0,0,0,0.4);
        }
        h2 {
            color: #f1f5f9;
            margin-bottom: 0.5rem;
            font-size: 1.5rem;
        }
        p { color: #64748b; margin-bottom: 1.5rem; font-size: 0.9rem; }
        input {
            width: 100%;
            padding: 0.75rem 1rem;
            background: #0f172a;
            border: 1px solid #334155;
            border-radius: 8px;
            color: #f1f5f9;
            font-size: 1rem;
            margin-bottom: 1rem;
            outline: none;
        }
        input:focus { border-color: #6366f1; }
        button {
            width: 100%;
            padding: 0.75rem;
            background: #6366f1;
            color: white;
            border: none;
            border-radius: 8px;
            font-size: 1rem;
            cursor: pointer;
            font-weight: 600;
        }
        button:hover { background: #4f46e5; }
        .error {
            color: #f87171;
            font-size: 0.85rem;
            margin-bottom: 1rem;
            background: rgba(248,113,113,0.1);
            padding: 0.5rem 0.75rem;
            border-radius: 6px;
        }
    </style>
</head>
<body>
    <div class="card">
        <h2>🔗 URL Tracker</h2>
        <p>Accede al panel administrativo</p>
        {% if error %}
        <div class="error">{{ error }}</div>
        {% endif %}
        <form method="POST">
            <input type="password" name="password" placeholder="Contraseña" autofocus required>
            <button type="submit">Entrar</button>
        </form>
    </div>
</body>
</html>
"""

def login_required(f):
    """Decorator que protege rutas que requieren autenticación."""
    @wraps(f)
    def decorated(*args, **kwargs):
        if not session.get("authenticated"):
            return redirect(url_for("bp.login", next=request.url))
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
            return redirect(next_url or url_for("bp.dashboard"))
        error = "Contraseña incorrecta"
    return render_template_string(LOGIN_TEMPLATE, error=error)

def handle_logout():
    """Cierra la sesión del usuario."""
    session.pop("authenticated", None)
    return redirect(url_for("bp.login"))
import os
import json
import string
import random
import datetime
import sqlite3
import io

from flask import (Blueprint, request, redirect, jsonify,
                   render_template, Response, send_file)
from database import get_db_connection
from auth import login_required, handle_login, handle_logout
import datetime
import requests
from flask import request, redirect, abort

try:
    import openpyxl
    from openpyxl.styles import Font, PatternFill, Alignment
except ImportError:
    openpyxl = None

bp = Blueprint('main', __name__)


# ─── AUTH ────────────────────────────────────────────────────────────────────

@bp.route('/login', methods=['GET', 'POST'])
def login():
    return handle_login()

@bp.route('/logout')
def logout():
    return handle_logout()


# ─── HELPERS ─────────────────────────────────────────────────────────────────

def generate_short_id(length=6):
    """Genera un short_id alfanumérico aleatorio."""
    chars = string.ascii_letters + string.digits
    return ''.join(random.choice(chars) for _ in range(length))

def parse_device(ua):
    """Detecta tipo de dispositivo desde User-Agent."""
    ua_lower = ua.lower()
    if any(x in ua_lower for x in ['mobile', 'android', 'iphone']):
        return 'mobile'
    if any(x in ua_lower for x in ['tablet', 'ipad']):
        return 'tablet'
    return 'desktop'

def parse_browser(ua):
    """Detecta navegador desde User-Agent."""
    ua_lower = ua.lower()
    if 'edg' in ua_lower:    return 'Edge'
    if 'chrome' in ua_lower: return 'Chrome'
    if 'firefox' in ua_lower: return 'Firefox'
    if 'safari' in ua_lower: return 'Safari'
    return 'Otro'


# ─── HOME ────────────────────────────────────────────────────────────────────

@bp.route('/')
def home():
    """Página principal con formulario de acortamiento."""
    return render_template('index.html')


# ─── CREAR URL ───────────────────────────────────────────────────────────────

@bp.route('/crear', methods=['POST'])
def crear_url():
    """Crea un nuevo enlace corto."""
    data = request.get_json()
    original_url = data.get('original_url')

    if not original_url:
        return jsonify({'error': 'URL requerida'}), 400

    short_id = generate_short_id()
    conn = get_db_connection()

    # Evitar colisiones
    while conn.execute("SELECT 1 FROM urls WHERE short_id = ?", (short_id,)).fetchone():
        short_id = generate_short_id()

    conn.execute(
        "INSERT INTO urls (short_id, original_url) VALUES (?, ?)",
        (short_id, original_url)
    )
    conn.commit()
    conn.close()
    return jsonify({'short_id': short_id})


# ─── REDIRECCIÓN + TRACKING ──────────────────────────────────────────────────

@bp.route('/<short_id>')
def redireccionar(short_id):
    """Redirige al destino y registra la visita con tracking completo."""
    if short_id in ('favicon.ico', 'robots.txt', 'sitemap.xml'):
        return "", 404

    conn = get_db_connection()
    url_row = conn.execute(
        "SELECT original_url, is_active FROM urls WHERE short_id = ?",
        (short_id,)
    ).fetchone()

    if not url_row:
        conn.close()
        return "Enlace no encontrado", 404

    if not url_row['is_active']:
        conn.close()
        return "Este enlace ha sido desactivado", 410

    original_url = url_row['original_url']
    ua = request.headers.get('User-Agent', '')

    # Capturar todos los parámetros adicionales no estándar
    known_params = {
        'utm_source','utm_medium','utm_campaign','utm_term','utm_content',
        'gclid','gbraid','wbraid','fbclid','fb_action_ids','fb_action_types',
        'ttclid','msclkid','twclid'
    }
    extra = {k: v for k, v in request.args.items() if k not in known_params}

    conn.execute('''
        INSERT INTO visits (
            short_id, ip_address, user_agent, referer,
            utm_source, utm_medium, utm_campaign, utm_term, utm_content,
            gclid, gbraid, wbraid,
            fbclid, fb_action_ids, fb_action_types,
            ttclid, msclkid, twclid,
            additional_params, device_type, browser,
            country, timestamp
        ) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
    ''', (
        short_id,
        request.remote_addr,
        ua,
        request.referrer,
        request.args.get('utm_source'),
        request.args.get('utm_medium'),
        request.args.get('utm_campaign'),
        request.args.get('utm_term'),
        request.args.get('utm_content'),
        request.args.get('gclid'),
        request.args.get('gbraid'),
        request.args.get('wbraid'),
        request.args.get('fbclid'),
        request.args.get('fb_action_ids'),
        request.args.get('fb_action_types'),
        request.args.get('ttclid'),
        request.args.get('msclkid'),
        request.args.get('twclid'),
        json.dumps(extra) if extra else None,
        parse_device(ua),
        parse_browser(ua),
        None,  # country — geolocation pendiente
        datetime.datetime.now()
    ))

    conn.commit()
    conn.close()
    return redirect(original_url, code=302)


# ─── DASHBOARD ───────────────────────────────────────────────────────────────

@bp.route('/reportes')
@login_required
def dashboard():
    """Panel administrativo con métricas y tabla de visitas."""
    conn = get_db_connection()

    visitas = conn.execute('''
        SELECT v.*, u.original_url, u.is_active
        FROM visits v
        LEFT JOIN urls u ON v.short_id = u.short_id
        ORDER BY v.timestamp DESC
    ''').fetchall()

    total_clics = conn.execute('SELECT COUNT(*) FROM visits').fetchone()[0]
    total_links = conn.execute('SELECT COUNT(*) FROM urls WHERE is_active = 1').fetchone()[0]

    clics_por_dia = conn.execute('''
        SELECT DATE(timestamp) as dia, COUNT(*) as total
        FROM visits
        WHERE timestamp >= DATE('now', '-7 days')
        GROUP BY DATE(timestamp)
        ORDER BY dia ASC
    ''').fetchall()

    devices = conn.execute('''
        SELECT device_type, COUNT(*) as total
        FROM visits WHERE device_type IS NOT NULL
        GROUP BY device_type
    ''').fetchall()

    top_sources = conn.execute('''
        SELECT utm_source, COUNT(*) as total
        FROM visits WHERE utm_source IS NOT NULL
        GROUP BY utm_source ORDER BY total DESC LIMIT 5
    ''').fetchall()

    browsers = conn.execute('''
        SELECT browser, COUNT(*) as total
        FROM visits WHERE browser IS NOT NULL
        GROUP BY browser ORDER BY total DESC
    ''').fetchall()

    top_countries = conn.execute('''
        SELECT country, COUNT(*) as total
        FROM visits WHERE country IS NOT NULL
        GROUP BY country ORDER BY total DESC LIMIT 5
    ''').fetchall()

    top_campaigns = conn.execute('''
        SELECT utm_campaign, COUNT(*) as total
        FROM visits WHERE utm_campaign IS NOT NULL
        GROUP BY utm_campaign ORDER BY total DESC LIMIT 5
    ''').fetchall()

    conn.close()

    return render_template('dashboard.html',
        visitas=visitas,
        total_clics=total_clics,
        total_links=total_links,
        clics_por_dia=[dict(r) for r in clics_por_dia],
        devices=[dict(r) for r in devices],
        top_sources=[dict(r) for r in top_sources],
        browsers=[dict(r) for r in browsers],
        top_countries=[dict(r) for r in top_countries],
        top_campaigns=[dict(r) for r in top_campaigns],
    )


# ─── TOGGLE ACTIVO/INACTIVO ──────────────────────────────────────────────────

@bp.route('/toggle/<short_id>', methods=['POST'])
@login_required
def toggle_link(short_id):
    """Activa o desactiva un enlace sin eliminarlo."""
    conn = get_db_connection()
    row = conn.execute(
        "SELECT is_active FROM urls WHERE short_id = ?", (short_id,)
    ).fetchone()

    if not row:
        conn.close()
        return jsonify({'error': 'No encontrado'}), 404

    new_state = 0 if row['is_active'] else 1
    conn.execute(
        "UPDATE urls SET is_active = ?, updated_at = datetime('now') WHERE short_id = ?",
        (new_state, short_id)
    )
    conn.commit()
    conn.close()
    return jsonify({'is_active': new_state})


# ─── EDITAR URL ──────────────────────────────────────────────────────────────

@bp.route('/editar', methods=['POST'])
@login_required
def editar_url():
    """Modifica la URL destino sin cambiar el short_id."""
    data = request.get_json()
    short_id = data.get('short_id')
    new_url  = data.get('new_url')

    if not short_id or not new_url:
        return jsonify({'error': 'Datos incompletos'}), 400

    conn = get_db_connection()
    conn.execute(
        "UPDATE urls SET original_url = ?, updated_at = datetime('now') WHERE short_id = ?",
        (new_url, short_id)
    )
    conn.commit()
    conn.close()
    return jsonify({'ok': True})


# ─── ELIMINAR URL ─────────────────────────────────────────────────────────────

@bp.route('/eliminar/<short_id>', methods=['DELETE'])
@login_required
def eliminar_url(short_id):
    """Elimina un enlace y todas sus visitas."""
    conn = get_db_connection()
    conn.execute("DELETE FROM visits WHERE short_id = ?", (short_id,))
    conn.execute("DELETE FROM urls WHERE short_id = ?", (short_id,))
    conn.commit()
    conn.close()
    return jsonify({'ok': True})


# ─── EXPORTAR EXCEL ──────────────────────────────────────────────────────────

@bp.route('/exportar-excel')
@login_required
def exportar_excel():
    """Exporta todas las visitas a un archivo Excel."""
    if not openpyxl:
        return "openpyxl no instalado", 500

    conn = get_db_connection()
    visitas = conn.execute('''
        SELECT v.timestamp, v.short_id, u.original_url,
               v.utm_source, v.utm_medium, v.utm_campaign,
               v.device_type, v.browser, v.ip_address, v.country
        FROM visits v
        LEFT JOIN urls u ON v.short_id = u.short_id
        ORDER BY v.timestamp DESC
    ''').fetchall()
    conn.close()

    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Visitas"

    headers = ['Fecha','Código','Destino','UTM Source','UTM Medium',
               'UTM Campaign','Dispositivo','Navegador','IP','País']
    ws.append(headers)

    for row in visitas:
        ws.append(list(row))

    output = io.BytesIO()
    wb.save(output)
    output.seek(0)

    return send_file(output,
        mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        as_attachment=True,
        download_name='url-tracker-visitas.xlsx'
    )


# ─── EXPORTAR CSV ────────────────────────────────────────────────────────────

@bp.route('/exportar-csv')
@login_required
def exportar_csv():
    """Exporta todas las visitas a un archivo CSV."""
    conn = get_db_connection()
    visitas = conn.execute('''
        SELECT v.timestamp, v.short_id, u.original_url,
               v.utm_source, v.utm_medium, v.utm_campaign,
               v.device_type, v.browser, v.ip_address, v.country
        FROM visits v
        LEFT JOIN urls u ON v.short_id = u.short_id
        ORDER BY v.timestamp DESC
    ''').fetchall()
    conn.close()

    def generate():
        headers = 'Fecha,Código,Destino,UTM Source,UTM Medium,UTM Campaign,Dispositivo,Navegador,IP,País\n'
        yield headers
        for row in visitas:
            yield ','.join(str(v or '') for v in row) + '\n'

    return Response(generate(),
        mimetype='text/csv',
        headers={'Content-Disposition': 'attachment; filename=url-tracker-visitas.csv'}
    )
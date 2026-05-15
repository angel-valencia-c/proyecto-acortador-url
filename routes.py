from flask import Blueprint, request, redirect, jsonify, render_template, url_for, Response, send_file
import datetime
import string
import random
import sqlite3
import io
from database import get_db_connection

# Al inicio de routes.py — agrega estos imports
from auth import login_required, handle_login, handle_logout
try:
    import openpyxl
    from openpyxl.styles import Font, PatternFill, Alignment
except ImportError:
    openpyxl = None 

bp = Blueprint('main', __name__)

@bp.route('/login', methods=['GET', 'POST'])
def login():
    return handle_login()

@bp.route('/logout')
def logout():
    return handle_logout()


def generate_short_id(length=6):
    chars = string.ascii_letters + string.digits
    return ''.join(random.choice(chars) for _ in range(length))


@bp.route('/')
def home():
    return render_template('index.html')

@bp.route('/crear', methods=['POST'])
def crear_url():
    data = request.get_json()
    original_url = data.get('original_url')
    
    if not original_url:
        return jsonify({'error': 'URL requerida'}), 400
        
    short_id = generate_short_id()
    
    conn = get_db_connection()
    conn.execute("INSERT INTO urls (short_id, original_url) VALUES (?, ?)", (short_id, original_url))
    conn.commit()
    conn.close()
    
    return jsonify({'short_id': short_id})


@bp.route('/<short_id>')
def redireccionar(short_id):
    if short_id == 'favicon.ico':
        return "", 404

    conn = get_db_connection()
    url_row = conn.execute("SELECT original_url FROM urls WHERE short_id = ?", (short_id,)).fetchone()
    
    if url_row:
        original_url = url_row['original_url']
        
        utm_source = request.args.get('utm_source')
        utm_medium = request.args.get('utm_medium')
        utm_campaign = request.args.get('utm_campaign')
        
        conn.execute('''
            INSERT INTO visits (short_id, ip_address, user_agent, referer, utm_source, utm_medium, utm_campaign, timestamp)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (short_id, request.remote_addr, request.headers.get('User-Agent'), request.headers.get('Referer'), 
              utm_source, utm_medium, utm_campaign, datetime.datetime.now()))
        conn.commit()
        conn.close()
        
        if request.query_string:
            params = request.query_string.decode("utf-8")
            final_url = f"{original_url}?{params}" if "?" not in original_url else f"{original_url}&{params}"
            return redirect(final_url)
            
        return redirect(original_url)
        
    conn.close()
    return "<h1>404 - Enlace no encontrado</h1>", 404


@bp.route('/reportes')
@login_required
def ver_reportes():
    conn = get_db_connection()
    query = """
        SELECT v.*, u.original_url 
        FROM visits v 
        JOIN urls u ON v.short_id = u.short_id 
        ORDER BY v.id DESC
    """
    visitas = conn.execute(query).fetchall()
    conn.close()
    return render_template('dashboard.html', visitas=visitas)

@bp.route('/editar', methods=['POST'])
def editar_url():
    data = request.get_json()
    short_id = data.get('short_id')
    new_url = data.get('new_url')
    
    if not short_id or not new_url:
        return jsonify({'error': 'Faltan datos'}), 400
        
    conn = get_db_connection()
    conn.execute("UPDATE urls SET original_url = ? WHERE short_id = ?", (new_url, short_id))
    conn.commit()
    conn.close()
    
    return jsonify({'message': 'Actualizado correctamente'})

@bp.route('/eliminar/<short_id>', methods=['DELETE'])
def eliminar_url(short_id):
    conn = get_db_connection()
    conn.execute("DELETE FROM visits WHERE short_id = ?", (short_id,))
    conn.execute("DELETE FROM urls WHERE short_id = ?", (short_id,))
    conn.commit()
    conn.close()
    return jsonify({'message': 'Eliminado correctamente'})



@bp.route('/exportar-excel')
def exportar_excel():
    if not openpyxl:
        return "Error: La librería 'openpyxl' no está instalada. Ejecuta 'pip install openpyxl'", 500

    conn = get_db_connection()
    query = """
        SELECT v.timestamp, v.short_id, u.original_url, v.utm_source, v.utm_medium, 
               v.utm_campaign, v.ip_address, v.user_agent, v.country
        FROM visits v 
        JOIN urls u ON v.short_id = u.short_id 
        ORDER BY v.id DESC
    """
    visitas = conn.execute(query).fetchall()
    conn.close()

    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Trafico"


    header_fill = PatternFill(start_color="4F81BD", end_color="4F81BD", fill_type="solid")
    header_font = Font(bold=True, color="FFFFFF")
    
    headers = ['Fecha', 'ID Corto', 'URL Destino', 'Fuente', 'Medio', 'Campaña', 'IP', 'Navegador', 'País']
    
    
    for col_num, header_title in enumerate(headers, 1):
        cell = ws.cell(row=1, column=col_num, value=header_title)
        cell.fill = header_fill
        cell.font = header_font


    for row_num, visita in enumerate(visitas, 2):
        ws.cell(row=row_num, column=1, value=visita['timestamp'])
        ws.cell(row=row_num, column=2, value=visita['short_id'])
        ws.cell(row=row_num, column=3, value=visita['original_url'])
        ws.cell(row=row_num, column=4, value=visita['utm_source'] or '-')
        ws.cell(row=row_num, column=5, value=visita['utm_medium'] or '-')
        ws.cell(row=row_num, column=6, value=visita['utm_campaign'] or '-')
        ws.cell(row=row_num, column=7, value=visita['ip_address'])
        ws.cell(row=row_num, column=8, value=visita['user_agent'])
       
        country = visita['country'] if 'country' in visita.keys() else 'Desconocido'
        ws.cell(row=row_num, column=9, value=country or 'Desconocido')


    ws.column_dimensions['A'].width = 22 # Fecha
    ws.column_dimensions['C'].width = 35 # URL
    ws.column_dimensions['H'].width = 25 # User Agent

  
    output = io.BytesIO()
    wb.save(output)
    output.seek(0)

    return send_file(
        output,
        mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        as_attachment=True,
        download_name='reporte_trafico.xlsx'
    )
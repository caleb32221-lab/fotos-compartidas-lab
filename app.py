import os
# Importamos todo lo necesario para Flask, Sesiones, Archivos y Rutas
from flask import Flask, render_template, request, redirect, url_for, session, send_from_directory
from werkzeug.utils import secure_filename 

# 1. Inicializa y Configura
# Usamos la inicialización simple para compatibilidad con el servidor Gunicorn
app = Flask(__name__) 
app.secret_key = 'TU_CLAVE_SECRETA_SUPER_LARGA_AQUI' 

# Configuración de Archivos
ACCESO_CODE = "MI-CLAVE-SECRETA-2025" 
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'pdf', 'mp4', 'doc', 'docx'}

# Crea la carpeta 'uploads' si no existe
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def allowed_file(filename):
    """Verifica si la extensión del archivo está en el conjunto de permitidas."""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# ----------------------------------------------------------------------
#                             RUTAS DE LA WEB
# ----------------------------------------------------------------------

# --- RUTA 1: Inicio (Verificación de Código) ---
# CORRECCIÓN FINAL: Usamos un array para asegurar que la ruta raíz sea accesible en Render
@app.route('/', methods=['GET', 'POST'])
def index():
    if session.get('autenticado'):
        return redirect(url_for('upload_page'))

    if request.method == 'POST':
        user_code = request.form.get('codigo')

        if user_code == ACCESO_CODE:
            session['autenticado'] = True
            return redirect(url_for('upload_page'))
        else:
            return render_template('index.html', error='Código incorrecto.')

    return render_template('index.html')


# --- RUTA 2: Página de Subida/Listado (Protegida) ---
@app.route('/upload')
def upload_page():
    if not session.get('autenticado'):
        return redirect(url_for('index'))

    try:
        files = os.listdir(app.config['UPLOAD_FOLDER'])
    except FileNotFoundError:
        files = []

    return render_template('upload.html', files=files)


# --- RUTA 3: Subir Archivo ---
@app.route('/upload_file', methods=['POST'])
def upload_file():
    if not session.get('autenticado'):
        return redirect(url_for('index'))

    if 'file' not in request.files:
        return redirect(url_for('upload_page'))

    file = request.files['file']

    if file.filename == '':
        return redirect(url_for('upload_page'))

    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        return redirect(url_for('upload_page'))

    return "Tipo de archivo no permitido", 400


# --- RUTA 4: Descarga de Archivos ---
@app.route('/downloads/<filename>')
def download_file(filename):
    if not session.get('autenticado'):
        return redirect(url_for('index'))

    return send_from_directory(
        app.config['UPLOAD_FOLDER'],
        filename,
        as_attachment=True
    )


# --- RUTA 5: Cerrar Sesión ---
@app.route('/logout')
def logout():
    session.pop('autenticado', None)
    return redirect(url_for('index'))


# EL BLOQUE DE INICIO LOCAL DEBE ESTAR ELIMINADO PARA COMPATIBILIDAD CON RENDER
# if __name__ == '__main__':
#     app.run(debug=True)

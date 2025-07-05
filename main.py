from flask import Flask, render_template, request, redirect, session, url_for, flash, jsonify
from supabase_client import supabase
from datetime import datetime
import os
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash, check_password_hash
from dotenv import load_dotenv
import uuid
import pandas as pd
import matplotlib.pyplot as plt
import base64
from io import BytesIO
from functools import wraps

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY")

# Datos para filtros y selects
PROYECTOS = ["Proyecto A", "Proyecto B", "Proyecto C", "Proyecto D", "Proyecto E", "Proyecto F", "Proyecto G", "Proyecto H", "Proyecto I", "Proyecto J"]
AREAS = ["Finanzas", "TI", "Logística", "Marketing"]
DIVISIONES = ["División Norte", "División Sur", "División Centro", "División Andina", "División Global"]
URGENCIAS = ["alta", "media", "baja"]
ROLES = ["Admin", "Analista SC", "Solicitante"]

# Decoradores para control de acceso
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Debes iniciar sesión para acceder a esta página.', 'error')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

def role_required(allowed_roles):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if 'user_id' not in session:
                flash('Debes iniciar sesión para acceder a esta página.', 'error')
                return redirect(url_for('login'))
            
            user_role = session.get('user_role')
            if user_role not in allowed_roles:
                return render_template('error_permisos.html', 
                                     required_roles=allowed_roles, 
                                     user_role=user_role)
            return f(*args, **kwargs)
        return decorated_function
    return decorator

def get_current_user():
    """Obtiene la información del usuario actual"""
    if 'user_id' not in session:
        return None
    
    user = supabase.table("usuarios").select("*").eq("id", session['user_id']).single().execute()
    return user.data if user.data else None

@app.route("/")
def home():
    return redirect(url_for("login"))

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        
        try:
            # Buscar usuario en la base de datos
            user_response = supabase.table("usuarios").select("*").eq("username", username).single().execute()
            
            if user_response.data and check_password_hash(user_response.data['password_hash'], password):
                user = user_response.data
                session['user_id'] = user['id']
                session['user_role'] = user['rol']
                session['username'] = user['username']
                session['user_email'] = user['email']
                
                flash(f'Bienvenido, {user["username"]}!', 'success')
                return redirect(url_for("lista_tickets"))
            else:
                flash('Usuario o contraseña incorrectos.', 'error')
        except Exception as e:
            flash('Error en el login. Intenta nuevamente.', 'error')
            print(f"Error de login: {str(e)}")
    
    return render_template("login.html")

@app.route("/logout")
def logout():
    session.clear()
    flash('Has cerrado sesión exitosamente.', 'info')
    return redirect(url_for("login"))

@app.route("/registro", methods=["GET", "POST"])
@role_required(["Admin"])
def registro():
    if request.method == "POST":
        username = request.form["username"]
        email = request.form["email"]
        password = request.form["password"]
        rol = request.form["rol"]
        
        # Validar que el usuario no exista
        existing_user = supabase.table("usuarios").select("*").eq("username", username).execute()
        if existing_user.data:
            flash('El usuario ya existe.', 'error')
            return render_template("registro.html", roles=ROLES)
        
        # Validar que el email no exista
        existing_email = supabase.table("usuarios").select("*").eq("email", email).execute()
        if existing_email.data:
            flash('El email ya está registrado.', 'error')
            return render_template("registro.html", roles=ROLES)
        
        # Crear usuario
        user_data = {
            "id": str(uuid.uuid4()),
            "username": username,
            "email": email,
            "password_hash": generate_password_hash(password),
            "rol": rol,
            "fecha_creacion": datetime.utcnow().isoformat(),
            "activo": True
        }
        
        try:
            supabase.table("usuarios").insert(user_data).execute()
            flash(f'Usuario {username} creado exitosamente con rol {rol}.', 'success')
            return redirect(url_for("gestion_usuarios"))
        except Exception as e:
            flash('Error al crear el usuario.', 'error')
            print(f"Error al crear usuario: {str(e)}")
    
    return render_template("registro.html", roles=ROLES)

@app.route("/gestion_usuarios")
@role_required(["Admin"])
def gestion_usuarios():
    try:
        usuarios = supabase.table("usuarios").select("*").order("fecha_creacion", desc=True).execute().data
        return render_template("gestionUsuario.html", usuarios=usuarios, roles=ROLES)
    except Exception as e:
        flash('Error al cargar los usuarios.', 'error')
        return redirect(url_for("lista_tickets"))

@app.route("/actualizar_rol", methods=["POST"])
@role_required(["Admin"])
def actualizar_rol():
    user_id = request.form["user_id"]
    nuevo_rol = request.form["nuevo_rol"]
    
    try:
        supabase.table("usuarios").update({"rol": nuevo_rol}).eq("id", user_id).execute()
        flash('Rol actualizado exitosamente.', 'success')
    except Exception as e:
        flash('Error al actualizar el rol.', 'error')
        print(f"Error al actualizar rol: {str(e)}")
    
    return redirect(url_for("gestion_usuarios"))

@app.route("/listaTickets")
@login_required
def lista_tickets():
    current_user = get_current_user()
    if not current_user:
        return redirect(url_for("login"))
    
    query = supabase.table("tickets").select("*").eq("completado", False)
    
    # Filtrar por usuario si es Solicitante
    if current_user['rol'] == 'Solicitante':
        query = query.eq("usuario_id", current_user['id'])
    
    # Aplicar filtros de búsqueda
    proyecto = request.args.get("proyecto")
    area = request.args.get("area")
    division = request.args.get("division")
    urgencia = request.args.get("urgencia")

    if proyecto:
        query = query.eq("proyecto", proyecto)
    if area:
        query = query.eq("area", area)
    if division:
        query = query.eq("division", division)
    if urgencia:
        query = query.eq("urgencia", urgencia)

    tickets = query.order("fecha_creacion", desc=True).execute().data
    
    return render_template(
        "listaTickets.html",
        tickets=tickets,
        proyectos=PROYECTOS,
        areas=AREAS,
        divisiones=DIVISIONES,
        urgencias=URGENCIAS,
        current_user=current_user
    )

@app.route("/nuevoTicket", methods=["GET", "POST"])
@login_required
def nuevo_ticket():
    current_user = get_current_user()
    if not current_user:
        return redirect(url_for("login"))
    
    if request.method == "POST":
        ticket_id = str(uuid.uuid4())
        data = {
            "id": ticket_id,
            "tipo_solicitud": request.form["tipo_solicitud"],
            "nombre_solicitante": request.form.get("nombre_solicitante", current_user['username']),
            "comprador_asignado": request.form.get("comprador_asignado", ""),
            "fecha_creacion": datetime.utcnow().strftime("%Y-%m-%d"),
            "urgencia": request.form["urgencia"],
            "proyecto": request.form["proyecto"],
            "area": request.form["area"],
            "division": request.form["division"],
            "comentario_inicial": request.form["comentario_inicial"],
            "completado": False,
            "usuario_id": current_user['id']
        }

        try:
            # Insertar ticket en la base de datos
            result = supabase.table("tickets").insert(data).execute()
            print(f"Ticket insertado: {result}")
            
            # Manejo de archivos
            for tipo in ["cotizaciones", "ordenes_compra", "otros_archivos"]:
                archivos = request.files.getlist(tipo)
                for archivo in archivos:
                    if archivo.filename:
                        nombre_archivo = secure_filename(archivo.filename)
                        path = f"{tipo}/{ticket_id}/{nombre_archivo}"
                        file_data = archivo.read()
                        supabase.storage.from_("archivos").upload(
                            path,
                            file_data,
                            file_options={"content-type": archivo.content_type}
                        )
                        supabase.table("archivos_ticket").insert({
                            "ticket_id": ticket_id,
                            "tipo_archivo": tipo,
                            "url": path
                        }).execute()
                        archivo.seek(0)

            flash('Ticket creado exitosamente.', 'success')
            return redirect(url_for("lista_tickets"))
        except Exception as e:
            flash('Error al crear el ticket.', 'error')
            print(f"Error al crear ticket: {str(e)}")
            print(f"Datos del ticket: {data}")
            import traceback
            traceback.print_exc()

    return render_template("nuevoTicket.html", 
                         proyectos=PROYECTOS, 
                         areas=AREAS, 
                         divisiones=DIVISIONES,
                         current_user=current_user)

@app.route("/detalleTicket/<ticket_id>")
@login_required
def detalle_ticket(ticket_id):
    current_user = get_current_user()
    if not current_user:
        return redirect(url_for("login"))
    
    try:
        ticket = supabase.table("tickets").select("*").eq("id", ticket_id).single().execute().data
        
        # Verificar permisos: Solicitantes solo pueden ver sus propios tickets
        if current_user['rol'] == 'Solicitante' and ticket['usuario_id'] != current_user['id']:
            return render_template('error_permisos.html', 
                                 required_roles=["Admin", "Analista SC"], 
                                 user_role=current_user['rol'])
        
        archivos = supabase.table("archivos_ticket").select("*").eq("ticket_id", ticket_id).execute().data
        supabase_url = os.getenv("SUPABASE_URL")
        
        return render_template("detalleTicket.html", 
                             ticket=ticket, 
                             archivos=archivos, 
                             supabase_url=supabase_url,
                             current_user=current_user)
    except Exception as e:
        flash('Error al cargar el ticket.', 'error')
        return redirect(url_for("lista_tickets"))

@app.route("/marcar_completado/<ticket_id>", methods=["POST"])
@role_required(["Admin", "Analista SC"])
def marcar_completado(ticket_id):
    try:
        supabase.table("tickets").update({"completado": True}).eq("id", ticket_id).execute()
        flash('Ticket marcado como completado.', 'success')
    except Exception as e:
        flash('Error al marcar el ticket como completado.', 'error')
        print(f"Error al completar ticket: {str(e)}")
    
    return redirect(url_for("lista_tickets"))

@app.route("/completedTickets")
@role_required(["Admin", "Analista SC"])
def completed_tickets():
    try:
        tickets = supabase.table("tickets").select("*").eq("completado", True).order("fecha_creacion", desc=True).execute().data
        return render_template("completedTickets.html", tickets=tickets)
    except Exception as e:
        flash('Error al cargar los tickets completados.', 'error')
        return redirect(url_for("lista_tickets"))

@app.route("/dashboard")
@role_required(["Admin"])
def dashboard():
    try:
        # Configurar matplotlib para no mostrar ventanas
        import matplotlib
        matplotlib.use('Agg')
        import matplotlib.pyplot as plt
        import seaborn as sns
        
        # Configurar el estilo moderno con seaborn
        sns.set_style("whitegrid")
        plt.rcParams['font.size'] = 10
        plt.rcParams['axes.labelsize'] = 12
        plt.rcParams['axes.titlesize'] = 14
        plt.rcParams['xtick.labelsize'] = 10
        plt.rcParams['ytick.labelsize'] = 10
        
        # Obtener todos los tickets
        tickets = supabase.table("tickets").select("*").execute().data
        
        # Gráfico 1: Tickets abiertos vs completados
        completados = sum(1 for ticket in tickets if ticket.get('completado', False))
        abiertos = len(tickets) - completados
        
        # Crear figura con fondo personalizado y mejor espaciado
        fig = plt.figure(figsize=(16, 8))
        fig.patch.set_facecolor('#f8fafc')
        
        # Gráfico circular - Estado de tickets con más espaciado
        ax1 = plt.subplot(1, 2, 1)
        # Posición del gráfico de torta con mejor margen izquierdo
        ax1.set_position([0.08, 0.1, 0.32, 0.8])
        
        estados = ['Abiertos', 'Completados']
        cantidades = [abiertos, completados]
        
        # Colores más modernos y vibrantes
        colores = ['#667eea', '#51cf66']
        explode = (0.05, 0.05)  # Separar ligeramente las secciones
        
        wedges, texts, autotexts = ax1.pie(cantidades, labels=estados, colors=colores, 
                                          autopct='%1.1f%%', startangle=90, explode=explode,
                                          shadow=True, textprops={'fontsize': 11, 'fontweight': 'bold'})
        
        # Mejorar el aspecto del texto
        for autotext in autotexts:
            autotext.set_color('white')
            autotext.set_fontsize(12)
            autotext.set_fontweight('bold')
            
        for text in texts:
            text.set_fontsize(12)
            text.set_fontweight('bold')
            text.set_color('#2d3748')
        
        ax1.set_title('Estado de Tickets', fontsize=16, fontweight='bold', 
                     color='#2d3748', pad=20)
        
        # Gráfico 2: Tickets por área con espaciado mejorado
        areas_count = {}
        for ticket in tickets:
            area = ticket.get('area', 'Sin área')
            areas_count[area] = areas_count.get(area, 0) + 1
        
        ax2 = plt.subplot(1, 2, 2)
        # Posición del gráfico de barras con mejor espaciado entre gráficos
        ax2.set_position([0.60, 0.1, 0.35, 0.8])
        
        if areas_count:
            areas = list(areas_count.keys())
            cantidades_areas = list(areas_count.values())
            
            # Gradiente de colores moderno
            colores_areas = ['#667eea', '#764ba2', '#f093fb', '#f5576c', '#4facfe', '#00f2fe']
            
            # Crear barras con bordes redondeados
            bars = ax2.bar(areas, cantidades_areas, color=colores_areas[:len(areas)], 
                          edgecolor='white', linewidth=2, alpha=0.8)
            
            # Agregar sombra a las barras
            for bar in bars:
                bar.set_linewidth(2)
                bar.set_edgecolor('#ffffff')
                
            # Personalizar el gráfico
            ax2.set_title('Tickets por Área', fontsize=16, fontweight='bold', 
                         color='#2d3748', pad=20)
            ax2.set_xlabel('Área', fontsize=12, fontweight='bold', color='#2d3748')
            ax2.set_ylabel('Cantidad', fontsize=12, fontweight='bold', color='#2d3748')
            
            # Rotar etiquetas del eje x
            plt.setp(ax2.get_xticklabels(), rotation=45, ha='right', fontsize=10, 
                    fontweight='bold', color='#2d3748')
            plt.setp(ax2.get_yticklabels(), fontsize=10, fontweight='bold', color='#2d3748')
            
            # Agregar valores en las barras con mejor diseño
            for i, (bar, cantidad) in enumerate(zip(bars, cantidades_areas)):
                height = bar.get_height()
                ax2.text(bar.get_x() + bar.get_width()/2., height + 0.1,
                        f'{int(cantidad)}',
                        ha='center', va='bottom', fontsize=11, fontweight='bold',
                        color='#2d3748',
                        bbox=dict(boxstyle="round,pad=0.3", facecolor='white', 
                                alpha=0.8, edgecolor='none'))
            
            # Personalizar la cuadrícula
            ax2.grid(True, alpha=0.3, linestyle='--', linewidth=0.5)
            ax2.set_axisbelow(True)
            
            # Mejorar el fondo del gráfico
            ax2.set_facecolor('#f8fafc')
        
        # Ajustar layout con espaciado personalizado
        # No usar tight_layout ya que tenemos posiciones manuales
        
        # Convertir a base64 con mejor calidad
        img = BytesIO()
        plt.savefig(img, format='png', bbox_inches='tight', facecolor='#f8fafc', 
                   dpi=200, edgecolor='none', pad_inches=0.3)
        img.seek(0)
        grafico_base64 = base64.b64encode(img.getvalue()).decode()
        plt.close(fig)
        
        # Estadísticas adicionales
        stats = {
            'total_tickets': len(tickets),
            'tickets_abiertos': abiertos,
            'tickets_completados': completados,
            'areas_count': areas_count,
            'urgencias_count': {}
        }
        
        # Contar por urgencia
        for ticket in tickets:
            urgencia = ticket.get('urgencia', 'Sin urgencia')
            stats['urgencias_count'][urgencia] = stats['urgencias_count'].get(urgencia, 0) + 1
        
        return render_template("dashboard.html", 
                             grafico=grafico_base64, 
                             stats=stats)
    except Exception as e:
        flash('Error al cargar el dashboard.', 'error')
        print(f"Error en dashboard: {str(e)}")
        import traceback
        traceback.print_exc()
        return redirect(url_for("lista_tickets"))

if __name__ == "__main__":
    app.run(debug=True, port=5002)
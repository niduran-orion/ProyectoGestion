from flask import Flask, render_template, request, redirect, session, url_for
from supabase_client import supabase
from datetime import datetime
import os
from werkzeug.utils import secure_filename
from dotenv import load_dotenv
import uuid
import pandas as pd
import matplotlib.pyplot as plt
import base64
from io import BytesIO


load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY")

# Datos para filtros y selects
PROYECTOS = ["Proyecto A", "Proyecto B", "Proyecto C", "Proyecto D", "Proyecto E", "Proyecto F", "Proyecto G", "Proyecto H", "Proyecto I", "Proyecto J"]
AREAS = ["Finanzas", "TI", "Logística", "Marketing"]
DIVISIONES = ["División Norte", "División Sur", "División Centro", "División Andina", "División Global"]
URGENCIAS = ["alta", "media", "baja"]


@app.route("/")
def home():
    return redirect(url_for("login"))


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]
        try:
            res = supabase.auth.sign_in_with_password({"email": email, "password": password})
            if res.user:
                session["user"] = res.user.id
                return redirect(url_for("lista_tickets"))
            else:
                return render_template("login.html", error="Login failed")
        except Exception as e:
            return render_template("login.html", error=str(e))
    return render_template("login.html")


@app.route("/listaTickets")
def lista_tickets():
    query = supabase.table("tickets").select("*").eq("completado", False)

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
        urgencias=URGENCIAS
    )


@app.route("/nuevoTicket", methods=["GET", "POST"])
def nuevo_ticket():
    if request.method == "POST":
        ticket_id = str(uuid.uuid4())
        data = {
            "id": ticket_id,
            "tipo_solicitud": request.form["tipo_solicitud"],
            "nombre_solicitante": request.form["nombre_solicitante"],
            "comprador_asignado": request.form["comprador_asignado"],
            "fecha_creacion": datetime.utcnow().strftime("%Y-%m-%d"),
            "urgencia": request.form["urgencia"],
            "proyecto": request.form["proyecto"],
            "area": request.form["area"],
            "division": request.form["division"],
            "comentario_inicial": request.form["comentario_inicial"],
            "completado": False
        }

        supabase.table("tickets").insert(data).execute()

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

        return redirect(url_for("lista_tickets"))

    return render_template("nuevoTicket.html", proyectos=PROYECTOS, areas=AREAS, divisiones=DIVISIONES)


@app.route("/detalleTicket/<ticket_id>")
def detalle_ticket(ticket_id):
    ticket = supabase.table("tickets").select("*").eq("id", ticket_id).single().execute().data
    archivos = supabase.table("archivos_ticket").select("*").eq("ticket_id", ticket_id).execute().data
    supabase_url = os.getenv("SUPABASE_URL") 
    return render_template("detalleTicket.html", ticket=ticket, archivos=archivos, supabase_url=supabase_url)



@app.route("/completedTickets")
def completed_tickets():
    tickets = supabase.table("tickets").select("*").eq("completado", True).order("fecha_creacion", desc=True).execute().data
    return render_template("completedTickets.html", tickets=tickets)


@app.route("/completarTicket/<ticket_id>", methods=["POST"])
def completar_ticket(ticket_id):
    supabase.table("tickets").update({"completado": True}).eq("id", ticket_id).execute()
    return redirect(url_for("lista_tickets"))


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))


if __name__ == "__main__":
    app.run(debug=True)

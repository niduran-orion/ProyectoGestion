from supabase_client import supabase
from datetime import datetime

sample_tickets = [
    {
        "tipo_solicitud": "Compra equipo",
        "nombre_solicitante": "Ana Pérez",
        "comprador_asignado": "Carlos Gómez",
        "fecha_creacion": "2024-06-01T00:00:00",
        "urgencia": "alta"
    },
    {
        "tipo_solicitud": "Reembolso",
        "nombre_solicitante": "Luis Fernández",
        "comprador_asignado": "Sofía Ramírez",
        "fecha_creacion": "2024-06-02T00:00:00",
        "urgencia": "media"
    },
    {
        "tipo_solicitud": "Compra suministros",
        "nombre_solicitante": "Camila Soto",
        "comprador_asignado": "Carlos Gómez",
        "fecha_creacion": "2024-06-03T00:00:00",
        "urgencia": "baja"
    }
]

for ticket in sample_tickets:
    supabase.table("tickets").insert(ticket).execute()

print("Dummy data inserted!")

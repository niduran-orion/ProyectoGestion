#!/usr/bin/env python3
"""
Script para corregir la estructura de la base de datos
"""

from supabase_client import supabase
from werkzeug.security import generate_password_hash
import uuid
from datetime import datetime

def create_complete_database():
    """Crea la estructura completa de la base de datos"""
    
    print("🔧 Creando estructura completa de la base de datos...")
    
    # SQL para crear todas las tablas necesarias
    sql_commands = """
-- Crear tabla usuarios
CREATE TABLE IF NOT EXISTS usuarios (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    rol VARCHAR(20) NOT NULL CHECK (rol IN ('Admin', 'Analista SC', 'Solicitante')),
    fecha_creacion TIMESTAMP DEFAULT NOW(),
    activo BOOLEAN DEFAULT TRUE
);

-- Crear tabla tickets con todas las columnas necesarias
CREATE TABLE IF NOT EXISTS tickets (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tipo_solicitud VARCHAR(100) NOT NULL,
    nombre_solicitante VARCHAR(100) NOT NULL,
    comprador_asignado VARCHAR(100),
    fecha_creacion DATE NOT NULL,
    urgencia VARCHAR(20) NOT NULL CHECK (urgencia IN ('alta', 'media', 'baja')),
    proyecto VARCHAR(100) NOT NULL,
    area VARCHAR(100) NOT NULL,
    division VARCHAR(100) NOT NULL,
    comentario_inicial TEXT,
    completado BOOLEAN DEFAULT FALSE,
    usuario_id UUID REFERENCES usuarios(id),
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Crear tabla archivos_ticket
CREATE TABLE IF NOT EXISTS archivos_ticket (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    ticket_id UUID REFERENCES tickets(id) ON DELETE CASCADE,
    tipo_archivo VARCHAR(50) NOT NULL,
    url TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Crear función para ejecutar SQL
CREATE OR REPLACE FUNCTION public.execute_sql(sql text)
RETURNS void AS $$
BEGIN
    EXECUTE sql;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Crear índices para mejor rendimiento
CREATE INDEX IF NOT EXISTS idx_tickets_usuario_id ON tickets(usuario_id);
CREATE INDEX IF NOT EXISTS idx_tickets_completado ON tickets(completado);
CREATE INDEX IF NOT EXISTS idx_tickets_fecha_creacion ON tickets(fecha_creacion);
CREATE INDEX IF NOT EXISTS idx_archivos_ticket_ticket_id ON archivos_ticket(ticket_id);
"""
    
    print("📋 SQL que se ejecutará:")
    print("=" * 60)
    print(sql_commands)
    print("=" * 60)
    
    try:
        # Ejecutar los comandos SQL
        supabase.rpc('execute_sql', {'sql': sql_commands}).execute()
        print("✅ Base de datos creada exitosamente")
        
        # Crear usuario administrador
        create_admin_user()
        
        print("\n🎉 Configuración completada!")
        print("🔑 Credenciales de admin:")
        print("   Usuario: admin")
        print("   Contraseña: admin123")
        
    except Exception as e:
        print(f"❌ Error al crear la base de datos: {str(e)}")
        print("\n📝 Si hay errores, ejecuta este SQL manualmente en Supabase Dashboard:")
        print(sql_commands)

def create_admin_user():
    """Crea un usuario administrador por defecto"""
    
    admin_data = {
        "id": str(uuid.uuid4()),
        "username": "admin",
        "email": "admin@proyectogestion.com",
        "password_hash": generate_password_hash("admin123"),
        "rol": "Admin",
        "fecha_creacion": datetime.utcnow().isoformat(),
        "activo": True
    }
    
    try:
        # Verificar si ya existe el usuario admin
        existing_admin = supabase.table("usuarios").select("*").eq("username", "admin").execute()
        
        if not existing_admin.data:
            supabase.table("usuarios").insert(admin_data).execute()
            print("✅ Usuario administrador creado")
        else:
            print("ℹ️  Usuario administrador ya existe")
            
    except Exception as e:
        print(f"❌ Error al crear usuario administrador: {str(e)}")

def check_database_structure():
    """Verifica la estructura actual de la base de datos"""
    
    print("🔍 Verificando estructura de la base de datos...")
    
    try:
        # Intentar insertar un ticket de prueba para ver qué columnas faltan
        test_data = {
            "id": str(uuid.uuid4()),
            "tipo_solicitud": "test",
            "nombre_solicitante": "test",
            "comprador_asignado": "test",
            "fecha_creacion": "2025-01-01",
            "urgencia": "baja",
            "proyecto": "test",
            "area": "test",
            "division": "test",
            "comentario_inicial": "test",
            "completado": False,
            "usuario_id": "test"
        }
        
        # Esto debería fallar y mostrar qué columnas faltan
        result = supabase.table("tickets").insert(test_data).execute()
        print("✅ Tabla tickets tiene la estructura correcta")
        
        # Limpiar el registro de prueba
        supabase.table("tickets").delete().eq("id", test_data["id"]).execute()
        
    except Exception as e:
        print(f"❌ Error en la estructura: {str(e)}")
        return False
    
    return True

if __name__ == "__main__":
    print("🚀 Iniciando corrección de la base de datos...")
    
    # Primero verificar la estructura actual
    if not check_database_structure():
        print("\n🔧 Creando estructura completa...")
        create_complete_database()
    else:
        print("✅ La base de datos ya tiene la estructura correcta")
        create_admin_user()

from supabase_client import supabase
from werkzeug.security import generate_password_hash
import uuid
from datetime import datetime

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
            print("✅ Usuario administrador creado:")
            print("   Usuario: admin")
            print("   Contraseña: admin123")
            print("   ⚠️  Cambia la contraseña después del primer login")
        else:
            print("ℹ️  Usuario administrador ya existe")
            
    except Exception as e:
        print(f"❌ Error al crear usuario administrador: {str(e)}")

def setup_database():
    """Configura la base de datos y crea el usuario admin"""
    
    print("🔧 Configuración de base de datos")
    print("📋 Para crear las tablas, ejecuta este SQL en tu Supabase Dashboard:")
    print("=" * 60)
    
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

-- Agregar campo usuario_id a tabla tickets (si la tabla tickets existe)
ALTER TABLE tickets 
ADD COLUMN IF NOT EXISTS usuario_id UUID REFERENCES usuarios(id);

-- Función para ejecutar SQL (opcional, para futuras operaciones)
CREATE OR REPLACE FUNCTION public.execute_sql(sql text)
RETURNS void AS $$
BEGIN
    EXECUTE sql;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;
"""
    
    print(sql_commands)
    print("=" * 60)
    print("\n📌 Pasos:")
    print("1. Ve a tu Supabase Dashboard")
    print("2. Abre el SQL Editor")
    print("3. Copia y pega el SQL de arriba")
    print("4. Ejecuta la consulta")
    print("5. Luego ejecuta este script nuevamente")
    
    # Intentar crear el usuario admin (solo funcionará si las tablas ya existen)
    print("\n🔄 Intentando crear usuario administrador...")
    try:
        create_admin_user()
    except Exception as e:
        print(f"❌ No se pudo crear el usuario admin: {str(e)}")
        print("📝 Ejecuta primero el SQL en Supabase Dashboard")

if __name__ == "__main__":
    setup_database()


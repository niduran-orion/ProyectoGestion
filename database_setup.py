from supabase_client import supabase
from werkzeug.security import generate_password_hash
import uuid
from datetime import datetime

def create_tables():
    """Crea las tablas necesarias en Supabase"""
    
    # Crear tabla usuarios
    create_usuarios_table = """
    CREATE TABLE IF NOT EXISTS usuarios (
        id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
        username VARCHAR(50) UNIQUE NOT NULL,
        email VARCHAR(100) UNIQUE NOT NULL,
        password_hash VARCHAR(255) NOT NULL,
        rol VARCHAR(20) NOT NULL CHECK (rol IN ('Admin', 'Analista SC', 'Solicitante')),
        fecha_creacion TIMESTAMP DEFAULT NOW(),
        activo BOOLEAN DEFAULT TRUE
    );
    """
    
    # Agregar campo usuario_id a tabla tickets
    add_usuario_id_to_tickets = """
    ALTER TABLE tickets 
    ADD COLUMN IF NOT EXISTS usuario_id UUID REFERENCES usuarios(id);
    """
    
    try:
        # Ejecutar las consultas SQL
        supabase.rpc('execute_sql', {'sql': create_usuarios_table}).execute()
        supabase.rpc('execute_sql', {'sql': add_usuario_id_to_tickets}).execute()
        
        print("✅ Tablas creadas exitosamente")
        
        # Crear usuario administrador por defecto
        create_admin_user()
        
    except Exception as e:
        print(f"❌ Error al crear tablas: {str(e)}")

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

if __name__ == "__main__":
    create_tables()
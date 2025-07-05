#!/usr/bin/env python3
"""
Script para crear la tabla tickets con la estructura correcta
"""

from supabase_client import supabase

def create_tickets_table():
    """Crea la tabla tickets con todas las columnas necesarias"""
    
    print("🔧 Creando tabla tickets...")
    
    # SQL para crear la tabla tickets
    create_table_sql = """
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
        usuario_id UUID,
        created_at TIMESTAMP DEFAULT NOW(),
        updated_at TIMESTAMP DEFAULT NOW()
    );
    """
    
    print("📋 SQL que se ejecutará:")
    print("=" * 60)
    print(create_table_sql)
    print("=" * 60)
    
    try:
        # Intentar crear la tabla usando una consulta SQL directa
        result = supabase.rpc('execute_sql', {'sql': create_table_sql}).execute()
        print("✅ Tabla tickets creada exitosamente")
        return True
        
    except Exception as e:
        print(f"❌ Error al crear tabla con RPC: {str(e)}")
        print("\n📝 Ejecuta este SQL manualmente en Supabase Dashboard:")
        print(create_table_sql)
        return False

def test_ticket_insertion():
    """Prueba insertar un ticket de prueba"""
    
    print("\n🧪 Probando inserción de ticket...")
    
    test_data = {
        'tipo_solicitud': 'Cotización',
        'nombre_solicitante': 'Usuario Test',
        'comprador_asignado': 'Comprador Test',
        'fecha_creacion': '2025-01-01',
        'urgencia': 'baja',
        'proyecto': 'Proyecto Test',
        'area': 'TI',
        'division': 'Centro',
        'comentario_inicial': 'Comentario de prueba',
        'completado': False
    }
    
    try:
        result = supabase.table('tickets').insert(test_data).execute()
        print("✅ Ticket de prueba insertado exitosamente")
        print(f"ID del ticket: {result.data[0]['id']}")
        
        # Eliminar el ticket de prueba
        supabase.table('tickets').delete().eq('id', result.data[0]['id']).execute()
        print("🧹 Ticket de prueba eliminado")
        return True
        
    except Exception as e:
        print(f"❌ Error al insertar ticket de prueba: {str(e)}")
        return False

if __name__ == "__main__":
    print("🚀 Iniciando creación de tabla tickets...")
    
    if create_tickets_table():
        test_ticket_insertion()
    else:
        print("\n⚠️  No se pudo crear la tabla automáticamente.")
        print("📝 Por favor, ejecuta el SQL manualmente en Supabase Dashboard.")

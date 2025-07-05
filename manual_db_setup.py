#!/usr/bin/env python3
"""
Información para crear manualmente la tabla tickets en Supabase
"""

print("🔧 CONFIGURACIÓN MANUAL DE LA BASE DE DATOS")
print("=" * 60)
print()
print("📋 Copia y pega este SQL en tu Supabase Dashboard > SQL Editor:")
print()

sql_command = """
-- Crear tabla tickets con todas las columnas necesarias
DROP TABLE IF EXISTS tickets CASCADE;

CREATE TABLE tickets (
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

-- Crear tabla archivos_ticket
CREATE TABLE IF NOT EXISTS archivos_ticket (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    ticket_id UUID REFERENCES tickets(id) ON DELETE CASCADE,
    tipo_archivo VARCHAR(50) NOT NULL,
    url TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Crear índices para mejor rendimiento
CREATE INDEX IF NOT EXISTS idx_tickets_usuario_id ON tickets(usuario_id);
CREATE INDEX IF NOT EXISTS idx_tickets_completado ON tickets(completado);
CREATE INDEX IF NOT EXISTS idx_tickets_fecha_creacion ON tickets(fecha_creacion);
CREATE INDEX IF NOT EXISTS idx_archivos_ticket_ticket_id ON archivos_ticket(ticket_id);
"""

print(sql_command)
print("=" * 60)
print()
print("📌 PASOS:")
print("1. Ve a tu Supabase Dashboard")
print("2. Abre el SQL Editor")
print("3. Copia y pega el SQL de arriba")
print("4. Ejecuta la consulta")
print("5. Verifica que las tablas se crearon correctamente")
print()
print("⚠️  NOTA: Este SQL eliminará la tabla tickets existente y creará una nueva.")
print("   Si tienes datos importantes, haz un respaldo primero.")
print()
print("✅ Una vez ejecutado el SQL, podrás crear tickets normalmente.")

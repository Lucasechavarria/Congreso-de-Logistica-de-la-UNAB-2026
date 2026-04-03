import sqlite3
import os

def generate_dynamic_migration():
    if not os.path.exists('db.sqlite3'):
        print("Error: No se encuentra db.sqlite3")
        return

    conn = sqlite3.connect('db.sqlite3')
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()

    # Obtener todas las tablas
    cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%';")
    all_tables = [t['name'] for t in cur.fetchall()]

    # Orden Jerárquico Manual Estricto para resolver dependencias REFERENCES
    ordered_list = [
        # Nivel 0: Tablas raíz de Django y Edición
        'django_content_type',
        'auth_group',
        'auth_user',
        'api_edicion',
        'django_migrations',
        'django_session',
        
        # Nivel 1: Tablas que dependen del Nivel 0
        'auth_permission',
        'auth_group_permissions',
        'auth_user_groups',
        'auth_user_user_permissions',
        'django_admin_log',
        
        # Nivel 2: Tablas de la App que dependen de Edicion/User
        'api_disertante',
        'api_inscripcionprensa',
        'api_empresa',
        'api_postulaciondisertante',
        
        # Nivel 3: Tablas que dependen de Disertante/Empresa/Prensa
        'api_asistente',
        'api_programa',
        
        # Nivel 4: Tablas que dependen de Asistente o son intermedias M2M
        'api_programa_disertantes',
        'api_inscripcion',
        'api_certificado',
        'api_miembrogrupo',
        'api_detallegrupo',
        'api_detalledocente',
        'api_detalleestudiante',
        'api_detalleprofesional',
        'api_dashboard', # Si existe
    ]

    # Agregar tablas que no estén en la lista manual (por si acaso)
    for t in all_tables:
        if t not in ordered_list:
            ordered_list.append(t)

    sql_output = "migrate_full_supabase.sql"
    processed_count = 0

    with open(sql_output, 'w', encoding='utf-8') as f:
        f.write("-- REGENERACIÓN JERÁRQUICA DE ESQUEMA Y DATOS (V4 FINAL)\n")
        f.write("SET session_replication_role = 'replica';\n\n")

        # Primero todos los DROPS en reversa para no tener problemas al limpiar
        for table in reversed(ordered_list):
            if table in all_tables:
                f.write(f"DROP TABLE IF EXISTS {table} CASCADE;\n")
        f.write("\n")

        for table in ordered_list:
            if table not in all_tables: continue
            
            print(f"Migrando {table}...")
            cur.execute(f"SELECT sql FROM sqlite_master WHERE name='{table}'")
            res = cur.fetchone()
            if not res or not res['sql']: continue
            
            # Traducción de DDL
            sqlite_sql = res['sql']
            pg_sql = sqlite_sql.replace('AUTOINCREMENT', '')
            pg_sql = pg_sql.replace('unsigned', '')
            pg_sql = pg_sql.replace('datetime', 'TIMESTAMP')
            pg_sql = pg_sql.replace('varchar', 'VARCHAR')
            pg_sql = pg_sql.replace('bool', 'BOOLEAN')
            pg_sql = pg_sql.replace('real', 'DOUBLE PRECISION')
            pg_sql = pg_sql.replace('"', '')
            
            # Corregir JSON: PostgreSQL usa JSONB, y no existe JSON_VALID
            import re
            # Reemplazar tipo json por JSONB (en minúsculas o mayúsculas)
            pg_sql = re.sub(r'\bjson\b', 'JSONB', pg_sql, flags=re.IGNORECASE)
            # Eliminar la restricción CHECK de JSON_VALID completa
            pg_sql = re.sub(r'CHECK\s*\(\(JSON_VALID\(.*?\)\s*OR\s*.*?IS NULL\)\)', '', pg_sql, flags=re.IGNORECASE)
            # Eliminar comas residuales si el CHECK era lo último antes del cierre de paréntesis
            pg_sql = pg_sql.replace(', );', ');')
            pg_sql = pg_sql.replace(',)', ')')
            
            # Corregir longitudes (como el DNI que a veces viene con basura)
            pg_sql = pg_sql.replace('VARCHAR(8)', 'VARCHAR(20)')
            
            if 'INTEGER PRIMARY KEY' in pg_sql.upper():
                pg_sql = pg_sql.replace('INTEGER PRIMARY KEY', 'SERIAL PRIMARY KEY')
            elif 'PRIMARY KEY' in pg_sql.upper() and 'id SERIAL' not in pg_sql:
                pg_sql = pg_sql.replace('id INTEGER NOT NULL PRIMARY KEY', 'id SERIAL PRIMARY KEY')
                pg_sql = pg_sql.replace('id INTEGER PRIMARY KEY', 'id SERIAL PRIMARY KEY')

            f.write(f"-- Estructura para {table}\n")
            f.write(pg_sql + ";\n\n")

            # Detectar booleanos para conversión
            cur.execute(f"PRAGMA table_info({table})")
            columns_info = cur.fetchall()
            bool_cols = []
            for col in columns_info:
                name = col['name']
                t_type = col['type'].upper()
                if 'BOOL' in t_type or name.startswith('is_') or name in ['activa', 'acepta_tyc', 'asistencia_confirmada', 'terminos_aceptados']:
                    bool_cols.append(name)

            # Insertar Datos
            cur.execute(f"SELECT * FROM {table}")
            rows = cur.fetchall()
            if rows:
                cols = rows[0].keys()
                chunk_size = 50
                for i in range(0, len(rows), chunk_size):
                    # Usar slice explícito (i:i+chunk_size)
                    chunk = rows[i : i + chunk_size]
                    f.write(f"INSERT INTO {table} ({', '.join(cols)}) VALUES\n")
                    vals = []
                    for row in chunk:
                        row_vals = []
                        for c in cols:
                            v = row[c]
                            if v is None: row_vals.append("NULL")
                            elif c in bool_cols:
                                row_vals.append("TRUE" if v in [1, '1', True, 'true', 't'] else "FALSE")
                            elif isinstance(v, (int, float)): row_vals.append(str(v))
                            else:
                                escaped_val = str(v).replace("'", "''")
                                row_vals.append(f"'{escaped_val}'")
                        vals.append(f"({', '.join(row_vals)})")
                    f.write(",\n".join(vals) + ";\n")
                f.write("\n")
            
            processed_count += 1

        f.write("SET session_replication_role = 'origin';\n\n")
        f.write("-- Sincronización de secuencias\n")
        for table in ordered_list:
            if table not in all_tables: continue
            cur.execute(f"PRAGMA table_info({table})")
            if any(c['name'] == 'id' for c in cur.fetchall()):
                f.write(f"SELECT setval(pg_get_serial_sequence('{table}', 'id'), COALESCE(MAX(id), 1)) FROM {table};\n")

    print(f"\n¡Listo! Generadas {processed_count} tablas en el orden correcto.")
    conn.close()

if __name__ == "__main__":
    generate_dynamic_migration()

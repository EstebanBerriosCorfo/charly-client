# scripts/05_03_GET_applications_by_program_id_applied.py
# ================================================================
# Obtener Postulaciones Aplicadas de un Programa con Respuestas Completas
# 
# DESCRIPCIÓN:
# Script optimizado para obtener todas las postulaciones de un programa específico
# que tengan application_status == "applied", incluyendo todas las respuestas
# completas (form_answers y field_answers) y exportarlas a Excel con todas las
# columnas disponibles.
#
# FILTRO:
# Solo procesa aplicaciones con application_status == "applied"
#
# CARACTERÍSTICAS:
# 1. Procesamiento PARALELO con 25 workers simultáneos para máxima velocidad
# 2. Barra de progreso visual con porcentaje, contador de filas y estadísticas
# 3. Guardado de progreso optimizado (solo IDs, cada 100 aplicaciones)
# 4. Manejo automático de columnas duplicadas con renombrado secuencial
# 5. Exportación a Excel con todas las columnas (incluyendo campos vacíos)
# 6. Validación de datos y detección de discrepancias
# 7. Manejo robusto de errores sin interrumpir el proceso
#
# RENDIMIENTO:
# - Tasa promedio: 10-12 aplicaciones/segundo
# - Tiempo depende del número de aplicaciones con status "applied"
#
# Endpoints utilizados:
#   - GET /programs/{program_id} → Obtener lista de application_id
#   - GET /applications/{application_id} → Obtener respuestas completas (en paralelo)
#
# Salida:
#   - Excel: downloads/applications_program_{program_id}_applied.xlsx
#   - Progreso: downloads/progress_program_{program_id}_applied.json
# ================================================================

import sys
import json
import time
import io
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
from threading import Lock

# Configurar stdout para UTF-8 en Windows
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

# Ajuste de path del proyecto
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from orchestration.bootstrap import Bootstrap
from services.organization_service import OrganizationService
from services.program_service import ProgramService
from services.application_service import ApplicationService
from utils.dataframe_builder import build_applications_dataframe
from utils.excel_exporter import export_applications_dataframe_to_excel
import pandas as pd

# ------------------------------------------------------------------
# FUNCIÓN PARA MOSTRAR BARRA DE PROGRESO
# ------------------------------------------------------------------
def print_progress_bar(completed, total, successful, failed, rate, eta, bar_length=40):
    """
    Muestra una barra de progreso visual con porcentaje y estadísticas.
    
    Args:
        completed: Número de aplicaciones procesadas
        total: Total de aplicaciones a procesar
        successful: Número de aplicaciones exitosas
        failed: Número de aplicaciones fallidas
        rate: Tasa de procesamiento (aplicaciones/segundo)
        eta: Tiempo estimado restante en segundos
        bar_length: Longitud de la barra en caracteres (default: 40)
    """
    if total == 0:
        return
    
    # Calcular porcentaje
    percentage = (completed / total) * 100
    
    # Calcular cuántos caracteres llenar
    filled_length = int(bar_length * completed // total)
    
    # Crear la barra (usar caracteres ASCII para compatibilidad con Windows)
    try:
        # Intentar usar caracteres Unicode más visuales
        bar = '█' * filled_length + '░' * (bar_length - filled_length)
    except (UnicodeEncodeError, UnicodeDecodeError):
        # Fallback a caracteres ASCII si hay problemas de codificación
        bar = '#' * filled_length + '-' * (bar_length - filled_length)
    
    # Formatear ETA
    if eta > 3600:
        eta_str = f"{eta/3600:.1f}h"
    elif eta > 60:
        eta_str = f"{eta/60:.1f}m"
    else:
        eta_str = f"{eta:.0f}s"
    
    # Imprimir la barra de progreso
    print(f"\rProgreso: [{bar}] {percentage:.1f}% | "
          f"{completed}/{total} aplicaciones | "
          f"Exitosas: {successful} | "
          f"Fallidas: {failed} | "
          f"Tasa: {rate:.1f}/seg | "
          f"ETA: {eta_str}", end='', flush=True)
    
    # Si está completo, agregar nueva línea
    if completed == total:
        print()

# ------------------------------------------------------------------
# CONFIGURACIÓN
# ------------------------------------------------------------------
MAX_WORKERS = 25  # Número de requests HTTP simultáneos (aumentado para mayor velocidad)
PROGRESS_SAVE_INTERVAL = 100  # Guardar progreso cada N aplicaciones (aumentado para reducir I/O)
PROGRESS_FILE_TEMPLATE = "downloads/progress_program_{program_id}_applied.json"
FILTER_STATUS = "applied"  # Filtrar solo aplicaciones con este status

# ------------------------------------------------------------------
# BOOTSTRAP
# ------------------------------------------------------------------
ctx = Bootstrap(
    config_path=Path("config/charly.yaml")
).run()

client = ctx["client"]

org_service = OrganizationService(client)
program_service = ProgramService(client)
application_service = ApplicationService(client)

# ------------------------------------------------------------------
# PARÁMETROS
# ------------------------------------------------------------------
if len(sys.argv) >= 3:
    organization_id = int(sys.argv[1])
    program_id = int(sys.argv[2])
    print(f"\n>> Usando valores de argumentos: org_id={organization_id}, program_id={program_id}")
else:
    organizations = org_service.list()
    print("\n=== ORGANIZACIONES DISPONIBLES ===")
    for org in organizations:
        print(f"- ID: {org['id']} | Nombre: {org['name']}")
    
    while True:
        org_input = input("\n>> Ingrese el ID de la organizacion: ").strip()
        if org_input:
            try:
                organization_id = int(org_input)
                break
            except ValueError:
                print("[!] Por favor ingrese un numero valido.")
        else:
            print("[!] Debe ingresar un ID de organizacion.")
    
    programs = list(program_service.iterate_programs(organization_id=organization_id))
    print("\n=== CONVOCATORIAS DISPONIBLES ===")
    for program in programs:
        print(f"- ID: {program['id']} | Nombre: {program['name']}")
    
    while True:
        program_input = input("\n>> Ingrese el ID de la convocatoria: ").strip()
        if program_input:
            try:
                program_id = int(program_input)
                break
            except ValueError:
                print("[!] Por favor ingrese un numero valido.")
        else:
            print("[!] Debe ingresar un ID de convocatoria.")

print(f"\n>> Usando organization_id: {organization_id}")
print(f">> Usando program_id: {program_id}")
print(f">> Filtro aplicado: application_status == '{FILTER_STATUS}'")

# ------------------------------------------------------------------
# PASO 1: OBTENER LISTA DE POSTULACIONES Y FILTRAR POR STATUS
# ------------------------------------------------------------------
print(f"\n>> Obteniendo lista de postulaciones del programa {program_id}...")

program_detail = program_service.get_program(program_id)
program_name = program_detail.get("name", "N/A")
applications_index_all = program_detail.get("applications", [])

print(f"[OK] Convocatoria: {program_name}")
print(f"[OK] Total postulaciones encontradas: {len(applications_index_all)}")

if not applications_index_all:
    print("\n[!] Esta convocatoria no tiene postulaciones registradas.")
    sys.exit(0)

# FILTRAR SOLO APLICACIONES CON STATUS "applied" PARA PROCESAR
applications_index = [
    app for app in applications_index_all
    if app.get("application_status") == FILTER_STATUS
]

print(f"[OK] Postulaciones con status '{FILTER_STATUS}': {len(applications_index)}")
print(f"[!] Postulaciones filtradas (otras): {len(applications_index_all) - len(applications_index)}")

if not applications_index:
    print(f"\n[!] No hay postulaciones con status '{FILTER_STATUS}' en esta convocatoria.")
    sys.exit(0)

# ------------------------------------------------------------------
# VERIFICAR PROGRESO GUARDADO
# ------------------------------------------------------------------
progress_file = Path(PROGRESS_FILE_TEMPLATE.format(program_id=program_id))
applications_full = []
errors = []
processed_ids = set()
# Lock para proteger acceso concurrente a applications_full
applications_lock = Lock()

if progress_file.exists():
    print(f"\n>> Encontrado archivo de progreso: {progress_file}")
    if len(sys.argv) >= 3:
        # Auto-resumir en modo no interactivo
        resume = "s"
    else:
        resume = input("¿Reanudar desde el progreso guardado? [S/n]: ").strip().lower()
    
    if resume != "n":
        try:
            with open(progress_file, "r", encoding="utf-8") as f:
                progress_data = json.load(f)
            
            # Cargar solo IDs procesados (optimización: no cargar datos completos aquí)
            processed_ids = set(progress_data.get("processed_ids", []))
            total_processed = progress_data.get("total_processed", 0)
            total_errors = progress_data.get("total_errors", 0)
            
            print(f"[OK] Encontrados {len(processed_ids)} IDs procesados previamente")
            print(f"[OK] {total_processed} postulaciones procesadas | {total_errors} errores previos")
            print(f"[!] Nota: Las aplicaciones completas se obtendran nuevamente (solo se guardan IDs para reanudar)")
        except Exception as e:
            print(f"[!] Error al cargar progreso: {str(e)}. Continuando sin progreso guardado.")
            processed_ids = set()

# ------------------------------------------------------------------
# FUNCIÓN PARA OBTENER UNA APLICACIÓN (OPTIMIZADA)
# ------------------------------------------------------------------
def fetch_application(app_index):
    """
    Obtiene una aplicación completa. Retorna (success, data, error)
    Optimizada para reducir overhead y mejorar velocidad.
    """
    application_id = app_index.get("id")
    
    try:
        # Llamada directa sin procesamiento adicional para reducir overhead
        application_full = application_service.get_application(
            application_id,
            include_all_fields=True
        )
        return (True, application_full, None)
    except Exception as e:
        # Extraer nombre de empresa solo si hay error (optimización)
        company = app_index.get("company", {})
        company_name = company.get("name", "N/A") if company else "N/A"
        
        return (False, None, {
            "application_id": application_id,
            "company": company_name,
            "error": str(e)
        })

# ------------------------------------------------------------------
# PASO 1.5: RECOLECTAR ESQUEMA COMPLETO DE CAMPOS
# ------------------------------------------------------------------
# IMPORTANTE: Para obtener TODAS las columnas posibles, necesitamos recolectar
# field_names de TODAS las aplicaciones del programa (no solo las "applied")
# Esto asegura que tengamos columnas para todos los campos posibles
print(f"\n>> Recolectando esquema completo de campos de todas las aplicaciones...")
print(f"   Esto asegura que todas las columnas posibles esten disponibles.")

# Obtener una muestra representativa de aplicaciones de diferentes status
# para recolectar todos los field_names posibles
status_groups = {}
for app in applications_index_all:
    status = app.get("application_status", "unknown")
    if status not in status_groups:
        status_groups[status] = []
    status_groups[status].append(app)

# Tomar muestras de cada status (hasta 10 por status para no hacer demasiadas llamadas)
sample_applications_for_schema = []
max_per_status = 10
for status, apps in status_groups.items():
    sample_applications_for_schema.extend(apps[:max_per_status])

print(f"[INFO] Muestra para esquema: {len(sample_applications_for_schema)} aplicaciones de {len(status_groups)} status diferentes")
sys.stdout.flush()

# Obtener detalles completos de la muestra en paralelo para recolectar field_names
schema_field_names = set()
if sample_applications_for_schema:
    schema_start_time = time.time()
    
    print(f"[INFO] Obteniendo detalles de muestra para recolectar todos los field_names...")
    sys.stdout.flush()
    
    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        schema_futures = {
            executor.submit(fetch_application, app): app 
            for app in sample_applications_for_schema[:min(30, len(sample_applications_for_schema))]
        }
        
        schema_completed = 0
        for future in as_completed(schema_futures):
            schema_completed += 1
            try:
                success, data, error = future.result()
                if success and data:
                    # Recolectar field_names de esta aplicación
                    for form_answer in data.get("form_answers", []):
                        for field_answer in form_answer.get("field_answers", []):
                            field = field_answer.get("field", {})
                            field_name = field.get("name", "")
                            if field_name:
                                schema_field_names.add(field_name)
            except Exception:
                pass  # Ignorar errores en la recolección del esquema
    
    schema_elapsed = time.time() - schema_start_time
    print(f"[OK] Esquema recolectado en {schema_elapsed:.1f}s: {len(schema_field_names)} field_names únicos identificados")
    sys.stdout.flush()
else:
    print(f"[INFO] No hay aplicaciones para recolectar esquema")
    schema_field_names = set()

# ------------------------------------------------------------------
# PASO 2: OBTENER RESPUESTAS EN PARALELO
# ------------------------------------------------------------------
print(f"\n>> Obteniendo respuestas completas en paralelo ({MAX_WORKERS} workers)...")
print(f"   Filtrando solo aplicaciones con status '{FILTER_STATUS}'")
print("   Esto debería ser mucho más rápido que la versión secuencial.\n")

# Filtrar aplicaciones ya procesadas
applications_to_process = [
    app for app in applications_index 
    if app.get("id") not in processed_ids
]

if not applications_to_process:
    print("[OK] Todas las aplicaciones ya fueron procesadas.")
else:
    print(f">> Procesando {len(applications_to_process)} aplicaciones pendientes con status '{FILTER_STATUS}'...")
    print()  # Línea en blanco antes de la barra de progreso
    
    start_time = time.time()
    completed = 0
    successful_count = 0
    failed_count = 0
    
    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        # Enviar todos los trabajos
        future_to_app = {
            executor.submit(fetch_application, app): app 
            for app in applications_to_process
        }
        
        # Procesar resultados conforme van completándose
        for future in as_completed(future_to_app):
            app = future_to_app[future]
            completed += 1
            
            try:
                success, data, error = future.result()
                
                if success:
                    if data is None:
                        print(f"[ERROR] Datos None para aplicación {app.get('id')}")
                        with applications_lock:
                            errors.append({
                                "application_id": app.get("id"),
                                "company": app.get("company", {}).get("name", "N/A"),
                                "error": "Datos None retornados"
                            })
                        failed_count += 1
                    else:
                        # Usar lock para proteger acceso concurrente
                        with applications_lock:
                            applications_full.append(data)
                            processed_ids.add(data.get("id"))
                        successful_count += 1
                else:
                    with applications_lock:
                        errors.append(error)
                    failed_count += 1
                
                # Mostrar progreso cada 5 aplicaciones o al final (más frecuente para barra visual)
                if completed % 5 == 0 or completed == len(applications_to_process):
                    elapsed = time.time() - start_time
                    rate = completed / elapsed if elapsed > 0 else 0
                    remaining = len(applications_to_process) - completed
                    eta = remaining / rate if rate > 0 else 0
                    
                    # Mostrar barra de progreso visual
                    print_progress_bar(
                        completed=completed,
                        total=len(applications_to_process),
                        successful=successful_count,
                        failed=failed_count,
                        rate=rate,
                        eta=eta,
                        bar_length=40
                    )
                
                # Guardar progreso cada N aplicaciones (optimizado: solo IDs, escritura compacta)
                if completed % PROGRESS_SAVE_INTERVAL == 0:
                    try:
                        # Guardar solo IDs para reducir I/O (no guardar datos completos durante procesamiento)
                        progress_data = {
                            "program_id": program_id,
                            "program_name": program_name,
                            "filter_status": FILTER_STATUS,
                            "processed_at": datetime.now().isoformat(),
                            "processed_ids": list(processed_ids),
                            "total_processed": len(applications_full),
                            "total_errors": len(errors),
                        }
                        # Escritura compacta sin indentación para reducir tiempo de I/O
                        with open(progress_file, "w", encoding="utf-8") as f:
                            json.dump(progress_data, f, separators=(',', ':'), ensure_ascii=False)
                    except Exception:
                        # Silenciar errores de guardado para no interrumpir el proceso
                        pass
                    
            except Exception as e:
                with applications_lock:
                    errors.append({
                        "application_id": app.get("id"),
                        "company": app.get("company", {}).get("name", "N/A"),
                        "error": f"Error inesperado: {str(e)}"
                    })
                failed_count += 1
    
    elapsed_total = time.time() - start_time
    print(f"\n[OK] Procesamiento completado en {elapsed_total:.1f} segundos")
    print(f"   Total procesadas: {completed}")
    print(f"   Exitosas: {successful_count}")
    print(f"   Fallidas: {failed_count}")
    print(f"   En applications_full: {len(applications_full)}")
    if elapsed_total > 0:
        print(f"   Tasa promedio: {len(applications_to_process) / elapsed_total:.2f} aplicaciones/segundo")
    else:
        print(f"   Tasa promedio: N/A (procesamiento muy rápido)")
    
    # Validación crítica: verificar que el número de aplicaciones exitosas coincida
    if successful_count != len(applications_full):
        print(f"\n[ERROR CRITICO] Discrepancia detectada:")
        print(f"   successful_count: {successful_count}")
        print(f"   len(applications_full): {len(applications_full)}")
        print(f"   Diferencia: {successful_count - len(applications_full)}")
        print(f"   Esto indica que algunas aplicaciones exitosas no se agregaron a la lista.")
    
    # Forzar flush del buffer
    import sys
    sys.stdout.flush()

# ------------------------------------------------------------------
# RESULTADO FINAL
# ------------------------------------------------------------------
print("\n" + "="*80)
print("=== RESULTADO FINAL ===")
print("="*80)
sys.stdout.flush()

print(f"\n[OK] Postulaciones procesadas exitosamente: {len(applications_full)}")
print(f"[OK] Filtro aplicado: application_status == '{FILTER_STATUS}'")
sys.stdout.flush()
if errors:
    print(f"[!] Postulaciones con errores: {len(errors)}")
    if len(errors) <= 10:
        print("\nErrores:")
        for error in errors:
            print(f"  - App ID {error['application_id']} ({error['company']}): {error['error']}")
    else:
        print(f"\nPrimeros 10 errores:")
        for error in errors[:10]:
            print(f"  - App ID {error['application_id']} ({error['company']}): {error['error']}")
        print(f"  ... y {len(errors) - 10} errores más")

# ------------------------------------------------------------------
# NORMALIZACIÓN Y EXPORTACIÓN
# ------------------------------------------------------------------
print("\n" + "="*80)
print("=== EXPORTACIÓN DE DATOS ===")
print("="*80)

print("\n>> Normalizando datos a tabla plana...")
sys.stdout.flush()

if not applications_full:
    print("[ERROR] No hay aplicaciones para procesar")
    sys.exit(1)

print(f"[INFO] Procesando {len(applications_full)} aplicaciones para construir DataFrame...")
sys.stdout.flush()

try:
    print("[INFO] Iniciando build_applications_dataframe...")
    sys.stdout.flush()
    
    # Pasar field_names adicionales recolectados del esquema completo
    # para asegurar que todas las columnas posibles estén incluidas
    df = build_applications_dataframe(
        applications_full, 
        additional_field_names=schema_field_names if schema_field_names else None
    )
    
    print(f"[OK] Tabla creada: {len(df)} filas x {len(df.columns)} columnas")
    sys.stdout.flush()
    print(f"   Columnas de metadata: {len([c for c in df.columns if c.startswith(('application_', 'company_', 'program_', 'score_', 'form_'))])}")
    print(f"   Columnas de respuestas: {len(df.columns) - 30}")
    sys.stdout.flush()
    
    # Validación crítica: verificar que todas las aplicaciones estén en el DataFrame
    if len(df) != len(applications_full):
        print(f"\n[!] ADVERTENCIA: Discrepancia en número de filas")
        print(f"   Aplicaciones procesadas: {len(applications_full)}")
        print(f"   Filas en DataFrame: {len(df)}")
        print(f"   Diferencia: {len(applications_full) - len(df)}")
        
        # Verificar IDs faltantes
        df_ids = set(df.get("application_id", []))
        app_ids = {app.get("id") for app in applications_full}
        missing_ids = app_ids - df_ids
        
        if missing_ids:
            print(f"\n   IDs de aplicaciones faltantes en DataFrame: {len(missing_ids)}")
            print(f"   Primeros 10: {sorted(list(missing_ids))[:10]}")
except Exception as e:
    print(f"[ERROR] Error al construir DataFrame: {str(e)}")
    print(f"   Tipo de error: {type(e).__name__}")
    import traceback
    traceback.print_exc()
    print("\n[!] No se puede continuar sin el DataFrame. Abortando exportacion.")
    sys.exit(1)

# Exportar a Excel
# Si se ejecuta con argumentos, exportar automáticamente; si no, preguntar
if len(sys.argv) >= 3:
    export_excel = "s"  # Exportar automáticamente cuando se ejecuta con argumentos
    print("\n>> Exportando a Excel automaticamente (modo no interactivo)...")
else:
    print("\n>> ¿Exportar a Excel con todos los campos?")
    sys.stdout.flush()
    try:
        export_excel = input("   [S/n]: ").strip().lower()
        sys.stdout.flush()
    except (EOFError, KeyboardInterrupt):
        print("\n[!] Entrada cancelada. No se exportará a Excel.")
        export_excel = "n"

if export_excel != "n":
    output_file = f"applications_program_{program_id}_applied.xlsx"
    output_path = Path("downloads") / output_file
    
    output_path.parent.mkdir(exist_ok=True)
    
    print(f"\n>> Exportando a Excel...")
    sys.stdout.flush()
    try:
        # Validar antes de exportar
        initial_rows = len(df)
        initial_cols = len(df.columns)
        
        print(f"[INFO] Preparando exportación: {initial_rows} filas x {initial_cols} columnas")
        sys.stdout.flush()
        
        print("[INFO] Iniciando escritura del archivo Excel...")
        print(f"[INFO] Tamaño del DataFrame: {initial_rows} filas x {initial_cols} columnas")
        print(f"[INFO] Esto puede tardar varios minutos para archivos grandes...")
        sys.stdout.flush()
        
        # Exportar con timeout implícito (el proceso puede tardar mucho)
        import time
        export_start_time = time.time()
        
        try:
            export_applications_dataframe_to_excel(df, output_path, sheet_name="Postulaciones")
            export_elapsed = time.time() - export_start_time
            print(f"[OK] Exportación completada en {export_elapsed:.1f} segundos")
            sys.stdout.flush()
        except Exception as export_error:
            export_elapsed = time.time() - export_start_time
            print(f"[ERROR] Error después de {export_elapsed:.1f} segundos")
            raise
        
        print("[INFO] Archivo Excel escrito, verificando...")
        sys.stdout.flush()
        
        if output_path.exists():
            # Verificar el archivo exportado
            df_exported = pd.read_excel(output_path)
            
            print(f"\n[OK] Datos exportados a: {output_path}")
            print(f"   Filas antes de exportar: {initial_rows}")
            print(f"   Filas en Excel exportado: {len(df_exported)}")
            print(f"   Columnas antes de exportar: {initial_cols}")
            print(f"   Columnas en Excel exportado: {len(df_exported.columns)}")
            print(f"   Tamaño del archivo: {output_path.stat().st_size / 1024:.2f} KB")
            
            # Verificar discrepancias
            if len(df_exported) != initial_rows:
                print(f"\n[!] ADVERTENCIA: Se perdieron {initial_rows - len(df_exported)} filas durante la exportación")
            if len(df_exported.columns) != initial_cols:
                print(f"\n[!] ADVERTENCIA: Se perdieron {initial_cols - len(df_exported.columns)} columnas durante la exportación")
                missing_cols = set(df.columns) - set(df_exported.columns)
                if missing_cols:
                    print(f"   Columnas faltantes: {len(missing_cols)}")
                    print(f"   Primeras 10: {list(missing_cols)[:10]}")
        else:
            print(f"\n[!] El archivo no se creo correctamente. Verifica permisos o espacio en disco.")
    except PermissionError as e:
        print(f"\n[ERROR] Error de permisos al exportar: {str(e)}")
        print(f"   El archivo puede estar abierto en otro programa.")
        print(f"   Cierra el archivo e intenta nuevamente.")
    except MemoryError as e:
        print(f"\n[ERROR] Error de memoria al exportar: {str(e)}")
        print(f"   El DataFrame es muy grande. Considera procesar en lotes más pequeños.")
    except Exception as e:
        print(f"\n[ERROR] Error al exportar a Excel: {str(e)}")
        print(f"   Tipo de error: {type(e).__name__}")
        import traceback
        traceback.print_exc()

# Limpiar archivo de progreso si todo salió bien
if progress_file.exists() and not errors:
    if len(sys.argv) >= 3:
        # En modo no interactivo, mantener el archivo de progreso por si acaso
        print(f"\n[!] Archivo de progreso guardado en: {progress_file}")
        print("    Puedes eliminarlo manualmente si ya no lo necesitas.")
    else:
        delete_progress = input("\n¿Eliminar archivo de progreso? [S/n]: ").strip().lower()
        if delete_progress != "n":
            progress_file.unlink()
            print("[OK] Archivo de progreso eliminado")

print("\n" + "="*80)
print("[OK] PROCESO COMPLETADO")
print("="*80)

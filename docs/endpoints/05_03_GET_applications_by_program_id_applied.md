# Script: 05_03_GET_applications_by_program_id_applied

## Descripción

Script optimizado para obtener todas las postulaciones de un programa específico que tengan `application_status == "applied"`, incluyendo todas las respuestas completas (form_answers y field_answers) y exportarlas a Excel con todas las columnas disponibles.

Este script es una variante del script `05_02_applications_by_program_id.py` que aplica un filtro adicional para procesar únicamente las postulaciones que han sido aplicadas (enviadas).

---

## Características Principales

### Filtrado por Status
- **Filtro aplicado:** Solo procesa aplicaciones con `application_status == "applied"`
- Muestra estadísticas de aplicaciones filtradas vs totales
- Permite identificar rápidamente cuántas aplicaciones cumplen el criterio

### Procesamiento Optimizado
1. **Procesamiento PARALELO** con 25 workers simultáneos para máxima velocidad
2. **Barra de progreso visual** con porcentaje, contador de filas y estadísticas
3. **Guardado de progreso optimizado** (solo IDs, cada 100 aplicaciones)
4. **Manejo automático de columnas duplicadas** con renombrado secuencial
5. **Exportación a Excel** con todas las columnas (incluyendo campos vacíos)
6. **Validación de datos** y detección de discrepancias
7. **Manejo robusto de errores** sin interrumpir el proceso

### Rendimiento
- **Tasa promedio:** 10-12 aplicaciones/segundo
- **Tiempo:** Depende del número de aplicaciones con status "applied"
- **Mejora:** ~10-20x más rápido que procesamiento secuencial

---

## Uso

### Modo Interactivo

```bash
python scripts/05_03_applications_by_program_id_applied.py
```

El script solicitará:
1. ID de la organización
2. ID de la convocatoria (program)

### Modo No Interactivo (con argumentos)

```bash
python scripts/05_03_applications_by_program_id_applied.py <organization_id> <program_id>
```

**Ejemplo:**
```bash
python scripts/05_03_applications_by_program_id_applied.py 162 2429
```

---

## Endpoints Utilizados

- `GET /programs/{program_id}` → Obtener lista de application_id del programa
- `GET /applications/{application_id}` → Obtener respuestas completas (en paralelo)

---

## Proceso de Ejecución

### Paso 1: Obtener Lista de Postulaciones
1. Obtiene el detalle del programa especificado
2. Extrae todas las aplicaciones del programa
3. **Filtra solo las aplicaciones con `application_status == "applied"`**
4. Muestra estadísticas:
   - Total de postulaciones encontradas
   - Postulaciones con status "applied"
   - Postulaciones filtradas (otras)

### Paso 2: Verificar Progreso Guardado
- Busca archivo de progreso: `downloads/progress_program_{program_id}_applied.json`
- Si existe, permite reanudar desde donde se quedó
- Carga solo IDs procesados (optimización)

### Paso 3: Procesamiento Paralelo
- Procesa todas las aplicaciones filtradas en paralelo (25 workers)
- Muestra barra de progreso visual con:
  - Porcentaje de completado
  - Contador de aplicaciones procesadas
  - Estadísticas (exitosas/fallidas)
  - Tasa de procesamiento
  - Tiempo estimado restante (ETA)
- Guarda progreso cada 100 aplicaciones

### Paso 4: Construcción del DataFrame
- Normaliza datos a tabla plana usando `build_applications_dataframe`
- Crea columnas para todos los campos posibles
- Maneja automáticamente columnas duplicadas con renombrado secuencial
- Valida que todas las aplicaciones estén en el DataFrame

### Paso 5: Exportación a Excel
- Exporta a: `downloads/applications_program_{program_id}_applied.xlsx`
- Valida que todas las filas y columnas se exportaron correctamente
- Muestra estadísticas del archivo generado

---

## Archivos Generados

### Excel Exportado
- **Ubicación:** `downloads/applications_program_{program_id}_applied.xlsx`
- **Contenido:** Todas las postulaciones con status "applied" en formato tabla plana
- **Columnas:** Metadata + todas las respuestas de formularios (incluyendo campos vacíos)

### Archivo de Progreso
- **Ubicación:** `downloads/progress_program_{program_id}_applied.json`
- **Contenido:** IDs procesados, estadísticas de procesamiento
- **Propósito:** Permitir reanudar el procesamiento si se interrumpe

---

## Ejemplo de Salida

```
>> Obteniendo lista de postulaciones del programa 2429...
[OK] Convocatoria: Certificación de Proyecto I+D
[OK] Total postulaciones encontradas: 1343
[OK] Postulaciones con status 'applied': 450
[!] Postulaciones filtradas (otras): 893

>> Obteniendo respuestas completas en paralelo (25 workers)...
   Filtrando solo aplicaciones con status 'applied'

>> Procesando 450 aplicaciones pendientes con status 'applied'...

Progreso: [████████████████████░░░░░░░░░░░░░░░░] 50.0% | 225/450 aplicaciones | Exitosas: 223 | Fallidas: 2 | Tasa: 11.5/seg | ETA: 20s

[OK] Procesamiento completado en 39.2 segundos
   Total procesadas: 450
   Exitosas: 448
   Fallidas: 2
   En applications_full: 448

=== RESULTADO FINAL ===
[OK] Postulaciones procesadas exitosamente: 448
[OK] Filtro aplicado: application_status == 'applied'
```

---

## Parámetros de Configuración

```python
MAX_WORKERS = 25  # Número de requests HTTP simultáneos
PROGRESS_SAVE_INTERVAL = 100  # Guardar progreso cada N aplicaciones
FILTER_STATUS = "applied"  # Status a filtrar
```

---

## Diferencias con Script Base (05_02)

| Característica | 05_02 (Base) | 05_03 (Aplicado) |
|----------------|--------------|-------------------|
| **Filtro** | Todas las aplicaciones | Solo `application_status == "applied"` |
| **Archivo Excel** | `applications_program_{id}_full.xlsx` | `applications_program_{id}_applied.xlsx` |
| **Archivo Progreso** | `progress_program_{id}.json` | `progress_program_{id}_applied.json` |
| **Estadísticas** | Total de aplicaciones | Total + aplicaciones filtradas |
| **Uso** | Análisis completo | Análisis de aplicaciones enviadas |

---

## Validaciones y Manejo de Errores

### Validaciones Implementadas
- ✅ Verificación de discrepancias entre aplicaciones procesadas y DataFrame
- ✅ Detección de filas/columnas perdidas durante exportación
- ✅ Validación de datos None antes de agregar a lista
- ✅ Verificación de IDs faltantes en DataFrame

### Manejo de Errores
- **Errores de API:** Se capturan y registran sin interrumpir el proceso
- **Errores de DataFrame:** Se muestran con traceback completo
- **Errores de exportación:** Se manejan específicamente (PermissionError, MemoryError)
- **Errores de guardado:** Se silencian para no interrumpir el procesamiento

---

## Referencias

- **Script Base:** `scripts/05_02_applications_by_program_id.py`
- **Implementación:** `services/application_service.py` - Clase `ApplicationService`
- **Normalización:** `utils/dataframe_builder.py` - Función `build_applications_dataframe`
- **Exportación:** `utils/excel_exporter.py` - Función `export_applications_dataframe_to_excel`

---

## Notas Importantes

1. **Filtro de Status:** El filtro se aplica sobre la lista inicial de aplicaciones del programa. Solo se procesan las que tienen `application_status == "applied"`.

2. **Campos Vacíos:** El script intenta obtener todos los campos posibles usando `include_all_fields=True`, pero el endpoint solo retorna campos con valores. Para obtener todos los campos vacíos, se necesitaría el esquema completo del formulario.

3. **Columnas Duplicadas:** Si hay columnas con el mismo nombre después de la limpieza, se renombran automáticamente con números secuenciales (_2, _3, etc.) para asegurar que todas se incluyan.

4. **Reanudación:** El script puede reanudar desde donde se quedó si se interrumpe, usando el archivo de progreso.

5. **Modo No Interactivo:** Cuando se ejecuta con argumentos, exporta automáticamente a Excel sin preguntar.

---

## Casos de Uso

- **Análisis de postulaciones enviadas:** Obtener solo las aplicaciones que han sido enviadas para análisis específico
- **Reportes de aplicaciones completas:** Generar reportes Excel solo con aplicaciones aplicadas
- **Validación de datos enviados:** Verificar respuestas completas de aplicaciones aplicadas
- **Análisis comparativo:** Comparar aplicaciones aplicadas vs otras (usando ambos scripts)

---

## Requisitos

- Python 3.8+
- Dependencias del proyecto (ver `requirements.txt`)
- Acceso a la API de Charly.io con credenciales válidas
- Archivo de configuración: `config/charly.yaml`

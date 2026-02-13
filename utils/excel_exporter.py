# ================================================================
# Excel Exporter
# ================================================================

from pathlib import Path
import pandas as pd
from typing import Optional


def export_applications_dataframe_to_excel(
    df: pd.DataFrame,
    output_path: Path,
    sheet_name: str = "applications"
) -> Path:
    """
    Exporta el DataFrame a Excel con manejo robusto de errores.
    
    Maneja:
    - Nombres de columnas muy largos o con caracteres especiales
    - Valores complejos (listas, dicts)
    - Valores None/NaN
    - Errores de escritura
    """
    
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    try:
        # Limpiar nombres de columnas antes de exportar
        # Excel tiene límites: máximo 255 caracteres, algunos caracteres prohibidos
        MAX_COLUMN_LENGTH = 100
        PROBLEMATIC_CHARS = ['/', '\\', '?', '*', '[', ']', ':']
        
        cleaned_columns = {}
        for col in df.columns:
            cleaned_col = str(col)
            
            # Reemplazar caracteres problemáticos
            for char in PROBLEMATIC_CHARS:
                cleaned_col = cleaned_col.replace(char, '_')
            
            # Truncar si es muy largo
            if len(cleaned_col) > MAX_COLUMN_LENGTH:
                cleaned_col = cleaned_col[:MAX_COLUMN_LENGTH]
            
            # Asegurar unicidad
            original_cleaned = cleaned_col
            counter = 1
            while cleaned_col in cleaned_columns.values():
                cleaned_col = f"{original_cleaned}_{counter}"
                counter += 1
            
            cleaned_columns[col] = cleaned_col
        
        # Renombrar columnas
        df_cleaned = df.rename(columns=cleaned_columns)
        
        # Limpiar valores antes de exportar
        # Convertir valores complejos a strings (optimizado para DataFrames grandes)
        import json
        import sys
        
        # Solo limpiar si el DataFrame no es demasiado grande (evitar timeout)
        # Para DataFrames muy grandes, la limpieza puede ser muy lenta
        MAX_ROWS_FOR_CLEANING = 10000  # Límite conservador
        
        if len(df_cleaned) <= MAX_ROWS_FOR_CLEANING:
            print(f"[INFO] Limpiando valores complejos en {len(df_cleaned.columns)} columnas...", end="", flush=True)
            sys.stdout.flush()
            
            cols_processed = 0
            for col in df_cleaned.columns:
                cols_processed += 1
                if cols_processed % 50 == 0:
                    print(f".", end="", flush=True)
                    sys.stdout.flush()
                
                # Verificar si hay valores complejos (muestra más pequeña para velocidad)
                sample_size = min(5, len(df_cleaned))
                if sample_size > 0:
                    sample = df_cleaned[col].dropna().head(sample_size)
                    has_complex = any(isinstance(val, (list, dict)) for val in sample)
                    
                    if has_complex:
                        # Convertir solo valores complejos (más eficiente que aplicar a todos)
                        def clean_value(x):
                            if isinstance(x, (list, dict)):
                                try:
                                    return json.dumps(x, ensure_ascii=False)
                                except:
                                    return str(x)
                            return x
                        
                        # Aplicar solo si hay valores complejos
                        df_cleaned[col] = df_cleaned[col].apply(clean_value)
            
            print(" [OK]", flush=True)
            sys.stdout.flush()
        else:
            print(f"[INFO] DataFrame muy grande ({len(df_cleaned)} filas). Omitiendo limpieza de valores complejos para evitar timeout.")
            print(f"[INFO] Los valores complejos se convertirán automáticamente durante la escritura.")
            sys.stdout.flush()
        
        # Exportar con manejo de errores y logging
        print(f"[INFO] Escribiendo archivo Excel ({df_cleaned.shape[0]} filas x {df_cleaned.shape[1]} columnas)...", end="", flush=True)
        sys.stdout.flush()
        
        # Usar modo de escritura más eficiente para archivos grandes
        # openpyxl puede ser lento para archivos muy grandes, pero es más compatible
        try:
            # Limpiar timezones antes de escribir (compatible con todas las versiones de pandas)
            # Convertir columnas datetime a naive datetime si tienen timezone
            for col in df_cleaned.columns:
                if df_cleaned[col].dtype.name.startswith('datetime'):
                    if hasattr(df_cleaned[col].dtype, 'tz') and df_cleaned[col].dtype.tz is not None:
                        df_cleaned[col] = df_cleaned[col].dt.tz_localize(None)
            
            with pd.ExcelWriter(
                output_path, 
                engine="openpyxl"
            ) as writer:
                df_cleaned.to_excel(writer, index=False, sheet_name=sheet_name)
            print(" [OK]", flush=True)
            sys.stdout.flush()
        except Exception as e:
            print(f" [ERROR]", flush=True)
            sys.stdout.flush()
            raise
        
        return output_path
        
    except Exception as e:
        error_msg = f"Error al exportar a Excel: {str(e)}"
        error_type = type(e).__name__
        
        # Información adicional para debugging
        debug_info = {
            "error_type": error_type,
            "error_message": str(e),
            "dataframe_shape": df.shape,
            "column_count": len(df.columns),
            "output_path": str(output_path),
        }
        
        # Intentar identificar el problema específico
        if "PermissionError" in error_type or "Permission denied" in str(e):
            raise PermissionError(
                f"{error_msg}\n"
                f"El archivo puede estar abierto en otro programa. "
                f"Cierra el archivo e intenta nuevamente."
            )
        elif "MemoryError" in error_type:
            raise MemoryError(
                f"{error_msg}\n"
                f"El DataFrame es muy grande. "
                f"Considera procesar en lotes o reducir el número de columnas."
            )
        else:
            raise Exception(
                f"{error_msg}\n"
                f"Debug info: {debug_info}"
            )
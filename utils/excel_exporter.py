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
        # Convertir valores complejos a strings
        for col in df_cleaned.columns:
            # Verificar si hay valores complejos
            sample = df_cleaned[col].dropna().head(10)
            has_complex = any(isinstance(val, (list, dict)) for val in sample)
            
            if has_complex:
                import json
                df_cleaned[col] = df_cleaned[col].apply(
                    lambda x: json.dumps(x, ensure_ascii=False) if isinstance(x, (list, dict)) else x
                )
        
        # Exportar con manejo de errores
        with pd.ExcelWriter(output_path, engine="openpyxl") as writer:
            df_cleaned.to_excel(writer, index=False, sheet_name=sheet_name)
        
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
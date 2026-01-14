# ================================================================
# Script 05_01_02_applications_dataframe_to_excel.py
#
# Objetivo:
#   Exportar a Excel un DataFrame de postulaciones normalizado,
#   donde:
#     - 1 fila = 1 postulación
#     - columnas = metadata + preguntas del formulario
#
# Resultado:
#   Archivo Excel equivalente al descargable de Charly
# ================================================================

from pathlib import Path
import re
import pandas as pd


# ------------------------------------------------------------------
# UTILIDAD
# ------------------------------------------------------------------
def _sanitize_filename(text: str) -> str:
    """
    Normaliza un texto para usarlo como nombre de archivo.

    - Reemplaza espacios por _
    - Elimina caracteres especiales
    """
    text = text.strip().lower()
    text = re.sub(r"\s+", "_", text)
    text = re.sub(r"[^a-z0-9_]+", "", text)
    return text


# ------------------------------------------------------------------
# FUNCIÓN PRINCIPAL
# ------------------------------------------------------------------
def export_applications_dataframe_to_excel(
    df: pd.DataFrame,
    output_dir: Path,
    program_id: int,
    program_name: str,
    sheet_name: str = "applications"
) -> Path:
    """
    Exporta el DataFrame de postulaciones a un archivo Excel.

    Parámetros:
        df (pd.DataFrame):
            DataFrame con postulaciones normalizadas.

        output_dir (Path):
            Directorio donde se guardará el archivo Excel.

        program_id (int):
            ID de la convocatoria.

        program_name (str):
            Nombre de la convocatoria.

        sheet_name (str):
            Nombre de la hoja Excel.
            Default: 'applications'

    Retorna:
        Path:
            Ruta del archivo Excel generado.
    """

    output_dir.mkdir(parents=True, exist_ok=True)

    safe_program_name = _sanitize_filename(program_name)

    filename = f"applications_program_{program_id}_{safe_program_name}.xlsx"
    output_path = output_dir / filename

    with pd.ExcelWriter(output_path, engine="openpyxl") as writer:
        df.to_excel(
            writer,
            index=False,
            sheet_name=sheet_name
        )

    return output_path
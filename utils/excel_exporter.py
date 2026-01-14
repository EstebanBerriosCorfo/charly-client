# ================================================================
# Excel Exporter
# ================================================================

from pathlib import Path
import pandas as pd


def export_applications_dataframe_to_excel(
    df: pd.DataFrame,
    output_path: Path,
    sheet_name: str = "applications"
) -> Path:
    """
    Exporta el DataFrame a Excel.
    """

    output_path.parent.mkdir(parents=True, exist_ok=True)

    with pd.ExcelWriter(output_path, engine="openpyxl") as writer:
        df.to_excel(writer, index=False, sheet_name=sheet_name)

    return output_path
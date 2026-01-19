# scripts/verify_repeated_fields.py
# Verificar que los campos repetidos se expandan correctamente

import pandas as pd
from pathlib import Path

excel_file = Path("downloads/applications_program_2429_normalized.xlsx")

df = pd.read_excel(excel_file)

print("="*80)
print("VERIFICACIÓN DE CAMPOS REPETIDOS EXPANDIDOS")
print("="*80)

# Buscar campos que deberían estar expandidos
test_fields = [
    "Nombre del Subcontrato",
    "Sueldo bruto promedio",
    "Hombres",
    "Mujeres",
    "Currúculum del Subcontrato"
]

for field_name in test_fields:
    matching_cols = [c for c in df.columns if field_name in c]
    if matching_cols:
        print(f"\n{field_name}:")
        print(f"  Total columnas: {len(matching_cols)}")
        for i, col in enumerate(matching_cols[:10], 1):
            non_null = df[col].notna().sum()
            print(f"  {i:2d}. {col[:70]:<70} ({non_null:4d} valores)")
        
        # Mostrar ejemplo de aplicación con múltiples valores
        if len(matching_cols) > 1:
            # Buscar aplicación que tenga valores en múltiples columnas
            for idx, row in df.iterrows():
                values = [row[col] for col in matching_cols if pd.notna(row.get(col))]
                if len(values) > 1:
                    print(f"\n  Ejemplo (App {row['application_id']}):")
                    for i, val in enumerate(values[:5], 1):
                        print(f"    {i}. {str(val)[:60]}")
                    break

print("\n" + "="*80)
print("RESUMEN")
print("="*80)
print(f"Total columnas: {len(df.columns)}")
print(f"Total filas: {len(df)}")

# Contar columnas numeradas (que terminan con número)
import re
numbered_cols = [c for c in df.columns if re.search(r'\s+\d+$', c)]
print(f"Columnas numeradas (expandidas): {len(numbered_cols)}")

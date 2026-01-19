# scripts/inspect_excel.py
# Inspeccionar el Excel generado para entender su estructura

import pandas as pd
from pathlib import Path

excel_file = Path("downloads/applications_program_2429_normalized.xlsx")

if not excel_file.exists():
    print(f"ERROR: No se encuentra el archivo {excel_file}")
    exit(1)

print(f"Leyendo Excel: {excel_file}\n")

# Leer Excel
df = pd.read_excel(excel_file, sheet_name="Postulaciones")

print("="*80)
print("ESTADÍSTICAS DEL EXCEL GENERADO")
print("="*80)
print(f"Total filas: {len(df)}")
print(f"Total columnas: {len(df.columns)}")
print()

print("="*80)
print("PRIMERAS 30 COLUMNAS")
print("="*80)
for i, col in enumerate(df.columns[:30], 1):
    non_null = df[col].notna().sum()
    print(f"{i:3d}. {col[:70]:<70} ({non_null:4d} valores)")

print("\n" + "="*80)
print("COLUMNAS QUE CONTIENEN 'Contribuyente Mandante'")
print("="*80)
contribuyente_cols = [col for col in df.columns if 'Contribuyente Mandante' in col]
print(f"Total: {len(contribuyente_cols)}")
for col in contribuyente_cols[:20]:
    non_null = df[col].notna().sum()
    print(f"  - {col[:80]:<80} ({non_null:4d} valores)")

print("\n" + "="*80)
print("COLUMNAS QUE CONTIENEN NÚMEROS (posibles campos repetidos)")
print("="*80)
import re
numbered_cols = [col for col in df.columns if re.search(r'\s+\d+\s*-\s*', col)]
print(f"Total: {len(numbered_cols)}")
for col in numbered_cols[:30]:
    non_null = df[col].notna().sum()
    print(f"  - {col[:80]:<80} ({non_null:4d} valores)")

print("\n" + "="*80)
print("MUESTRA DE PRIMERAS 3 FILAS (primeras 15 columnas)")
print("="*80)
print(df.iloc[:3, :15].to_string())

print("\n" + "="*80)
print("BUSCAR COLUMNAS CON PATRONES ESPECÍFICOS")
print("="*80)

# Buscar columnas que parecen ser parte de una serie
patterns = [
    r'Región.*Provincia.*Comuna',
    r'Dirección',
    r'Contribuyente Mandante',
    r'Última actualización',
]

for pattern in patterns:
    matching = [col for col in df.columns if re.search(pattern, col, re.IGNORECASE)]
    if matching:
        print(f"\nPatrón '{pattern}': {len(matching)} columnas")
        for col in matching[:10]:
            print(f"  - {col}")

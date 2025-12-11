import sqlite3
import pandas as pd
import numpy as np

"""
SCRIPT DE EXTRACCIÓN DE DATOS DE SUELO HWSD2 PARA PyAEZ
========================================================

BASE FUNDAMENTAL Y REFERENCIAS:
-------------------------------
1. HWSD v2.0 (Harmonized World Soil Database v2.0) - FAO/IIASA
   - Fuente: https://www.fao.org/soils-portal/data-hub/soil-maps-and-databases/

2. Clasificación WRB (World Reference Base for Soil Resources) - IUSS/FAO
   - Referencia: IUSS Working Group WRB (2015)
   - URL: http://www.fao.org/3/i3794en/I3794en.pdf

3. Sistema de Textura USDA (United States Department of Agriculture)
   - 12 clases texturales basadas en % arena, limo y arcilla
   - Referencia: USDA-NRCS Soil Survey Manual

4. PyAEZ (Python-based Agro-Ecological Zones)
   - Sistema FAO para evaluación de aptitud agrícola
   - Referencia: FAO (1996) - Agro-ecological zoning guidelines
   - GitHub: https://github.com/gicait/PyAEZ

FUNDAMENTOS DE VARIABLES:
-------------------------

TXT (Textura): Clasificación USDA de textura del suelo
    - Determina retención de agua, aireación, laborabilidad
    - 12 clases: Clay, Sandy loam, Loam, etc.

OC (Carbono Orgánico): % en peso del suelo
    - Indicador de fertilidad y estructura
    - Rango típico: 0.5-5% en topsoil

pH: Potencial de hidrógeno en solución acuosa
    - Escala 0-14, óptimo agrícola 6.0-7.5
    - Afecta disponibilidad de nutrientes

TEB (Total Exchangeable Bases): cmol(+)/kg
    - Suma de Ca²⁺ + Mg²⁺ + K⁺ + Na⁺
    - Indicador de fertilidad química

BS (Base Saturation): %
    - BS = (TEB / CEC_soil) × 100
    - >50% = suelo fértil, <35% = ácido/pobre

CEC_soil (Capacidad de Intercambio Catiónico): cmol(+)/kg
    - Capacidad de retener nutrientes catiónicos
    - Alto CEC = mayor fertilidad potencial

CEC_clay (CEC de la fracción arcilla): cmol(+)/kg
    - CEC específico de arcillas
    - Identifica tipo de arcillas (expansivas vs. no expansivas)

RSD (Root System Depth): cm
    - Profundidad efectiva del sistema radicular
    - Limitada por obstáculos físicos o químicos

SPR (Soil Phase Rocky): Fase física superficial
    - Limitaciones: Stony, Lithic, Petric, Skeletic
    - Afecta laborabilidad y arraigo de raíces

SPH (Soil Phase High): Fase química o profunda
    - Limitaciones: Salic, Sodic, Gelic, Aridic
    - Afecta disponibilidad de agua/nutrientes

OSD (Obstacle to roots Depth): cm
    - Profundidad del obstáculo para raíces
    - Referencia: FAO Guidelines for Soil Profile Description

DRG (Drainage): Clase de drenaje natural
    - Códigos: VP/P/I/MW/W/SW/E (Very Poor a Excessively)
    - Afecta oxigenación y régimen hídrico

ESP (Exchangeable Sodium Percentage): %
    - ESP = (Na⁺ / CEC) × 100
    - >15% = suelo sódico con problemas de estructura

EC (Electrical Conductivity): dS/m
    - Indicador de salinidad
    - >4 dS/m = problemas para cultivos sensibles

CCB (Calcium Carbonate equivalent): %
    - Contenido de carbonatos (CaCO₃)
    - >15% = suelo calcáreo, afecta pH y P disponible

GYP (Gypsum): %
    - Contenido de yeso (CaSO₄·2H₂O)
    - >25% = yermosols gipsicos

GRC (Gravel Content): %
    - % volumen de fragmentos >2mm
    - Reduce capacidad de retención de agua

VSP (Vertic Soil Phase): 0/1 (binario)
    - Identifica suelos con arcillas expansivas
    - Criterios WRB: >35% arcilla + CEC_clay >40 cmol/kg
    - Comportamiento: grietas al secar, expansión al humedecer

METODOLOGÍA DE CONSOLIDACIÓN:
-----------------------------
- Variables numéricas continuas: PROMEDIO (media aritmética)
- Variables categóricas: MODA (valor más frecuente)
- Justificación: Representa comportamiento promedio del tipo de suelo
  cuando existen múltiples perfiles en la base de datos
"""

# IDs de Eswatini (31 tipos de suelo)
ids_eswatini = [7001, 18372, 27072, 27073, 27074, 27075, 27076, 27077, 27078, 27079,
                27080, 27081, 27082, 27083, 27084, 27085, 27086, 27087, 27088, 27089,
                28093, 30424, 30803, 30866, 30898, 30975, 30998, 31032, 31044, 31048, 31100]

conn = sqlite3.connect('HWSD2.db')

print("="*80)
print("GENERANDO FORMATO PyAEZ PARA ESWATINI")
print("="*80)

# ============================================================================
# SECCIÓN 1: CARGA DE TABLAS DE REFERENCIA
# ============================================================================
print("\n[1] Cargando tablas de referencia...")

# D_DRAINAGE - Códigos de drenaje
df_drainage = pd.read_sql_query("SELECT * FROM D_DRAINAGE", conn)
drainage_map = dict(zip(df_drainage['SYMBOL'], df_drainage['CODE']))
print(f"✓ Drenaje: {drainage_map}")

# D_PHASE - Fases del suelo
df_phase = pd.read_sql_query("SELECT * FROM D_PHASE", conn)
phase_map = dict(zip(df_phase['CODE'], df_phase['VALUE']))
print(f"✓ Fases: {len(phase_map)} códigos")

# D_ROOTS - Obstáculos para raíces
df_roots = pd.read_sql_query("SELECT * FROM D_ROOTS", conn)
roots_map = dict(zip(df_roots['CODE'], df_roots['VALUE']))
print(f"✓ Obstáculos raíces: {roots_map}")

# D_TEXTURE_USDA - Texturas
df_texture = pd.read_sql_query("SELECT * FROM D_TEXTURE_USDA", conn)
texture_map = dict(zip(df_texture['CODE'], df_texture['VALUE']))
print(f"✓ Texturas: {len(texture_map)} tipos")

# ============================================================================
# SECCIÓN 2: CÁLCULO DE VSP (Vertic Soil Phase)
# ============================================================================
print("\n" + "="*80)
print("[2] CALCULANDO VSP (Vertic Soil Phase)")
print("="*80)

# Cargar clasificación WRB
df_smu_wrb = pd.read_sql_query(f"""
    SELECT HWSD2_SMU_ID, WRB4, WRB2
    FROM HWSD2_SMU
    WHERE HWSD2_SMU_ID IN ({','.join(map(str, ids_eswatini))})
""", conn)

df_wrb4 = pd.read_sql_query("SELECT * FROM D_WRB4", conn)
df_wrb2 = pd.read_sql_query("SELECT * FROM D_WRB2", conn)

wrb4_map = dict(zip(df_wrb4['CODE'], df_wrb4['VALUE']))
wrb2_map = dict(zip(df_wrb2['CODE'], df_wrb2['Value']))

df_smu_wrb['WRB4_NAME'] = df_smu_wrb['WRB4'].map(wrb4_map)
df_smu_wrb['WRB2_NAME'] = df_smu_wrb['WRB2'].map(wrb2_map)

# Criterio 1: Clasificación WRB contiene "Vertic"
df_smu_wrb['VERTIC_WRB'] = df_smu_wrb['WRB4_NAME'].fillna('').str.contains('Vertic', case=False, na=False) | \
                            df_smu_wrb['WRB2_NAME'].fillna('').str.contains('Vertic', case=False, na=False)

# Criterio 2: >35% arcilla + CEC_clay >40 (arcillas expansivas tipo montmorillonita)
df_clay_props = pd.read_sql_query(f"""
    SELECT 
        HWSD2_SMU_ID,
        AVG(CLAY) as avg_clay,
        AVG(CEC_CLAY) as avg_cec_clay
    FROM HWSD2_LAYERS
    WHERE HWSD2_SMU_ID IN ({','.join(map(str, ids_eswatini))})
      AND LAYER = 'D1'
      AND CLAY > 0
    GROUP BY HWSD2_SMU_ID
""", conn)

df_clay_props['VERTIC_CLAY'] = (df_clay_props['avg_clay'] > 35) & (df_clay_props['avg_cec_clay'] > 40)

# Combinar criterios
df_vsp = df_smu_wrb.merge(df_clay_props[['HWSD2_SMU_ID', 'avg_clay', 'avg_cec_clay', 'VERTIC_CLAY']], 
                          on='HWSD2_SMU_ID', how='left')

df_vsp['VSP'] = (df_vsp['VERTIC_WRB'] | df_vsp['VERTIC_CLAY'].fillna(False)).astype(int)

vsp_map = dict(zip(df_vsp['HWSD2_SMU_ID'], df_vsp['VSP']))

print(f"✓ VSP calculado: {len(vsp_map)} suelos")
print(f"  - Vérticos (VSP=1): {sum(vsp_map.values())}")
print(f"  - No vérticos (VSP=0): {len(vsp_map) - sum(vsp_map.values())}")

if sum(vsp_map.values()) > 0:
    vertic_soils = df_vsp[df_vsp['VSP'] == 1][['HWSD2_SMU_ID', 'WRB4_NAME', 'avg_clay', 'avg_cec_clay']]
    print("\nSuelos vérticos identificados:")
    print(vertic_soils.to_string(index=False))

# ============================================================================
# SECCIÓN 3: EXTRACCIÓN DE DATOS DE CAPAS
# ============================================================================
print("\n" + "="*80)
print("[3] OBTENIENDO DATOS DE HWSD2_LAYERS")
print("="*80)

query = """
SELECT *
FROM HWSD2_LAYERS
WHERE HWSD2_SMU_ID IN ({})
ORDER BY HWSD2_SMU_ID, ID, TOPDEP
""".format(','.join(map(str, ids_eswatini)))

df_all = pd.read_sql_query(query, conn)
print(f"✓ Total registros: {len(df_all)}")
print(f"✓ SMU_IDs únicos: {df_all['HWSD2_SMU_ID'].nunique()}")
print(f"✓ Capas disponibles:")
print(df_all['LAYER'].value_counts().sort_index())

# ============================================================================
# SECCIÓN 4: FUNCIÓN DE PROCESAMIENTO POR CAPA
# ============================================================================

def convertir_osd_a_cm(osd_code):
    """
    Convierte código OSD a valor numérico en cm (punto medio del rango)
    Referencia: D_ROOTS tabla HWSD2
    """
    osd_ranges = {
        0: 0,      # Sin obstáculo
        1: 90,     # >80 cm → usar 90 (profundo)
        2: 70,     # 60-80 cm → punto medio 70
        3: 50,     # 40-60 cm → punto medio 50
        4: 30,     # 20-40 cm → punto medio 30
        5: 40,     # 0-80 cm → punto medio 40 (rango amplio)
        6: 10      # 0-20 cm → punto medio 10 (muy superficial)
    }
    
    try:
        code = int(osd_code)
        return osd_ranges.get(code, 0)
    except (ValueError, TypeError):
        return 0

def clasificar_sph(phase1, phase2, phase_map):
    """
    SPH (Soil Phase High/Deep): Fases químicas o profundas
    
    Fundamento: Limitaciones químicas o climáticas que afectan desarrollo del cultivo
    - Salic: Acumulación de sales solubles
    - Sodic: Alto contenido de sodio intercambiable
    - Gelic: Permafrost o congelamiento estacional
    - Aridic: Condiciones de aridez extrema
    - Yermic: Costra superficial en climas áridos
    
    Prioridad: Busca en ambas fases (PHASE1 y PHASE2)
    """
    sph_phases = ['Salic', 'Sodic', 'Gelic', 'Yermic', 'Aridic', 'Duric']
    
    for phase_code in [phase1, phase2]:
        if pd.notna(phase_code):
            try:
                phase_name = phase_map.get(int(phase_code), '')
                if any(p in str(phase_name) for p in sph_phases):
                    return phase_name
            except (ValueError, TypeError):
                pass
    return 0

def clasificar_spr(phase1, phase2, phase_map):
    """
    SPR (Soil Phase Rocky): Fases físicas superficiales
    
    Fundamento: Limitaciones físicas que afectan laborabilidad y desarrollo radicular
    - Stony: Fragmentos rocosos en superficie (15-40%)
    - Lithic: Roca continua cerca de superficie (<50cm)
    - Petric: Horizonte cementado (hardpan)
    - Skeletic: Alto contenido de gravas/piedras (>40%)
    - Rudic: Fragmentos gruesos muy abundantes
    
    Prioridad: PHASE1 primero (fase dominante >15% área)
    """
    spr_phases = ['Stony', 'Lithic', 'Petric', 'Skeletic', 'Rudic', 'Gravelly']
    
    for phase_code in [phase1, phase2]:
        if pd.notna(phase_code):
            try:
                phase_name = phase_map.get(int(phase_code), '')
                if any(p in str(phase_name) for p in spr_phases):
                    return phase_name
            except (ValueError, TypeError):
                pass
    return 0

def generar_pyaez_por_capa(df, layer_name):
    """
    Genera formato PyAEZ para una capa específica
    
    Parámetros:
    - df: DataFrame con datos de HWSD2_LAYERS
    - layer_name: Nombre de capa (D1-D7)
    
    Retorna:
    - DataFrame en formato PyAEZ
    """
    print(f"\n{'='*80}")
    print(f"[4.{layer_name}] PROCESANDO CAPA {layer_name}")
    print(f"{'='*80}")
    
    df_layer = df[df['LAYER'] == layer_name].copy()
    print(f"✓ Registros en {layer_name}: {len(df_layer)}")
    
    # Filtrar registros válidos (ORG_CARBON > 0 indica dato real)
    df_valid = df_layer[df_layer['ORG_CARBON'] > 0].copy()
    print(f"✓ Registros válidos: {len(df_valid)}")
    
    if len(df_valid) == 0:
        print(f"⚠️  No hay datos válidos para {layer_name}")
        return None
    
    # ========================================================================
    # CONSOLIDACIÓN: Promediar múltiples perfiles del mismo tipo de suelo
    # ========================================================================
    print(f"✓ Consolidando múltiples perfiles...")
    
    def get_mode_or_first(series):
        """Obtiene moda (valor más frecuente) o primer valor"""
        mode = series.mode()
        return mode[0] if len(mode) > 0 else series.iloc[0]
    
    # Agregación por tipo de suelo
    df_consolidated = df_valid.groupby('HWSD2_SMU_ID').agg({
        'TEXTURE_USDA': get_mode_or_first,
        'ORG_CARBON': 'mean',
        'PH_WATER': 'mean',
        'TEB': 'mean',
        'CEC_SOIL': 'mean',
        'CEC_CLAY': 'mean',
        'ROOT_DEPTH': get_mode_or_first,
        'PHASE1': get_mode_or_first,
        'PHASE2': get_mode_or_first,
        'ROOTS': get_mode_or_first,
        'DRAINAGE': get_mode_or_first,
        'ESP': 'mean',
        'ELEC_COND': 'mean',
        'TCARBON_EQ': 'mean',
        'GYPSUM': 'mean',
        'COARSE': 'mean'
    }).reset_index()
    
    print(f"✓ Tipos de suelo consolidados: {len(df_consolidated)}")
    
    # ========================================================================
    # MAPEO DE VARIABLES CATEGÓRICAS
    # ========================================================================
    
    # TXT: Textura USDA
    df_consolidated['TXT'] = df_consolidated['TEXTURE_USDA'].map(texture_map).fillna(df_consolidated['TEXTURE_USDA'])
    
    # DRG: Drenaje (maneja códigos numéricos y texto)
    def map_drainage(val):
        if pd.isna(val):
            return ''
        if isinstance(val, str):
            return val
        try:
            return drainage_map.get(int(val), '')
        except (ValueError, TypeError):
            return ''
    
    df_consolidated['DRG'] = df_consolidated['DRAINAGE'].apply(map_drainage)
    
    # SPH y SPR: Fases del suelo
    df_consolidated['SPH'] = df_consolidated.apply(
        lambda row: clasificar_sph(row['PHASE1'], row['PHASE2'], phase_map), 
        axis=1
    )
    
    df_consolidated['SPR'] = df_consolidated.apply(
        lambda row: clasificar_spr(row['PHASE1'], row['PHASE2'], phase_map), 
        axis=1
    )
    
    # OSD: Obstáculo a raíces
    df_consolidated['OSD'] = df_consolidated['ROOTS'].apply(convertir_osd_a_cm)
    
    # VSP: Fase vértica
    df_consolidated['VSP'] = df_consolidated['HWSD2_SMU_ID'].map(vsp_map).fillna(0).astype(int)
    
    # ========================================================================
    # CÁLCULO DE BS (Base Saturation)
    # ========================================================================
    # Fundamento: BS = (TEB / CEC_soil) × 100
    # NO se debe promediar BS directamente, sino recalcular desde TEB/CEC
    
    df_consolidated['BS_calculated'] = (
        (df_consolidated['TEB'] / df_consolidated['CEC_SOIL']) * 100
    ).fillna(0)
    
    # Validar rango 0-100%
    df_consolidated['BS_calculated'] = df_consolidated['BS_calculated'].clip(0, 100)
    
    # ========================================================================
    # VALIDACIÓN DE RANGOS (Agregar controles de calidad)
    # ========================================================================
    
    # pH debe estar entre 3.0 y 11.0
    df_consolidated['PH_WATER'] = df_consolidated['PH_WATER'].clip(3.0, 11.0)
    
    # ESP debe estar entre 0 y 100
    df_consolidated['ESP'] = df_consolidated['ESP'].clip(0, 100)
    
    # ========================================================================
    # CREACIÓN DEL DATAFRAME FINAL PyAEZ
    # ========================================================================
    
    def safe_int(series, default=0):
        """Convierte a entero manejando NaN"""
        return series.fillna(default).round(0).astype(int)
    
    df_pyaez = pd.DataFrame({
        'CODE': df_consolidated['HWSD2_SMU_ID'],
        'TXT': df_consolidated['TXT'],
        'OC': df_consolidated['ORG_CARBON'].fillna(0).round(3),
        'pH': df_consolidated['PH_WATER'].fillna(7.0).round(1),
        'TEB': df_consolidated['TEB'].fillna(0).round(1),
        'BS': safe_int(df_consolidated['BS_calculated'], 0),  
        'CEC_soil': safe_int(df_consolidated['CEC_SOIL'], 0),
        'CEC_clay': safe_int(df_consolidated['CEC_CLAY'], 0),
        'RSD': safe_int(df_consolidated['ROOT_DEPTH'], 100),
        'SPR': df_consolidated['SPR'],
        'SPH': df_consolidated['SPH'],
        'OSD': df_consolidated['OSD'],
        'DRG': df_consolidated['DRG'].fillna(''),
        'ESP': safe_int(df_consolidated['ESP'], 0),
        'EC': safe_int(df_consolidated['ELEC_COND'], 0),
        'CCB': safe_int(df_consolidated['TCARBON_EQ'], 0),
        'GYP': df_consolidated['GYPSUM'].fillna(0).round(1),
        'GRC': safe_int(df_consolidated['COARSE'], 0),
        'VSP': df_consolidated['VSP'].astype(int)
    })
    
    df_pyaez = df_pyaez.sort_values('CODE').reset_index(drop=True)
    
    print(f"\n✓ Capa {layer_name} procesada: {len(df_pyaez)} tipos de suelo")
    print(f"\nPrimeras 3 filas:")
    print(df_pyaez.head(3).to_string(index=False))
    
    return df_pyaez

# ============================================================================
# SECCIÓN 5: PROCESAMIENTO DE TODAS LAS CAPAS
# ============================================================================
print("\n" + "="*80)
print("[5] GENERANDO ARCHIVOS POR CAPA")
print("="*80)

resultados = {}
capas = ['D1', 'D2', 'D3', 'D4', 'D5', 'D6', 'D7']

for capa in capas:
    df_pyaez = generar_pyaez_por_capa(df_all, capa)
    if df_pyaez is not None:
        resultados[capa] = df_pyaez

# ============================================================================
# SECCIÓN 6: CREAR ARCHIVO CONSOLIDADO MULTICAPA
# ============================================================================
print("\n" + "="*80)
print("[6] CREANDO ARCHIVO CONSOLIDADO MULTICAPA")
print("="*80)

dfs_con_layer = []
for capa, df in resultados.items():
    df_temp = df.copy()
    df_temp.insert(1, 'LAYER', capa)
    dfs_con_layer.append(df_temp)

df_multicapa = pd.concat(dfs_con_layer, ignore_index=True)

# Guardar archivo final
output_filename = "eswatini_soil_ALL_LAYERS_pyaez.xlsx"
df_multicapa.to_excel(output_filename, index=False)

print(f"✓ Guardado: {output_filename}")
print(f"  - {len(df_multicapa)} registros totales")
print(f"  - {df_multicapa['CODE'].nunique()} tipos de suelo únicos")
print(f"  - {df_multicapa['LAYER'].nunique()} capas de profundidad")

# ============================================================================
# SECCIÓN 7: ESTADÍSTICAS Y VALIDACIÓN
# ============================================================================
print("\n" + "="*80)
print("[7] ESTADÍSTICAS DE VALIDACIÓN")
print("="*80)

print(f"\nDistribución de registros por capa:")
print(df_multicapa['LAYER'].value_counts().sort_index())

print(f"\nRangos de variables clave (todas las capas):")
print(f"  - pH: {df_multicapa['pH'].min():.1f} - {df_multicapa['pH'].max():.1f}")
print(f"  - BS: {df_multicapa['BS'].min()}% - {df_multicapa['BS'].max()}%")
print(f"  - OC: {df_multicapa['OC'].min():.3f}% - {df_multicapa['OC'].max():.3f}%")
print(f"  - CEC_soil: {df_multicapa['CEC_soil'].min()} - {df_multicapa['CEC_soil'].max()} cmol/kg")
print(f"  - ESP: {df_multicapa['ESP'].min()}% - {df_multicapa['ESP'].max()}%")

print(f"\nTexturas presentes:")
print(df_multicapa['TXT'].value_counts())

print(f"\nDrenaje:")
print(df_multicapa['DRG'].value_counts())

print(f"\nSuelos con limitaciones:")
print(f"  - SPR (rocosos): {(df_multicapa['SPR'] != 0).sum()} registros")
print(f"  - SPH (químicos): {(df_multicapa['SPH'] != 0).sum()} registros")
print(f"  - VSP (vérticos): {(df_multicapa['VSP'] == 1).sum()} registros")

conn.close()

print("\n" + "="*80)
print("✓ PROCESO COMPLETADO EXITOSAMENTE")
print("="*80)
print(f"""

ARCHIVO GENERADO:
-----------------
{output_filename}
  - Formato: Excel (.xlsx)
  - Estructura: Todas las capas D1-D7 en un solo archivo
  - Columnas: 19 variables PyAEZ + LAYER identifier
  - Compatible con PyAEZ para análisis agroecológico

REFERENCIAS APLICADAS:
---------------------
- FAO HWSD v2.0 Database Structure
- WRB Soil Classification (IUSS 2015)
- USDA Soil Texture Classification
- FAO Agro-Ecological Zones Guidelines (1996)
- PyAEZ Technical Documentation
""")
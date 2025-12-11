# HWSD2 a PyAEZ - Extractor de Datos de Suelo

Script de Python para extraer y procesar datos de la base de datos **HWSD v2.0** (Harmonized World Soil Database) y convertirlos al formato requerido por **PyAEZ** (Python-based Agro-Ecological Zones).

## 📋 Descripción

Este script extrae características de suelo para una región específica (Eswatini - 31 tipos de suelo) desde la base de datos HWSD2 SQLite y genera archivos Excel compatibles con PyAEZ para análisis de zonas agroecológicas.

### Características principales:
- ✅ Procesa 7 capas de profundidad (D1-D7: 0-200cm)
- ✅ Calcula 19 variables edafológicas estándar PyAEZ
- ✅ Identifica suelos vérticos automáticamente
- ✅ Clasifica limitaciones físicas y químicas del suelo
- ✅ Consolida múltiples perfiles del mismo tipo de suelo
- ✅ Valida rangos de variables según estándares FAO
- ✅ Genera archivo Excel consolidado listo para usar

---

## 🔧 Requisitos

### Software necesario:
```bash
Python 3.8+
```

### Librerías de Python:
```bash
pip install pandas numpy openpyxl
```

### Archivos requeridos:
- `HWSD2.db` - Base de datos SQLite de HWSD v2.0
- `maiz_soil_characteristics_topsoil.xlsx` (opcional - solo para comparación)

---

## 🗂️ Estructura de Archivos
```
proyecto/
│
├── eswatini_pyaez_suelos.py          # Script principal
├── README.md                          # Este archivo
├── HWSD2.db                          # Base de datos HWSD2
│
└── outputs/                          # Archivos generados
    └── eswatini_soil_ALL_LAYERS_pyaez.xlsx
```

---

## 🚀 Uso

### Ejecución básica:
```bash
python eswatini_pyaez_suelos.py
```

### Modificar región de estudio:
Editar la lista de IDs de tipos de suelo en el script:
```python
# Línea 71-73
ids_eswatini = [7001, 18372, 27072, ...]  # Reemplazar con tus IDs
```

Para obtener IDs de otra región, consultar:
```sql
SELECT HWSD2_SMU_ID, WRB4 
FROM HWSD2_SMU 
WHERE -- tus condiciones de filtrado
```

---

## 📊 Salida del Script

### Archivo generado:
**`eswatini_soil_ALL_LAYERS_pyaez.xlsx`**

Contiene todas las capas D1-D7 en un solo archivo con las siguientes columnas:

| Columna | Descripción | Unidad | Rango |
|---------|-------------|--------|-------|
| `CODE` | ID del tipo de suelo (HWSD2_SMU_ID) | - | - |
| `LAYER` | Capa de profundidad | - | D1-D7 |
| `TXT` | Textura USDA | - | 12 clases |
| `OC` | Carbono orgánico | % | 0-10 |
| `pH` | pH en agua | - | 3-11 |
| `TEB` | Bases intercambiables totales | cmol/kg | 0-100 |
| `BS` | Saturación de bases | % | 0-100 |
| `CEC_soil` | CEC del suelo | cmol/kg | 0-100 |
| `CEC_clay` | CEC de la arcilla | cmol/kg | 0-200 |
| `RSD` | Profundidad radicular | cm | 0-200 |
| `SPR` | Fase rocosa | - | 0 o nombre |
| `SPH` | Fase química/profunda | - | 0 o nombre |
| `OSD` | Obstáculo para raíces | cm | 0-90 |
| `DRG` | Clase de drenaje | - | VP/P/I/MW/W/SW/E |
| `ESP` | Porcentaje de sodio intercambiable | % | 0-100 |
| `EC` | Conductividad eléctrica | dS/m | 0-50 |
| `CCB` | Carbonatos equivalentes | % | 0-100 |
| `GYP` | Yeso | % | 0-100 |
| `GRC` | Contenido de gravas | % | 0-100 |
| `VSP` | Fase vértica | - | 0 o 1 |

---

## 🧮 Metodología y Fundamentos

### 1. Consolidación de datos
Cuando existen múltiples perfiles del mismo tipo de suelo:
- **Variables continuas**: Se calcula la **media aritmética**
- **Variables categóricas**: Se usa la **moda** (valor más frecuente)

### 2. Cálculos corregidos

#### Base Saturation (BS)
```python
BS = (TEB / CEC_soil) × 100
```
✅ **Corrección**: Se recalcula desde TEB/CEC en lugar de promediar valores de BS

#### Obstacle to roots Depth (OSD)
Conversión de códigos D_ROOTS a centímetros (punto medio):
```
Código 0 → 0 cm    (sin obstáculo)
Código 1 → 90 cm   (>80 cm)
Código 2 → 70 cm   (60-80 cm)
Código 3 → 50 cm   (40-60 cm)
Código 4 → 30 cm   (20-40 cm)
Código 5 → 40 cm   (0-80 cm)
Código 6 → 10 cm   (0-20 cm)
```

#### Soil Phase Rocky (SPR)
Fases **físicas superficiales**:
- Stony, Lithic, Petric, Skeletic, Rudic, Gravelly
- Afectan laborabilidad y desarrollo radicular

#### Soil Phase High (SPH)
Fases **químicas o profundas**:
- Salic, Sodic, Gelic, Yermic, Aridic, Duric
- Afectan disponibilidad de agua/nutrientes

#### Vertic Soil Phase (VSP)
Identifica suelos con arcillas expansivas mediante **dos criterios**:

**Criterio 1 - Clasificación WRB**:
```python
WRB4_NAME o WRB2_NAME contiene "Vertic"
```

**Criterio 2 - Propiedades físico-químicas**:
```python
(Arcilla > 35%) AND (CEC_clay > 40 cmol/kg)
```

Si cumple **cualquiera** de los dos → `VSP = 1`

---

## 📚 Referencias Científicas

### Bases de datos:
1. **HWSD v2.0** - Harmonized World Soil Database version 2.0
   - FAO/IIASA (2023)
   - URL: https://www.fao.org/soils-portal/data-hub/soil-maps-and-databases/

2. **WRB** - World Reference Base for Soil Resources
   - IUSS Working Group WRB (2015)
   - URL: http://www.fao.org/3/i3794en/I3794en.pdf

### Sistemas de clasificación:
3. **USDA Soil Texture Classification**
   - 12 clases texturales basadas en % arena, limo y arcilla
   - USDA-NRCS Soil Survey Manual

4. **PyAEZ** - Python-based Agro-Ecological Zones
   - Sistema FAO para evaluación de aptitud agrícola
   - FAO (1996) - Agro-ecological zoning guidelines
   - GitHub: https://github.com/gicait/PyAEZ

### Metodologías:
5. **FAO Guidelines for Soil Profile Description** (4th edition, 2006)
6. **FAO Soil Map of the World** - Revised Legend (1988)

---

## 📖 Capas de Profundidad

| Capa | Profundidad | Descripción |
|------|-------------|-------------|
| D1 | 0-20 cm | Topsoil - Capa superficial |
| D2 | 20-40 cm | Subsuelo superior |
| D3 | 40-60 cm | Subsuelo medio |
| D4 | 60-80 cm | Subsuelo inferior |
| D5 | 80-100 cm | Subsuelo profundo |
| D6 | 100-150 cm | Horizonte C superior |
| D7 | 150-200 cm | Horizonte C inferior |

---

## ⚠️ Validaciones Implementadas

El script valida automáticamente:
```python
pH:  3.0 ≤ pH ≤ 11.0      # Rango físico posible
BS:  0 ≤ BS ≤ 100         # Porcentaje válido
ESP: 0 ≤ ESP ≤ 100        # Porcentaje válido
```

Valores fuera de rango se ajustan automáticamente a los límites.

---

## 🐛 Solución de Problemas

### Error: "No such table: HWSD2_LAYERS"
**Causa**: Base de datos HWSD2.db no encontrada o corrupta  
**Solución**: Verificar que el archivo existe y tiene permisos de lectura

### Error: "No data found for layer D1"
**Causa**: IDs de suelo incorrectos o no existen en la base de datos  
**Solución**: Verificar IDs con:
```sql
SELECT DISTINCT HWSD2_SMU_ID FROM HWSD2_LAYERS LIMIT 100;
```

### Advertencia: "No hay datos válidos para D7"
**Causa**: Algunos tipos de suelo no tienen información para capas profundas  
**Solución**: Normal - el script continúa con las capas disponibles

---

## 🔄 Personalización

### Cambiar región de estudio:
```python
# Línea 71-73
ids_tu_region = [ID1, ID2, ID3, ...]
```

### Modificar nombre del archivo de salida:
```python
# Línea 410
output_filename = "tu_nombre_archivo.xlsx"
```

### Agregar más validaciones:
```python
# Sección 4, después de línea 340
# Agregar validaciones personalizadas
df_consolidated['TU_VARIABLE'] = df_consolidated['TU_VARIABLE'].clip(min, max)
```

---

## 📊 Estadísticas de Salida

El script muestra automáticamente:
- ✅ Total de registros procesados
- ✅ Tipos de suelo únicos
- ✅ Distribución por capa
- ✅ Rangos de variables clave
- ✅ Texturas presentes
- ✅ Clases de drenaje
- ✅ Suelos con limitaciones (SPR, SPH, VSP)

---

## 📝 Notas Importantes

1. **Datos faltantes**: El script usa valores por defecto razonables:
   - pH = 7.0 (neutro)
   - RSD = 100 cm (profundidad típica)
   - OSD = 0 (sin obstáculos)

2. **Consolidación**: Cuando hay múltiples perfiles del mismo tipo, se promedian para representar el comportamiento típico del suelo.

3. **VSP**: La identificación de suelos vérticos es conservadora - solo marca como vérticos aquellos que cumplen criterios estrictos WRB o propiedades físico-químicas.

4. **Compatibilidad PyAEZ**: El formato de salida es 100% compatible con las funciones de entrada de PyAEZ para análisis de aptitud de cultivos.

---

## 👤 Autor

Desarrollado para análisis agroecológicos en Eswatini.

## 📄 Licencia

Este script es de código abierto. Puedes usarlo, modificarlo y distribuirlo libremente con atribución apropiada a las fuentes de datos (FAO/IIASA HWSD v2.0).

---

## 🆘 Soporte

Para problemas relacionados con:
- **HWSD2**: https://www.fao.org/soils-portal/
- **PyAEZ**: https://github.com/gicait/PyAEZ/issues
- **Script**: Revisar código fuente y comentarios internos

---

# 🔍 Consultas SQL de Validación y Exploración

Esta sección contiene consultas SQL útiles para validar datos, explorar la base de datos HWSD2 y verificar la correcta extracción de información.

---

## 📋 Tabla de Contenidos

1. [Exploración General](#1-exploración-general)
2. [Validación de IDs de Suelo](#2-validación-de-ids-de-suelo)
3. [Verificación de Capas](#3-verificación-de-capas)
4. [Validación de Variables](#4-validación-de-variables)
5. [Clasificación WRB](#5-clasificación-wrb)
6. [Fases del Suelo](#6-fases-del-suelo)
7. [Propiedades Químicas](#7-propiedades-químicas)
8. [Texturas y Drenaje](#8-texturas-y-drenaje)
9. [Análisis Estadístico](#9-análisis-estadístico)
10. [Queries de Debugging](#10-queries-de-debugging)

---

## 1. Exploración General

### 1.1 Listar todas las tablas de la base de datos
```sql
SELECT name 
FROM sqlite_master 
WHERE type='table' 
ORDER BY name;
```

### 1.2 Ver estructura de tabla HWSD2_LAYERS
```sql
PRAGMA table_info(HWSD2_LAYERS);
```

### 1.3 Contar registros totales por tabla
```sql
SELECT 'HWSD2_SMU' as tabla, COUNT(*) as registros FROM HWSD2_SMU
UNION ALL
SELECT 'HWSD2_LAYERS', COUNT(*) FROM HWSD2_LAYERS
UNION ALL
SELECT 'D_TEXTURE_USDA', COUNT(*) FROM D_TEXTURE_USDA
UNION ALL
SELECT 'D_DRAINAGE', COUNT(*) FROM D_DRAINAGE
UNION ALL
SELECT 'D_PHASE', COUNT(*) FROM D_PHASE
UNION ALL
SELECT 'D_ROOTS', COUNT(*) FROM D_ROOTS
UNION ALL
SELECT 'D_WRB4', COUNT(*) FROM D_WRB4
UNION ALL
SELECT 'D_WRB2', COUNT(*) FROM D_WRB2;
```

---

## 2. Validación de IDs de Suelo

### 2.1 Verificar que todos los IDs de Eswatini existen
```sql
-- Reemplazar con tus IDs específicos
WITH eswatini_ids AS (
    SELECT 7001 as id UNION SELECT 18372 UNION SELECT 27072 UNION SELECT 27073
    -- ... agregar todos los IDs
)
SELECT 
    e.id,
    CASE WHEN s.HWSD2_SMU_ID IS NOT NULL THEN 'EXISTE' ELSE 'NO EXISTE' END as estado
FROM eswatini_ids e
LEFT JOIN HWSD2_SMU s ON e.id = s.HWSD2_SMU_ID
ORDER BY e.id;
```

### 2.2 Encontrar IDs de suelo para una región específica (ejemplo: por coordenadas)
```sql
-- Nota: HWSD2 puede tener campos de georeferencia diferentes según versión
SELECT DISTINCT HWSD2_SMU_ID
FROM HWSD2_SMU
WHERE LAT BETWEEN -27.5 AND -25.5  -- Ajustar coordenadas
  AND LON BETWEEN 30.5 AND 32.5
LIMIT 100;
```

### 2.3 Ver información básica de un tipo de suelo específico
```sql
SELECT *
FROM HWSD2_SMU
WHERE HWSD2_SMU_ID = 7001;
```

---

## 3. Verificación de Capas

### 3.1 Contar capas disponibles por tipo de suelo
```sql
SELECT 
    HWSD2_SMU_ID,
    COUNT(DISTINCT LAYER) as num_capas,
    GROUP_CONCAT(DISTINCT LAYER) as capas_disponibles
FROM HWSD2_LAYERS
WHERE HWSD2_SMU_ID IN (7001, 18372, 27072, 27073, 27074)
GROUP BY HWSD2_SMU_ID;
```

### 3.2 Verificar profundidades de cada capa
```sql
SELECT 
    LAYER,
    MIN(TOPDEP) as prof_min,
    MAX(BOTDEP) as prof_max,
    COUNT(*) as registros
FROM HWSD2_LAYERS
WHERE HWSD2_SMU_ID IN (7001, 18372, 27072)
GROUP BY LAYER
ORDER BY LAYER;
```

### 3.3 Identificar suelos sin capa D7
```sql
SELECT DISTINCT HWSD2_SMU_ID
FROM HWSD2_LAYERS
WHERE HWSD2_SMU_ID IN (7001, 18372, 27072, 27073, 27074)
  AND HWSD2_SMU_ID NOT IN (
      SELECT DISTINCT HWSD2_SMU_ID 
      FROM HWSD2_LAYERS 
      WHERE LAYER = 'D7'
  );
```

### 3.4 Ver todos los datos de una capa específica
```sql
SELECT *
FROM HWSD2_LAYERS
WHERE HWSD2_SMU_ID = 7001
  AND LAYER = 'D1'
ORDER BY TOPDEP;
```

---

## 4. Validación de Variables

### 4.1 Detectar valores inválidos (-9, NULL) por variable
```sql
SELECT 
    'ORG_CARBON' as variable,
    COUNT(*) as total,
    SUM(CASE WHEN ORG_CARBON = -9 OR ORG_CARBON IS NULL THEN 1 ELSE 0 END) as invalidos,
    ROUND(100.0 * SUM(CASE WHEN ORG_CARBON = -9 OR ORG_CARBON IS NULL THEN 1 ELSE 0 END) / COUNT(*), 2) as pct_invalidos
FROM HWSD2_LAYERS
WHERE HWSD2_SMU_ID IN (7001, 18372, 27072)

UNION ALL

SELECT 
    'PH_WATER',
    COUNT(*),
    SUM(CASE WHEN PH_WATER = -9 OR PH_WATER IS NULL THEN 1 ELSE 0 END),
    ROUND(100.0 * SUM(CASE WHEN PH_WATER = -9 OR PH_WATER IS NULL THEN 1 ELSE 0 END) / COUNT(*), 2)
FROM HWSD2_LAYERS
WHERE HWSD2_SMU_ID IN (7001, 18372, 27072)

UNION ALL

SELECT 
    'CEC_SOIL',
    COUNT(*),
    SUM(CASE WHEN CEC_SOIL = -9 OR CEC_SOIL IS NULL THEN 1 ELSE 0 END),
    ROUND(100.0 * SUM(CASE WHEN CEC_SOIL = -9 OR CEC_SOIL IS NULL THEN 1 ELSE 0 END) / COUNT(*), 2)
FROM HWSD2_LAYERS
WHERE HWSD2_SMU_ID IN (7001, 18372, 27072);
```

### 4.2 Rangos de valores por variable (detectar outliers)
```sql
SELECT 
    LAYER,
    ROUND(MIN(ORG_CARBON), 3) as OC_min,
    ROUND(AVG(ORG_CARBON), 3) as OC_avg,
    ROUND(MAX(ORG_CARBON), 3) as OC_max,
    ROUND(MIN(PH_WATER), 1) as pH_min,
    ROUND(AVG(PH_WATER), 1) as pH_avg,
    ROUND(MAX(PH_WATER), 1) as pH_max,
    MIN(CEC_SOIL) as CEC_min,
    ROUND(AVG(CEC_SOIL), 1) as CEC_avg,
    MAX(CEC_SOIL) as CEC_max
FROM HWSD2_LAYERS
WHERE HWSD2_SMU_ID IN (7001, 18372, 27072, 27073)
  AND ORG_CARBON > 0
GROUP BY LAYER
ORDER BY LAYER;
```

### 4.3 Verificar cálculo de Base Saturation (BS)
```sql
-- Comparar BS almacenado vs. calculado desde TEB/CEC
SELECT 
    HWSD2_SMU_ID,
    LAYER,
    BSAT as BS_almacenado,
    ROUND((TEB / NULLIF(CEC_SOIL, 0)) * 100, 1) as BS_calculado,
    ABS(BSAT - ROUND((TEB / NULLIF(CEC_SOIL, 0)) * 100, 1)) as diferencia
FROM HWSD2_LAYERS
WHERE HWSD2_SMU_ID IN (7001, 18372, 27072)
  AND LAYER = 'D1'
  AND TEB > 0 
  AND CEC_SOIL > 0
ORDER BY diferencia DESC
LIMIT 10;
```

### 4.4 Validar que TEB ≤ CEC_SOIL (regla química básica)
```sql
SELECT 
    HWSD2_SMU_ID,
    LAYER,
    TEB,
    CEC_SOIL,
    TEB - CEC_SOIL as diferencia
FROM HWSD2_LAYERS
WHERE HWSD2_SMU_ID IN (7001, 18372, 27072)
  AND TEB > CEC_SOIL  -- Casos anómalos
  AND TEB > 0
ORDER BY diferencia DESC;
```

---

## 5. Clasificación WRB

### 5.1 Ver clasificación WRB completa de tus suelos
```sql
SELECT 
    s.HWSD2_SMU_ID,
    w4.VALUE as WRB_nivel4,
    w2.Value as WRB_nivel2
FROM HWSD2_SMU s
LEFT JOIN D_WRB4 w4 ON s.WRB4 = w4.CODE
LEFT JOIN D_WRB2 w2 ON s.WRB2 = w2.CODE
WHERE s.HWSD2_SMU_ID IN (7001, 18372, 27072, 27073, 27074)
ORDER BY s.HWSD2_SMU_ID;
```

### 5.2 Identificar todos los suelos vérticos por WRB
```sql
SELECT 
    s.HWSD2_SMU_ID,
    w4.VALUE as WRB_nivel4,
    w2.Value as WRB_nivel2
FROM HWSD2_SMU s
LEFT JOIN D_WRB4 w4 ON s.WRB4 = w4.CODE
LEFT JOIN D_WRB2 w2 ON s.WRB2 = w2.CODE
WHERE s.HWSD2_SMU_ID IN (7001, 18372, 27072, 27073, 27074)
  AND (w4.VALUE LIKE '%Vertic%' OR w2.Value LIKE '%Vertic%')
ORDER BY s.HWSD2_SMU_ID;
```

### 5.3 Contar tipos de suelos por grupo WRB
```sql
SELECT 
    w4.VALUE as grupo_suelo,
    COUNT(DISTINCT s.HWSD2_SMU_ID) as num_tipos
FROM HWSD2_SMU s
LEFT JOIN D_WRB4 w4 ON s.WRB4 = w4.CODE
WHERE s.HWSD2_SMU_ID IN (7001, 18372, 27072, 27073, 27074)
GROUP BY w4.VALUE
ORDER BY num_tipos DESC;
```

### 5.4 Ver todos los grupos WRB disponibles en la base de datos
```sql
SELECT CODE, VALUE 
FROM D_WRB4 
ORDER BY CODE;
```

---

## 6. Fases del Suelo

### 6.1 Ver tabla completa de fases
```sql
SELECT * 
FROM D_PHASE 
ORDER BY CODE;
```

### 6.2 Identificar suelos con fases rocosas (SPR)
```sql
SELECT 
    l.HWSD2_SMU_ID,
    l.LAYER,
    l.PHASE1,
    p1.VALUE as fase1_nombre,
    l.PHASE2,
    p2.VALUE as fase2_nombre
FROM HWSD2_LAYERS l
LEFT JOIN D_PHASE p1 ON l.PHASE1 = p1.CODE
LEFT JOIN D_PHASE p2 ON l.PHASE2 = p2.CODE
WHERE l.HWSD2_SMU_ID IN (7001, 18372, 27072)
  AND l.LAYER = 'D1'
  AND (p1.VALUE IN ('Stony', 'Lithic', 'Petric', 'Skeletic', 'Rudic', 'Gravelly')
       OR p2.VALUE IN ('Stony', 'Lithic', 'Petric', 'Skeletic', 'Rudic', 'Gravelly'));
```

### 6.3 Identificar suelos con fases químicas (SPH)
```sql
SELECT 
    l.HWSD2_SMU_ID,
    l.LAYER,
    l.PHASE1,
    p1.VALUE as fase1_nombre,
    l.PHASE2,
    p2.VALUE as fase2_nombre
FROM HWSD2_LAYERS l
LEFT JOIN D_PHASE p1 ON l.PHASE1 = p1.CODE
LEFT JOIN D_PHASE p2 ON l.PHASE2 = p2.CODE
WHERE l.HWSD2_SMU_ID IN (7001, 18372, 27072)
  AND l.LAYER = 'D1'
  AND (p1.VALUE IN ('Salic', 'Sodic', 'Gelic', 'Yermic', 'Aridic', 'Duric')
       OR p2.VALUE IN ('Salic', 'Sodic', 'Gelic', 'Yermic', 'Aridic', 'Duric'));
```

### 6.4 Distribución de fases en tus suelos
```sql
SELECT 
    p.VALUE as fase,
    COUNT(*) as ocurrencias
FROM HWSD2_LAYERS l
JOIN D_PHASE p ON (l.PHASE1 = p.CODE OR l.PHASE2 = p.CODE)
WHERE l.HWSD2_SMU_ID IN (7001, 18372, 27072, 27073)
  AND p.VALUE != '-'
GROUP BY p.VALUE
ORDER BY ocurrencias DESC;
```

---

## 7. Propiedades Químicas

### 7.1 Identificar suelos vérticos por propiedades (Arcilla + CEC_clay)
```sql
SELECT 
    HWSD2_SMU_ID,
    LAYER,
    ROUND(AVG(CLAY), 1) as arcilla_pct,
    ROUND(AVG(CEC_CLAY), 1) as CEC_arcilla,
    CASE 
        WHEN AVG(CLAY) > 35 AND AVG(CEC_CLAY) > 40 THEN 'VÉRTICO'
        ELSE 'NO VÉRTICO'
    END as clasificacion
FROM HWSD2_LAYERS
WHERE HWSD2_SMU_ID IN (7001, 18372, 27072, 27073, 27074)
  AND LAYER = 'D1'
  AND CLAY > 0
GROUP BY HWSD2_SMU_ID, LAYER
ORDER BY arcilla_pct DESC;
```

### 7.2 Identificar suelos salinos (alta EC)
```sql
SELECT 
    HWSD2_SMU_ID,
    LAYER,
    ROUND(AVG(ELEC_COND), 1) as EC_promedio,
    CASE 
        WHEN AVG(ELEC_COND) > 16 THEN 'Fuertemente salino'
        WHEN AVG(ELEC_COND) > 8 THEN 'Salino'
        WHEN AVG(ELEC_COND) > 4 THEN 'Ligeramente salino'
        ELSE 'No salino'
    END as clasificacion_salinidad
FROM HWSD2_LAYERS
WHERE HWSD2_SMU_ID IN (7001, 18372, 27072, 27073)
  AND LAYER = 'D1'
  AND ELEC_COND > 0
GROUP BY HWSD2_SMU_ID, LAYER
ORDER BY EC_promedio DESC;
```

### 7.3 Identificar suelos sódicos (alto ESP)
```sql
SELECT 
    HWSD2_SMU_ID,
    LAYER,
    ROUND(AVG(ESP), 1) as ESP_promedio,
    CASE 
        WHEN AVG(ESP) > 15 THEN 'SÓDICO'
        WHEN AVG(ESP) > 6 THEN 'Riesgo de sodicidad'
        ELSE 'No sódico'
    END as clasificacion_sodio
FROM HWSD2_LAYERS
WHERE HWSD2_SMU_ID IN (7001, 18372, 27072, 27073)
  AND LAYER = 'D1'
  AND ESP > 0
GROUP BY HWSD2_SMU_ID, LAYER
ORDER BY ESP_promedio DESC;
```

### 7.4 Identificar suelos calcáreos (alto CCB)
```sql
SELECT 
    HWSD2_SMU_ID,
    LAYER,
    ROUND(AVG(TCARBON_EQ), 1) as carbonatos_pct,
    CASE 
        WHEN AVG(TCARBON_EQ) > 40 THEN 'Extremadamente calcáreo'
        WHEN AVG(TCARBON_EQ) > 15 THEN 'Calcáreo'
        WHEN AVG(TCARBON_EQ) > 2 THEN 'Ligeramente calcáreo'
        ELSE 'No calcáreo'
    END as clasificacion
FROM HWSD2_LAYERS
WHERE HWSD2_SMU_ID IN (7001, 18372, 27072, 27073)
  AND LAYER = 'D1'
  AND TCARBON_EQ > 0
GROUP BY HWSD2_SMU_ID, LAYER
ORDER BY carbonatos_pct DESC;
```

### 7.5 Perfil completo de fertilidad química
```sql
SELECT 
    HWSD2_SMU_ID,
    LAYER,
    ROUND(AVG(PH_WATER), 1) as pH,
    ROUND(AVG(ORG_CARBON), 2) as OC_pct,
    ROUND(AVG(TEB), 1) as TEB,
    ROUND(AVG(CEC_SOIL), 1) as CEC,
    ROUND((AVG(TEB) / NULLIF(AVG(CEC_SOIL), 0)) * 100, 1) as BS_pct,
    CASE 
        WHEN (AVG(TEB) / NULLIF(AVG(CEC_SOIL), 0)) * 100 > 50 THEN 'Fértil'
        WHEN (AVG(TEB) / NULLIF(AVG(CEC_SOIL), 0)) * 100 > 35 THEN 'Moderado'
        ELSE 'Pobre'
    END as fertilidad
FROM HWSD2_LAYERS
WHERE HWSD2_SMU_ID IN (7001, 18372, 27072)
  AND LAYER = 'D1'
  AND ORG_CARBON > 0
GROUP BY HWSD2_SMU_ID, LAYER
ORDER BY BS_pct DESC;
```

---

## 8. Texturas y Drenaje

### 8.1 Ver tabla completa de texturas USDA
```sql
SELECT * 
FROM D_TEXTURE_USDA 
ORDER BY CODE;
```

### 8.2 Distribución de texturas en tus suelos
```sql
SELECT 
    t.VALUE as textura,
    COUNT(*) as ocurrencias,
    ROUND(100.0 * COUNT(*) / (SELECT COUNT(*) FROM HWSD2_LAYERS 
                               WHERE HWSD2_SMU_ID IN (7001, 18372, 27072) 
                               AND LAYER = 'D1'), 1) as porcentaje
FROM HWSD2_LAYERS l
JOIN D_TEXTURE_USDA t ON l.TEXTURE_USDA = t.CODE
WHERE l.HWSD2_SMU_ID IN (7001, 18372, 27072, 27073)
  AND l.LAYER = 'D1'
GROUP BY t.VALUE
ORDER BY ocurrencias DESC;
```

### 8.3 Ver tabla de drenaje
```sql
SELECT * 
FROM D_DRAINAGE 
ORDER BY SYMBOL;
```

### 8.4 Distribución de clases de drenaje
```sql
SELECT 
    d.CODE as clase_drenaje,
    d.VALUE as descripcion,
    COUNT(*) as ocurrencias
FROM HWSD2_LAYERS l
JOIN D_DRAINAGE d ON l.DRAINAGE = d.SYMBOL
WHERE l.HWSD2_SMU_ID IN (7001, 18372, 27072, 27073)
  AND l.LAYER = 'D1'
GROUP BY d.CODE, d.VALUE
ORDER BY d.SYMBOL;
```

### 8.5 Identificar suelos mal drenados
```sql
SELECT 
    l.HWSD2_SMU_ID,
    l.LAYER,
    d.CODE as clase_drenaje,
    d.VALUE as descripcion
FROM HWSD2_LAYERS l
JOIN D_DRAINAGE d ON l.DRAINAGE = d.SYMBOL
WHERE l.HWSD2_SMU_ID IN (7001, 18372, 27072)
  AND l.LAYER = 'D1'
  AND d.CODE IN ('VP', 'P', 'I')  -- Very Poor, Poor, Imperfect
ORDER BY l.HWSD2_SMU_ID;
```

---

## 9. Análisis Estadístico

### 9.1 Estadísticas descriptivas completas por capa
```sql
SELECT 
    LAYER,
    COUNT(*) as n,
    ROUND(AVG(ORG_CARBON), 3) as OC_media,
    ROUND(MIN(ORG_CARBON), 3) as OC_min,
    ROUND(MAX(ORG_CARBON), 3) as OC_max,
    ROUND(AVG(PH_WATER), 2) as pH_media,
    ROUND(AVG(CEC_SOIL), 1) as CEC_media,
    ROUND(AVG(CLAY), 1) as arcilla_media,
    ROUND(AVG(SAND), 1) as arena_media,
    ROUND(AVG(SILT), 1) as limo_media
FROM HWSD2_LAYERS
WHERE HWSD2_SMU_ID IN (7001, 18372, 27072, 27073, 27074)
  AND ORG_CARBON > 0
GROUP BY LAYER
ORDER BY LAYER;
```

### 9.2 Comparar topsoil vs. subsoil (D1 vs D3)
```sql
SELECT 
    'D1 (Topsoil)' as capa,
    ROUND(AVG(ORG_CARBON), 3) as OC_pct,
    ROUND(AVG(PH_WATER), 1) as pH,
    ROUND(AVG(CEC_SOIL), 1) as CEC,
    ROUND(AVG(TEB), 1) as TEB
FROM HWSD2_LAYERS
WHERE HWSD2_SMU_ID IN (7001, 18372, 27072)
  AND LAYER = 'D1'
  AND ORG_CARBON > 0

UNION ALL

SELECT 
    'D3 (Subsoil)',
    ROUND(AVG(ORG_CARBON), 3),
    ROUND(AVG(PH_WATER), 1),
    ROUND(AVG(CEC_SOIL), 1),
    ROUND(AVG(TEB), 1)
FROM HWSD2_LAYERS
WHERE HWSD2_SMU_ID IN (7001, 18372, 27072)
  AND LAYER = 'D3'
  AND ORG_CARBON > 0;
```

### 9.3 Correlación entre arcilla y CEC
```sql
SELECT 
    HWSD2_SMU_ID,
    ROUND(AVG(CLAY), 1) as arcilla_pct,
    ROUND(AVG(CEC_SOIL), 1) as CEC_soil,
    ROUND(AVG(CEC_CLAY), 1) as CEC_clay,
    ROUND(AVG(CEC_SOIL) / NULLIF(AVG(CLAY), 0), 2) as ratio_CEC_arcilla
FROM HWSD2_LAYERS
WHERE HWSD2_SMU_ID IN (7001, 18372, 27072, 27073)
  AND LAYER = 'D1'
  AND CLAY > 0
GROUP BY HWSD2_SMU_ID
ORDER BY ratio_CEC_arcilla DESC;
```

### 9.4 Identificar suelos con mayor potencial agrícola
```sql
SELECT 
    HWSD2_SMU_ID,
    ROUND(AVG(ORG_CARBON), 2) as OC_pct,
    ROUND(AVG(PH_WATER), 1) as pH,
    ROUND((AVG(TEB) / NULLIF(AVG(CEC_SOIL), 0)) * 100, 1) as BS_pct,
    ROUND(AVG(CEC_SOIL), 1) as CEC,
    ROUND(AVG(ROOT_DEPTH), 0) as prof_raices_cm,
    -- Puntuación simple (ajustar pesos según criterios)
    (
        CASE WHEN AVG(ORG_CARBON) > 2 THEN 2 ELSE 1 END +
        CASE WHEN AVG(PH_WATER) BETWEEN 6.0 AND 7.5 THEN 2 ELSE 1 END +
        CASE WHEN (AVG(TEB) / NULLIF(AVG(CEC_SOIL), 0)) * 100 > 50 THEN 2 ELSE 1 END +
        CASE WHEN AVG(CEC_SOIL) > 15 THEN 2 ELSE 1 END +
        CASE WHEN AVG(ROOT_DEPTH) > 80 THEN 2 ELSE 1 END
    ) as puntuacion_total
FROM HWSD2_LAYERS
WHERE HWSD2_SMU_ID IN (7001, 18372, 27072, 27073, 27074)
  AND LAYER = 'D1'
  AND ORG_CARBON > 0
GROUP BY HWSD2_SMU_ID
ORDER BY puntuacion_total DESC, BS_pct DESC;
```

---

## 10. Queries de Debugging

### 10.1 Encontrar duplicados en capas
```sql
SELECT 
    HWSD2_SMU_ID,
    LAYER,
    COUNT(*) as num_registros
FROM HWSD2_LAYERS
WHERE HWSD2_SMU_ID IN (7001, 18372, 27072)
GROUP BY HWSD2_SMU_ID, LAYER
HAVING COUNT(*) > 1
ORDER BY num_registros DESC;
```

### 10.2 Ver todos los perfiles de un tipo de suelo
```sql
SELECT 
    ID as perfil_id,
    LAYER,
    TOPDEP,
    BOTDEP,
    TEXTURE_USDA,
    ORG_CARBON,
    PH_WATER,
    CEC_SOIL
FROM HWSD2_LAYERS
WHERE HWSD2_SMU_ID = 7001
ORDER BY ID, TOPDEP;
```

### 10.3 Comparar valores antes/después de consolidación
```sql
-- Ver variabilidad entre perfiles del mismo tipo
SELECT 
    HWSD2_SMU_ID,
    LAYER,
    ID as perfil,
    ROUND(ORG_CARBON, 3) as OC,
    ROUND(PH_WATER, 1) as pH,
    CEC_SOIL
FROM HWSD2_LAYERS
WHERE HWSD2_SMU_ID = 7001
  AND LAYER = 'D1'
  AND ORG_CARBON > 0
ORDER BY HWSD2_SMU_ID, ID;
```

### 10.4 Verificar tabla D_ROOTS (para OSD)
```sql
SELECT * FROM D_ROOTS;
```

### 10.5 Detectar inconsistencias en profundidades
```sql
SELECT 
    HWSD2_SMU_ID,
    LAYER,
    TOPDEP,
    BOTDEP,
    BOTDEP - TOPDEP as espesor_cm
FROM HWSD2_LAYERS
WHERE HWSD2_SMU_ID IN (7001, 18372, 27072)
  AND (BOTDEP <= TOPDEP OR BOTDEP - TOPDEP > 100)  -- Capas anómalas
ORDER BY HWSD2_SMU_ID, TOPDEP;
```

### 10.6 Verificar consistencia CLAY + SAND + SILT ≈ 100%
```sql
SELECT 
    HWSD2_SMU_ID,
    LAYER,
    CLAY,
    SAND,
    SILT,
    CLAY + SAND + SILT as suma_total,
    ABS((CLAY + SAND + SILT) - 100) as desviacion
FROM HWSD2_LAYERS
WHERE HWSD2_SMU_ID IN (7001, 18372, 27072)
  AND LAYER = 'D1'
  AND CLAY > 0
  AND ABS((CLAY + SAND + SILT) - 100) > 5  -- Desviación >5%
ORDER BY desviacion DESC;
```

### 10.7 Encontrar registros con múltiples anomalías
```sql
SELECT 
    HWSD2_SMU_ID,
    LAYER,
    ID,
    CASE WHEN ORG_CARBON < 0 OR ORG_CARBON > 20 THEN 'OC_anómalo' ELSE 'OK' END as check_OC,
    CASE WHEN PH_WATER < 3 OR PH_WATER > 11 THEN 'pH_anómalo' ELSE 'OK' END as check_pH,
    CASE WHEN TEB > CEC_SOIL THEN 'TEB>CEC' ELSE 'OK' END as check_TEB,
    CASE WHEN BSAT < 0 OR BSAT > 100 THEN 'BS_anómalo' ELSE 'OK' END as check_BS,
    CASE WHEN ESP < 0 OR ESP > 100 THEN 'ESP_anómalo' ELSE 'OK' END as check_ESP
FROM HWSD2_LAYERS
WHERE HWSD2_SMU_ID IN (7001, 18372, 27072, 27073)
  AND LAYER = 'D1'
  AND (
      ORG_CARBON < 0 OR ORG_CARBON > 20 OR
      PH_WATER < 3 OR PH_WATER > 11 OR
      TEB > CEC_SOIL OR
      BSAT < 0 OR BSAT > 100 OR
      ESP < 0 OR ESP > 100
  );
```

---

## 📊 Queries de Reporte Final

### Resumen completo para validar el output del script
```sql
-- Ejecutar DESPUÉS de generar el Excel
-- Comparar con estadísticas del archivo generado

SELECT 
    'Tipos de suelo únicos' as metrica,
    COUNT(DISTINCT HWSD2_SMU_ID) as valor
FROM HWSD2_LAYERS
WHERE HWSD2_SMU_ID IN (7001, 18372, 27072, 27073, 27074)

UNION ALL

SELECT 
    'Capas con datos',
    COUNT(DISTINCT LAYER)
FROM HWSD2_LAYERS
WHERE HWSD2_SMU_ID IN (7001, 18372, 27072, 27073, 27074)
  AND ORG_CARBON > 0

UNION ALL

SELECT 
    'Total registros válidos',
    COUNT(*)
FROM HWSD2_LAYERS
WHERE HWSD2_SMU_ID IN (7001, 18372, 27072, 27073, 27074)
  AND ORG_CARBON > 0

UNION ALL

SELECT 
    'Suelos vérticos (WRB)',
    COUNT(DISTINCT s.HWSD2_SMU_ID)
FROM HWSD2_SMU s
LEFT JOIN D_WRB4 w4 ON s.WRB4 = w4.CODE
LEFT JOIN D_WRB2 w2 ON s.WRB2 = w2.CODE
WHERE s.HWSD2_SMU_ID IN (7001, 18372, 27072, 27073, 27074)
  AND (w4.VALUE LIKE '%Vertic%' OR w2.Value LIKE '%Vertic%')

UNION ALL

SELECT 
    'Suelos vérticos (propiedades)',
    COUNT(DISTINCT HWSD2_SMU_ID)
FROM HWSD2_LAYERS
WHERE HWSD2_SMU_ID IN (7001, 18372, 27072, 27073, 27074)
  AND LAYER = 'D1'
  AND CLAY > 35
  AND CEC_CLAY > 40;
```

---

## 💡 Tips de Uso

1. **Ajustar IDs**: Reemplaza `(7001, 18372, 27072, ...)` con tus IDs específicos en todas las queries

2. **SQLite Browser**: Usa [DB Browser for SQLite](https://sqlitebrowser.org/) para ejecutar estas queries visualmente

3. **Exportar resultados**: 
```bash
sqlite3 HWSD2.db < tu_query.sql > resultados.csv
```

4. **Python alternativo**:
```python
import sqlite3
import pandas as pd

conn = sqlite3.connect('HWSD2.db')
df = pd.read_sql_query("TU QUERY AQUÍ", conn)
print(df)
conn.close()
```

5. **Guardar queries frecuentes**: Crea un archivo `queries_frecuentes.sql` con tus queries más usadas

---

## 🎯 Queries Recomendadas para Validación

Antes de ejecutar el script principal, ejecutar:
1. Query **2.1** - Verificar IDs existen
2. Query **3.1** - Contar capas disponibles
3. Query **4.1** - Detectar valores inválidos

Después de ejecutar el script, ejecutar:
1. Query **4.3** - Verificar cálculo de BS
2. Query **5.1** - Confirmar clasificación WRB
3. Query **Resumen completo** - Validar estadísticas finales

---

## ⚠️ Advertencias

- Algunas queries pueden tardar varios minutos en bases de datos grandes
- Siempre usa `LIMIT` al explorar nuevas queries
- Los códigos de tablas de referencia pueden variar entre versiones de HWSD2
- Verifica que los nombres de columnas coincidan con tu versión de HWSD2

---

Esta sección te permite auditar completamente la extracción de datos y verificar que el script está funcionando correctamente.

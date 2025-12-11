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
├── script_hwsd2_to_pyaez.py          # Script principal
├── README.md                          # Este archivo
├── HWSD2.db                          # Base de datos HWSD2
│
└── outputs/                          # Archivos generados
    └── eswatini_soil_ALL_LAYERS_pyaez_CORRECTED.xlsx
```

---

## 🚀 Uso

### Ejecución básica:
```bash
python script_hwsd2_to_pyaez.py
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
**`eswatini_soil_ALL_LAYERS_pyaez_CORRECTED.xlsx`**

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

## 📌 Versión

**v1.0.0** - Diciembre 2024
- Implementación inicial con todas las correcciones
- Soporte para 7 capas de profundidad
- Validaciones automáticas
- Documentación completa

---

## ✨ Próximas Mejoras

- [ ] Soporte para múltiples regiones en un solo run
- [ ] Exportar también a formato CSV
- [ ] Visualizaciones automáticas de distribuciones
- [ ] Integración directa con PyAEZ
- [ ] Validación contra datos de campo (si disponibles)

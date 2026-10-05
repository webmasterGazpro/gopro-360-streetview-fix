<div align="center">

# 🌍 GoPro MAX (.360) to Google Street View Studio
### Extractor automático de GPX limpio y sincronizador de reloj UTC para videos 360°

![Python](https://img.shields.io/badge/Python-3.8%2B-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Platform](https://img.shields.io/badge/Platform-macOS%20%7C%20Windows%20%7C%20Linux-000000?style=for-the-badge&logo=apple&logoColor=white)
![ExifTool](https://img.shields.io/badge/Powered%20by-ExifTool-10B981?style=for-the-badge)
![Street View](https://img.shields.io/badge/Google-Street%20View%20Studio-4285F4?style=for-the-badge&logo=googlemaps&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-F59E0B?style=for-the-badge)

</div>

---

## ⚠️ El Problema

Las versiones recientes de **GoPro Player** presentan dos fallos críticos al exportar videos `.360` a `.mp4` para subirlos a **[Google Street View Studio](https://streetviewstudio.maps.google.com/)**:

1. **Error `No GPS data` (Triángulo naranja):** Incluso activando la casilla *Retain GPMF data*, Street View Studio suele rechazar la pista GPS incrustada en el `.mp4`.
2. **Encabezado vacío al extraer con ExifTool tradicional:** El archivo `.360` guarda una primera coordenada en el encabezado `Main` sin etiqueta de fecha/hora (`Warning: [Minor] Tag 'Main:gpsdatetime' not defined`), dejando el primer punto `<time></time>` vacío en el `.gpx` y provocando que Google lo rechace.
3. **Desfase de zona horaria (`Timestamps don't overlap`):** GoPro Player estampa en el archivo `.mp4` la **hora local** de exportación de tu computadora, mientras que los satélites GPS guardan la ruta `.gpx` en **horario universal UTC**. Al subir ambos archivos, Google detecta varias horas de diferencia y rechaza el recorrido.

---

## 🚀 La Solución (`gopro360_streetview_fix.py`)

Este script en Python resuelve todo el flujo automáticamente en **2 segundos** sin volver a renderizar el video ni perder calidad:

- ✅ **Filtra cabeceras corruptas:** Crea una plantilla dinámica (`#[IF] $gpslatitude $gpslongitude $gpsdatetime`) que extrae únicamente los puntos satelitales válidos con marca de tiempo completa desde tu archivo `.360`.
- 🕒 **Sincroniza el reloj del `.mp4` a UTC:** Lee el primer segundo exacto en horario UTC del archivo `.gpx` generado y actualiza los encabezados internos (`CreateDate`, `TrackCreateDate`, `MediaCreateDate`) de tu archivo `.mp4`.
- 📦 **Procesamiento individual o por lotes:** Puedes arrastrar un solo archivo `.360` o procesar decenas de recorridos dentro de una carpeta con un solo comando.

---

## 🛠️ Requisitos Previos

Necesitas tener instalado **Python 3** y **ExifTool** en tu computadora:

### En macOS (vía Homebrew):
```bash
brew install exiftool
```

### En Windows (vía Winget):
```powershell
winget install OliverBetz.ExifTool
```

---

## 💻 Cómo Usarlo

### Paso 1: Prepara tus archivos
Coloca en una misma carpeta tu archivo original **`.360`** de la GoPro y el archivo **`.mp4`** exportado desde GoPro Player con **exactamente el mismo nombre**:

```text
📂 Mi_Carpeta_360/
 ├── 📄 gopro360_streetview_fix.py
 ├── 🎥 recorrido_01.360
 └── 🎬 recorrido_01.mp4
```

### Paso 2: Ejecuta el script

**Opción A — Procesar todos los videos de la carpeta automáticamente:**
```bash
python3 gopro360_streetview_fix.py
```

**Opción B — Procesar un archivo específico:**
```bash
python3 gopro360_streetview_fix.py recorrido_01.360
```

### Salida esperada en Terminal:
```text
🎬 Analizando: recorrido_01.360 ...
   ✅ GPX generado: recorrido_01.gpx (385 puntos GPS extraídos)
   🕒 MP4 sincronizado a UTC (2026:10:02 15:28:50): recorrido_01.mp4
   🚀 ¡Listo para subir MP4 + GPX a Google Street View Studio!
```

---

## 🗺️ Paso 3: Subir a Google Street View Studio

1. Entra a [Google Street View Studio](https://streetviewstudio.maps.google.com/) y haz clic en **Subir**.
2. Selecciona tu archivo **`recorrido_01.mp4`** (ya sincronizado por el script).
3. Haz clic en los **tres puntos verticales (`⋮`)** en la tarjeta del video y selecciona **Añadir GPX / Upload GPX**.
4. Elige el archivo **`recorrido_01.gpx`** generado por el script.
5. ¡Listo! El triángulo de advertencia desaparecerá al instante y el estado cambiará a **Procesando**.

---

## 📄 Licencia

Distribuido bajo la licencia **MIT**. Eres libre de usar, modificar y compartir este código.

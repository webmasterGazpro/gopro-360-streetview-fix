#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
=============================================================================
GOPRO 360 TO GOOGLE STREET VIEW STUDIO - GPX EXTRACTOR & TIME SYNC
=============================================================================
Resuelve los 2 errores más comunes al subir videos de GoPro MAX (.360 -> .mp4)
a Google Street View Studio:
  1. Extrae el archivo .gpx limpio desde el archivo original .360 (ignorando
     encabezados vacíos para evitar errores de lectura en Google).
  2. Si encuentra el archivo .mp4 con el mismo nombre en la carpeta, sincroniza
     automáticamente su reloj interno a la hora exacta UTC del GPS para evitar
     el error de "Timestamps don't overlap".

Requisitos:
  - Tener instalado ExifTool:
      macOS (Homebrew): brew install exiftool
      Windows (Winget): winget install OliverBetz.ExifTool

Cómo usarlo:
  Opción A (Procesar todos los videos de la carpeta actual):
      python3 gopro360_streetview_fix.py

  Opción B (Arrastrar o indicar un archivo .360 específico):
      python3 gopro360_streetview_fix.py MI_VIDEO.360
=============================================================================
"""

import sys
import re
import shutil
import subprocess
from pathlib import Path

# Plantilla GPX que filtra puntos sin timestamp para que Street View no falle
GPX_FMT = """#[HEAD]<?xml version="1.0" encoding="utf-8"?>
#[HEAD]<gpx version="1.0" creator="ExifTool" xmlns="http://www.topografix.com/GPX/1/0">
#[HEAD]<trk><trkseg>
#[IF] $gpslatitude $gpslongitude $gpsdatetime
#[BODY]<trkpt lat="$gpslatitude#" lon="$gpslongitude#">
#[BODY]  <ele>$gpsaltitude#</ele>
#[BODY]  <time>${gpsdatetime#;my ($ss)=/\.\d+/g;DateFmt("%Y-%m-%dT%H:%M:%SZ");s/Z/${ss}Z/ if $ss}</time>
#[BODY]</trkpt>
#[TAIL]</trkseg></trk></gpx>
"""


def check_exiftool() -> bool:
    if shutil.which("exiftool") is None:
        print("❌ Error: No se encontró 'exiftool' instalado en tu sistema.")
        print("   👉 En Mac instala con: brew install exiftool")
        print("   👉 En Windows descarga desde: https://exiftool.org/")
        return False
    return True


def process_video(file_360: Path, fmt_path: Path):
    base_name = file_360.stem
    parent_dir = file_360.parent
    gpx_path = parent_dir / f"{base_name}.gpx"

    print(f"
🎬 Analizando: {file_360.name} ...")

    # 1. Extraer GPX desde el archivo .360
    cmd_extract = ["exiftool", "-m", "-p", str(fmt_path), "-ee", str(file_360)]
    with open(gpx_path, "w", encoding="utf-8") as out_file:
        subprocess.run(cmd_extract, stdout=out_file, stderr=subprocess.DEVNULL, text=True)

    if not gpx_path.exists():
        print(f"   ❌ No se pudo generar el archivo GPX para {file_360.name}.")
        return

    content = gpx_path.read_text(encoding="utf-8", errors="ignore")
    points = re.findall(r'<trkpt\s+lat="([^"]+)"\s+lon="([^"]+)">', content)
    times = re.findall(r'<time>([0-9]{4})-([0-9]{2})-([0-9]{2})T([0-9]{2}:[0-9]{2}:[0-9]{2}).*?</time>', content)

    if not points or not times:
        print(f"   ⚠️ El archivo '{file_360.name}' no contiene datos GPS grabados.")
        gpx_path.unlink(missing_ok=True)
        return

    first_utc = f"{times[0][0]}:{times[0][1]}:{times[0][2]} {times[0][3]}"
    print(f"   ✅ GPX generado: {gpx_path.name} ({len(points)} puntos GPS extraídos)")

    # 2. Buscar si existe el archivo .mp4 con el mismo nombre para sincronizar su hora
    mp4_candidates = [parent_dir / f"{base_name}.mp4", parent_dir / f"{base_name}.MP4"]
    file_mp4 = next((f for f in mp4_candidates if f.exists()), None)

    if file_mp4:
        cmd_sync = [
            "exiftool", "-m", "-overwrite_original",
            f"-AllDates={first_utc}",
            f"-TrackCreateDate={first_utc}",
            f"-TrackModifyDate={first_utc}",
            f"-MediaCreateDate={first_utc}",
            f"-MediaModifyDate={first_utc}",
            "-Keys:CreationDate=",
            "-UserData:DateTimeOriginal=",
            str(file_mp4)
        ]
        res = subprocess.run(cmd_sync, capture_output=True, text=True)
        if res.returncode == 0:
            print(f"   🕒 MP4 sincronizado a UTC ({first_utc}): {file_mp4.name}")
            print("   🚀 ¡Listo para subir MP4 + GPX a Google Street View Studio!")
        else:
            print(f"   ⚠️ Se creó el GPX, pero hubo un detalle al sincronizar {file_mp4.name}.")
    else:
        print(f"   ℹ️ Nota: No se encontró '{base_name}.mp4' en la misma carpeta.")
        print("      (Si ya tienes tu .gpx, recuerda que el .mp4 debe tener el mismo nombre si quieres sincronizar su reloj).")


def main():
    if not check_exiftool():
        sys.exit(1)

    # Si el usuario pasó un archivo como argumento (ej. arrastrándolo a la Terminal)
    if len(sys.argv) > 1:
        targets = [Path(arg).resolve() for arg in sys.argv[1:] if Path(arg).exists()]
    else:
        # Si no pasó argumentos, busca todos los .360 en la carpeta actual
        work_dir = Path.cwd()
        targets = sorted([
            f for f in work_dir.iterdir()
            if f.is_file() and f.suffix.lower() == ".360" and not f.name.startswith("._")
        ])

    if not targets:
        print("⚠️ No se encontraron archivos .360 en esta carpeta.")
        print("   Coloca este script junto a tus archivos .360 (y .mp4) o arrastra un archivo .360 al comando.")
        sys.exit(0)

    fmt_path = Path.cwd() / "_temp_gpx.fmt"
    fmt_path.write_text(GPX_FMT, encoding="utf-8")

    try:
        for target in targets:
            if target.suffix.lower() == ".360":
                process_video(target, fmt_path)
            else:
                print(f"⚠️ Ignorando '{target.name}' (debe ser un archivo .360).")
    finally:
        fmt_path.unlink(missing_ok=True)

    print("
✨ Proceso terminado.
")


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Aplica la práctica S13 encima de un proyecto individual que ya tiene S12."""
from pathlib import Path
import re
import shutil
import sys

folder = Path(__file__).resolve().parent
root = folder.parent.parent
layout = root / "app/src/main/res/layout/activity_main.xml"
ids = ["etNombreTarea", "btnAgregarTarea", "lvTareas", "tvListaEtiqueta", "tvNota"]
resource = root / "app/src/main/res/values/taskmaster_s12.xml"

try:
    if not layout.exists() or not resource.exists():
        raise RuntimeError("Faltan archivos de S12. Aplica y verifica primero la actualización S12.")
    xml = layout.read_text(encoding="utf-8")
    missing = [s for s in ids if f'@+id/{s}' not in xml and f'@id/{s}' not in xml]
    if missing:
        raise RuntimeError("La interfaz no coincide con S12. Faltan IDs: " + ", ".join(missing))

    candidates = list((root / "app/src/main/java").rglob("MainActivity.kt")) if (root / "app/src/main/java").exists() else []
    if (root / "app/src/main/kotlin").exists():
        candidates += list((root / "app/src/main/kotlin").rglob("MainActivity.kt"))
    if len(candidates) != 1:
        raise RuntimeError(f"Se esperaba un único MainActivity.kt; encontrados: {len(candidates)}. No se modificó el proyecto.")
    main = candidates[0]
    original = main.read_text(encoding="utf-8")
    package_match = re.search(r'^\s*package\s+([\w.]+)\s*$', original, re.MULTILINE)
    if not package_match:
        raise RuntimeError("No se pudo localizar el package de MainActivity.kt.")
    package = package_match.group(1)
    helper = main.parent / "TaskMasterS13.kt"
    if helper.exists() and "fun Activity.configurarTaskMasterS13()" not in helper.read_text(encoding="utf-8"):
        raise RuntimeError("TaskMasterS13.kt ya existe y contiene código diferente. No se sobrescribió.")
    template = (folder / "TaskMasterS13.kt.template").read_text(encoding="utf-8")
    expected = template.replace("__PACKAGE__", package)

    # Únicamente insertar después de la carga real del layout; no modificar si usa otro mecanismo.
    pattern = r'(setContentView\s*\(\s*R\.layout\.activity_main\s*\))'
    if not re.search(pattern, original):
        raise RuntimeError("No se encontró setContentView(R.layout.activity_main). Revisar MainActivity.kt antes de aplicar S13.")

    backup_dir = root / "respaldos/S12"
    backup_dir.mkdir(parents=True, exist_ok=True)
    backup = backup_dir / "MainActivity.kt.bak"
    if not backup.exists():
        shutil.copy2(main, backup)

    if "configurarTaskMasterS13()" not in original:
        modified = re.sub(pattern, r'\1\n        configurarTaskMasterS13()', original, count=1)
        main.write_text(modified, encoding="utf-8")
        print("OK: llamada a configurarTaskMasterS13() añadida en MainActivity.kt")
    else:
        print("OK: MainActivity.kt ya tenía la llamada S13; no se duplicó")
    if not helper.exists() or helper.read_text(encoding="utf-8") != expected:
        helper.write_text(expected, encoding="utf-8")
        print("OK: TaskMasterS13.kt creado/actualizado con package", package)
    else:
        print("OK: TaskMasterS13.kt ya estaba correcto")
    print("Listo. Compila con: ./gradlew assembleDebug")
except Exception as exc:
    print("ERROR:", exc, file=sys.stderr)
    sys.exit(1)

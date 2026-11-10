#!/usr/bin/env python3
"""Aplica S14 sobre un TaskMaster que ya completó S12 y S13."""
from pathlib import Path
import re
import sys

folder = Path(__file__).resolve().parent
root = folder.parent.parent
layout = root / "app/src/main/res/layout/activity_main.xml"
resources = root / "app/src/main/res/values/taskmaster_s12.xml"
required_ids = [
    "main", "etNombreTarea", "btnAgregarTarea", "lvTareas",
    "rgPrioridad", "rbAlta", "rbMedia", "rbBaja", "spCategoria",
    "cbRecordatorio", "ibEliminarEjemplo", "tvListaEtiqueta", "tvNota",
]

def ensure(condition, message):
    if not condition:
        raise RuntimeError(message)

try:
    ensure(layout.is_file() and resources.is_file(),
           "Faltan los XML de S12. Aplica primero esa sesión.")
    xml = layout.read_text(encoding="utf-8")
    missing = [x for x in required_ids if not re.search(r'android:id\s*=\s*["\']@\+?id/' + re.escape(x) + r'["\']', xml)]
    ensure(not missing, "Los controles de S12 no coinciden. IDs faltantes: " + ", ".join(missing))
    ensure("categorias_taskmaster_s12" in resources.read_text(encoding="utf-8") and
           "tareas_ejemplo_taskmaster_s12" in resources.read_text(encoding="utf-8"),
           "Faltan las listas de recursos de S12.")

    candidates = []
    for base in (root / "app/src/main/java", root / "app/src/main/kotlin"):
        if base.is_dir():
            candidates += list(base.rglob("MainActivity.kt"))
    ensure(len(candidates) == 1, "Se esperaba un único MainActivity.kt; encontrados: " + str(len(candidates)))
    main = candidates[0]
    original = main.read_text(encoding="utf-8")
    match = re.search(r'^\s*package\s+([\w.]+)\s*$', original, re.MULTILINE)
    ensure(match is not None, "MainActivity.kt no declara su paquete Kotlin.")
    package = match.group(1)
    ensure(re.search(r'setContentView\s*\(\s*R\.layout\.activity_main\s*\)', original),
           "MainActivity.kt no carga activity_main.xml.")
    s13 = main.parent / "TaskMasterS13.kt"
    ensure(s13.is_file() and "configurarTaskMasterS13" in s13.read_text(encoding="utf-8"),
           "No se encontró TaskMasterS13.kt. Completa primero S13.")
    new_file = main.parent / "TaskMasterS14.kt"
    template = (folder / "TaskMasterS14.kt.template").read_text(encoding="utf-8")
    output = template.replace("__PACKAGE__", package)
    ensure(not new_file.exists() or "fun Activity.configurarTaskMasterS14()" in new_file.read_text(encoding="utf-8"),
           "TaskMasterS14.kt ya existe con otro contenido. No se sobrescribió.")

    # S14 reemplaza la llamada S13: no activar ambos listeners a la vez.
    old_call = r'(?m)^(\s*)configurarTaskMasterS13\(\)\s*$'
    has_s14 = bool(re.search(r'(?m)^\s*configurarTaskMasterS14\(\)\s*$', original))
    ensure(has_s14 or re.search(old_call, original),
           "No se encontró la llamada a configurarTaskMasterS13() en MainActivity.kt.")
    updated_main = original if has_s14 else re.sub(
        old_call, lambda m: m.group(1) + "configurarTaskMasterS14()", original, count=1
    )
    # Verificar que no se llamen simultáneamente las dos funciones.
    ensure(not re.search(old_call, updated_main),
           "Se detectó otra llamada a S13; revisar MainActivity.kt manualmente.")

    # Cambiar solo el texto del CheckBox existente, sin alterar su ID ni estructura.
    checkbox = re.search(r'<CheckBox\b[^>]*?/>', xml, re.DOTALL)
    ensure(checkbox is not None and 'cbRecordatorio' in checkbox.group(),
           "No se encontró el CheckBox de S12 para actualizar su etiqueta.")
    new_checkbox, count = re.subn(
        r'android:text\s*=\s*"[^"]*"',
        'android:text="Tarea importante"', checkbox.group(), count=1
    )
    ensure(count == 1, "El CheckBox no contiene el atributo android:text.")
    updated_xml = xml[:checkbox.start()] + new_checkbox + xml[checkbox.end():]

    # Mantener copias fuera de res/ para no introducir un .bak en recursos Android.
    backup_dir = root / "respaldos/S13"
    backup_dir.mkdir(parents=True, exist_ok=True)
    for source, target in ((main, "MainActivity.kt.bak"), (layout, "activity_main.xml.bak")):
        destination = backup_dir / target
        if not destination.exists():
            destination.write_bytes(source.read_bytes())

    if updated_main != original:
        main.write_text(updated_main, encoding="utf-8")
    if not new_file.exists() or new_file.read_text(encoding="utf-8") != output:
        new_file.write_text(output, encoding="utf-8")
    if updated_xml != xml:
        layout.write_text(updated_xml, encoding="utf-8")

    print("OK: MainActivity.kt activa configurarTaskMasterS14() (sin duplicar S13).")
    print("OK: TaskMasterS14.kt creado/actualizado para el paquete " + package)
    print("OK: CheckBox muestra 'Tarea importante'; se conservan los IDs de S12.")
    print("OK: respaldos guardados fuera de app/src/main/res/.")
    print("Siguiente paso: compilar y probar las funciones de S14.")
except Exception as exc:
    print("ERROR:", exc, file=sys.stderr)
    sys.exit(1)

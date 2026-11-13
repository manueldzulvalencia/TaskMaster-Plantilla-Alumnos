#!/usr/bin/env python3
"""Aplica S16 sobre TaskMaster después de S14, sin duplicar listeners ni tocar XML."""
from pathlib import Path
import argparse
import re
import sys

FOLDER = Path(__file__).resolve().parent
ROOT = FOLDER.parent.parent


def ensure(condition, message):
    if not condition:
        raise RuntimeError(message)


def run(dry_run: bool):
    layout = ROOT / "app/src/main/res/layout/activity_main.xml"
    resources = ROOT / "app/src/main/res/values/taskmaster_s12.xml"
    ensure(layout.is_file() and resources.is_file(), "Faltan los XML de S12.")
    xml = layout.read_text(encoding="utf-8")
    for field in ("etNombreTarea", "btnAgregarTarea", "lvTareas", "rgPrioridad",
                  "spCategoria", "cbRecordatorio", "ibEliminarEjemplo"):
        ensure(re.search(r'android:id\s*=\s*["\']@\+?id/' + field + r'["\']', xml),
               "Falta el control XML requerido: " + field)

    candidates = []
    for base in (ROOT / "app/src/main/java", ROOT / "app/src/main/kotlin"):
        if base.is_dir():
            candidates += list(base.rglob("MainActivity.kt"))
    ensure(len(candidates) == 1, "Se esperaba un único MainActivity.kt; encontrados: " + str(len(candidates)))
    main = candidates[0]
    original_main = main.read_text(encoding="utf-8")
    pkg_match = re.search(r'^\s*package\s+([\w.]+)\s*$', original_main, re.MULTILINE)
    ensure(pkg_match is not None, "MainActivity.kt no declara paquete Kotlin.")
    package = pkg_match.group(1)
    ensure(re.search(r'setContentView\s*\(\s*R\.layout\.activity_main\s*\)', original_main),
           "MainActivity.kt no carga activity_main.xml.")

    s13 = main.parent / "TaskMasterS13.kt"
    s14 = main.parent / "TaskMasterS14.kt"
    s16 = main.parent / "TaskMasterS16.kt"
    ensure(s13.is_file() and "configurarTaskMasterS13" in s13.read_text(encoding="utf-8"),
           "Falta S13. Aplica esa sesión primero.")
    ensure(s14.is_file(), "Falta TaskMasterS14.kt. Aplica primero S14.")
    source_s14 = s14.read_text(encoding="utf-8")
    ensure("fun Activity.configurarTaskMasterS14()" in source_s14,
           "TaskMasterS14.kt no contiene la función esperada.")

    template = (FOLDER / "TaskMasterS16.kt.template").read_text(encoding="utf-8")
    ensure(template.startswith("package __PACKAGE__\n"), "Plantilla Kotlin S16 inválida.")
    output = template.replace("__PACKAGE__", package, 1)

    # Verificamos la estructura de la S14 real antes de reemplazarla en el punto de entrada.
    # Si el proyecto difiere del S14 facilitado por el docente, se detiene sin alterar archivos.
    expected_s14 = output.replace("configurarTaskMasterS16", "configurarTaskMasterS14")
    expected_s14 = expected_s14.replace(
        "Sesión 16: notificaciones Toast en el formulario funcional de TaskMaster.",
        "Sesión 14: formulario funcional de TaskMaster.")
    expected_s14 = expected_s14.replace(
        " * Conserva XML de S12 y toda la lógica de S14; reemplaza solo la configuración de eventos.",
        " * Conserva los controles XML de S12 y sustituye la configuración de eventos de S13.")
    expected_s14 = expected_s14.replace(
        "S16: TaskMaster informa cuándo una tarea se agrega, se elimina o falta información.",
        "S14: agrega tareas completas; toca una tarea y usa la papelera para eliminarla.")
    expected_s14 = expected_s14.replace(
        "    // 4. Leer, validar y registrar tareas con sus opciones (Toast de error o éxito).",
        "    // 4. Leer, validar y registrar tareas con sus opciones.")
    expected_s14 = expected_s14.replace(
        "    // 5. Eliminar SOLO la tarea seleccionada y mostrar Toast de advertencia o éxito.",
        "    // 5. Eliminar SOLO la tarea seleccionada y actualizar la lista.")
    expected_s14 = expected_s14.replace('"Ingresa el nombre de la tarea", Toast.LENGTH_SHORT',
                                        '"No puedes agregar una tarea vacía", Toast.LENGTH_SHORT')
    expected_s14 = expected_s14.replace('"Tarea agregada correctamente", Toast.LENGTH_SHORT',
                                        '"Tarea agregada", Toast.LENGTH_SHORT')
    expected_s14 = expected_s14.replace('"Tarea eliminada correctamente", Toast.LENGTH_SHORT',
                                        '"Tarea eliminada", Toast.LENGTH_SHORT')
    ensure(source_s14.strip() == expected_s14.strip(),
           "TaskMasterS14.kt difiere de la plantilla S14 original. No se sobrescribió ni se instaló S16."
           " Revisa las modificaciones del proyecto antes de actualizar.")
    ensure(not s16.exists() or s16.read_text(encoding="utf-8") == output,
           "TaskMasterS16.kt ya existe con contenido diferente. No se sobrescribió.")

    call_s14 = r'(?m)^(\s*)configurarTaskMasterS14\(\)\s*$'
    call_s16 = r'(?m)^\s*configurarTaskMasterS16\(\)\s*$'
    has_s14 = bool(re.search(call_s14, original_main))
    has_s16 = bool(re.search(call_s16, original_main))
    ensure(has_s14 != has_s16,
           "MainActivity.kt debe llamar exactamente a S14 o a S16 (no ambas).")
    ensure(not re.search(r'(?m)^\s*configurarTaskMasterS13\(\)\s*$', original_main),
           "MainActivity.kt todavía activa S13. Completa primero S14.")
    ensure(len(re.findall(r'configurarTaskMasterS1[46]\(\)', original_main)) == 1,
           "Llamadas duplicadas a S14/S16 en MainActivity.kt.")
    updated_main = original_main if has_s16 else re.sub(
        call_s14, lambda m: m.group(1) + "configurarTaskMasterS16()", original_main, count=1)

    if dry_run:
        print("OK: S14 validada; actualización S16 compatible con el proyecto.")
        print("OK: MainActivity.kt podrá activar configurarTaskMasterS16().")
        print("OK: Se conservarán las tareas, prioridad, categoría, importancia y eliminación de S14.")
        print("OK: No se modificará el XML ni se duplicarán listeners.")
        print("Prueba concluida: no se modificó ningún archivo.")
        return

    # Realizar respaldo fuera de res/ y escribir solo al terminar las validaciones.
    backup_dir = ROOT / "respaldos/S14"
    backup_dir.mkdir(parents=True, exist_ok=True)
    for source, filename in ((main, "MainActivity.kt.bak"), (s14, "TaskMasterS14.kt.bak")):
        backup = backup_dir / filename
        if not backup.exists():
            backup.write_bytes(source.read_bytes())
    if updated_main != original_main:
        main.write_text(updated_main, encoding="utf-8")
    if not s16.exists():
        s16.write_text(output, encoding="utf-8")
    print("OK: MainActivity.kt activa configurarTaskMasterS16() (sin duplicar S14).")
    print("OK: TaskMasterS16.kt listo para el paquete " + package)
    print("OK: lógica de S14 conservada y cuatro mensajes Toast disponibles.")
    print("OK: XML intacto; respaldos en respaldos/S14/.")
    print("Siguiente paso: compilar y probar TaskMaster-S16.apk.")


def main():
    parser = argparse.ArgumentParser(description="Actualización automática TaskMaster S16")
    parser.add_argument("--probar", action="store_true", help="Valida compatibilidad sin modificar el proyecto")
    args = parser.parse_args()
    try:
        run(dry_run=args.probar)
    except Exception as exc:
        print("ERROR:", exc, file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()

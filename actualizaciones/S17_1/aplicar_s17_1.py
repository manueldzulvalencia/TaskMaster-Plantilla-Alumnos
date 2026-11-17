#!/usr/bin/env python3
"""S17.1: mejora visual segura de TaskMaster S17; no cambia la lógica de tareas."""
from pathlib import Path
import argparse
import re
import sys
import xml.etree.ElementTree as ET

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent


def check(condition, message):
    if not condition:
        raise RuntimeError(message)


def run(dry_run):
    candidates = [p for b in (ROOT / 'app/src/main/java', ROOT / 'app/src/main/kotlin')
                  if b.is_dir() for p in b.rglob('MainActivity.kt')]
    check(len(candidates) == 1, 'Se necesita un único MainActivity.kt.')
    main = candidates[0]
    main_old = main.read_text(encoding='utf-8')
    pkg_match = re.search(r'^\s*package\s+([\w.]+)\s*$', main_old, re.M)
    check(pkg_match is not None, 'No se encontró el paquete de Kotlin.')
    pkg = pkg_match.group(1)
    check('setContentView(R.layout.activity_main)' in main_old or
          re.search(r'setContentView\s*\(\s*R\.layout\.activity_main\s*\)', main_old),
          'MainActivity no usa activity_main.')
    check((main.parent / 'TaskMasterS16.kt').is_file(), 'Falta S16.')
    s17 = main.parent / 'TaskMasterS17.kt'
    check(s17.is_file(), 'Falta TaskMasterS17.kt. Debes aplicar S17 primero.')
    s17_text = s17.read_text(encoding='utf-8')
    check('fun Activity.configurarTaskMasterS17()' in s17_text and
          'startActivity(navegar)' in s17_text and 'Toast.makeText' in s17_text,
          'No se reconoció la versión original de S17: se cancela para protegerla.')
    main_layout = ROOT / 'app/src/main/res/layout/activity_main.xml'
    detail_layout = ROOT / 'app/src/main/res/layout/activity_detalle.xml'
    detail_kt = main.parent / 'DetalleActivity.kt'
    check(all(p.is_file() for p in (main_layout, detail_layout, detail_kt)),
          'Faltan archivos de interfaz S17.')
    original_layout = detail_layout.read_text(encoding='utf-8')
    check('tvDetalleTarea' in original_layout and 'btnVolverTareas' in original_layout,
          'DetalleActivity tiene un diseño no reconocido. No se sobrescribirá.')
    check('EXTRA_TAREA' in detail_kt.read_text(encoding='utf-8'),
          'No se encontró la recepción de datos en DetalleActivity.')
    check(re.search(r'configurarTaskMasterS17\(\)', main_old) is not None or
          re.search(r'configurarTaskMasterS171\(\)', main_old) is not None,
          'MainActivity no está activando S17.')
    check(len(re.findall(r'configurarTaskMasterS17(?:1)?\(\)', main_old)) == 1,
          'Se detectaron llamadas duplicadas a S17 o S17.1.')
    new_main = re.sub(r'(?m)^(\s*)configurarTaskMasterS17\(\)(\s*)$',
                      r'\1configurarTaskMasterS171()\2', main_old, count=1)
    check('configurarTaskMasterS171()' in new_main, 'No se pudo activar S17.1.')
    new_kotlin = (HERE / 'TaskMasterS171.kt.template').read_text(encoding='utf-8').replace('__PACKAGE__', pkg)
    new_detail = (HERE / 'activity_detalle.xml.template').read_text(encoding='utf-8')
    drawables = [(ROOT / 'app/src/main/res/drawable' / name,
                  (HERE / name).read_text(encoding='utf-8'))
                 for name in ('tm171_header.xml', 'tm171_card.xml', 'tm171_button.xml')]
    for txt in (new_detail, *(x[1] for x in drawables)):
        ET.fromstring(txt)
    new_kt_file = main.parent / 'TaskMasterS171.kt'
    outputs = [(new_kt_file, new_kotlin), (detail_layout, new_detail), *drawables]
    backup = ROOT / 'respaldos/S17_1'
    original_backup = backup / 'activity_detalle.xml.bak'
    # Impedir modificar un XML intervenido sin respaldo correspondiente.
    if detail_layout.read_text(encoding='utf-8') != new_detail and original_backup.is_file():
        check(original_layout == original_backup.read_text(encoding='utf-8'),
              'El XML de detalle ha cambiado desde la instalación S17.1. No se sobrescribirá.')
    for dest, content in outputs:
        if dest != detail_layout and dest.exists():
            check(dest.read_text(encoding='utf-8') == content,
                  f'{dest.name} tiene modificaciones: no se sobrescribirá.')
    if dry_run:
        print('OK: S17 detectada; Toast, Intents y funciones anteriores conservados.')
        print('OK: se aplicará estilo visual a la pantalla principal y al detalle.')
        print('OK: prueba completada sin alterar archivos.')
        return
    backup.mkdir(parents=True, exist_ok=True)
    for original in (main, detail_layout):
        dest = backup / (original.name + '.bak')
        if not dest.exists():
            dest.write_bytes(original.read_bytes())
    for dest, content in outputs:
        dest.parent.mkdir(parents=True, exist_ok=True)
        if not dest.exists() or dest.read_text(encoding='utf-8') != content:
            dest.write_text(content, encoding='utf-8')
    if main_old != new_main:
        main.write_text(new_main, encoding='utf-8')
    print('OK: S17.1 aplicada correctamente.')
    print('OK: S17 y S16 no fueron modificadas; los listeners siguen activos.')
    print('OK: respaldos disponibles en respaldos/S17_1/.')
    print('Siguiente: ./gradlew assembleDebug y probar en un dispositivo.')


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--probar', action='store_true', help='No modifica archivos')
    args = parser.parse_args()
    try:
        run(args.probar)
    except Exception as error:
        print('ERROR:', error, file=sys.stderr)
        sys.exit(1)

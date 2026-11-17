#!/usr/bin/env python3
"""S17: navegación desde TaskMaster S16 a una nueva Activity, sin perder S16."""
from pathlib import Path
import argparse
import re
import sys
import xml.etree.ElementTree as ET

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent
ANDROID_NS = 'http://schemas.android.com/apk/res/android'


def require(ok, msg):
    if not ok:
        raise RuntimeError(msg)


def render(name, package):
    return (HERE / name).read_text(encoding='utf-8').replace('__PACKAGE__', package)


def run(dry_run=False):
    bases = [ROOT / 'app/src/main/java', ROOT / 'app/src/main/kotlin']
    mains = [f for b in bases if b.exists() for f in b.rglob('MainActivity.kt')]
    require(len(mains) == 1, f'Se requiere un MainActivity.kt único; encontrados: {len(mains)}')
    main = mains[0]
    main_text = main.read_text(encoding='utf-8')
    match = re.search(r'^\s*package\s+([\w.]+)\s*$', main_text, re.M)
    require(match, 'MainActivity.kt no declara package')
    package = match.group(1)
    require(re.search(r'setContentView\s*\(\s*R\.layout\.activity_main\s*\)', main_text), 'No se encontró activity_main en MainActivity')
    s16 = main.parent / 'TaskMasterS16.kt'
    s17 = main.parent / 'TaskMasterS17.kt'
    detail = main.parent / 'DetalleActivity.kt'
    detail_layout = ROOT / 'app/src/main/res/layout/activity_detalle.xml'
    main_layout = ROOT / 'app/src/main/res/layout/activity_main.xml'
    manifest = ROOT / 'app/src/main/AndroidManifest.xml'
    for f in (s16, main_layout, manifest):
        require(f.is_file(), f'Falta archivo requerido: {f.relative_to(ROOT)}')
    s16_text = s16.read_text(encoding='utf-8')
    require('fun Activity.configurarTaskMasterS16()' in s16_text, 'No se reconoce función S16')
    require('listaVisual.setOnItemClickListener' in s16_text, 'No se encontró listener de selección S16')
    require('"Tarea agregada correctamente"' in s16_text and '"Tarea eliminada correctamente"' in s16_text, 'No se reconocen Toast principales S16')
    require('android:id="@+id/lvTareas"' in main_layout.read_text(encoding='utf-8') or re.search(r'@\+?id/lvTareas', main_layout.read_text(encoding='utf-8')), 'No se encuentra lvTareas de S12')

    # Solo se permite el cambio puntual en S16: el toque de una tarea abre DetalleActivity.
    # La función activa de MainActivity cambia de S16 a S17; no duplica listeners.
    s17_text = s16_text.replace('fun Activity.configurarTaskMasterS16()', 'fun Activity.configurarTaskMasterS17()', 1)
    marker = 'import android.app.Activity\n'
    require(s17_text.count(marker) == 1, 'No se encontró import Activity único en S16')
    s17_text = s17_text.replace(marker, marker + 'import android.content.Intent\n', 1)
    listener = '''        listaVisual.setItemChecked(posicion, true)
'''
    require(s17_text.count(listener) == 1, 'La selección de tareas S16 no coincide con lo esperado')
    s17_text = s17_text.replace(listener, listener + '''        val navegar = Intent(this, DetalleActivity::class.java)
        navegar.putExtra(DetalleActivity.EXTRA_TAREA, tareas[posicion])
        startActivity(navegar)
''', 1)
    s17_text = s17_text.replace('Sesión 16: notificaciones Toast en el formulario funcional de TaskMaster.', 'Sesión 17: navegación por Activities manteniendo los Toast de S16.', 1)
    s17_text = s17_text.replace('S16: TaskMaster informa cuándo una tarea se agrega, se elimina o falta información.', 'S17: toca una tarea para abrir su detalle; conserva los Toast.', 1)
    require('configurarTaskMasterS17' in s17_text and 'putExtra' in s17_text, 'No fue posible generar TaskMasterS17')

    detail_text = render('DetalleActivity.kt.template', package)
    layout_text = (HERE / 'activity_detalle.xml.template').read_text(encoding='utf-8')
    ET.fromstring(layout_text)  # XML válido antes de escribir
    ET.fromstring(main_layout.read_text(encoding='utf-8'))
    manifest_text = manifest.read_text(encoding='utf-8')
    require('<!DOCTYPE' not in manifest_text and '<!ENTITY' not in manifest_text, 'Manifest contiene entidades no admitidas')
    manifest_tree = ET.fromstring(manifest_text)
    require(manifest_tree.tag == 'manifest', 'Manifest inválido')
    apps = manifest_tree.findall('application')
    require(len(apps) == 1, 'Se requiere un único application en el Manifest')
    app = apps[0]
    activity_names = [x.get(f'{{{ANDROID_NS}}}name', '') for x in app.findall('activity')]
    require('.DetalleActivity' not in activity_names and f'{package}.DetalleActivity' not in activity_names or s17.is_file(), 'Manifest ya tiene DetalleActivity sin S17; revisar manualmente')
    # Preservar texto y comentarios: inserción puntual antes de </application>.
    if '.DetalleActivity' not in activity_names and f'{package}.DetalleActivity' not in activity_names:
        closes = list(re.finditer(r'</application\s*>', manifest_text))
        require(len(closes) == 1, 'No se puede insertar la Activity de forma segura')
        insert = '        <activity android:name=".DetalleActivity" android:exported="false" />\n    '
        updated_manifest = manifest_text[:closes[0].start()] + insert + manifest_text[closes[0].start():]
    else:
        updated_manifest = manifest_text
    ET.fromstring(updated_manifest)
    s16_call = re.findall(r'(?m)^\s*configurarTaskMasterS16\(\)\s*$', main_text)
    s17_call = re.findall(r'(?m)^\s*configurarTaskMasterS17\(\)\s*$', main_text)
    require(len(s16_call) + len(s17_call) == 1, 'MainActivity debe activar S16 o S17, nunca ambas')
    updated_main = main_text if s17_call else re.sub(r'(?m)^(\s*)configurarTaskMasterS16\(\)\s*$', r'\1configurarTaskMasterS17()', main_text, count=1)
    require(not re.search(r'(?m)^\s*configurarTaskMasterS14\(\)\s*$', updated_main), 'S14 sigue activa; revisar antes de continuar')
    outputs = [(s17, s17_text), (detail, detail_text), (detail_layout, layout_text)]
    for f, text in outputs:
        require(not f.exists() or f.read_text(encoding='utf-8') == text, f'{f.name} ya existe con cambios distintos: no se sobrescribirá')
    if dry_run:
        print('OK: S16 reconocida, MainActivity, controles XML y Manifest compatibles.')
        print('OK: se crearán DetalleActivity, diseño visual y TaskMasterS17.')
        print('OK: no se modificará S16 ni activity_main.xml. Ningún archivo alterado.')
        return
    # Respaldar antes de escribir: verificaciones anteriores completadas.
    backup = ROOT / 'respaldos/S17'
    backup.mkdir(parents=True, exist_ok=True)
    for f in (main, manifest):
        target = backup / (f.name + '.bak')
        if not target.exists():
            target.write_bytes(f.read_bytes())
    for f, text in outputs:
        f.parent.mkdir(parents=True, exist_ok=True)
        if not f.exists():
            f.write_text(text, encoding='utf-8')
    if main_text != updated_main:
        main.write_text(updated_main, encoding='utf-8')
    if manifest_text != updated_manifest:
        manifest.write_text(updated_manifest, encoding='utf-8')
    print('OK: S17 aplicada. La S16 original se conserva sin modificaciones.')
    print('OK: tocar una tarea abrirá DetalleActivity con su información.')
    print('OK: respaldo del MainActivity y Manifest en respaldos/S17/.')
    print('Siguiente paso: ./gradlew assembleDebug y comprobar el APK.')


if __name__ == '__main__':
    p = argparse.ArgumentParser()
    p.add_argument('--probar', action='store_true', help='Verificar compatibilidad sin cambios')
    args = p.parse_args()
    try:
        run(args.probar)
    except Exception as ex:
        print('ERROR:', ex, file=sys.stderr)
        sys.exit(1)

#!/usr/bin/env python3
"""S22: agrega centro multimedia configurable a TaskMaster Pro S21, sin borrar datos.

Ejemplos:
  python3 actualizaciones/S22/aplicar_s22.py --probar
  python3 actualizaciones/S22/aplicar_s22.py
  python3 actualizaciones/S22/aplicar_s22.py --editar
"""
import argparse
from datetime import datetime
import json
from pathlib import Path
import shutil
import sys
import xml.etree.ElementTree as ET
from xml.sax.saxutils import escape

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent
MAIN = ROOT / 'app/src/main'
PKG = MAIN / 'java/com/itcancun/mjdzul/taskmaster'
UI = PKG / 'TaskMasterS20.kt'
MANIFEST = MAIN / 'AndroidManifest.xml'
ACTIVITY = PKG / 'MultimediaS22Activity.kt'
VALUES = MAIN / 'res/values/tm22_multimedia.xml'
RAW = MAIN / 'res/raw/tm22_audio_demo.wav'
S20 = ROOT / 'configuracion/proyecto.json'
S21 = ROOT / 'documentacion/S21_avances.md'
CONFIG = ROOT / 'configuracion/multimedia_s22.json'
REPORT = ROOT / 'documentacion/S22_avances.md'
START_OLD = '"Estadísticas", "Exportar datos", "Configuración", "Acerca de"'
START_NEW = '"Estadísticas", "Exportar datos", "Centro multimedia", "Configuración", "Acerca de"'
BRANCH = '"Centro multimedia" -> host.startActivity(Intent(host, MultimediaS22Activity::class.java))'
ACTIVITY_TAG = '<activity android:name=".MultimediaS22Activity" android:exported="false" />'

USOS = {'1': 'Instrucciones', '2': 'Recordatorios', '3': 'Apoyo al aprendizaje', '4': 'Bienestar', '5': 'Otro'}


def ask(msg, default):
    response = input(f'{msg} [{default}]: ').strip()
    return response if response else default


def limited(value, max_len, label):
    value = ' '.join(value.split()).strip()
    if not value or len(value) > max_len:
        raise ValueError(f'{label}: ingresa entre 1 y {max_len} caracteres.')
    if any(ord(c) < 32 for c in value):
        raise ValueError(f'{label}: caracteres de control no permitidos.')
    return value


def elegir_config(args, proyecto):
    if CONFIG.exists() and not args.editar:
        cfg = json.loads(CONFIG.read_text(encoding='utf-8'))
        validar_config(cfg)
        print('Se conserva la configuración S22 existente:', cfg['tituloModulo'])
        print('Para modificarla, utiliza --editar.')
        return cfg
    anterior = json.loads(CONFIG.read_text(encoding='utf-8')) if CONFIG.exists() else {}
    default_title = anterior.get('tituloModulo', 'Centro multimedia')
    default_msg = anterior.get('mensaje', 'Reproduce el audio de prueba y practica los controles.')
    print('\n=== S22 · Personalización del módulo multimedia ===')
    print('Aplicación existente:', proyecto['nombreApp'])
    print('El audio de prueba es común; el título y los textos son propios de tu app.')
    title = limited(ask('1. Nombre del módulo', default_title), 60, 'Nombre del módulo')
    print('\n2. Propósito del audio:')
    for key, val in USOS.items():
        print(f'   {key}. {val}')
    prev = anterior.get('proposito', 'Apoyo al aprendizaje')
    prev_opt = next((k for k, v in USOS.items() if v == prev), '5')
    op = ask('Opción', prev_opt)
    if op not in USOS:
        raise ValueError('Opción de propósito no válida. Elige 1–5.')
    if op == '5':
        proposito = limited(ask('Escribe tu propósito', prev if prev not in USOS.values() else 'Orientación a usuarios'), 80, 'Propósito')
    else:
        proposito = USOS[op]
    msg = limited(ask('3. Mensaje que verá el usuario', default_msg), 180, 'Mensaje')
    prev_show = anterior.get('mostrarIndicaciones', True)
    answer = ask('4. ¿Mostrar indicaciones? (S/N)', 'S' if prev_show else 'N').upper()
    if answer not in ('S', 'N'):
        raise ValueError('Responde S o N.')
    return {'version': 1, 'tituloModulo': title, 'proposito': proposito,
            'mensaje': msg, 'mostrarIndicaciones': answer == 'S',
            'audio': 'tm22_audio_demo.wav', 'audioDescripcion': 'Audio instrumental de prueba sin voz'}


def validar_config(cfg):
    for k, length in [('tituloModulo', 60), ('proposito', 80), ('mensaje', 180)]:
        if not isinstance(cfg.get(k), str):
            raise ValueError('Configuración S22 inválida: '+k)
        limited(cfg[k], length, k)
    if not isinstance(cfg.get('mostrarIndicaciones'), bool):
        raise ValueError('Configuración S22 inválida: mostrarIndicaciones')


def verificar():
    required = [UI, MANIFEST, S20, S21, HERE / 'MultimediaS22Activity.kt.template',
                HERE / 'tm22_audio_demo.wav', ROOT / 'app/build.gradle.kts']
    missing = [str(p.relative_to(ROOT)) for p in required if not p.is_file()]
    if missing:
        raise ValueError('Faltan archivos S20/S21 o de la actualización: '+', '.join(missing))
    proyecto = json.loads(S20.read_text(encoding='utf-8'))
    if not all(proyecto.get(k) for k in ('nombreApp', 'giro', 'colorPrincipal', 'categorias')):
        raise ValueError('Personalización S20 incompleta')
    ui = UI.read_text(encoding='utf-8')
    if 'class TaskMasterS20' not in ui or 'ExportarS21Activity::class.java' not in ui:
        raise ValueError('Debes aplicar S21 antes de S22. La exportación debe permanecer conectada.')
    if START_NEW not in ui:
        if ui.count(START_OLD) != 1:
            raise ValueError('No se encontró el menú de S21 compatible con S22.')
        ui = ui.replace(START_OLD, START_NEW, 1)
    if BRANCH not in ui:
        needle = '"Exportar datos" -> host.startActivity(Intent(host, ExportarS21Activity::class.java))'
        if ui.count(needle) != 1:
            raise ValueError('No se encontró la entrada de exportación de S21 para añadir multimedia.')
        ui = ui.replace(needle, needle+'\n                    '+BRANCH, 1)
    if ui.count(BRANCH) != 1 or ui.count('"Centro multimedia"') != 2:
        raise ValueError('Menú multimedia duplicado o mal conectado.')
    manifest = MANIFEST.read_text(encoding='utf-8')
    if '.MultimediaS22Activity' not in manifest:
        if manifest.count('</application>') != 1:
            raise ValueError('Manifest sin cierre único de application.')
        manifest = manifest.replace('</application>', '    '+ACTIVITY_TAG+'\n    </application>', 1)
    try:
        parsed = ET.fromstring(manifest)
        ns = '{http://schemas.android.com/apk/res/android}'
        matches = [el for el in parsed.iter('activity') if el.attrib.get(ns+'name') == '.MultimediaS22Activity']
        if len(matches) != 1 or matches[0].attrib.get(ns+'exported') != 'false':
            raise ValueError('MultimediaS22Activity debe estar declarada una sola vez como privada')
    except ET.ParseError as ex:
        raise ValueError('Manifest inválido: '+str(ex))
    source = (HERE / 'MultimediaS22Activity.kt.template').read_text(encoding='utf-8')
    if not all(x in source for x in ('MediaPlayer.create', 'R.raw.tm22_audio_demo', 'player?.release()', 'R.string.tm22_titulo')):
        raise ValueError('Plantilla Kotlin multimedia incompleta')
    if (HERE / 'tm22_audio_demo.wav').stat().st_size < 10000:
        raise ValueError('Audio original de prueba incompleto')
    return proyecto, ui, manifest, source


def xml_config(cfg):
    xml = '''<?xml version="1.0" encoding="utf-8"?>\n<resources>\n'''
    for key, value in [('tm22_titulo', cfg['tituloModulo']), ('tm22_proposito', cfg['proposito']),
                       ('tm22_mensaje', cfg['mensaje'])]:
        # XML string resources: escape HTML/XML; neutralize Android formatting and apostrophes
        safe = escape(value.replace('\\', '\\\\').replace("'", "\\'").replace('@', '\\@').replace('?', '\\?'))
        safe = safe.replace('%', '%%')
        xml += f'    <string name="{key}" formatted="false">{safe}</string>\n'
    xml += f'    <bool name="tm22_mostrar_indicaciones">{str(cfg["mostrarIndicaciones"]).lower()}</bool>\n</resources>\n'
    ET.fromstring(xml)
    return xml


def build_outputs(args):
    proyecto, ui, manifest, source = verificar()
    cfg = elegir_config(args, proyecto)
    validar_config(cfg)
    outputs = {UI: ui, MANIFEST: manifest, ACTIVITY: source, VALUES: xml_config(cfg),
               CONFIG: json.dumps(cfg, indent=2, ensure_ascii=False)+'\n'}
    if not REPORT.exists():
        outputs[REPORT] = f'''# S22 · Registro técnico automático: centro multimedia\n\n- **Aplicación:** {proyecto['nombreApp']}\n- **Giro:** {proyecto['giro']}\n- **Tema:** 3.4 Multimedia (reproducción, pausa, reanudación y detención)\n- **Nombre del módulo:** {cfg['tituloModulo']}\n- **Propósito:** {cfg['proposito']}\n- **Mensaje:** {cfg['mensaje']}\n- **Mostrar indicaciones:** {'Sí' if cfg['mostrarIndicaciones'] else 'No'}\n- **Audio:** archivo instrumental original incluido en la app; mismo audio de prueba para todos.\n\n## Cambios técnicos\n\n1. `TaskMasterS20.kt`: incorpora la opción «Centro multimedia» sin eliminar «Exportar datos».\n2. `MultimediaS22Activity.kt`: controles reproducir, pausar, reanudar y detener.\n3. `res/raw/tm22_audio_demo.wav`: sonido instrumental local (sin internet).\n4. `res/values/tm22_multimedia.xml`: textos personalizados.\n5. `AndroidManifest.xml`: actividad multimedia privada.\n\n## Validación en Android (pendiente)\n\nComprobar controles, audio audible, salida de pantalla, conservación de tareas y exportación S21.\nLa evidencia académica y las observaciones del alumno se documentan en **Google Docs S22**, no aquí.\n\nEste archivo es generado automáticamente una sola vez. Al ejecutar --editar se actualiza la configuración, pero se conserva este archivo previo.\n'''
    if not RAW.exists():
        outputs[RAW] = (HERE / 'tm22_audio_demo.wav').read_bytes()
    return outputs


def aplicar(outputs):
    diff = {}
    for p, content in outputs.items():
        if not p.exists() or (p.read_bytes() if isinstance(content, bytes) else p.read_text(encoding='utf-8')) != content:
            diff[p] = content
    if not diff:
        print('OK: S22 ya estaba aplicada. Ningún archivo modificado.')
        return
    backups = ROOT / 'respaldos' / ('S22_'+datetime.now().strftime('%Y%m%d_%H%M%S_%f'))
    for p in diff:
        if p.exists():
            b = backups / p.relative_to(ROOT)
            b.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(p, b)
    for p, content in diff.items():
        p.parent.mkdir(parents=True, exist_ok=True)
        if isinstance(content, bytes):
            p.write_bytes(content)
        else:
            p.write_text(content, encoding='utf-8')
    print(f'OK: S22 instalada. {len(diff)} archivos nuevos/actualizados.')
    print('Menú «Centro multimedia» habilitado; S21 «Exportar datos» conservado.')
    print('Registro técnico automático: documentacion/S22_avances.md')
    print('Compila, guarda versiones/TaskMaster-S22.apk e instala ENCIMA de S21.')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--probar', action='store_true', help='Validar sin escribir ni solicitar respuestas')
    parser.add_argument('--editar', action='store_true', help='Volver a preguntar las opciones')
    args = parser.parse_args()
    if args.probar and args.editar:
        parser.error('--probar y --editar no se combinan')
    try:
        if args.probar:
            verificar()
            print('OK --probar: S20+S21 detectadas; menú y recursos S22 compatibles. No se modificó nada.')
        else:
            aplicar(build_outputs(args))
    except (ValueError, OSError, json.JSONDecodeError) as exc:
        print('ERROR S22:', exc, file=sys.stderr)
        sys.exit(1)

if __name__ == '__main__':
    main()

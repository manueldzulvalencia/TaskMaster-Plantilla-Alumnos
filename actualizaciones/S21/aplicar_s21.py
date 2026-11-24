#!/usr/bin/env python3
"""S21 · TaskMaster Pro: habilitar exportación de tareas JSON con selector Android.

Uso: python3 actualizaciones/S21/aplicar_s21.py [--probar]
--probar: verifica todo sin cambiar archivos.
Normal: instala la Activity exportadora, conecta menú y genera registro técnico.
No edita identidad S20 ni JSON almacenado en Android. Es idempotente.
"""
import argparse
from datetime import datetime
import json
from pathlib import Path
import shutil
import sys
import xml.etree.ElementTree as ET

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent
SOURCE = ROOT / 'app/src/main'
PKG = SOURCE / 'java/com/itcancun/mjdzul/taskmaster'
MAIN_UI = PKG / 'TaskMasterS20.kt'
NEW_ACTIVITY = PKG / 'ExportarS21Activity.kt'
MANIFEST = SOURCE / 'AndroidManifest.xml'
CONFIG = ROOT / 'configuracion/proyecto.json'
S20_REPORT = ROOT / 'documentacion/S20_decisiones.md'
S21_REPORT = ROOT / 'documentacion/S21_avances.md'

OLD = 'if (destino == "Ver JSON") mostrarJson() else navegar(destino)'
NEW = '''when (destino) {
                    "Ver JSON" -> mostrarJson()
                    "Exportar datos" -> host.startActivity(Intent(host, ExportarS21Activity::class.java))
                    else -> navegar(destino)
                }'''
ACTIVITY_TAG = '<activity android:name=".ExportarS21Activity" android:exported="false" />'


def preparar():
    required = [MAIN_UI, MANIFEST, CONFIG, HERE / 'ExportarS21Activity.kt.template',
                PKG / 'TareasRepository.kt', PKG / 'Tarea.kt', ROOT / 'app/build.gradle.kts']
    missing = [str(x.relative_to(ROOT)) for x in required if not x.is_file()]
    if missing:
        raise ValueError('Falta S20.2 o archivos necesarios: ' + ', '.join(missing))
    cfg = json.loads(CONFIG.read_text(encoding='utf-8'))
    if not all(cfg.get(k) for k in ['nombreApp', 'giro', 'colorPrincipal', 'categorias']):
        raise ValueError('Configuración S20 incompleta')
    ui = MAIN_UI.read_text(encoding='utf-8')
    if '"Exportar datos"' not in ui or 'class TaskMasterS20' not in ui:
        raise ValueError('No se reconoce TaskMasterS20: consulta la actualización instalada')
    if 'ExportarS21Activity::class.java' not in ui:
        if ui.count(OLD) != 1:
            raise ValueError('Menú S20 no compatible: no se puede conectar Exportar datos con seguridad')
        ui = ui.replace(OLD, NEW, 1)
    else:
        if ui.count('ExportarS21Activity::class.java') != 1:
            raise ValueError('La acción de exportación aparece varias veces en el menú')
    manifest = MANIFEST.read_text(encoding='utf-8')
    if '.ExportarS21Activity' not in manifest:
        if manifest.count('</application>') != 1:
            raise ValueError('AndroidManifest.xml sin etiqueta de aplicación reconocible')
        manifest = manifest.replace('</application>', '    '+ACTIVITY_TAG+'\n    </application>', 1)
    try:
        parsed = ET.fromstring(manifest)
        ns = '{http://schemas.android.com/apk/res/android}'
        matched = [x for x in parsed.iter('activity') if x.attrib.get(ns+'name') == '.ExportarS21Activity']
        if len(matched) != 1 or matched[0].attrib.get(ns+'exported') != 'false':
            raise ValueError('La Activity exportadora debe declararse una vez y ser privada')
    except ET.ParseError as e:
        raise ValueError('Manifest XML inválido: '+str(e))
    exporter = (HERE / 'ExportarS21Activity.kt.template').read_text(encoding='utf-8')
    if 'ACTION_CREATE_DOCUMENT' not in exporter or 'openFileInput("tareas.json")' not in exporter:
        raise ValueError('Plantilla de exportación incompleta')
    outputs = {MAIN_UI: ui, MANIFEST: manifest, NEW_ACTIVITY: exporter}
    if not S21_REPORT.exists():
        outputs[S21_REPORT] = f'''# S21 · Registro técnico automático · Exportación JSON

- **Aplicación:** {cfg['nombreApp']}
- **Giro:** {cfg['giro']}
- **Tema:** 3.3 Almacenamiento externo y compartido
- **Función implementada:** Exportar una copia de tareas.json mediante ACTION_CREATE_DOCUMENT.
- **Archivo de salida sugerido:** {''.join(c if c.isalnum() or c in '_-' else '_' for c in cfg['nombreApp']).strip('_')[:40] or 'TaskMasterPro'}_S21.json
- **Formato:** JSON v2; todos los campos de cada tarea se conservan.
- **Garantía de diseño:** no se modifica el JSON privado durante la exportación.
- **Permisos:** no requiere permisos generales de almacenamiento.

## Qué cambió en el código

1. `TaskMasterS20.kt`: se activa la entrada «Exportar datos» del menú.
2. `ExportarS21Activity.kt`: selector de destino, escritura de copia y mensaje de resultado.
3. `AndroidManifest.xml`: registra la nueva Activity de forma no exportada.

## Validación pendiente por el estudiante

La instalación del código NO garantiza por sí sola que se haya ejecutado la prueba.
Realizar en Android/BlueStacks: guardar tarea, exportar, abrir copia y verificar datos.
Documentar evidencias y reflexión en el Google Docs de S21.

**Nota:** Este archivo se genera automáticamente una sola vez. No sustituye Google Docs.
'''
    return outputs


def aplicar(outputs):
    diffs = {p: content for p, content in outputs.items()
             if not p.exists() or p.read_text(encoding='utf-8') != content}
    if not diffs:
        print('OK: S21 ya está instalada. No se modificó ningún archivo.'); return
    backups = ROOT / 'respaldos' / ('S21_'+datetime.now().strftime('%Y%m%d_%H%M%S_%f'))
    for path in diffs:
        if path.exists():
            dest = backups / path.relative_to(ROOT)
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(path, dest)
    for path, content in diffs.items():
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding='utf-8')
    print(f'OK: S21 aplicada. Archivos creados/actualizados: {len(diffs)}.')
    print('La configuración S20 y las tareas del teléfono se conservan.')
    print('Bitácora técnica: documentacion/S21_avances.md')
    print('Continuar: compilar el APK e instalarlo ENCIMA de S20, sin desinstalar.')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--probar', action='store_true', help='Solo validar; no escribir nada')
    args = parser.parse_args()
    try:
        changes = preparar()
        if args.probar:
            print(f'OK --probar: S20 detectada, {len(changes)} archivos S21 previstos/validados, sin modificaciones.')
            return
        aplicar(changes)
    except Exception as error:
        print('ERROR S21:', error, file=sys.stderr)
        sys.exit(1)

if __name__ == '__main__':
    main()

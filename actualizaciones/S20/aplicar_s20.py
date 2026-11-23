#!/usr/bin/env python3
"""S20 · TaskMaster Pro: desde S19, sin pasos intermedios.

--probar: verifica compatibilidad sin alterar el proyecto ni pedir datos.
--editar: vuelve a preguntar la identidad del proyecto, conservando app/JSON.
--nombre, --giro, --publico, --color: configuración no interactiva (útil en pruebas).
"""
import argparse
from datetime import datetime
import json
from pathlib import Path
import re
import shutil
import sys
import xml.etree.ElementTree as ET
from xml.sax.saxutils import escape

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent
SRC = ROOT / 'app/src/main'
PKG = SRC / 'java/com/itcancun/mjdzul/taskmaster'
RES = SRC / 'res'
MAIN = PKG / 'MainActivity.kt'
DETAIL = PKG / 'DetalleActivity.kt'
MANIFEST = SRC / 'AndroidManifest.xml'
LAY_MAIN = RES / 'layout/activity_main.xml'
LAY_DETAIL = RES / 'layout/activity_detalle.xml'
CONFIG = ROOT / 'configuracion/proyecto.json'
REPORT = ROOT / 'documentacion/S20_decisiones.md'
COLORES = {'1': ('Morado', '#6824C4'), '2': ('Azul', '#235EB2'), '3': ('Verde', '#278669'), '4': ('Naranja', '#CC772C')}
GIROS = {'1': 'Educación', '2': 'Negocios', '3': 'Hogar', '4': 'Salud y bienestar', '5': 'Personal', '6': 'Otro'}
CATEGORIAS = {
    'Educación': ['Tareas', 'Exámenes', 'Proyectos'],
    'Negocios': ['Pedidos', 'Clientes', 'Pendientes'],
    'Hogar': ['Limpieza', 'Compras', 'Mantenimiento'],
    'Salud y bienestar': ['Ejercicio', 'Alimentación', 'Hábitos'],
    'Personal': ['Personal', 'Trámites', 'Recordatorios'],
    'Otro': ['General', 'Prioritario', 'Pendiente'],
}
FILES = {
    'Tarea.kt.template': PKG / 'Tarea.kt',
    'TareasRepository.kt.template': PKG / 'TareasRepository.kt',
    'TaskMasterDetalleS19.kt.template': PKG / 'TaskMasterDetalleS19.kt',
    'TaskMasterS20.kt.template': PKG / 'TaskMasterS20.kt',
    'EnConstruccionActivity.kt.template': PKG / 'EnConstruccionActivity.kt',
}

def comprobar():
    required = [MAIN, DETAIL, MANIFEST, LAY_MAIN, LAY_DETAIL,
                PKG/'TaskMasterS19.kt', PKG/'TaskMasterDetalleS19.kt',
                RES/'layout/tm172_item.xml', ROOT/'app/build.gradle.kts']
    missing = [str(p.relative_to(ROOT)) for p in required if not p.is_file()]
    if missing:
        raise ValueError('No se detecta la S19 completa. Faltan: ' + ', '.join(missing))
    texto = MAIN.read_text(encoding='utf-8')
    detalle = DETAIL.read_text(encoding='utf-8')
    if 'configurarTaskMasterS19()' not in texto and 'configurarTaskMasterS20()' not in texto:
        raise ValueError('MainActivity no tiene una llamada de S19/S20 reconocible')
    if 'configurarDetalleVisualS19()' not in detalle:
        raise ValueError('DetalleActivity no tiene la configuración visual S19')
    if 'DAMN-S18-LIFECYCLE' not in texto or 'DAMN-S18-LIFECYCLE' not in detalle:
        raise ValueError('No se encontraron las trazas S18 de ciclo de vida; verifica la versión')
    ET.parse(MANIFEST); ET.parse(LAY_MAIN); ET.parse(LAY_DETAIL)
    for nombre in FILES:
        if not (HERE/nombre).is_file(): raise ValueError('Falta plantilla ' + nombre)
    return texto

def elegir(mensaje, options, default):
    print('\n' + mensaje)
    for k, v in options.items(): print(f'  {k}. {v}')
    ans = input(f'Opción [{default}]: ').strip() or default
    if ans not in options: raise ValueError('Opción no válida: ' + ans)
    return options[ans]

def nueva_config(args):
    if CONFIG.exists() and not args.editar and not any([args.nombre,args.giro,args.publico,args.color]):
        stored=json.loads(CONFIG.read_text(encoding='utf-8'))
        print('Se conservará la configuración existente:',stored['nombreApp'])
        return stored
    if not sys.stdin.isatty() and not all([args.nombre,args.giro,args.publico,args.color]):
        raise ValueError('Se requieren datos interactivos o --nombre --giro --publico --color')
    print('\n=== TASKMASTER PRO · PERSONALIZACIÓN S20 ===')
    nombre = (args.nombre or input('Nombre de la aplicación: ')).strip()
    if not 2 <= len(nombre) <= 35 or '\n' in nombre: raise ValueError('Nombre: entre 2 y 35 caracteres')
    giro = args.giro or elegir('Selecciona giro:', GIROS, '1')
    if giro in GIROS: giro = GIROS[giro]
    if giro not in CATEGORIAS: raise ValueError('Giro no reconocido')
    publico = (args.publico or input('Público objetivo: ')).strip()
    if not 2 <= len(publico) <= 70 or '\n' in publico: raise ValueError('Público: entre 2 y 70 caracteres')
    color = args.color or elegir('Elige un color:', {k: v[0] for k,v in COLORES.items()}, '2')
    if color in COLORES: color = COLORES[color][1]
    if color not in [c[1] for c in COLORES.values()]: raise ValueError('Color no reconocido')
    return {'nombreApp':nombre,'giro':giro,'publicoObjetivo':publico,'colorPrincipal':color,
            'categorias':CATEGORIAS[giro], 'sesionOrigen':'S19', 'configuracion':'S20'}

def preparar(config,main):
    outputs={p:(HERE/name).read_text(encoding='utf-8') for name,p in FILES.items()}
    if 'configurarTaskMasterS19()' in main:
        main=main.replace('configurarTaskMasterS19()', 'configurarTaskMasterS20()', 1)
    outputs[MAIN] = main
    # Identificadores de las sesiones anteriores: su Kotlin se conserva en el repositorio
    # aunque las pantallas antiguas ya no se invoquen. Esto evita referencias R.id ausentes.
    legacy_ids = ["btnAgregarTarea", "cbRecordatorio", "etNombreTarea", "ibEliminarEjemplo",
                  "lvTareas", "rbAlta", "rbBaja", "rbMedia", "rgPrioridad", "spCategoria",
                  "tvListaEtiqueta", "tvNota", "btnVerJsonS19"]
    outputs[RES/'values/tm20_ids_compat.xml'] = (
        '<?xml version="1.0" encoding="utf-8"?>\n<resources>\n'
        + ''.join(f'    <item type="id" name="{x}" />\n' for x in legacy_ids)
        + '</resources>\n'
    )
    outputs[LAY_MAIN] = '''<?xml version="1.0" encoding="utf-8"?>
<FrameLayout xmlns:android="http://schemas.android.com/apk/res/android"
    android:id="@+id/main" android:layout_width="match_parent"
    android:layout_height="match_parent" android:background="#F6F8FC" />
'''
    detail = LAY_DETAIL.read_text(encoding='utf-8')
    if '@+id/tvDetalleFechaPro' not in detail:
        anchor='<Button android:id="@+id/btnVolverTareas"'
        if detail.count(anchor)!=1: raise ValueError('No se localizó el botón de regreso del detalle S19')
        insert='''<TextView android:id="@+id/tvDetalleFechaPro"
            android:layout_width="match_parent" android:layout_height="wrap_content"
            android:layout_marginTop="14dp" android:padding="15dp"
            android:background="@drawable/tm172_card"
            android:text="Fecha sin asignar" android:textSize="16sp" android:textColor="#203759" />
        '''
        detail=detail.replace(anchor,insert+anchor,1)
    outputs[LAY_DETAIL]=detail
    manifest=MANIFEST.read_text(encoding='utf-8')
    # Sustituir solo el atributo de etiqueta de aplicación.
    if 'android:label="@string/app_name"' in manifest:
        manifest=manifest.replace('android:label="@string/app_name"','android:label="@string/tm20_nombre_app"',1)
    elif 'android:label="@string/tm20_nombre_app"' not in manifest:
        raise ValueError('La etiqueta Android del manifiesto es inesperada')
    activity='<activity android:name=".EnConstruccionActivity" android:exported="false" />'
    if '.EnConstruccionActivity' not in manifest:
        manifest=manifest.replace('</application>', '    '+activity+'\n    </application>',1)
    outputs[MANIFEST]=manifest
    categories = '\n'.join('        <item>'+escape(c)+'</item>' for c in config['categorias'])
    values=f'''<?xml version="1.0" encoding="utf-8"?>
<resources>
    <string name="tm20_nombre_app">{escape(config['nombreApp'])}</string>
    <string name="tm20_giro">{escape(config['giro'])}</string>
    <string name="tm20_publico">{escape(config['publicoObjetivo'])}</string>
    <string name="tm20_color">{escape(config['colorPrincipal'])}</string>
    <string-array name="tm20_categorias">
{categories}
    </string-array>
</resources>
'''
    outputs[RES/'values/tm20_identidad.xml']=values
    outputs[CONFIG]=json.dumps(config,ensure_ascii=False,indent=2)+'\n'
    outputs[REPORT]=f'''# S20 · Decisiones de proyecto

- **Nombre:** {config['nombreApp']}
- **Giro:** {config['giro']}
- **Público:** {config['publicoObjetivo']}
- **Color:** {config['colorPrincipal']}
- **Categorías iniciales:** {', '.join(config['categorias'])}

## Comprensión y pruebas

1. ¿Qué problema resolverá mi aplicación? (Responder brevemente)
2. ¿Qué diferencia hay entre tareas.json y las preferencias?
3. ¿Conservo las tareas después de cerrar y abrir? (Sí / No y evidencia)

**Próxima etapa:** S21, almacenamiento externo y adaptación de datos al giro.
'''
    for p,txt in outputs.items():
        if p.suffix=='.xml': ET.fromstring(txt)
    return outputs

def aplicar(outputs):
    changes={p:s for p,s in outputs.items() if not p.exists() or p.read_text(encoding='utf-8')!=s}
    if not changes:
        print('OK: S20 ya aplicada; no hay modificaciones.'); return
    backup=ROOT/'respaldos'/('S20_'+datetime.now().strftime('%Y%m%d_%H%M%S_%f'))
    for file in changes:
        if file.exists():
            dest=backup/file.relative_to(ROOT)
            dest.parent.mkdir(parents=True,exist_ok=True)
            shutil.copy2(file,dest)
    for file,text in changes.items():
        file.parent.mkdir(parents=True,exist_ok=True)
        file.write_text(text,encoding='utf-8')
    print(f'OK: {len(changes)} archivos creados/actualizados. Respaldo local: {backup.relative_to(ROOT)}')
    print('IMPORTANTE: tareas.json se migra en Android al abrir el nuevo APK, NO en Codespaces.')
    print('Instala ENCIMA de S19, con el mismo applicationId y firma. No borres datos.')

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--probar',action='store_true')
    p.add_argument('--editar',action='store_true')
    p.add_argument('--nombre'); p.add_argument('--giro'); p.add_argument('--publico'); p.add_argument('--color')
    args=p.parse_args()
    try:
        original=comprobar()
        if args.probar:
            config=json.loads(CONFIG.read_text(encoding='utf-8')) if CONFIG.exists() else {
                'nombreApp':'StudyMaster','giro':'Educación','publicoObjetivo':'Estudiantes',
                'colorPrincipal':'#235EB2','categorias':CATEGORIAS['Educación'],
                'sesionOrigen':'S19','configuracion':'S20'}
            out=preparar(config,original)
            print(f'OK --probar: S19 detectada, {len(out)} archivos validados, sin cambios en el proyecto.')
            return
        config=nueva_config(args)
        outputs=preparar(config,original)
        aplicar(outputs)
    except Exception as e:
        print('ERROR S20:',e,file=sys.stderr)
        sys.exit(1)

if __name__=='__main__': main()

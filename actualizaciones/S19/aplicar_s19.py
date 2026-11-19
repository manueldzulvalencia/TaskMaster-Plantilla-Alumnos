#!/usr/bin/env python3
"""TaskMaster S19: persistencia JSON privada y nuevo diseño de DetalleActivity.
Requiere S18 definitiva funcionando. No instala S18 ni modifica la lógica de Logcat.
"""
from pathlib import Path
from datetime import datetime
import argparse
import re
import shutil
import sys
import xml.etree.ElementTree as ET

HERE=Path(__file__).resolve().parent
ROOT=HERE.parent.parent
SRC=ROOT/'app/src/main'
PKG=SRC/'java/com/itcancun/mjdzul/taskmaster'
MAIN=PKG/'MainActivity.kt'
DETAIL=PKG/'DetalleActivity.kt'
LAY=SRC/'res/layout'
DRAW=SRC/'res/drawable'
MARK='DAMN-S19-DETALLE'
FILES=[
 ('TaskMasterS19.kt.template', PKG/'TaskMasterS19.kt'),
 ('TaskMasterDetalleS19.kt.template', PKG/'TaskMasterDetalleS19.kt'),
 ('activity_detalle.xml.template', LAY/'activity_detalle.xml'),
 ('tm18_detalle_tarjeta.xml',DRAW/'tm18_detalle_tarjeta.xml'),
 ('tm18_etiqueta_alta.xml',DRAW/'tm18_etiqueta_alta.xml'),
 ('tm18_etiqueta_categoria.xml',DRAW/'tm18_etiqueta_categoria.xml'),
 ('tm18_etiqueta_si.xml',DRAW/'tm18_etiqueta_si.xml'),
]
CALL_RE=re.compile(r'\bconfigurarTaskMasterS(?:17|171|172|19)\(\)')

def prepare():
    required=[MAIN,DETAIL,PKG/'TaskMasterS172.kt',LAY/'tm172_item.xml',LAY/'activity_main.xml',SRC/'AndroidManifest.xml']
    missing=[str(p.relative_to(ROOT)) for p in required if not p.is_file()]
    if missing: raise ValueError('S18 incompleta. Faltan: '+', '.join(missing))
    m=MAIN.read_text(encoding='utf-8')
    d=DETAIL.read_text(encoding='utf-8')
    if 'DAMN-S18-LIFECYCLE' not in m or 'DAMN-S18-LIFECYCLE' not in d:
        raise ValueError('No se detectaron los registros de ciclo de vida de S18 en ambas Activities')
    if not CALL_RE.search(m): raise ValueError('No se encontró la llamada de configuración S17/S18/S19 en MainActivity')
    if not re.search(r'\bconfigurarTaskMasterS19\(\)',m):
        m=CALL_RE.sub('configurarTaskMasterS19()',m,count=1)
    if MARK not in d:
        anchor='findViewById<android.widget.Button>(R.id.btnVolverTareas)'
        if d.count(anchor)!=1: raise ValueError('No se identifica el botón Volver en DetalleActivity.kt')
        d=d.replace(anchor, f'configurarDetalleVisualS19() // {MARK}\n        '+anchor,1)
    # Validación de cada recurso y los IDs críticos antes de modificar nada.
    for original,dest in FILES:
        f=HERE/original
        if not f.is_file(): raise ValueError('Falta archivo del paquete: '+original)
        if original.endswith('.xml') or original.endswith('.xml.template'): ET.parse(f)
    kotlin=(HERE/'TaskMasterS19.kt.template').read_text(encoding='utf-8')
    for required_token in ('configurarTaskMasterS19()', 'cargarTareasS19(', 'guardarTareasS19(tareas)',
                          'R.id.tm181VerDetalle','R.id.tm181Eliminar','AlertDialog.Builder','ajustarAlturaLista(true)'):
        if required_token not in kotlin: raise ValueError('Falta función de S19: '+required_token)
    layout=(HERE/'activity_detalle.xml.template').read_text(encoding='utf-8')
    for required_id in ('tvDetalleTarea','tvDetalleCategoria','tvDetallePrioridad','tvDetalleImportante','btnVolverTareas'):
        if '@+id/'+required_id not in layout: raise ValueError('Falta ID de detalle: '+required_id)
    return {MAIN:m,DETAIL:d,**{dest:(HERE/original).read_text(encoding='utf-8') for original,dest in FILES}}

def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--probar',action='store_true',help='Validar sin modificar el proyecto')
    args=ap.parse_args()
    try:
        outputs=prepare()
        if args.probar:
            print('OK: S18 identificada, recursos S19 y XML verificados. Sin cambios (--probar).')
            print('S19 guardará tareas en tareas.json y renovará DetalleActivity.')
            return
        changes={path:content for path,content in outputs.items() if not path.is_file() or path.read_text(encoding='utf-8')!=content}
        if not changes:
            print('OK: S19 ya instalada; no hay cambios ni duplicados.')
            return
        backup=ROOT/'respaldos'/('S19_'+datetime.now().strftime('%Y%m%d_%H%M%S'))
        for path in changes:
            if path.is_file():
                dest=backup/path.relative_to(ROOT)
                dest.parent.mkdir(parents=True,exist_ok=True)
                shutil.copy2(path,dest)
        for path,content in changes.items():
            path.parent.mkdir(parents=True,exist_ok=True)
            path.write_text(content,encoding='utf-8')
        print('OK: S19 instalada, '+str(len(changes))+' archivos modificados/creados.')
        print('OK: tareas.json privado, guardado tras agregar/eliminar y recuperación al iniciar.')
        print('OK: DetalleActivity estilo portada, Toast, scroll, acciones y Logcat conservados.')
        print('Respaldos:',backup.relative_to(ROOT))
        print('SIGUIENTE: compilar y probar en Android. No hay APK compilado todavía.')
    except Exception as e:
        print('ERROR:',e,file=sys.stderr)
        sys.exit(1)

if __name__=='__main__': main()

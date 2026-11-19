#!/usr/bin/env python3
"""Parche didáctico S19: botón Ver JSON guardado sin ADB ni root.
Requiere S19 instalada. Solo modifica MainActivity.kt y activity_main.xml
además de crear TaskMasterVisorJsonS19.kt. Admite --probar.
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
LAY=SRC/'res/layout/activity_main.xml'
NEW=PKG/'TaskMasterVisorJsonS19.kt'
MARK='DAMN-S19-VISOR-JSON'
ID='btnVerJsonS19'

def plan():
    for p in (MAIN, LAY, PKG/'TaskMasterS19.kt'):
        if not p.is_file(): raise ValueError(f'No se detectó S19 instalada. Falta {p.relative_to(ROOT)}')
    m=MAIN.read_text(encoding='utf-8')
    layout=LAY.read_text(encoding='utf-8')
    if 'configurarTaskMasterS19()' not in m:
        raise ValueError('MainActivity no llama configurarTaskMasterS19(). No se modificó nada.')
    if 'fun Activity.configurarTaskMasterS19()' not in (PKG/'TaskMasterS19.kt').read_text(encoding='utf-8'):
        raise ValueError('No se detectó el módulo S19 correcto.')
    if 'configurarVisorJsonS19()' not in m:
        pattern=r'(?m)^(\s*)configurarTaskMasterS19\(\)\s*$'
        if len(re.findall(pattern,m))!=1:
            raise ValueError('No se encontró una única llamada a S19 en MainActivity.')
        m=re.sub(pattern,lambda x: x.group(0)+'\n'+x.group(1)+f'configurarVisorJsonS19() // {MARK}',m,count=1)
    if f'@+id/{ID}' not in layout:
        anchor='<TextView android:id="@+id/tvNota"'
        if layout.count(anchor)!=1:
            raise ValueError('No se encontró el punto de inserción del botón en activity_main.xml')
        button='''<Button android:id="@+id/btnVerJsonS19"
            android:layout_width="match_parent"
            android:layout_height="wrap_content"
            android:layout_marginLeft="18dp"
            android:layout_marginRight="18dp"
            android:layout_marginTop="10dp"
            android:backgroundTint="#6B21B4"
            android:textColor="#FFFFFF"
            android:text="VER JSON GUARDADO"
            android:contentDescription="Mostrar archivo tareas.json guardado"
            android:textStyle="bold"/>
        '''
        layout=layout.replace(anchor,button+anchor,1)
    ET.fromstring(layout)
    source=(HERE/'TaskMasterVisorJsonS19.kt.template').read_text(encoding='utf-8')
    if 'configurarVisorJsonS19()' not in source: raise ValueError('Plantilla Kotlin inválida')
    return {MAIN:m,LAY:layout,NEW:source}

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--probar',action='store_true',help='Validar compatibilidad sin modificar archivos')
    a=p.parse_args()
    try:
        outputs=plan()
        changes={k:v for k,v in outputs.items() if not k.exists() or k.read_text(encoding='utf-8')!=v}
        if a.probar:
            print('OK: S19 reconocida. XML válido. '+str(len(changes))+' archivos por crear/actualizar. Sin cambios (--probar).')
            return
        if not changes:
            print('OK: visor JSON ya instalado. Sin duplicados ni cambios.')
            return
        backup=ROOT/'respaldos'/('S19_VISOR_'+datetime.now().strftime('%Y%m%d_%H%M%S'))
        for f in changes:
            if f.is_file():
                dest=backup/f.relative_to(ROOT)
                dest.parent.mkdir(parents=True,exist_ok=True)
                shutil.copy2(f,dest)
        for f,content in changes.items():
            f.parent.mkdir(parents=True,exist_ok=True)
            f.write_text(content,encoding='utf-8')
        print('OK: botón VER JSON GUARDADO incorporado en TaskMaster S19.')
        print('Lee tareas.json de forma privada y solo lectura; no altera tareas ni JSON.')
        print('Archivos modificados/creados:',len(changes))
        print('Siguiente: compilar APK y comprobar en Android.')
    except Exception as exc:
        print('ERROR:',exc,file=sys.stderr)
        sys.exit(1)

if __name__=='__main__': main()

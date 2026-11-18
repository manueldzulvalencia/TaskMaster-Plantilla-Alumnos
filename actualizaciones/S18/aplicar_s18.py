#!/usr/bin/env python3
"""DAMN S18: instala conjuntamente el diseño S17.2 y el diagnóstico de ciclo de vida S18."""
from pathlib import Path
import argparse
import re
import shutil
import sys
from datetime import datetime
import xml.etree.ElementTree as ET

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent
SRC = ROOT / "app/src/main"
PKG = SRC / "java/com/itcancun/mjdzul/taskmaster"
LAY = SRC / "res/layout"
DRAW = SRC / "res/drawable"
MAIN = PKG / "MainActivity.kt"
DETAIL = PKG / "DetalleActivity.kt"
ORIGINAL = PKG / "TaskMasterS17.kt"
CALL = re.compile(r"\bconfigurarTaskMasterS17(?:1|2)?\(\)")
MARK = "DAMN-S18-LIFECYCLE"
FILES = [
    ("TaskMasterS172.kt.template", PKG / "TaskMasterS172.kt"),
    ("activity_main.xml.template", LAY / "activity_main.xml"),
    ("activity_detalle.xml.template", LAY / "activity_detalle.xml"),
    ("tm172_item.xml", LAY / "tm172_item.xml"),
    ("tm172_card.xml", DRAW / "tm172_card.xml"),
    ("tm172_header.xml", DRAW / "tm172_header.xml"),
    ("tm172_button.xml", DRAW / "tm172_button.xml"),
]
IDS = ("etNombreTarea", "btnAgregarTarea", "lvTareas", "rgPrioridad", "spCategoria", "cbRecordatorio", "ibEliminarEjemplo", "tvListaEtiqueta", "tvNota", "rbAlta", "rbMedia", "rbBaja")


def lifecycle_patch(content: str, activity_name: str) -> str:
    if MARK in content:
        return content
    if "import android.util.Log" not in content:
        header = re.search(r"^package [^\n]+\n", content, re.M)
        if not header:
            raise ValueError(f"Falta package en {activity_name}")
        content = content[:header.end()] + "\nimport android.util.Log\n" + content[header.end():]
    anchor = "super.onCreate(savedInstanceState)"
    if content.count(anchor) != 1:
        raise ValueError(f"Se esperaba un onCreate en {activity_name}; se encontraron {content.count(anchor)}")
    content = content.replace(anchor, anchor + f'\n        Log.d("TaskMasterCiclo", "{activity_name}: onCreate") // {MARK}', 1)
    if not re.search(r"class\s+"+re.escape(activity_name)+r"\b",content):
        raise ValueError(f"No se encontró clase {activity_name}")
    if not content.rstrip().endswith("}"):
        raise ValueError(f"Final inesperado de {activity_name}")
    functions = ['onStart','onResume','onPause','onStop','onRestart','onDestroy']
    # Los métodos se añaden solo si el archivo no los tenía declarados previamente.
    additions=[]
    for fn in functions:
        if re.search(r"override\s+fun\s+"+fn+r"\s*\(",content):
            raise ValueError(f"{activity_name} ya implementa {fn}; requiere revisión antes de combinar")
        additions.append(f'    override fun {fn}() {{\n        super.{fn}()\n        Log.d("TaskMasterCiclo", "{activity_name}: {fn}") // {MARK}\n    }}')
    content = content.rstrip()[:-1].rstrip()+"\n\n"+"\n\n".join(additions)+"\n}\n"
    return content


def validate():
    expected = [MAIN,DETAIL,ORIGINAL,SRC/"AndroidManifest.xml",LAY/"activity_main.xml",LAY/"activity_detalle.xml"]
    missing = [str(p.relative_to(ROOT)) for p in expected if not p.is_file()]
    if missing: raise ValueError("No está instalada S17 o faltan archivos: " + ", ".join(missing))
    m = MAIN.read_text(encoding="utf-8")
    if not CALL.search(m): raise ValueError("MainActivity no llama configurarTaskMasterS17/S171/S172")
    for name,path in FILES:
        f=HERE/name
        if not f.is_file(): raise ValueError("Falta recurso: " +name)
        if name.endswith('.xml') or name.endswith('.xml.template'): ET.parse(f)
    xml=(HERE/'activity_main.xml.template').read_text(encoding='utf-8')
    for item in IDS:
        if '@+id/'+item not in xml: raise ValueError('La plantilla elimina ID requerido: '+item)
    d=DETAIL.read_text(encoding='utf-8')
    # Revisar que podemos aplicar las inserciones antes de modificar ningún archivo.
    newmain=lifecycle_patch(CALL.sub('configurarTaskMasterS172()',m,count=1),'MainActivity')
    newdetail=lifecycle_patch(d,'DetalleActivity')
    return newmain,newdetail


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--probar',action='store_true',help='Revisar compatibilidad sin modificar archivos')
    args=parser.parse_args()
    try:
        newmain,newdetail=validate()
        if args.probar:
            print('OK: S17 identificada; S17.1 es opcional.')
            print('OK: archivos Kotlin, XML, Manifest e identificadores verificados.')
            print('OK: se aplicará diseño S17.2 + registro Logcat del ciclo de vida S18.')
            print('OK: no se modificaron archivos (modo --probar).')
            return
        if (MAIN.read_text(encoding='utf-8')==newmain and DETAIL.read_text(encoding='utf-8')==newdetail and all(path.is_file() and path.read_bytes()==(HERE/name).read_bytes() for name,path in FILES)):
            print('OK: S18 ya está instalada; no se duplicaron cambios.')
            return
        stamp=datetime.now().strftime('%Y%m%d_%H%M%S')
        backup=ROOT/'respaldos'/('S18_'+stamp)
        targets=[MAIN,DETAIL]+[p for _,p in FILES]
        for file in targets:
            if file.is_file():
                f=backup/file.relative_to(ROOT)
                f.parent.mkdir(parents=True,exist_ok=True)
                shutil.copy2(file,f)
        for name,path in FILES:
            path.parent.mkdir(parents=True,exist_ok=True)
            shutil.copy2(HERE/name,path)
        MAIN.write_text(newmain,encoding='utf-8')
        DETAIL.write_text(newdetail,encoding='utf-8')
        print('OK: S18 instalada (incluye la interfaz S17.2).')
        print('OK: onCreate, onStart, onResume, onPause, onStop, onRestart y onDestroy registran eventos.')
        print('OK: TAG para observar con adb logcat: TaskMasterCiclo')
        print('OK: respaldos:',backup.relative_to(ROOT))
        print('SIGUIENTE: compilar una sola vez y probar en Android.')
    except Exception as e:
        print('ERROR:',e,file=sys.stderr)
        sys.exit(1)

if __name__=='__main__':main()

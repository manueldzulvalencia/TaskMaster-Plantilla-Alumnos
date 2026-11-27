#!/usr/bin/env python3
"""S24: conserva SQL del alumno e incorpora dos Activities CRUD dinámicas.
  python3 actualizaciones/S24/aplicar_s24.py --probar
  python3 actualizaciones/S24/aplicar_s24.py
"""
import argparse, json, re, sqlite3, shutil, sys, xml.etree.ElementTree as ET
from pathlib import Path
from datetime import datetime
from mejorar_pantallas_s24 import plan as plan_pantallas
HERE=Path(__file__).resolve().parent
ROOT=HERE.parent.parent
MAIN=ROOT/'app/src/main'
PKG=MAIN/'java/com/itcancun/mjdzul/taskmaster'
SQL=ROOT/'base_datos/S23/S23_base_datos.sql'
MANIFEST=MAIN/'AndroidManifest.xml'
UI=PKG/'TaskMasterS20.kt'
ASSET=MAIN/'assets/S23_base_datos.sql'
REPORT=ROOT/'documentacion/S24_avances.md'
A1=PKG/'TablaS24Activity.kt'
A2=PKG/'BaseDatosS24Helper.kt'
THEME=PKG/'EstiloS24.kt'
HUB=PKG/'MisDatosS24Activity.kt'
ADDED=['<activity android:name=".TablaPrincipalS24Activity" android:exported="false" />','<activity android:name=".TablaDependienteS24Activity" android:exported="false" />','<activity android:name=".MisDatosS24Activity" android:exported="false" />']
NAMES=['"Base de datos: principal"','"Base de datos: relacionada"']
BRANCHES=['"Base de datos: principal" -> host.startActivity(Intent(host, TablaPrincipalS24Activity::class.java))','"Base de datos: relacionada" -> host.startActivity(Intent(host, TablaDependienteS24Activity::class.java))']

def validar():
    for p in [SQL,MANIFEST,UI,HERE/'TablaS24Activity.kt',HERE/'BaseDatosS24Helper.kt',HERE/'EstiloS24.kt',HERE/'MisDatosS24Activity.kt']:
        if not p.is_file(): raise ValueError('Falta '+str(p.relative_to(ROOT)))
    sql=SQL.read_text(encoding='utf-8-sig')
    no_comments=re.sub(r'--[^\n]*','',sql)
    if re.search(r'\b(INSERT|UPDATE|DELETE|DROP|ALTER|ATTACH|DETACH|TRIGGER|VIEW|CREATE\s+INDEX)\b',no_comments,re.I):
        raise ValueError('S23 debe contener solo CREATE TABLE y PRAGMA. Conserva el SQL estructural.')
    # En Android se ejecutan instrucciones por separado; S23 se limita a sentencias sencillas.
    for stmt in no_comments.split(';'):
        stmt=stmt.strip()
        if stmt and not re.match(r'^(CREATE\s+TABLE|PRAGMA\s+foreign_keys\s*=\s*ON\s*$)',stmt,re.I):
            raise ValueError('Instrucción SQL no compatible con S24: '+stmt[:50])
    c=sqlite3.connect(':memory:')
    try:
        c.execute('PRAGMA foreign_keys=ON');c.executescript(sql)
        tabs=[r[0] for r in c.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'")]
        if len(tabs)!=2:raise ValueError('S24 necesita exactamente 2 tablas')
        relations=[]
        for t in tabs:
            if not re.fullmatch(r'[A-Za-z_][A-Za-z_0-9]*',t):raise ValueError('Nombre inválido de tabla: '+t)
            cols=c.execute(f'PRAGMA table_info("{t}")').fetchall()
            if len(cols)<3:raise ValueError('Cada tabla debe tener 3 o más campos')
            pk=[x for x in cols if x[5]]
            if len(pk)!=1 or pk[0][2].upper()!='INTEGER':raise ValueError('PK debe ser INTEGER única en '+t)
            for x in cols:
                if not re.fullmatch(r'[A-Za-z_][A-Za-z_0-9]*',x[1]) or x[2].upper() not in ('INTEGER','TEXT','REAL'):
                    raise ValueError('Campo no compatible: '+t+'.'+x[1])
            for f in c.execute(f'PRAGMA foreign_key_list("{t}")'):relations.append((t,f))
        if len(relations)!=1:raise ValueError('Se requiere exactamente una FK')
        hija,fk=relations[0];padre=fk[2]
        if padre not in tabs or padre==hija:raise ValueError('La FK debe referenciar la otra tabla')
        if fk[4]!=next(x[1] for x in c.execute(f'PRAGMA table_info("{padre}")') if x[5]):raise ValueError('FK apunta a una columna que no es PK')
        ref=next((x for x in c.execute(f'PRAGMA table_info("{hija}")') if x[1]==fk[3]),None)
        if ref is None or ref[2].upper()!='INTEGER' or not ref[3]:raise ValueError('FK requiere INTEGER NOT NULL')
        if fk[5]!='NO ACTION' or fk[6]!='NO ACTION':raise ValueError('No usar CASCADE en S24')
        # comprobar que la BD de Android puede ser creada con esta misma secuencia
        print('SQL validado:',padre,'(principal) ->',hija,'(dependiente)')
    finally:c.close()
    ui=UI.read_text(encoding='utf-8')
    if 'class TaskMasterS20' not in ui or 'Centro multimedia' not in ui:
        raise ValueError('Primero aplica S20-S22 y conserva el menú Centro multimedia')
    # La navegación se integra por plan_navegacion() y reemplaza entradas
    # genéricas de versiones anteriores de S24 sin duplicar opciones.
    manifest=MANIFEST.read_text(encoding='utf-8')
    for tag in ADDED:
        if tag.split('android:name="')[1].split('"')[0] not in manifest:
            manifest=manifest.replace('</application>','    '+tag+'\n    </application>',1)
    ET.fromstring(manifest)
    # También valida de antemano las pantallas anteriores, incluso con --probar.
    plan_pantallas(PKG, ui)
    return sql,ui,manifest

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--probar',action='store_true'); args=p.parse_args()
    try:
        sql,ui,manifest=validar()
        if args.probar:
            print('OK S24 --probar: SQL válido, S22 detectada, no se modificó el proyecto.');return
        outputs={ASSET:sql,UI:ui,MANIFEST:manifest,
                 A1:(HERE/'TablaS24Activity.kt').read_text(encoding='utf8'),
                 A2:(HERE/'BaseDatosS24Helper.kt').read_text(encoding='utf8'),
                 THEME:(HERE/'EstiloS24.kt').read_text(encoding='utf8'),
                 HUB:(HERE/'MisDatosS24Activity.kt').read_text(encoding='utf8')}
        # Una sola ejecución integra CRUD, calendario e identidad S20 en pantallas anteriores.
        outputs.update(plan_pantallas(PKG, ui))
        if not REPORT.exists():
            outputs[REPORT]='# S24 · Bitácora técnica automática\n\n- SQL conservado en `base_datos/S23/S23_base_datos.sql`.\n- Dos Activities CRUD: tabla principal y tabla dependiente.\n- Base local SQLite: `taskmaster_s24.db`.\n- Formularios dinámicos para TEXT, INTEGER, REAL; FK desde selector.\n- Pruebas en dispositivo y evidencias académicas: Google Docs.\n'
        changes={p:v for p,v in outputs.items() if not p.is_file() or p.read_text(encoding='utf-8')!=v}
        if changes:
            backup=ROOT/'respaldos'/('S24_'+datetime.now().strftime('%Y%m%d_%H%M%S_%f'))
            for file,contents in changes.items():
                if file.exists():
                    dst=backup/file.relative_to(ROOT);dst.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(file,dst)
                file.parent.mkdir(parents=True,exist_ok=True);file.write_text(contents,encoding='utf-8')
        print('S24 aplicada:',len(changes),'archivos nuevos/actualizados. SQL de S23 intacto.')
        print('Compila el APK y prueba ambas Activities en Android.')
    except (ValueError,sqlite3.Error,OSError,ET.ParseError) as e:
        print('ERROR S24:',e,file=sys.stderr);sys.exit(1)
if __name__=='__main__':main()

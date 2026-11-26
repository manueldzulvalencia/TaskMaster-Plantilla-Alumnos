#!/usr/bin/env python3
"""S23: verifica el SQL escrito por el alumno y crea una base SQLite.
No genera tablas ni SQL; ejecuta exclusivamente el archivo recibido.
"""
from __future__ import annotations
import argparse
import re
import sqlite3
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DEFAULT_SQL = ROOT / 'base_datos' / 'S23' / 'S23_base_datos.sql'
DEFAULT_DB = ROOT / 'base_datos' / 'S23' / 'mi_app.db'
VALID_NAME = re.compile(r'^[A-Za-z_][A-Za-z0-9_]*$')


def inspect_schema(connection: sqlite3.Connection) -> tuple[list[str], list[str]]:
    errors = []
    rows = connection.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%' ORDER BY name").fetchall()
    tables = [r[0] for r in rows]
    if len(tables) != 2:
        errors.append(f'Se esperaban exactamente 2 tablas, se encontraron {len(tables)}.')
    all_fk = []
    for table in tables:
        if not VALID_NAME.fullmatch(table):
            errors.append(f'Nombre de tabla no compatible con S24: {table!r}.')
        cols = connection.execute(f'PRAGMA table_info("{table}")').fetchall()
        if len(cols) < 3:
            errors.append(f'{table}: minimo 3 campos (incluyendo la PK).')
        pk = [c for c in cols if c[5] > 0]
        if len(pk) != 1 or pk[0][2].upper() != 'INTEGER':
            errors.append(f'{table}: debe existir una sola PRIMARY KEY de tipo INTEGER.')
        for c in cols:
            if not VALID_NAME.fullmatch(c[1]):
                errors.append(f'{table}: nombre de campo no compatible con S24: {c[1]!r}.')
            if c[2].upper() not in {'INTEGER', 'TEXT', 'REAL'}:
                errors.append(f'{table}.{c[1]}: usa INTEGER, TEXT o REAL; actual: {c[2]!r}.')
        for fk in connection.execute(f'PRAGMA foreign_key_list("{table}")').fetchall():
            all_fk.append((table, fk))
    if len(all_fk) != 1:
        errors.append(f'Se requiere exactamente una FOREIGN KEY 1:N; se encontraron {len(all_fk)}.')
    else:
        child, fk = all_fk[0]
        parent = fk[2]
        if parent not in tables or child == parent:
            errors.append('La FOREIGN KEY debe apuntar a la otra tabla.')
        else:
            parent_cols = connection.execute(f'PRAGMA table_info("{parent}")').fetchall()
            parent_pk = [c[1] for c in parent_cols if c[5] > 0]
            if not parent_pk or fk[4] != parent_pk[0]:
                errors.append('La FOREIGN KEY debe referenciar la PRIMARY KEY de la tabla principal.')
            child_cols = connection.execute(f'PRAGMA table_info("{child}")').fetchall()
            col = next((c for c in child_cols if c[1] == fk[3]), None)
            if col is None or col[2].upper() != 'INTEGER' or not col[3]:
                errors.append('La FOREIGN KEY de la tabla dependiente debe ser INTEGER NOT NULL.')
            if fk[5] != 'NO ACTION' or fk[6] != 'NO ACTION':
                errors.append('Para S24, no utilices ON UPDATE/DELETE CASCADE u otras acciones.')
    return tables, errors


def main() -> int:
    p = argparse.ArgumentParser(description='Verifica tu SQL y crea mi_app.db si cumple los requisitos S23.')
    p.add_argument('--archivo', type=Path, default=DEFAULT_SQL, help='Archivo SQL elaborado por el alumno')
    p.add_argument('--salida', type=Path, default=DEFAULT_DB, help='Ruta del archivo .db a crear')
    args = p.parse_args()
    if not args.archivo.is_file():
        print(f'ERROR: no existe {args.archivo}')
        return 1
    if args.salida.exists():
        print(f'ERROR: ya existe {args.salida}. No se sobrescribio. Cambia --salida o resguarda el archivo existente.')
        return 1
    sql = args.archivo.read_text(encoding='utf-8-sig')
    # Exigir unicamente estructura para la fase S23 (sin DML).
    if re.search(r'\b(?:INSERT|UPDATE|DELETE|DROP|ALTER|ATTACH|DETACH|TRIGGER)\b', re.sub(r'--[^\n]*', '', sql), flags=re.I):
        print('ERROR: S23 solo incluye la creacion de tablas. Deja operaciones y cambios para S24.')
        return 1
    con = sqlite3.connect(':memory:')
    con.execute('PRAGMA foreign_keys = ON')
    try:
        con.executescript(sql)
        con.execute('PRAGMA foreign_keys = ON')
        tables, errors = inspect_schema(con)
        issues = con.execute('PRAGMA foreign_key_check').fetchall()
        if issues:
            errors.append('SQLite detecto problemas de integridad referencial.')
        integrity = con.execute('PRAGMA integrity_check').fetchone()[0]
        if integrity != 'ok':
            errors.append(f'Integridad de base de datos: {integrity}')
        if errors:
            print('REVISION NECESARIA:')
            for err in errors:
                print(f' - {err}')
            return 1
        args.salida.parent.mkdir(parents=True, exist_ok=True)
        with sqlite3.connect(args.salida) as dest:
            con.backup(dest)
        print('VALIDACION CORRECTA')
        for table in tables:
            fields = con.execute(f'PRAGMA table_info("{table}")').fetchall()
            fks = con.execute(f'PRAGMA foreign_key_list("{table}")').fetchall()
            print(f' - {table}: {len(fields)} campos, {len(fks)} clave(s) foranea(s)')
        print(f'Base SQLite creada: {args.salida}')
        return 0
    except sqlite3.Error as exc:
        print(f'ERROR DE SQL: {exc}')
        return 1
    finally:
        con.close()


if __name__ == '__main__':
    sys.exit(main())

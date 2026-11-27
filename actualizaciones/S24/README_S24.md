# S24 | Del SQL de S23 a dos Activities Android CRUD

**Requisitos previos:** haber aplicado S20, S21 y S22; disponer de `base_datos/S23/S23_base_datos.sql` completo, validado en S23, con **exactamente dos tablas**, una relación 1:N y columnas `TEXT`, `INTEGER` o `REAL`.

## Qué hace esta actualización

- Respeta **sin modificar** `base_datos/S23/S23_base_datos.sql`.
- Incorpora el SQL como `app/src/main/assets/S23_base_datos.sql` para crear la base **en el teléfono** al abrir S24 por primera vez.
- Agrega **dos Activities**: `TablaPrincipalS24Activity` y `TablaDependienteS24Activity`.
- Ambas usan el **mismo** `BaseDatosS24Helper.kt` y la base interna `taskmaster_s24.db`.
- Detecta campos y PK por introspección; los controles `TEXT`, `INTEGER`, `REAL` y el selector de clave foránea se construyen dinámicamente.
- Permite **crear, listar, editar y eliminar**; bloquea por integridad la eliminación de un padre con registros asociados.
- Agrega dos entradas al menú lateral, **Base de datos: principal** y **Base de datos: relacionada**, sin eliminar multimedia/exportación.

## Instrucciones en Codespaces

Desde la raíz de **tu repositorio**, donde `actualizaciones`, `app` y `base_datos` están al mismo nivel:

```bash
# Primero, descargar SOLO el kit S24. No restaurar base_datos/ ni tu S23_base_datos.sql.
git fetch plantilla main
git restore --source=plantilla/main -- actualizaciones/S24/

# Validar compatibilidad sin modificar archivos
python3 actualizaciones/S24/aplicar_s24.py --probar

# Instalar las dos Activities y la BD Android
python3 actualizaciones/S24/aplicar_s24.py

# Compilar Android
./gradlew assembleDebug --no-configuration-cache --no-daemon -Dorg.gradle.java.home=/usr/lib/jvm/msopenjdk-current

# Guardar una copia del APK
mkdir -p versiones
cp app/build/outputs/apk/debug/app-debug.apk versiones/TaskMaster-S24.apk
```

**Si tu Codespaces utiliza otro JDK compatible con el proyecto**, adapta el parámetro `-Dorg.gradle.java.home` antes de compilar.

## Pruebas manuales de Android

1. Abrir la aplicación e ir a «Base de datos: principal». Registrar y consultar una fila.
2. Abrir «Base de datos: relacionada» y seleccionar la fila principal. Crear registro relacionado.
3. Editar y eliminar registros en ambas pantallas. Para eliminar un padre con hijos, primero elimina los hijos.
4. Cerrar y reabrir la app: comprobar persistencia local de S24 y conservación de las funcionalidades S20–S22.
5. Personalización guiada de Kotlin: revisar `TablaS24Activity.kt`, localizar `hint=col.nombre` y explicar de dónde se obtiene ese nombre. **No cambies `col.nombre` por un nombre fijo**, porque se perdería la adaptación a tu SQL.

## Final de S24: un commit de S23 y S24

```bash
git status
git add base_datos/S23/S23_base_datos.sql app/src/main actualizaciones/S24/ documentacion/S24_avances.md
git commit -m "S23-S24 - SQLite y dos Activities CRUD"
git push origin HEAD
```

Si no deseas guardar en tu repositorio los archivos de la actualización o la bitácora, ajusta el `git add` a los archivos que realmente entregarás. **No es necesario subir `mi_app.db`**, pues los registros se crean en el dispositivo.

## Limitaciones y advertencias

- Este kit se diseñó para el **formato restringido de S23**, no SQL arbitrario: sin `ALTER`, índices complejos, triggers, restricciones personalizadas ni varias claves foráneas.
- El asistente genera **dos Activities reutilizables**, no un archivo Kotlin diferente por entidad: cada Activity administra su tabla en tiempo de ejecución.
- Los datos de la base S23 creada en Codespaces **no se copian** al dispositivo. S24 crea la estructura, inicialmente vacía.
- La base SQLite de Android se crea la **primera vez** que se abre; editar el SQL después **no migra** las tablas ya creadas en el teléfono. No borres datos para forzar el cambio sin respaldo.
- Es necesario realizar pruebas reales de compilación e instalación antes de asignar S24 a todo el grupo.

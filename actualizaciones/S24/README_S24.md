# S24 · CRUD + identidad S20: una única instalación

El mismo `aplicar_s24.py` integra **2 Activities con CRUD dinámico**, los calendarios para campos `TEXT` llamados `fecha`/`date`, y la mejora visual de pantallas anteriores (Nueva tarea, tarjetas, detalle, multimedia). **No requiere un instalador visual adicional**.

## Alumno / docente · Comandos en Codespaces

```bash
python3 actualizaciones/S24/aplicar_s24.py --probar
python3 actualizaciones/S24/aplicar_s24.py
./gradlew assembleDebug --no-configuration-cache --no-daemon -Dorg.gradle.java.home=/usr/lib/jvm/msopenjdk-current
mkdir -p versiones
cp app/build/outputs/apk/debug/app-debug.apk versiones/TaskMaster-S24.apk
```

La identidad visual se lee del color elegido en **S20** (`tm20_color`); no se fuerza el azul de HomeTask. Se usa una paleta suave derivada, encabezados y botones legibles mediante contraste automático.

**Compatibilidad:** el SQL del estudiante debe cumplir S23 (2 tablas; 1 relación 1:N, PK INTEGER, FK INTEGER NOT NULL; columnas TEXT, INTEGER o REAL). Puede tener campos adicionales. El instalador no modifica `base_datos/S23/S23_base_datos.sql` ni `tareas.json`, no borra registros ni crea tablas distintas; realiza respaldo de los archivos que cambian en `respaldos/S24_*`. Puede ejecutarse de nuevo sin duplicar cambios.

**Antes de distribuirlo:** compilar y probar en BlueStacks el menú, CRUD en ambas tablas, campo de fecha, relación, persistencia, regreso, multimedia, tareas y exportación JSON. La prueba del instalador no sustituye la compilación Android.

## Navegación unificada (incluida en S24)

- Barra inferior: **Inicio · Tareas · Nueva · Datos** (reemplaza Estadísticas pendiente).
- Menú lateral ordenado: **Organización** (Inicio, Mis tareas, Nueva tarea), **Administración de datos** (Mis datos, Ver JSON, Exportar datos) y **Herramientas** (Centro multimedia).
- **Mis datos** abre un centro con dos tarjetas que toman sus nombres reales del SQL S23 y abren las dos Activities CRUD. Sus flechas «Volver» regresan a este centro, y desde él se regresa al inicio.
- No se publican en el menú opciones de «En construcción»; no se elimina su código, y las funciones de sesiones anteriores siguen disponibles.
- El diseño utiliza el color S20; no se cambia el archivo SQL ni se regeneran los datos existentes.

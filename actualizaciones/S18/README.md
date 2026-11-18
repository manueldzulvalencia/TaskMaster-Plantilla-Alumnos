# DAMN Studio — S18 definitiva (un solo instalador)

**Tema académico:** 3.2 Manipulación de Activities: comunicación y ciclo de vida.

La actualización incluye en una sola instalación:
- Rediseño visual S17.2 (encabezado morado y tarjetas).
- Registro del ciclo de vida de MainActivity y DetalleActivity en Logcat (`TaskMasterCiclo`).
- Lista desplazable que muestra todas las tareas nuevas.
- Dos botones por tarea: **Ver detalle** y **Eliminar**.
- Confirmación con **Cancelar / Eliminar** antes de borrar.
- Toast de éxito/error y las opciones de prioridad, categoría e importante.

**Requisito:** TaskMaster S17. Compatible con S17.1 opcional y también puede sustituir una instalación S18 anterior. **No se necesita instalar S17.2 ni S18.1 por separado.**

## Desde la raíz del repositorio personal en Codespaces

```bash
git fetch plantilla main
git restore --source=plantilla/main -- actualizaciones/S18/
/usr/bin/python3 actualizaciones/S18/aplicar_s18.py --probar
/usr/bin/python3 actualizaciones/S18/aplicar_s18.py
./gradlew assembleDebug --no-configuration-cache --no-daemon -Dorg.gradle.java.home=/usr/lib/jvm/msopenjdk-current
mkdir -p versiones
cp app/build/outputs/apk/debug/app-debug.apk versiones/TaskMaster-S18.apk
```

## Pruebas
1. Agrega cinco tareas y desplázate para visualizar las ocho.
2. Pulsa **Ver detalle** en una tarjeta y regresa correctamente.
3. Pulsa **Eliminar**, luego **Cancelar**: la tarea permanece.
4. Vuelve a pulsar **Eliminar** y confirma: la tarea desaparece y aparece Toast.
5. Comprueba prioridades, categorías y mensajes Toast de agregar/error.
6. Observa los estados de las Activities con `adb logcat -s TaskMasterCiclo:D '*:S'` cuando haya ADB conectado.

## Guardado
```bash
git add -- actualizaciones/S18/ app/src/main versiones/TaskMaster-S18.apk
git commit -m "S18 - Interfaz, ciclo de vida y acciones por tarea"
git push origin main
```

No añadir `respaldos/` ni `app/build/`. Las tareas siguen almacenadas temporalmente en memoria; S19 tratará la persistencia.

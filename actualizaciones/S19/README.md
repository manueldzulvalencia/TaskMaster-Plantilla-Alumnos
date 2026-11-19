# TaskMaster S19 — Guardar y recuperar tareas

Instalación acumulativa **sobre S18 definitiva**. No requiere instalar ninguna S19.1.

- `TaskMasterS19.kt`: controla lista, altas, eliminaciones, Toast y guardado en `tareas.json`.
- `TaskMasterDetalleS19.kt`: presenta título, categoría, prioridad e importancia por separado.
- `activity_detalle.xml` y recursos: pantalla de detalle renovada.
- Se conserva la instrumentación `TaskMasterCiclo` de S18.

## Requisitos
1. Proyecto con S18 definitiva funcionando (incluye `TaskMasterS172.kt` y registros `DAMN-S18-LIFECYCLE`).
2. Estar en la raíz del repositorio y tener `/usr/bin/python3`.
3. Guardar un commit de las modificaciones locales antes de instalar.

```bash
/usr/bin/python3 actualizaciones/S19/aplicar_s19.py --probar
/usr/bin/python3 actualizaciones/S19/aplicar_s19.py
./gradlew assembleDebug --no-configuration-cache --no-daemon -Dorg.gradle.java.home=/usr/lib/jvm/msopenjdk-current
```

## Pruebas funcionales
1. Agregar dos tareas, cerrar la app realmente y volver a abrir: deben conservarse.
2. Eliminar una tarea, reiniciar y verificar que no reaparezca.
3. Eliminar todas, reiniciar y verificar lista vacía (no reinsertar ejemplos).
4. Abrir detalle: mostrar título, prioridad, categoría e importancia correctos.
5. Revisar navegación, scroll, Toast y Logcat.

El archivo `tareas.json` se almacena en el espacio privado de Android. Borrar datos de la app o desinstalarla puede eliminarlo. No se ha compilado el APK en este paquete.

# S17 — Activities, navegación y diseño visual

**Requisitos:** TaskMaster S16 instalado; ejecutar en GitHub Codespaces desde la raíz del repositorio del alumno. **No utiliza Android Studio.**

## Funcionalidad
Toca cualquier tarea en la lista para abrir `DetalleActivity` y ver su descripción. Usa «Volver a mis tareas» o Atrás para regresar. La actualización incorpora un diseño visual básico para la segunda pantalla, conserva los Toast de S16 y no cambia el almacenamiento en memoria. En S18 se profundizará en comunicación y estructura de datos entre Activities.

## Instalación desde la plantilla
```bash
git fetch plantilla main
git restore --source=plantilla/main -- actualizaciones/S17/
python3 actualizaciones/S17/aplicar_s17.py --probar
python3 actualizaciones/S17/aplicar_s17.py
```

**IMPORTANTE:** Estos comandos requieren que el docente haya publicado previamente `actualizaciones/S17/` en el remoto `plantilla`. Si `--probar` reporta incompatibilidad, no forzar ni sobrescribir archivos; reportar el error.

## Compilación
```bash
./gradlew --stop
./gradlew assembleDebug --no-configuration-cache --no-daemon -Dorg.gradle.java.home=/usr/lib/jvm/msopenjdk-current
```
Solo si aparece `BUILD SUCCESSFUL`:
```bash
mkdir -p versiones
cp app/build/outputs/apk/debug/app-debug.apk versiones/TaskMaster-S17.apk
ls -lh versiones/TaskMaster-S17.apk
```

## Pruebas
1. Abre TaskMaster y toca una tarea de ejemplo. Debe abrirse «Detalle de tarea» con el texto de esa tarea.
2. Usa «Volver a mis tareas»: debe regresar sin cerrar la aplicación.
3. Registra una tarea nueva con prioridad Alta. Debe aparecer el Toast «Tarea agregada correctamente».
4. Toca la tarea nueva: debe mostrarse su descripción en la pantalla secundaria.
5. Regresa y elimina una tarea seleccionada: debe aparecer «Tarea eliminada correctamente».
6. Intenta crear una tarea vacía: debe aparecer el mensaje de error de S16.

## Evidencias
Captura de `BUILD SUCCESSFUL`, captura de la pantalla de detalles y enlace al repositorio. No subir APK ni respaldos al repositorio.

## Nota técnica
La S17 se genera como una copia enriquecida de la lógica S16 y se activa en `MainActivity.kt`. No modifica el archivo `TaskMasterS16.kt` ni `activity_main.xml`; crea `TaskMasterS17.kt`, `DetalleActivity.kt`, `activity_detalle.xml` y registra la Activity en el Manifest. Los cambios del Manifest y MainActivity se respaldan en `respaldos/S17/`. El instalador puede reejecutarse si los archivos generados no han sido modificados manualmente.

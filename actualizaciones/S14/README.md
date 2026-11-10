# S14 — Formulario funcional de TaskMaster

**Entorno:** GitHub Codespaces. **Requisitos:** S12 y S13 completadas. No se usa Android Studio.

## ¿Qué hace la actualización?

- Conserva el diseño XML creado en S12 y las funcionalidades realizadas en S13.
- Modifica `MainActivity.kt` para llamar a `configurarTaskMasterS14()` en vez de `configurarTaskMasterS13()`; ambas llamadas NO deben ejecutarse juntas.
- Crea `TaskMasterS14.kt` junto a `MainActivity.kt`, con lógica para registrar tareas usando prioridad, categoría y la marca de importancia.
- Cambia únicamente el texto del CheckBox de S12, de «Activar recordatorio» a «Tarea importante», manteniendo el ID `cbRecordatorio`.
- Permite tocar una tarea para seleccionarla y luego eliminarla con la papelera (`ImageButton`).
- Valida nombre vacío y eliminación sin selección.
- Crea copias de seguridad en `respaldos/S13/`, fuera de los recursos Android.

**Limitación:** las tareas se mantienen en memoria; no existe persistencia entre reinicios. El CheckBox de S14 representa **importancia**, no crea alarmas ni notificaciones. Los tres ejemplos de S12 permanecen visibles y pueden eliminarse durante la prueba.

## Comandos para el alumno

En la raíz del repositorio personal, con el remoto `plantilla` ya configurado:

```bash
git fetch plantilla main
git restore --source=plantilla/main -- actualizaciones/S14/
ls -l actualizaciones/S14/
python3 actualizaciones/S14/aplicar_s14.py
```

**Compilación en Codespaces con el JDK 21 comprobado en S13:**

```bash
./gradlew --stop
./gradlew assembleDebug --no-configuration-cache --no-daemon -Dorg.gradle.java.home=/usr/lib/jvm/msopenjdk-current
```

Solo si aparece `BUILD SUCCESSFUL`:

```bash
mkdir -p versiones
cp app/build/outputs/apk/debug/app-debug.apk versiones/TaskMaster-S14.apk
ls -lh versiones/TaskMaster-S14.apk
```

Prueba el APK en un teléfono Android o emulador. Al guardar el trabajo:

```bash
printf '\n/versiones/\n/respaldos/\n' >> .gitignore
git status --short
git add .gitignore actualizaciones/S14/ app/src/main/res/layout/activity_main.xml
# Incluye los dos archivos Kotlin desde la carpeta donde esté MainActivity.kt:
git add "$(find app/src/main -name MainActivity.kt -print -quit | xargs dirname)"
```

Comprueba los cambios antes de registrar el commit:

```bash
git diff --cached --stat
git commit -m "S14 - Formulario funcional TaskMaster"
git push origin main
git status
```

## Pruebas mínimas

1. Agregar `Preparar evaluación U2` con Alta, Estudio y CheckBox activado. Debe aparecer `★` y las propiedades en la lista.
2. Agregar una tarea con importancia desactivada. No debe aparecer `★`.
3. Presionar Agregar tarea con el nombre vacío: debe mostrar un error y no registrar.
4. Presionar la papelera sin seleccionar: debe mostrar un aviso.
5. Tocar una tarea de la lista y presionar la papelera: debe desaparecer.
6. Comprobar que la aplicación mantiene las tareas de ejemplo y no se cierra inesperadamente.

## Evidencias sugeridas para AulaVirtual

Captura de `BUILD SUCCESSFUL`, captura de una tarea registrada con opciones, captura de eliminación o validación y una breve explicación de los resultados. El APK se puede guardar de forma local; su archivo binario no se sube al repositorio Git.

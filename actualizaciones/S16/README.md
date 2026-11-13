# S16 — Mensajes de confirmación y error con Toast

**Entorno:** GitHub Codespaces. **Requisitos:** S12, S13 y S14 completadas. No se usa Android Studio.

## ¿Qué hace esta actualización?

- Conserva el diseño XML creado en S12 y todas las funcionalidades de S14.
- Sustituye la llamada `configurarTaskMasterS14()` por `configurarTaskMasterS16()` en `MainActivity.kt`; no ejecuta ambas a la vez.
- Crea `TaskMasterS16.kt` junto a `MainActivity.kt`, con el mismo formulario y comportamiento de S14.
- Mejora los mensajes Toast de cuatro situaciones: título vacío, registro exitoso, eliminación sin selección y eliminación exitosa.
- Crea respaldos de S14 en `respaldos/S14/`, fuera de los recursos Android.
- No agrega pantallas, controles XML, permisos ni dependencias Gradle.

**Limitaciones:** las tareas permanecen únicamente en memoria. Un Toast confirma la operación que acaba de realizarse, pero no significa que la información esté guardada permanentemente. La versión S16 está preparada para el código **S14 original de esta plantilla**; si el archivo S14 fue modificado, el instalador se detiene sin sobrescribirlo.

## Comandos para el alumno

Desde la raíz del repositorio personal; el remoto `plantilla` debe estar configurado:

```bash
# 1. Obtener la versión actual del repositorio docente.
git fetch plantilla main

# 2. Importar exclusivamente la carpeta S16.
git restore --source=plantilla/main -- actualizaciones/S16/

# 3. Verificar archivos importados.
ls -l actualizaciones/S16/

# 4. Comprobar compatibilidad sin cambiar el proyecto.
python3 actualizaciones/S16/aplicar_s16.py --probar

# 5. Instalar la S16.
python3 actualizaciones/S16/aplicar_s16.py
```

**Compilación en Codespaces con JDK 21, como en S14:**

```bash
# Detener demonios de compilaciones anteriores.
./gradlew --stop

# Compilar APK de depuración.
./gradlew assembleDebug --no-configuration-cache --no-daemon -Dorg.gradle.java.home=/usr/lib/jvm/msopenjdk-current
```

Solo si aparece `BUILD SUCCESSFUL`:

```bash
# Guardar una copia del APK para entrega fuera de Git.
mkdir -p versiones
cp app/build/outputs/apk/debug/app-debug.apk versiones/TaskMaster-S16.apk
ls -lh versiones/TaskMaster-S16.apk
```

Prueba el APK en un teléfono Android o emulador. Para registrar los cambios:

```bash
# Ignorar binarios y respaldos, sin duplicar entradas.
touch .gitignore
grep -qxF '/versiones/' .gitignore || printf '\n/versiones/\n' >> .gitignore
grep -qxF '/respaldos/' .gitignore || printf '/respaldos/\n' >> .gitignore

# Revisar cambios e incluir la actualización y el código Kotlin.
git status --short
git add .gitignore actualizaciones/S16/
git add "$(dirname "$(find app/src/main -name MainActivity.kt -print -quit)")"

# Examinar y registrar lo que vamos a subir.
git diff --cached --stat
git commit -m "S16 - Notificaciones Toast TaskMaster"
git push origin main
git status
```

## Pruebas mínimas

1. Registrar `Preparar evaluación U3` con prioridad Alta, categoría Estudio e importancia marcada: debe aparecer `★`, el resto de los datos y el Toast **«Tarea agregada correctamente»**.
2. Registrar otra tarea con importancia desactivada: no debe incluir `★` y debe aparecer el mismo Toast de éxito.
3. Presionar Agregar con nombre vacío: muestra **«Ingresa el nombre de la tarea»**, marca el campo como obligatorio y no agrega nada.
4. Presionar la papelera sin seleccionar: muestra **«Selecciona una tarea para eliminar»**.
5. Tocar una tarea y presionar la papelera: desaparece de la lista y aparece **«Tarea eliminada correctamente»**.
6. Comprobar que las tareas de ejemplo, prioridades, categorías y demás funciones anteriores siguen presentes.

## Evidencias para AulaVirtual

Captura de `BUILD SUCCESSFUL`, captura o video breve de los Toast de éxito y error, enlace al repositorio individual y copia local del APK cuando se solicite. **No subir el APK ni respaldos al repositorio Git.**

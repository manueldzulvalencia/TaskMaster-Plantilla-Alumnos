# TaskMaster · Actualización S13
## Programación de eventos y acciones en Kotlin

**Asignatura:** Desarrollo de Aplicaciones Móviles Nativas  
**Entorno:** GitHub Codespaces  
**Objetivo:** agregar tareas a `ListView` con un evento Kotlin y validar el campo de entrada.

### ¿Qué conseguirás?
- Al tocar **Agregar tarea**, TaskMaster captura el texto del `EditText`.
- Si está vacío (o solo contiene espacios), se muestra un mensaje de error.
- Si contiene texto, se añade a la lista de tareas y se limpia el campo.
- La lista se mantiene **en memoria**. El guardado permanente se verá posteriormente.
- La prioridad, la categoría, el CheckBox y el botón de eliminar se programarán en S14.

### Requisito previo
Tu proyecto debe **tener aplicada y comprobada S12** (incluidos `activity_main.xml` y `taskmaster_s12.xml`). Trabaja en tu repositorio individual desde su carpeta raíz, no en el repositorio del docente.

### Paso 1. Recuperar S13
Si `plantilla` ya existe, omite el primer comando.

```bash
git remote add plantilla https://github.com/manueldzulvalencia/TaskMaster-Plantilla-Alumnos.git
```

```bash
git fetch plantilla main
git restore --source=plantilla/main -- actualizaciones/S13/
ls -l actualizaciones/S13/
```

**Atención:** `git restore` copia solo la carpeta de actualización; no reemplaza toda la aplicación.

### Paso 2. Aplicar la funcionalidad S13
El siguiente script verifica los IDs de S12, localiza el `package` real de tu proyecto, guarda un respaldo de `MainActivity.kt` **fuera de `res/`** e incorpora la lógica Kotlin. No reemplaza todo `MainActivity.kt`.

```bash
python3 actualizaciones/S13/aplicar_s13.py
```

Si muestra `ERROR`, **detente y reporta el mensaje**; no intentes compilar archivos incompletos.

### Paso 3. Revisar lo aprendido
Abre `MainActivity.kt` y observa la llamada a `configurarTaskMasterS13()`. Luego abre `TaskMasterS13.kt`, en el mismo paquete. Identifica:
- `setOnClickListener`: escucha el clic.
- `campoTarea.text.toString().trim()`: lee el texto.
- `isBlank()`: evita una tarea vacía.
- `tareas.add(nombre)`: agrega información a la lista.
- `adaptador.notifyDataSetChanged()`: actualiza `ListView`.
- `campoTarea.text.clear()`: prepara otra captura.

### Paso 4. Compilar

```bash
./gradlew assembleDebug
```

Continúa únicamente si aparece **BUILD SUCCESSFUL**. Si aparece un error relativo a `jlink`, verifica primero la instalación del JDK; en Codespaces configurados como en S12 puedes probar:

```bash
./gradlew assembleDebug --no-configuration-cache --no-daemon -Dorg.gradle.java.home=/usr/lib/jvm/msopenjdk-current
```

### Paso 5. Identificar el APK

```bash
mkdir -p versiones
cp app/build/outputs/apk/debug/app-debug.apk versiones/TaskMaster-S13.apk
ls -lh versiones/TaskMaster-S13.apk
```

Descarga el archivo desde Codespaces e instálalo en tu dispositivo Android o BlueStacks.

### Paso 6. Probar las funciones
1. Presiona **Agregar tarea** con el campo vacío: debe mostrar una advertencia y no agregar filas.
2. Escribe `Preparar exposición` y presiona **Agregar tarea**: debe aparecer en **Mis tareas**.
3. Verifica que el campo quede vacío y puedas agregar una segunda tarea.
4. Confirma que las tareas de ejemplo anteriores siguen visibles.
5. Observa que los demás controles continúan siendo visuales; se completarán en S14.

### Paso 7. Entregar evidencias
- Captura del código Kotlin (listener y validación).
- Captura de **BUILD SUCCESSFUL**.
- Captura de TaskMaster con la nueva tarea agregada.
- APK **TaskMaster-S13.apk** y enlace al repositorio individual (si lo solicita el docente).

### Paso 8. Registrar avances en el repositorio individual
Primero revisa los archivos cambiados:

```bash
git status --short
```

Evita incorporar copias APK y respaldos binarios al historial. Agrega a `.gitignore` si no lo habías hecho:

```bash
printf '\n/versiones/\n/respaldos/\n' >> .gitignore
```

Luego registra los archivos del proyecto y las instrucciones:

```bash
git add .gitignore actualizaciones/S13/ app/src/main/
git commit -m "S13 - Eventos y validacion de tareas en Kotlin"
git push origin main
git status
```

**Resultado esperado:** TaskMaster permite agregar tareas a una lista mediante Kotlin y tiene su APK S13. No se exige persistencia de datos.

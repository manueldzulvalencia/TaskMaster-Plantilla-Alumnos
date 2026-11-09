# Actualización S12 — TaskMaster
## Controles de interfaz gráfica en Android

**Asignatura:** Desarrollo de Aplicaciones Móviles Nativas  
**Entorno de desarrollo:** GitHub Codespaces  
**Proyecto:** TaskMaster  
**Sesión:** 12

### Objetivo

Incorporar los controles de interfaz gráfica de Android al proyecto TaskMaster, compilar la aplicación y comprobar su funcionamiento mediante la instalación del APK.

### 1. Componentes incluidos

La actualización incorpora los siguientes controles:

- TextView: mostrar información.
- EditText: capturar el nombre de una tarea.
- Button: representar la acción de agregar una tarea.
- RadioGroup y RadioButton: seleccionar la prioridad.
- CheckBox: marcar una opción independiente.
- Spinner: seleccionar una categoría.
- ListView: mostrar tareas de ejemplo.
- ImageButton: representar una acción mediante una imagen.

**Nota:** La programación de las acciones para agregar o eliminar tareas se realizará en la sesión 13 o posteriores.

### 2. Archivos de la actualización

Esta carpeta contiene:

- `README.md`: instrucciones de la práctica.
- `activity_main.xml`: nueva interfaz de TaskMaster.
- `taskmaster_s12.xml`: categorías y tareas de ejemplo.

### 3. Abrir el proyecto individual

Ingresa a tu repositorio personal de TaskMaster y abre GitHub Codespaces.

Todos los comandos siguientes deben ejecutarse desde la terminal, ubicada en la raíz del proyecto individual.

### 4. Conectar con la plantilla oficial

Ejecuta el siguiente comando solamente si todavía no tienes configurada la conexión `plantilla`:

```bash
git remote add plantilla https://github.com/manueldzulvalencia/TaskMaster-Plantilla-Alumnos.git
```

Verifica la conexión:

```bash
git remote -v
```

### 5. Recuperar la actualización S12

```bash
git fetch plantilla main
```

```bash
git restore --source=plantilla/main -- actualizaciones/S12/
```

Verifica los archivos descargados:

```bash
ls -l actualizaciones/S12/
```

### 6. Respaldar la interfaz anterior

Crea una carpeta de respaldos fuera de los recursos Android:

```bash
mkdir -p respaldos/S11
```

Guarda una copia de la interfaz anterior:

```bash
cp app/src/main/res/layout/activity_main.xml respaldos/S11/activity_main.xml.bak
```

**Importante:** nunca guardes archivos `.bak` dentro de `app/src/main/res/layout/`, porque pueden provocar errores durante la compilación.

### 7. Incorporar la nueva interfaz

```bash
cp actualizaciones/S12/activity_main.xml app/src/main/res/layout/activity_main.xml
```

### 8. Incorporar los recursos

```bash
cp actualizaciones/S12/taskmaster_s12.xml app/src/main/res/values/taskmaster_s12.xml
```

### 9. Compilar la aplicación

Ejecuta:

```bash
./gradlew assembleDebug
```

La compilación será correcta cuando aparezca:

```text
BUILD SUCCESSFUL
```

Si aparece `BUILD FAILED`, revisa el error y solicita orientación antes de continuar.

### 10. Generar el APK identificado

Una vez que la compilación termine correctamente:

```bash
mkdir -p versiones
```

```bash
cp app/build/outputs/apk/debug/app-debug.apk versiones/TaskMaster-S12.apk
```

Verifica:

```bash
ls -lh versiones/TaskMaster-S12.apk
```

### 11. Descargar, instalar y comprobar

Desde el explorador de archivos de Codespaces:

1. Abre la carpeta `versiones`.
2. Localiza `TaskMaster-S12.apk`.
3. Haz clic derecho y selecciona **Download**.
4. Instala el APK en tu teléfono Android.
5. Abre TaskMaster y verifica que aparezcan los controles.

Comprueba lo siguiente:

- Puedes escribir el nombre de una tarea.
- Puedes seleccionar una prioridad.
- Puedes activar o desactivar el CheckBox.
- Puedes seleccionar una categoría en el Spinner.
- Puedes visualizar las tareas de ejemplo.

La instalación también podrá comprobarse mediante BlueStacks, si está disponible.

### 12. Evidencias de aprendizaje

Entrega las siguientes evidencias:

1. Captura del archivo XML actualizado.
2. Captura de la terminal con `BUILD SUCCESSFUL`.
3. Captura de TaskMaster funcionando en Android.
4. Breve explicación de los controles incorporados.

### 13. Guardar los avances en GitHub

Antes de guardar, ejecuta:

```bash
git status --short
```

Prepara los archivos de la práctica:

```bash
git add app/src/main/res/layout/activity_main.xml app/src/main/res/values/taskmaster_s12.xml actualizaciones/S12/
```

Registra los cambios:

```bash
git commit -m "S12 - Controles de interfaz TaskMaster"
```

Publica en tu repositorio individual:

```bash
git push origin main
```

**Importante:** no publiques tu trabajo en el repositorio oficial del docente.

---

### Resultado esperado

Al finalizar tendrás una nueva pantalla de TaskMaster con controles de interfaz Android, un APK identificado como `TaskMaster-S12.apk` y tu trabajo registrado en GitHub.

**Próxima sesión (S13):** programación de eventos y acciones en Kotlin para comenzar a dar funcionalidad a los controles.

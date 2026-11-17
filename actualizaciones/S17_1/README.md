# DAMN Studio | S17.1 - Rediseño visual de TaskMaster

Actualización **incremental** para proyectos que ya tienen S17 instalada y funcionando.

## Qué cambia
- **Principal**: fondo claro, campos de entrada estilizados, encabezado, lista con tarjeta y botón morado.
- **Detalle**: encabezado en degradado morado, tarjeta informativa y botón de regreso.
- **No cambia**: los Toast de S16, Intents y navegación de S17, tareas en memoria, agregar/eliminar tareas.

## Comandos (raíz del proyecto, Codespaces)

```bash
# 1. Descargar la actualización
 git fetch plantilla main
 git restore --source=plantilla/main -- actualizaciones/S17_1/

# 2. Probar sin modificar
 /usr/bin/python3 actualizaciones/S17_1/aplicar_s17_1.py --probar

# 3. Aplicar solo si la prueba termina en OK
 /usr/bin/python3 actualizaciones/S17_1/aplicar_s17_1.py

# 4. Compilar
 ./gradlew --stop
 ./gradlew assembleDebug --no-configuration-cache --no-daemon -Dorg.gradle.java.home=/usr/lib/jvm/msopenjdk-current

# 5. Guardar el APK (únicamente si hubo BUILD SUCCESSFUL)
 mkdir -p versiones
 cp app/build/outputs/apk/debug/app-debug.apk versiones/TaskMaster-S17_1.apk
 ls -lh versiones/TaskMaster-S17_1.apk
```

### Si aparece `ModuleNotFoundError: No module named 'xml'`

Solo en Codespaces Debian con Python 3.11 y ese error:

```bash
sudo apt-get update
sudo apt-get install --reinstall -y libpython3.11-stdlib
/usr/bin/python3 -c "import xml.etree.ElementTree as ET; print('XML disponible')"
```

Si el entorno es diferente, detenerse y consultar al docente.

## Pruebas funcionales
1. Abrir la pantalla principal y revisar los nuevos colores y componentes.
2. Agregar una tarea y verificar el Toast de S16.
3. Tocar una tarea y comprobar que se abre la nueva pantalla estilizada.
4. Regresar y comprobar que la tarea permanece en la lista.
5. Seleccionar y eliminar una tarea; comprobar el Toast.
6. Confirmar que el proyecto compila y el APK se instala.

**Observación:** la información de las tareas sigue almacenada en memoria. Los cambios visuales no agregan persistencia.

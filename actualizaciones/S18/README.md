# DAMN Studio — Actualización S18 unificada

**Tema académico:** 3.2 Manipulación de Activities: comunicación y ciclo de vida.  
**Contenido técnico del paquete:** rediseño visual S17.2 + diagnóstico de ciclo de vida S18.  
**Requisito mínimo:** TaskMaster S17 instalado. No hace falta instalar S17.2 por separado. Compatible con S17.1 opcional.

## Comandos desde la raíz del repositorio personal

```bash
git fetch plantilla main
git restore --source=plantilla/main -- actualizaciones/S18/
/usr/bin/python3 actualizaciones/S18/aplicar_s18.py --probar
/usr/bin/python3 actualizaciones/S18/aplicar_s18.py
./gradlew --stop
./gradlew assembleDebug --no-configuration-cache --no-daemon -Dorg.gradle.java.home=/usr/lib/jvm/msopenjdk-current
mkdir -p versiones
cp app/build/outputs/apk/debug/app-debug.apk versiones/TaskMaster-S18.apk
```

**Si aparece `No module named xml`:** en Codespaces Debian/Python 3.11, solo entonces ejecutar `sudo apt-get update` y `sudo apt-get install --reinstall -y libpython3.11-stdlib`, verificar con `/usr/bin/python3 -c "import xml.etree.ElementTree as ET; print('XML disponible')"` y repetir la prueba.

## Comprobar funcionamiento
- Agregar, consultar y eliminar tareas con los Toast existentes
- Abrir DetalleActivity y regresar sin crear pantallas duplicadas
- Ver el nuevo estilo visual de las dos pantallas
- Pasar la app a segundo plano y regresar
- En un equipo con ADB conectado, ver el registro: `adb logcat -s TaskMasterCiclo:D '*:S'` (si no hay ADB, registrar el comportamiento de manera visual y explicar los métodos)

## Guardar en GitHub
```bash
git status --short
git add -- actualizaciones/S18/ app/src/main
git diff --cached --stat
git commit -m "S18 - Diseno visual y ciclo de vida de Activities"
git push origin main
```

No añadir `respaldos/`, `.gradle/`, `app/build/` ni `versiones/` al commit.

**Advertencia:** el registro de eventos se añade a los archivos `MainActivity.kt` y `DetalleActivity.kt`, no persiste las tareas tras la recreación del proceso. La persistencia se aborda en S19.

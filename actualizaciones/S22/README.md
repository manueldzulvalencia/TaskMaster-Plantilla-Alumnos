# TaskMaster Pro · Sesión 22 · Multimedia

## Requisitos

- Repositorio personal con S20.2 y S21 **ya aplicadas**.
- Remote Git `plantilla` configurado hacia la plantilla oficial.
- **No borres los datos ni desinstales la aplicación** al instalar S22.

## Contenido

- `aplicar_s22.py`: instalador interactivo (con `--probar` y `--editar`).
- `MultimediaS22Activity.kt.template`: reproductor de audio usando `MediaPlayer`.
- `tm22_audio_demo.wav`: audio instrumental de demostración original de 12 segundos; no necesita internet.
- El instalador genera recursos Android, `configuracion/multimedia_s22.json` y, una sola vez, `documentacion/S22_avances.md`.

## Instalación

```bash
git fetch plantilla main
git restore --source=plantilla/main -- actualizaciones/S22/
/usr/bin/python3 actualizaciones/S22/aplicar_s22.py --probar
/usr/bin/python3 actualizaciones/S22/aplicar_s22.py
./gradlew assembleDebug --no-configuration-cache --no-daemon -Dorg.gradle.java.home=/usr/lib/jvm/msopenjdk-current
mkdir -p versiones
cp app/build/outputs/apk/debug/app-debug.apk versiones/TaskMaster-S22.apk
```

Si deseas cambiar título, propósito, mensaje o indicaciones:

```bash
/usr/bin/python3 actualizaciones/S22/aplicar_s22.py --editar
./gradlew assembleDebug --no-configuration-cache --no-daemon -Dorg.gradle.java.home=/usr/lib/jvm/msopenjdk-current
cp app/build/outputs/apk/debug/app-debug.apk versiones/TaskMaster-S22.apk
```

## Prueba

1. Instalar el APK como **actualización** de S21, no como app nueva.
2. Abrir menú lateral > `Centro multimedia`.
3. Comprobar título, propósito y mensaje personalizados.
4. Reproducir y escuchar el audio, pausar, reanudar, detener y volver a reproducir.
5. Regresar y comprobar que tareas/JSON/exportación S21 siguen funcionando.
6. Documentar observaciones y evidencias en Google Docs S22.

## Precauciones

- `--probar` valida y **no modifica ni solicita respuestas**.
- Ejecutar de nuevo sin `--editar` conserva la configuración, y el registro `.md` existente nunca se sobrescribe.
- `--editar` modifica la configuración y textos visibles, pero no reescribe la bitácora inicial ya creada; el estado actualizado estará en `configuracion/multimedia_s22.json`.
- El audio es genérico: evita afirmar que contiene consejos específicos de mascotas, salud o estudio.
- Al salir de la pantalla se libera el audio.
- El instalador preserva el código de exportación de S21; no ejecuta el de S20 después de S21/S22.

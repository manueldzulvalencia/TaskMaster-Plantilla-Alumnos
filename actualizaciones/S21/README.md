# S21 · TaskMaster Pro — Exportación JSON

## Propósito
Activar «Exportar datos» en la app S20.2 personalizada, utilizando el selector de documentos de Android (`ACTION_CREATE_DOCUMENT`). El estudiante elige la carpeta y crea una copia de `tareas.json`, que conserva el esquema JSON v2. **No implementa la importación ni restauración.**

## Requisitos
- Proyecto con S20.2 ejecutada y compilable.
- `configuracion/proyecto.json` y `TaskMasterS20.kt` existentes.
- Misma firma y `applicationId` al actualizar el APK, para no perder datos.

## Instalación

```bash
git fetch plantilla main
git restore --source=plantilla/main -- actualizaciones/S21/
/usr/bin/python3 actualizaciones/S21/aplicar_s21.py --probar
/usr/bin/python3 actualizaciones/S21/aplicar_s21.py
./gradlew assembleDebug --no-configuration-cache --no-daemon -Dorg.gradle.java.home=/usr/lib/jvm/msopenjdk-current
```

APK: `app/build/outputs/apk/debug/app-debug.apk`.

## Prueba real en Android / BlueStacks
1. Instala encima de S20 (sin desinstalar ni borrar datos).
2. Agrega una tarea de prueba, con fecha y categoría.
3. Abre menú ☰ > **Exportar datos**.
4. Selecciona Documentos o Descargas y confirma guardar (nombre sugerido: `NombreDeLaApp_S21.json`).
5. Abre el archivo exportado desde un gestor de archivos y verifica JSON v2 y tarea nueva.
6. Regresa a TaskMaster Pro: las tareas originales siguen allí.
7. Prueba opcional: cancelar el selector, sin perder las tareas.

## Bitácora técnica y Google Docs
- `documentacion/S21_avances.md` se crea automáticamente **solo si no existe**. No requiere edición por el alumno.
- La reflexión, capturas y evidencia académica se entregan **en Google Docs**, no en Markdown.
- `documentacion/S20_decisiones.md` y `configuracion/proyecto.json` no son alterados.

## Precauciones
- **No ejecutar de nuevo el instalador S20 después de S21**, porque S20 podría regenerar la clase `TaskMasterS20.kt` y desactivar el menú de exportación. Si ocurre, vuelve a ejecutar `aplicar_s21.py` y compila de nuevo.
- No desinstales la app antes de actualizar: Android podría borrar sus datos privados.
- El destino escogido puede variar entre Android real y BlueStacks. El selector requiere un proveedor de documentos disponible.
- Si falla la escritura, podría quedar un archivo vacío o incompleto en el destino; revisar contenido antes de dar el respaldo por válido.
- El campo `fechaProgramada` de tareas heredadas de S19 puede ser `null`; las tareas nuevas creadas en S20 exigen fecha.

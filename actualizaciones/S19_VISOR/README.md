# S19 · Mini parche de laboratorio: Ver JSON guardado

**Objetivo:** observar el contenido REAL de `tareas.json` en la app, sin ADB ni permisos root.

**Requisito:** S19 instalada, compilada y funcional.

Desde la raíz del proyecto:

```bash
/usr/bin/python3 actualizaciones/S19_VISOR/aplicar_visor_s19.py --probar
/usr/bin/python3 actualizaciones/S19_VISOR/aplicar_visor_s19.py
./gradlew assembleDebug --no-configuration-cache --no-daemon -Dorg.gradle.java.home=/usr/lib/jvm/msopenjdk-current
```

El botón **VER JSON GUARDADO** se agrega debajo de la lista. Abre un cuadro con el contenido leído del archivo privado de la app y permite copiarlo. No modifica ni exporta automáticamente el archivo. Los cambios al archivo solo los realiza la lógica ya implementada en S19 al agregar o eliminar tareas.

**Nota docente:** Para distribuir S19 a los alumnos con una sola compilación, fusionar previamente este parche en el instalador S19 oficial. El paquete S19_VISOR está pensado primero para pruebas docentes sobre S19 instalada.

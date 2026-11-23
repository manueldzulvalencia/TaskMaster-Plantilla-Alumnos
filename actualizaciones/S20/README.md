# S20 · TaskMaster Pro — Desde S19 (actualización acumulativa)

**Punto de partida:** repositorio del alumno al finalizar S19. **No requiere S19.1 ni S19_PRO_BASE.**

## Funcionalidad

- Nueva interfaz Android: bienvenida inicial, Inicio, Mis tareas (búsqueda/filtro), Nueva tarea (fecha obligatoria), Detalle, menú lateral.
- Funcionalidad activa: tareas, detalle, eliminación con confirmación, visor JSON v2 y preferencias.
- Categorías, Calendario, Estadísticas, Exportar, Configuración y Acerca de abren **En construcción**.
- Migración del **arreglo de cadenas JSON de S19** a documento JSON **v2** con `version` y `tareas`.
- Primera migración: guarda `tareas_s19_respaldo.json` en el almacenamiento privado Android (no en Codespaces).
- Las tareas anteriores **no reciben fechas inventadas** (`fechaProgramada: null`). Las nuevas requieren fecha.
- Si el JSON antiguo contenía `[]`, seguirá habiendo cero tareas. Si borraste tareas en S19, no se recuperan.
- La identidad se guarda en `configuracion/proyecto.json`, preferencias Android y recursos compilados.
- El archivo `documentacion/S20_decisiones.md` se genera automáticamente para la fase de reporte.
- Conserva MainActivity, DetalleActivity y sus registros de ciclo de vida de S18. Deja el código anterior en el repositorio para consulta.

## Docente (en el repositorio plantilla)

1. Copia `actualizaciones/S20` al repositorio plantilla (sin `__pycache__`).
2. Publica los archivos con `git add actualizaciones/S20 && git commit -m "S20 - TaskMaster Pro" && git push origin main`.
3. **Primero prueba con tu repositorio docente** partiendo de una copia o commit de S19.
4. Ejecuta `--probar`; después, instalador interactivo o argumentos de prueba:

```bash
/usr/bin/python3 actualizaciones/S20/aplicar_s20.py --probar
/usr/bin/python3 actualizaciones/S20/aplicar_s20.py --nombre StudyMaster --giro Educación --publico Estudiantes --color 2
```

## Alumno (GitHub Codespaces)

```bash
git status --short
git fetch plantilla main
git restore --source=plantilla/main -- actualizaciones/S20/
/usr/bin/python3 actualizaciones/S20/aplicar_s20.py --probar
/usr/bin/python3 actualizaciones/S20/aplicar_s20.py
./gradlew assembleDebug --no-configuration-cache --no-daemon -Dorg.gradle.java.home=/usr/lib/jvm/msopenjdk-current
mkdir -p versiones
cp app/build/outputs/apk/debug/app-debug.apk versiones/TaskMaster-S20.apk
git add -- actualizaciones/S20/ app/src/main/ configuracion/proyecto.json documentacion/S20_decisiones.md versiones/TaskMaster-S20.apk
git commit -m "S20 - Personalizacion y persistencia TaskMaster Pro"
git push origin main
```

**Nota:** si `git status --short` muestra modificaciones S19 sin confirmar, primero guarda ese avance en un commit. Si `plantilla` no existe, configúralo con la URL oficial que te dio el docente; no se incluye ninguna URL inventada aquí.

## Validación esencial en Android / BlueStacks

1. No desinstalar ni borrar datos de la S19. Instalar el APK de S20 **sobre la misma app**. Firma e ID deben coincidir.
2. Si el APK anterior se firmó con otra clave, Android bloqueará la actualización. No desinstalar para resolverlo sin un respaldo recuperable.
3. Comprobar la bienvenida, el nuevo nombre, el color y la navegación.
4. En el menú, abrir **Ver JSON** y comprobar `version: 2` y tareas como objetos.
5. Crear una tarea con fecha. Revisar la propiedad `fechaProgramada`.
6. Eliminar una tarea y volver a abrir **Ver JSON**: no debe aparecer.
7. Eliminar todas y reiniciar; debe mantenerse `"tareas": []`.
8. Las funciones futuras deben abrir la Activity «En construcción».
9. Las tareas migradas de S19 no tienen fecha inventada; se presentan como «Sin fecha».
10. Revisar que S18 Logcat `TaskMasterCiclo` sigue funcionando.

## Reconfiguración

```bash
/usr/bin/python3 actualizaciones/S20/aplicar_s20.py --editar
```

`--editar` cambia la **identidad compilada** y los archivos locales, no el archivo privado de tareas Android. Después debes compilar un nuevo APK.

## Límites y estado de validación

El instalador y XML fueron probados sobre una reconstrucción local S17 → S18 → S19 → S20; el simulador no dispone del SDK Android ni emulador para certificar la compilación/ejecución. **El docente debe compilar y probar el APK antes de distribuirlo a los alumnos**.

## Personalización abierta — edición S20.2

El instalador ahora acepta un giro libre, un color hexadecimal `#RRGGBB` y de tres a ocho categorías personalizadas. Las opciones propuestas siguen disponibles y son opcionales.

**Ejemplo interactivo:**

```text
Nombre: PetCare
Giro: 6 → Cuidado de mascotas
Público: Personas con mascotas
Color: 5 → #00897B
Categorías: Alimentación, Veterinario, Higiene
```

**Ejemplo no interactivo para probar:**

```bash
/usr/bin/python3 actualizaciones/S20/aplicar_s20.py --nombre PetCare --giro "Cuidado de mascotas" --publico "Personas con mascotas" --color '#00897B' --categorias 'Alimentación,Veterinario,Higiene'
```

Para cambiar de giro, nombre o color de una aplicación S20 ya configurada, se ejecuta `--editar` y se vuelve a compilar. **Esta operación conserva `tareas.json` dentro de Android**, por lo que no renombra automáticamente categorías en tareas antiguas. La selección de categorías afecta a las opciones para tareas nuevas.

Los colores claros usan texto oscuro en encabezado y botones para mantener legibilidad. Debes validar el contraste y comportamiento visual con BlueStacks.

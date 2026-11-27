"""Modernización idempotente de pantallas anteriores con identidad de S20."""
from pathlib import Path

MARK = '// S24-IDENTIDAD-UNIFICADA'


def cambiar(src, antes, despues, componente):
    if antes not in src:
        raise ValueError('No se encontró '+componente+' en el código actual. Sin cambios para preservar el proyecto.')
    return src.replace(antes, despues, 1)


def plan_s20(src):
    if MARK in src:
        return src
    src = cambiar(src,
        '    private fun card() = vertical().apply { background = bg(Color.WHITE, 18); elevation = dp(2).toFloat(); setPadding(margen, margen, margen, margen) }',
        '    private fun card() = vertical().apply { background = bg(Color.WHITE, 18, EstiloS24.suave(tono)); elevation = dp(2).toFloat(); setPadding(margen, margen, margen, margen) }', 'tarjetas')
    src = cambiar(src,
        '        val titulo = EditText(host).apply { hint = "Ej. Preparar exposición"; setSingleLine(true) }',
        '''        val titulo = EditText(host).apply {
            hint = "Ej. Preparar exposición"; setSingleLine(true)
            background = bg(Color.rgb(249, 249, 253), 12, EstiloS24.suave(tono))
            setPadding(dp(14), 0, dp(14), 0)
        }''', 'campo nombre de tarea')
    src = cambiar(src, '        formulario.append(titulo); gap(formulario)',
        '        formulario.append(titulo, dp(54)); gap(formulario, 16)', 'altura de nombre')
    src = cambiar(src,
        '        val categoriasVista = Spinner(host).apply { adapter = ArrayAdapter(host, android.R.layout.simple_spinner_dropdown_item, categorias) }',
        '''        val categoriasVista = Spinner(host).apply {
            adapter = ArrayAdapter(host, android.R.layout.simple_spinner_dropdown_item, categorias)
            background = bg(Color.rgb(249, 249, 253), 12, EstiloS24.suave(tono))
            setPadding(dp(12), 0, dp(12), 0)
        }''', 'campo categoria')
    src = cambiar(src, '        formulario.append(categoriasVista); gap(formulario)',
        '        formulario.append(categoriasVista, dp(54)); gap(formulario, 16)', 'altura de categoria')
    src = cambiar(src, '        prioridades.check(2001); formulario.append(prioridades); gap(formulario)',
        '        prioridades.check(2001); formulario.append(prioridades); gap(formulario, 16)', 'espacio prioridades')
    src = cambiar(src, '        formulario.append(fechaBtn, dp(48)); gap(formulario)',
        '        formulario.append(fechaBtn, dp(52)); gap(formulario, 16)', 'selector fecha tareas')
    src = cambiar(src, '        cuerpo.append(text("Nueva tarea", 24f, azulOscuro, true)); gap(cuerpo)',
        '''        cuerpo.append(text("Nueva tarea", 24f, azulOscuro, true)); gap(cuerpo)
        val introS24 = card()
        introS24.background = bg(EstiloS24.suave(tono), 18)
        introS24.append(text("Personaliza y organiza tus pendientes", 14f, azulOscuro))
        cuerpo.append(introS24); gap(cuerpo, 14)''', 'encabezado tarea')
    src = cambiar(src, '    private fun nueva() {',
        '    '+MARK+'\n    private fun nueva() {', 'marcador de tarea')
    return src


def plan_s22(src):
    if MARK in src:
        return src
    src = cambiar(src, '''        val tono = try { Color.parseColor(getString(R.string.tm20_color)) }
            catch (_: Exception) { Color.rgb(104, 36, 196) }''',
        '        val tono = EstiloS24.primario(this)', 'color multimedia')
    src = cambiar(src, '        val oscuro = Color.rgb(20, 38, 68)',
        '        val oscuro = EstiloS24.texto', 'texto multimedia')
    src = cambiar(src, '            setBackgroundColor(Color.rgb(246, 248, 252))',
        '            setBackgroundColor(EstiloS24.fondo)', 'fondo multimedia')
    src = cambiar(src, '        header.addView(etiqueta(getString(R.string.tm20_nombre_app), 15f, contraste))',
        '''        header.addView(etiqueta("‹  Volver  ·  " + getString(R.string.tm20_nombre_app), 15f, contraste).apply {
            setOnClickListener { finish() }
        })''', 'navegacion multimedia')
    src = cambiar(src, '        root.addView(header, LinearLayout.LayoutParams(-1, -2))',
        '''        header.elevation = dp(3).toFloat()
        root.addView(header, LinearLayout.LayoutParams(-1, -2))''', 'encabezado multimedia')
    src = cambiar(src, '    private fun nuevoReproductor(): Boolean {',
        '    '+MARK+'\n    private fun nuevoReproductor(): Boolean {', 'marcador multimedia')
    return src


def plan_detalle(src):
    if MARK in src:
        return src
    return cambiar(src, '        configurarDetalleVisualS19() // DAMN-S19-DETALLE',
        '''        configurarDetalleVisualS19() // DAMN-S19-DETALLE
        EstiloS24.aplicarDetalle(this) // S24-IDENTIDAD-UNIFICADA''', 'detalle de tarea')


# Integración de navegación en la misma S24, incluida para proyectos ya actualizados.
NAV_MARK = '// S24-NAVEGACION-UNIFICADA'

def plan_navegacion(src):
    if NAV_MARK in src:
        return src
    bottom = 'listOf("⌂" to "Inicio", "☷" to "Mis tareas", "+" to "Nueva tarea", "▥" to "Estadísticas")'
    label_old = 'else if (destino == "Nueva tarea") "Nueva" else destino'
    nav_old = '        } else {\n            host.startActivity(Intent(host, EnConstruccionActivity::class.java).putExtra("seccion", destino))\n        }\n    }\n    private fun cargarDatos()'
    nav_new = '        } else if (destino == "Mis datos") {\n            host.startActivity(Intent(host, MisDatosS24Activity::class.java))\n        } else {\n            host.startActivity(Intent(host, EnConstruccionActivity::class.java).putExtra("seccion", destino))\n        }\n    }\n    private fun cargarDatos()'
    access = '        cuerpo.append(button("Ver todas las tareas", { navegar("Mis tareas") }, false))'
    checks = [bottom, label_old, nav_old, access, '    private fun mostrarMenu() {', '\n}\n\nfun Activity.configurarTaskMasterS20()']
    if any(x not in src for x in checks):
        raise ValueError('No se reconoce la navegación S20/S24. No se hizo ningún cambio.')
    src = src.replace(bottom, 'listOf("⌂" to "Inicio", "☷" to "Mis tareas", "+" to "Nueva tarea", "▤" to "Mis datos")', 1)
    src = src.replace(label_old, 'else if (destino == "Nueva tarea") "Nueva" else if (destino == "Mis datos") "Datos" else destino', 1)
    src = src.replace(nav_old, nav_new, 1)
    src = src.replace(access, access + '\n        gap(cuerpo, 14)\n        cuerpo.append(button("▤  Mis datos · SQLite", { navegar("Mis datos") }))', 1)
    start = src.index('    private fun mostrarMenu() {')
    end = src.index('\n}\n\nfun Activity.configurarTaskMasterS20()', start)
    replacement = '''    // S24-NAVEGACION-UNIFICADA
    private fun mostrarMenu() {
        val contenedor = FrameLayout(host).apply { setBackgroundColor(0x88000000.toInt()) }
        val fondoTap = View(host).apply { setOnClickListener { raiz.removeView(contenedor) } }
        contenedor.addView(fondoTap, FrameLayout.LayoutParams(-1, -1))
        val panel = vertical().apply { setBackgroundColor(Color.WHITE) }
        val ancho = (host.resources.displayMetrics.widthPixels * 0.83f).toInt()
        contenedor.addView(panel, FrameLayout.LayoutParams(ancho, -1, Gravity.START))
        val encabezado = vertical().apply {
            setBackgroundColor(tono)
            setPadding(dp(20), dp(24), dp(14), dp(20))
        }
        encabezado.append(text(nombreApp, 23f, textoSobreTono, true))
        encabezado.append(text(giro, 13f, textoSobreTono))
        panel.append(encabezado)
        val scrolling = ScrollView(host)
        val opciones = vertical().apply { setPadding(dp(14), dp(12), dp(14), dp(18)) }
        scrolling.addView(opciones)
        panel.addView(scrolling, LinearLayout.LayoutParams(-1, 0, 1f))
        fun seccion(titulo: String) {
            gap(opciones, 12)
            opciones.append(text(titulo, 11f, tono, true).apply { setPadding(dp(8), dp(6), 0, dp(4)) })
        }
        fun opcion(nombre: String, icono: String, accion: () -> Unit) {
            val item = text("$icono   $nombre", 16f, azulOscuro).apply {
                setPadding(dp(12), dp(12), dp(7), dp(12))
                isClickable = true
                setOnClickListener { raiz.removeView(contenedor); accion() }
            }
            opciones.append(item)
        }
        seccion("ORGANIZACIÓN")
        opcion("Inicio", "⌂") { navegar("Inicio") }
        opcion("Mis tareas", "☷") { navegar("Mis tareas") }
        opcion("Nueva tarea", "+") { navegar("Nueva tarea") }
        seccion("ADMINISTRACIÓN DE DATOS")
        opcion("Mis datos · SQLite", "▤") { navegar("Mis datos") }
        opcion("Ver JSON", "{}") { mostrarJson() }
        opcion("Exportar datos", "⇩") { host.startActivity(Intent(host, ExportarS21Activity::class.java)) }
        seccion("HERRAMIENTAS")
        opcion("Centro multimedia", "♫") { host.startActivity(Intent(host, MultimediaS22Activity::class.java)) }
        raiz.addView(contenedor, FrameLayout.LayoutParams(-1, -1))
    }
'''
    return src[:start] + replacement.rstrip() + src[end:]

def plan(pkg, ui_propuesta):
    return {
        pkg/'TaskMasterS20.kt': plan_navegacion(plan_s20(ui_propuesta)),
        pkg/'MultimediaS22Activity.kt': plan_s22((pkg/'MultimediaS22Activity.kt').read_text(encoding='utf8')),
        pkg/'DetalleActivity.kt': plan_detalle((pkg/'DetalleActivity.kt').read_text(encoding='utf8')),
    }

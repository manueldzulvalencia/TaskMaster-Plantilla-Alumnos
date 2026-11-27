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


def plan(pkg, ui_propuesta):
    return {
        pkg/'TaskMasterS20.kt': plan_s20(ui_propuesta),
        pkg/'MultimediaS22Activity.kt': plan_s22((pkg/'MultimediaS22Activity.kt').read_text(encoding='utf8')),
        pkg/'DetalleActivity.kt': plan_detalle((pkg/'DetalleActivity.kt').read_text(encoding='utf8')),
    }

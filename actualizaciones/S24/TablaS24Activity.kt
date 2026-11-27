package com.itcancun.mjdzul.taskmaster

import android.app.DatePickerDialog
import android.content.ContentValues
import android.content.res.ColorStateList
import android.graphics.Color
import android.graphics.Typeface
import android.graphics.drawable.GradientDrawable
import android.os.Bundle
import android.text.InputType
import java.util.Calendar
import java.util.Locale
import android.view.Gravity
import android.view.View
import android.widget.*
import androidx.appcompat.app.AlertDialog
import androidx.appcompat.app.AppCompatActivity

/** S24: dos Activities con formularios dinámicos, navegación y tarjetas visuales. */
abstract class TablaS24Activity : AppCompatActivity() {
    protected abstract val dependiente: Boolean
    private lateinit var helper: BaseDatosS24Helper
    private lateinit var tabla: String
    private lateinit var relacion: RelacionS24
    private lateinit var cuerpo: LinearLayout
    private lateinit var listado: LinearLayout
    private lateinit var scroll: ScrollView
    private val entradas = linkedMapOf<String, EditText>()
    private var fkSelector: Spinner? = null
    private var fkIds: List<Long> = emptyList()
    private var seleccionado: Long? = null
    private var botonGuardar: Button? = null
    private val navy get() = EstiloS24.texto
    private val purple get() = EstiloS24.primario(this)
    private val lime get() = EstiloS24.suave(purple)
    private val bg get() = EstiloS24.fondo
    private val gray get() = EstiloS24.secundario

    private fun dp(value: Int) = (value * resources.displayMetrics.density).toInt()
    private fun shape(color: Int, stroke: Int? = null, radius: Int = 16): GradientDrawable =
        GradientDrawable().apply {
            setColor(color); cornerRadius = dp(radius).toFloat()
            if (stroke != null) setStroke(dp(1), stroke)
        }
    private fun vertical(pad: Int = 0) = LinearLayout(this).apply {
        orientation = LinearLayout.VERTICAL; setPadding(dp(pad), dp(pad), dp(pad), dp(pad))
    }
    private fun label(s: String, size: Float = 14f, color: Int = navy, bold: Boolean = false) =
        TextView(this).apply {
            text = s; textSize = size; setTextColor(color)
            if (bold) setTypeface(null, Typeface.BOLD)
        }
    private fun line(padTop: Int = 10) = View(this).apply {
        background = shape(Color.rgb(226, 227, 237), radius = 1)
        layoutParams = LinearLayout.LayoutParams(-1, dp(1)).apply { topMargin = dp(padTop) }
    }
    private fun actionButton(s: String, color: Int, onClick: () -> Unit) = Button(this).apply {
        text = s; isAllCaps = false; textSize = 14f
        setTextColor(EstiloS24.contraste(color))
        backgroundTintList = ColorStateList.valueOf(color)
        setOnClickListener { onClick() }
    }
    private fun sectionTitle(s: String) = label(s, 18f, navy, true).apply {
        setPadding(0, dp(4), 0, dp(12))
    }
    private fun friendly(raw: String) = raw.replace('_', ' ').replaceFirstChar { it.uppercase() }

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        try {
            helper = BaseDatosS24Helper(this)
            relacion = helper.relacion()
            tabla = if (dependiente) relacion.hija else relacion.padre
            construir()
        } catch (e: Exception) { errorPantalla(e.message ?: "No se pudo abrir S24") }
    }

    private fun toolbar(title: String): LinearLayout {
        val bar = LinearLayout(this).apply {
            orientation = LinearLayout.HORIZONTAL; gravity = Gravity.CENTER_VERTICAL
            setPadding(dp(10), dp(12), dp(14), dp(12)); setBackgroundColor(purple)
        }
        val back = TextView(this).apply {
            text = "‹"; textSize = 36f; setTextColor(EstiloS24.contraste(purple))
            gravity = Gravity.CENTER; contentDescription = "Volver al menú principal"
            setOnClickListener { finish() }
        }
        bar.addView(back, LinearLayout.LayoutParams(dp(50), dp(52)))
        val stack = vertical().apply { setPadding(dp(6), 0, 0, 0) }
        stack.addView(label("S24  ·  BASE DE DATOS", 11f, EstiloS24.contraste(purple), true))
        stack.addView(label(title, 22f, EstiloS24.contraste(purple), true))
        bar.addView(stack, LinearLayout.LayoutParams(0, -2, 1f))
        return bar
    }

    private fun construir() {
        val root = vertical().apply { setBackgroundColor(bg) }
        root.addView(toolbar(friendly(tabla)))
        scroll = ScrollView(this).apply { isFillViewport = true }
        cuerpo = vertical(16)
        scroll.addView(cuerpo)
        root.addView(scroll, LinearLayout.LayoutParams(-1, 0, 1f))
        setContentView(root)
        val intro = vertical(14).apply { background = shape(EstiloS24.suave(purple)) }
        intro.addView(label(if (dependiente) "TABLA RELACIONADA" else "TABLA PRINCIPAL", 11f, purple, true))
        intro.addView(label(if (dependiente) "Registra datos asociados a ${friendly(relacion.padre)}" else "Administra tus registros de ${friendly(tabla)}", 15f, navy))
        cuerpo.addView(intro, LinearLayout.LayoutParams(-1, -2).apply { bottomMargin = dp(16) })
        val formCard = vertical(16).apply { background = shape(Color.WHITE, EstiloS24.suave(purple)) }
        formCard.addView(sectionTitle("Nuevo registro"))
        cuerpo.addView(formCard)
        construirFormulario(formCard)
        cuerpo.addView(sectionTitle("Registros existentes").apply { setPadding(0, dp(22), 0, dp(10)) })
        listado = vertical()
        cuerpo.addView(listado)
        refrescar()
    }

    private fun construirFormulario(card: LinearLayout) {
        for (col in helper.columnas(tabla)) {
            if (col.pk) continue
            card.addView(label(friendly(col.nombre) + if (col.obligatorio) " *" else " (opcional)", 13f, navy, true).apply {
                setPadding(0, dp(8), 0, dp(4))
            })
            if (dependiente && col.nombre == relacion.columnaHija) {
                fkSelector = Spinner(this).apply {
                    background = shape(Color.rgb(249, 249, 253), EstiloS24.suave(purple), 10)
                    minimumHeight = dp(52); setPadding(dp(10), 0, dp(10), 0)
                }
                card.addView(fkSelector, LinearLayout.LayoutParams(-1, dp(52)))
                continue
            }
            val input = EditText(this).apply {
                hint = "Escribe ${friendly(col.nombre).lowercase()}"
                textSize = 15f; setSingleLine(true)
                setPadding(dp(12), 0, dp(12), 0)
                background = shape(Color.rgb(249, 249, 253), EstiloS24.suave(purple), 10)
                inputType = when (col.tipo) {
                    "INTEGER" -> InputType.TYPE_CLASS_NUMBER or InputType.TYPE_NUMBER_FLAG_SIGNED
                    "REAL" -> InputType.TYPE_CLASS_NUMBER or InputType.TYPE_NUMBER_FLAG_DECIMAL or InputType.TYPE_NUMBER_FLAG_SIGNED
                    else -> InputType.TYPE_CLASS_TEXT
                }
            }
            // Campos de fecha TEXT usan calendario nativo, también si se añadieron en S23.
            if (col.tipo == "TEXT" && (col.nombre.contains("fecha", ignoreCase = true) ||
                        col.nombre.equals("date", ignoreCase = true) || col.nombre.endsWith("_date", ignoreCase = true))) {
                input.hint = "Seleccionar fecha 📅"
                input.isFocusable = false
                input.isClickable = true
                input.setOnClickListener {
                    val cal = Calendar.getInstance()
                    DatePickerDialog(this, { _, year, month, day ->
                        input.setText(String.format(Locale.US, "%04d-%02d-%02d", year, month + 1, day))
                    }, cal.get(Calendar.YEAR), cal.get(Calendar.MONTH), cal.get(Calendar.DAY_OF_MONTH)).show()
                }
            }
            entradas[col.nombre] = input
            card.addView(input, LinearLayout.LayoutParams(-1, dp(52)))
        }
        botonGuardar = actionButton("＋  Guardar registro", purple) { guardar() }
        card.addView(botonGuardar, LinearLayout.LayoutParams(-1, dp(50)).apply { topMargin = dp(14) })
        card.addView(actionButton("Limpiar formulario", navy) { limpiar() }, LinearLayout.LayoutParams(-1, dp(46)))
    }

    private fun cargarSelector(preseleccion: Long? = null) {
        if (!dependiente) return
        val registros = helper.registros(relacion.padre)
        fkIds = registros.mapNotNull { (it[relacion.columnaPadre] as? Number)?.toLong() }
        val opciones = registros.map { r ->
            r.entries.filter { it.key != relacion.columnaPadre }
                .take(2).joinToString(" · ") { "${it.value ?: ""}" }
                .ifBlank { "#${r[relacion.columnaPadre]}" }
        }
        fkSelector?.adapter = ArrayAdapter(this, android.R.layout.simple_spinner_dropdown_item,
            opciones.ifEmpty { listOf("Primero registra ${friendly(relacion.padre)}") })
        if (preseleccion != null) fkIds.indexOf(preseleccion).takeIf { it >= 0 }?.let { fkSelector?.setSelection(it) }
    }

    private fun guardar() {
        try {
            val values = ContentValues()
            for (col in helper.columnas(tabla)) {
                if (col.pk) continue
                if (dependiente && col.nombre == relacion.columnaHija) {
                    val id = fkIds.getOrNull(fkSelector?.selectedItemPosition ?: -1)
                        ?: throw IllegalArgumentException("Primero registra ${friendly(relacion.padre)}")
                    values.put(col.nombre, id)
                    continue
                }
                val s = entradas[col.nombre]?.text?.toString()?.trim().orEmpty()
                if (s.isEmpty()) {
                    if (col.obligatorio) throw IllegalArgumentException("Completa ${friendly(col.nombre)}")
                    values.putNull(col.nombre)
                } else when (col.tipo) {
                    "INTEGER" -> values.put(col.nombre, s.toLongOrNull() ?: throw IllegalArgumentException("${col.nombre} debe ser entero"))
                    "REAL" -> values.put(col.nombre, s.toDoubleOrNull() ?: throw IllegalArgumentException("${col.nombre} debe ser decimal"))
                    else -> values.put(col.nombre, s)
                }
            }
            helper.guardar(tabla, values, seleccionado)
            Toast.makeText(this, "Registro guardado correctamente", Toast.LENGTH_SHORT).show()
            limpiar(); refrescar()
        } catch (e: Exception) { mensaje(e.message ?: "Error al guardar") }
    }

    private fun limpiar() {
        seleccionado = null
        entradas.values.forEach { it.setText("") }
        botonGuardar?.text = "＋  Guardar registro"
        cargarSelector()
    }

    private fun editar(r: Map<String, Any?>) {
        val pk = helper.columnas(tabla).first { it.pk }.nombre
        seleccionado = (r[pk] as Number).toLong()
        entradas.forEach { (name, edit) -> edit.setText(r[name]?.toString() ?: "") }
        cargarSelector(if (dependiente) (r[relacion.columnaHija] as? Number)?.toLong() else null)
        botonGuardar?.text = "✓  Actualizar registro #$seleccionado"
        scroll.smoothScrollTo(0, 0)
    }

    private fun eliminar(r: Map<String, Any?>) {
        val pk = helper.columnas(tabla).first { it.pk }.nombre
        val id = (r[pk] as Number).toLong()
        AlertDialog.Builder(this).setTitle("¿Eliminar registro?")
            .setMessage("Se eliminará el registro #$id. Si tiene registros relacionados, SQLite impedirá borrarlo.")
            .setNegativeButton("Cancelar", null)
            .setPositiveButton("Eliminar") { _, _ ->
                try {
                    helper.eliminar(tabla, id)
                    Toast.makeText(this, "Registro eliminado", Toast.LENGTH_SHORT).show()
                    limpiar(); refrescar()
                } catch (e: Exception) { mensaje("No se pudo eliminar: existen referencias o restricciones. ${e.message ?: ""}") }
            }.show()
    }

    private fun refrescar() {
        if (dependiente) cargarSelector()
        listado.removeAllViews()
        val registros = helper.registros(tabla)
        if (registros.isEmpty()) {
            val vacio = vertical(18).apply { background = shape(Color.WHITE, EstiloS24.suave(purple)) }
            vacio.addView(label("Aún no hay registros", 16f, navy, true))
            vacio.addView(label("Completa el formulario para agregar el primero.", 13f, gray))
            listado.addView(vacio)
            return
        }
        val pk = helper.columnas(tabla).first { it.pk }.nombre
        registros.forEach { r ->
            val card = vertical(14).apply { background = shape(Color.WHITE, EstiloS24.suave(purple)) }
            val first = r.entries.firstOrNull { it.key != pk && (!dependiente || it.key != relacion.columnaHija) }
            card.addView(label(first?.value?.toString() ?: "Registro #${r[pk]}", 17f, navy, true))
            r.entries.filter { it.key != pk && it.key != first?.key }.forEach { (k, v) ->
                card.addView(label("${friendly(k)}: ${v ?: "—"}", 13f, gray).apply {
                    setPadding(0, dp(3), 0, 0)
                })
            }
            card.addView(line(12))
            val buttons = LinearLayout(this).apply { orientation = LinearLayout.HORIZONTAL; gravity = Gravity.END }
            val edit = actionButton("Editar", purple) { editar(r) }
            val delete = actionButton("Eliminar", navy) { eliminar(r) }
            buttons.addView(edit, LinearLayout.LayoutParams(0, dp(46), 1f))
            buttons.addView(delete, LinearLayout.LayoutParams(0, dp(46), 1f).apply { leftMargin = dp(8) })
            card.addView(buttons, LinearLayout.LayoutParams(-1, -2).apply { topMargin = dp(10) })
            listado.addView(card, LinearLayout.LayoutParams(-1, -2).apply { bottomMargin = dp(12) })
        }
    }

    private fun errorPantalla(msg: String) {
        val root = vertical().apply { setBackgroundColor(bg) }
        root.addView(toolbar("Error en base de datos"))
        val content = vertical(18).apply { background = shape(Color.WHITE) }
        content.addView(label("No se pudo abrir la pantalla", 19f, purple, true))
        content.addView(label(msg, 15f, navy))
        root.addView(content, LinearLayout.LayoutParams(-1, -2).apply {
            setMargins(dp(16), dp(20), dp(16), 0)
        })
        setContentView(root)
    }
    private fun mensaje(msg: String) {
        AlertDialog.Builder(this).setMessage(msg).setPositiveButton("Aceptar", null).show()
    }
}

class TablaPrincipalS24Activity : TablaS24Activity() { override val dependiente = false }
class TablaDependienteS24Activity : TablaS24Activity() { override val dependiente = true }

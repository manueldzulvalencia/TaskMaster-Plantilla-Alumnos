package com.itcancun.mjdzul.taskmaster

import android.content.Intent
import android.graphics.Color
import android.graphics.Typeface
import android.os.Bundle
import android.view.Gravity
import android.view.View
import android.widget.LinearLayout
import android.widget.ScrollView
import android.widget.TextView
import androidx.appcompat.app.AppCompatActivity

/** Centro único de navegación SQLite; los nombres proceden del SQL S23, no de textos fijos. */
class MisDatosS24Activity : AppCompatActivity() {
    private fun dp(n: Int) = (resources.displayMetrics.density * n).toInt()
    private fun texto(s: String, size: Float, color: Int, bold: Boolean = false) = TextView(this).apply {
        text = s
        textSize = size
        setTextColor(color)
        if (bold) setTypeface(null, Typeface.BOLD)
    }
    private fun tarjeta(): LinearLayout = LinearLayout(this).apply {
        orientation = LinearLayout.VERTICAL
        setPadding(dp(18), dp(18), dp(18), dp(18))
        background = EstiloS24.forma(this@MisDatosS24Activity, Color.WHITE, 18, EstiloS24.suave(EstiloS24.primario(this@MisDatosS24Activity)))
        elevation = dp(2).toFloat()
    }
    private fun nombre(s: String) = s.replace('_', ' ').replaceFirstChar { it.uppercase() }

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        val primary = EstiloS24.primario(this)
        val contrast = EstiloS24.contraste(primary)
        val root = LinearLayout(this).apply {
            orientation = LinearLayout.VERTICAL
            setBackgroundColor(EstiloS24.fondo)
        }
        val header = LinearLayout(this).apply {
            orientation = LinearLayout.HORIZONTAL
            gravity = Gravity.CENTER_VERTICAL
            setPadding(dp(10), dp(12), dp(16), dp(12))
            setBackgroundColor(primary)
        }
        header.addView(texto("‹", 36f, contrast, true).apply {
            gravity = Gravity.CENTER
            contentDescription = "Regresar al inicio"
            setOnClickListener { finish() }
        }, LinearLayout.LayoutParams(dp(50), dp(52)))
        val titles = LinearLayout(this).apply { orientation = LinearLayout.VERTICAL }
        titles.addView(texto(getString(R.string.tm20_nombre_app), 12f, contrast))
        titles.addView(texto("Mis datos", 23f, contrast, true))
        header.addView(titles)
        root.addView(header)
        val scroll = ScrollView(this)
        val content = LinearLayout(this).apply {
            orientation = LinearLayout.VERTICAL
            setPadding(dp(16), dp(20), dp(16), dp(25))
        }
        scroll.addView(content)
        root.addView(scroll, LinearLayout.LayoutParams(-1, 0, 1f))
        setContentView(root)
        try {
            val relacion = BaseDatosS24Helper(this).relacion()
            content.addView(texto("Administra la información de tu aplicación", 16f, EstiloS24.texto, true))
            content.addView(texto("Dos tablas, una base SQLite y una relación 1:N.", 13f, EstiloS24.secundario).apply {
                setPadding(0, dp(5), 0, dp(20))
            })
            fun opcion(table: String, subtitle: String, detail: String, target: Class<out AppCompatActivity>) {
                val card = tarjeta()
                card.addView(texto(nombre(table), 20f, EstiloS24.texto, true))
                card.addView(texto(subtitle, 12f, primary, true).apply { setPadding(0, dp(6), 0, dp(8)) })
                card.addView(texto(detail, 14f, EstiloS24.secundario))
                card.addView(texto("Abrir registros  ›", 14f, primary, true).apply { setPadding(0, dp(14), 0, 0) })
                card.isClickable = true
                card.isFocusable = true
                card.contentDescription = "Administrar ${nombre(table)}"
                card.setOnClickListener { startActivity(Intent(this, target)) }
                content.addView(card, LinearLayout.LayoutParams(-1, -2).apply { bottomMargin = dp(16) })
            }
            opcion(relacion.padre, "TABLA PRINCIPAL", "Crear, consultar, editar y eliminar registros.", TablaPrincipalS24Activity::class.java)
            opcion(relacion.hija, "TABLA RELACIONADA", "Administrar registros asociados a ${nombre(relacion.padre)}.", TablaDependienteS24Activity::class.java)
            val info = tarjeta()
            info.setBackgroundColor(EstiloS24.suave(primary))
            info.addView(texto("Relación 1:N", 15f, EstiloS24.texto, true))
            info.addView(texto("1 ${nombre(relacion.padre)}  →  varios ${nombre(relacion.hija)}", 13f, EstiloS24.texto))
            content.addView(info)
        } catch (e: Exception) {
            content.addView(texto("No se pudo abrir la base de datos: ${e.message ?: "Error desconocido"}", 15f, EstiloS24.texto))
        }
    }
}

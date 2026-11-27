package com.itcancun.mjdzul.taskmaster

import android.app.Activity
import android.content.Context
import android.content.res.ColorStateList
import android.graphics.Color
import android.graphics.drawable.GradientDrawable
import android.view.ViewGroup
import android.widget.Button
import android.widget.LinearLayout
import android.widget.ScrollView
import android.widget.TextView

/** Tema compartido. La fuente oficial es el color elegido por cada alumno en S20. */
object EstiloS24 {
    val texto: Int = Color.rgb(20, 38, 68)
    val secundario: Int = Color.rgb(92, 104, 122)
    val fondo: Int = Color.rgb(246, 248, 252)

    fun primario(ctx: Context): Int = try {
        Color.parseColor(ctx.getString(R.string.tm20_color))
    } catch (_: Exception) { Color.rgb(35, 94, 178) }

    fun contraste(color: Int): Int {
        val luminosidad = (Color.red(color) * 299 + Color.green(color) * 587 + Color.blue(color) * 114) / 1000
        return if (luminosidad >= 150) Color.BLACK else Color.WHITE
    }

    fun suave(color: Int): Int = Color.rgb(
        (Color.red(color) * 0.11f + 255f * 0.89f).toInt(),
        (Color.green(color) * 0.11f + 255f * 0.89f).toInt(),
        (Color.blue(color) * 0.11f + 255f * 0.89f).toInt()
    )

    fun forma(ctx: Context, color: Int, radio: Int = 14, borde: Int? = null): GradientDrawable =
        GradientDrawable().apply {
            setColor(color)
            cornerRadius = ctx.resources.displayMetrics.density * radio
            if (borde != null) setStroke((ctx.resources.displayMetrics.density).toInt().coerceAtLeast(1), borde)
        }

    /** Moderniza la Activity de detalle sin alterar sus datos ni su ciclo de vida. */
    fun aplicarDetalle(activity: Activity) {
        val color = primario(activity)
        val content = activity.findViewById<ViewGroup>(android.R.id.content)
        val scroll = content.getChildAt(0) as? ScrollView ?: return
        scroll.setBackgroundColor(fondo)
        val column = scroll.getChildAt(0) as? LinearLayout ?: return
        val header = column.getChildAt(0) as? LinearLayout ?: return
        header.background = forma(activity, color, 0)
        for (i in 0 until header.childCount) {
            (header.getChildAt(i) as? TextView)?.setTextColor(contraste(color))
        }
        (header.getChildAt(0) as? TextView)?.apply {
            contentDescription = "Regresar"
            setOnClickListener { activity.finish() }
        }
        val button = activity.findViewById<Button>(R.id.btnVolverTareas)
        button?.apply {
            backgroundTintList = ColorStateList.valueOf(color)
            setTextColor(contraste(color))
            isAllCaps = false
        }
    }
}

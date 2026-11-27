package com.itcancun.mjdzul.taskmaster

import android.content.ContentValues
import android.database.sqlite.SQLiteConstraintException
import android.os.Bundle
import android.graphics.Color
import android.view.Gravity
import android.view.View
import android.widget.*
import android.text.InputType
import androidx.appcompat.app.AlertDialog
import androidx.appcompat.app.AppCompatActivity

/** Motor de formularios compartido. Dos Activities concretas heredan esta clase. */
abstract class TablaS24Activity : AppCompatActivity() {
    protected abstract val dependiente:Boolean
    private lateinit var helper:BaseDatosS24Helper
    private lateinit var tabla:String
    private lateinit var relacion:RelacionS24
    private lateinit var area:LinearLayout
    private lateinit var lista:LinearLayout
    private val entradas=linkedMapOf<String,EditText>()
    private var fkSelector:Spinner?=null
    private var fkIds:List<Long> = emptyList()
    private var seleccionado:Long?=null
    private var boton:Button?=null
    private val morado=Color.rgb(104,37,168)
    override fun onCreate(savedInstanceState:Bundle?) {
        super.onCreate(savedInstanceState)
        try {
            helper=BaseDatosS24Helper(this); relacion=helper.relacion()
            tabla=if(dependiente) relacion.hija else relacion.padre
            construir()
        } catch (e:Exception) { errorPantalla(e.message ?: "No se pudo abrir S24") }
    }
    private fun errorPantalla(mensaje:String) { val tv=TextView(this).apply {text="S24: $mensaje";textSize=18f;setPadding(24,40,24,24)}; setContentView(tv) }
    private fun dp(n:Int)=(n*resources.displayMetrics.density).toInt()
    private fun contenedor()=LinearLayout(this).apply {orientation=LinearLayout.VERTICAL;setPadding(dp(16),dp(12),dp(16),dp(12))}
    private fun titulo(s:String)=TextView(this).apply {text=s;textSize=21f;setTextColor(morado);setPadding(0,dp(12),0,dp(10))}
    private fun texto(s:String)=TextView(this).apply {text=s;textSize=15f;setPadding(0,dp(5),0,dp(2))}
    private fun construir(){
        val scroll=ScrollView(this)
        area=contenedor()
        scroll.addView(area)
        setContentView(scroll)
        area.addView(titulo("S24 · ${tabla.replaceFirstChar { it.uppercase() }}"))
        area.addView(texto("CRUD de tu tabla creada en S23"))
        formulario()
        area.addView(titulo("Registros existentes"))
        lista=contenedor().apply {setPadding(0,0,0,0)}
        area.addView(lista)
        refrescar()
    }
    private fun formulario(){
        for(col in helper.columnas(tabla)) {
            if(col.pk) continue
            if(dependiente && col.nombre==relacion.columnaHija) {
                area.addView(texto("${col.nombre} · Selecciona ${relacion.padre}"))
                fkSelector=Spinner(this)
                area.addView(fkSelector)
                continue
            }
            area.addView(texto(col.nombre + if(col.obligatorio) " *" else " (opcional)"))
            val input=EditText(this).apply {
                hint=col.nombre
                setSingleLine(true)
                inputType=when(col.tipo){
                    "INTEGER"->InputType.TYPE_CLASS_NUMBER or InputType.TYPE_NUMBER_FLAG_SIGNED
                    "REAL"->InputType.TYPE_CLASS_NUMBER or InputType.TYPE_NUMBER_FLAG_DECIMAL or InputType.TYPE_NUMBER_FLAG_SIGNED
                    else->InputType.TYPE_CLASS_TEXT
                }
            }
            entradas[col.nombre]=input
            area.addView(input)
        }
        boton=Button(this).apply {text="Guardar nuevo registro";setOnClickListener { guardar() }}
        area.addView(boton)
        area.addView(Button(this).apply {text="Limpiar formulario";setOnClickListener { limpiar() }})
    }
    private fun cargarSelector(preseleccion:Long?=null){
        if(!dependiente)return
        val registros=helper.registros(relacion.padre)
        fkIds=registros.mapNotNull { (it[relacion.columnaPadre] as? Number)?.toLong() }
        val opciones=registros.map { r -> r.entries.filter { it.key != relacion.columnaPadre }.take(2).joinToString(" · "){"${it.value ?: ""}"}.ifBlank { "#${r[relacion.columnaPadre]}" } }
        fkSelector?.adapter=ArrayAdapter(this,android.R.layout.simple_spinner_dropdown_item,opciones.ifEmpty {listOf("Primero registra ${relacion.padre}")})
        if(preseleccion!=null) fkIds.indexOf(preseleccion).takeIf{it>=0}?.let{fkSelector?.setSelection(it)}
    }
    private fun guardar(){
        try {
            val values=ContentValues()
            for(col in helper.columnas(tabla)){
                if(col.pk) continue
                if(dependiente && col.nombre==relacion.columnaHija){
                    val id=fkIds.getOrNull(fkSelector?.selectedItemPosition ?: -1) ?: throw IllegalArgumentException("Registra primero ${relacion.padre}")
                    values.put(col.nombre,id);continue
                }
                val s=entradas[col.nombre]?.text?.toString()?.trim().orEmpty()
                if(s.isEmpty()){
                    if(col.obligatorio) throw IllegalArgumentException("Completa ${col.nombre}")
                    values.putNull(col.nombre)
                } else when(col.tipo){
                    "INTEGER"->values.put(col.nombre,s.toLongOrNull() ?: throw IllegalArgumentException("${col.nombre} debe ser entero"))
                    "REAL"->values.put(col.nombre,s.toDoubleOrNull() ?: throw IllegalArgumentException("${col.nombre} debe ser decimal"))
                    else->values.put(col.nombre,s)
                }
            }
            helper.guardar(tabla,values,seleccionado)
            Toast.makeText(this,"Registro guardado",Toast.LENGTH_SHORT).show()
            limpiar(); refrescar()
        } catch(e:Exception){mensaje(e.message ?: "Error al guardar")}
    }
    private fun limpiar(){ seleccionado=null;entradas.values.forEach{it.setText("")};boton?.text="Guardar nuevo registro"; cargarSelector() }
    private fun editar(r:Map<String,Any?>){
        val pk=helper.columnas(tabla).first{it.pk}.nombre
        seleccionado=(r[pk] as Number).toLong()
        entradas.forEach{(campo,edit)->edit.setText(r[campo]?.toString() ?: "")}
        cargarSelector(if(dependiente)(r[relacion.columnaHija] as? Number)?.toLong() else null)
        boton?.text="Actualizar registro #$seleccionado"
        (area.parent as? ScrollView)?.smoothScrollTo(0,0)
    }
    private fun eliminar(r:Map<String,Any?>){
        val pk=helper.columnas(tabla).first{it.pk}.nombre
        val id=(r[pk] as Number).toLong()
        AlertDialog.Builder(this).setTitle("Confirmar eliminación")
            .setMessage("¿Eliminar el registro #$id? Si tiene registros relacionados, SQLite impedirá eliminarlo.")
            .setNegativeButton("Cancelar",null)
            .setPositiveButton("Eliminar") { _,_->
                try { helper.eliminar(tabla,id); Toast.makeText(this,"Registro eliminado",Toast.LENGTH_SHORT).show(); limpiar();refrescar() }
                catch(e:Exception){mensaje("No se puede eliminar: existen referencias o restricciones. ${e.message ?: ""}")}
            }.show()
    }
    private fun refrescar(){
        if(dependiente)cargarSelector()
        lista.removeAllViews()
        val registros=helper.registros(tabla)
        if(registros.isEmpty()){lista.addView(texto("Todavía no hay registros."));return}
        registros.forEach { r ->
            val fila=contenedor().apply {setPadding(dp(8),dp(8),dp(8),dp(8))}
            val visible=r.entries.joinToString("  ·  "){"${it.key}: ${it.value ?: "—"}"}
            fila.addView(texto(visible))
            val acciones=LinearLayout(this).apply {orientation=LinearLayout.HORIZONTAL;gravity=Gravity.END}
            acciones.addView(Button(this).apply {text="Editar";setOnClickListener{editar(r)}})
            acciones.addView(Button(this).apply {text="Eliminar";setOnClickListener{eliminar(r)}})
            fila.addView(acciones)
            lista.addView(fila)
            val linea=View(this).apply{setBackgroundColor(Color.LTGRAY)}
            lista.addView(linea,LinearLayout.LayoutParams(-1,dp(1)))
        }
    }
    private fun mensaje(msg:String){AlertDialog.Builder(this).setMessage(msg).setPositiveButton("Aceptar",null).show()}
}

class TablaPrincipalS24Activity:TablaS24Activity(){ override val dependiente=false }
class TablaDependienteS24Activity:TablaS24Activity(){ override val dependiente=true }

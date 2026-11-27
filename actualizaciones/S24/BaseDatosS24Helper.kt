package com.itcancun.mjdzul.taskmaster

import android.content.Context
import android.content.ContentValues
import android.database.sqlite.SQLiteDatabase
import android.database.sqlite.SQLiteOpenHelper

data class ColumnaS24(val nombre: String, val tipo: String, val obligatorio: Boolean, val pk: Boolean)
data class RelacionS24(val padre: String, val hija: String, val columnaHija: String, val columnaPadre: String)

class BaseDatosS24Helper(private val ctx: Context): SQLiteOpenHelper(ctx, "taskmaster_s24.db", null, 1) {
    override fun onConfigure(db: SQLiteDatabase) { super.onConfigure(db); db.setForeignKeyConstraintsEnabled(true) }
    override fun onCreate(db: SQLiteDatabase) {
        val sql = ctx.assets.open("S23_base_datos.sql").bufferedReader().use { it.readText() }
        // El paquete S23 admite CREATE TABLE y PRAGMA; el instalador comprueba su seguridad.
        val sinComentarios = sql.lineSequence()
            .filterNot { it.trimStart().startsWith("--") }
            .joinToString("\n")
        sinComentarios.split(';')
            .map { it.trim() }
            .filter { it.isNotBlank() && !it.startsWith("PRAGMA", ignoreCase = true) }
            .forEach { db.execSQL(it) }
    }
    override fun onUpgrade(db: SQLiteDatabase, oldVersion: Int, newVersion: Int) {
        // Nunca eliminar tablas o registros automáticamente.
    }
    fun tablas(): List<String> {
        val result = mutableListOf<String>()
        readableDatabase.rawQuery("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%' ORDER BY name", null).use { c ->
            while (c.moveToNext()) result.add(c.getString(0))
        }
        return result
    }
    fun columnas(tabla: String): List<ColumnaS24> {
        val result = mutableListOf<ColumnaS24>()
        readableDatabase.rawQuery("PRAGMA table_info(\"${seguro(tabla)}\")", null).use { c ->
            while(c.moveToNext()) result.add(ColumnaS24(c.getString(1), c.getString(2).uppercase(), c.getInt(3)!=0, c.getInt(5)!=0))
        }
        return result
    }
    fun relacion(): RelacionS24 {
        for (tabla in tablas()) {
            readableDatabase.rawQuery("PRAGMA foreign_key_list(\"${seguro(tabla)}\")", null).use { c ->
                if (c.moveToFirst()) return RelacionS24(c.getString(2), tabla, c.getString(3), c.getString(4))
            }
        }
        error("El esquema de S23 no contiene una relación 1:N")
    }
    fun registros(tabla: String): List<Map<String, Any?>> {
        val result= mutableListOf<Map<String,Any?>>()
        readableDatabase.rawQuery("SELECT * FROM \"${seguro(tabla)}\" ORDER BY rowid DESC", null).use { c ->
            while(c.moveToNext()) {
                val fila = linkedMapOf<String,Any?>()
                for (i in 0 until c.columnCount) fila[c.getColumnName(i)] = if(c.isNull(i)) null else when(c.getType(i)) {
                    android.database.Cursor.FIELD_TYPE_INTEGER -> c.getLong(i)
                    android.database.Cursor.FIELD_TYPE_FLOAT -> c.getDouble(i)
                    else -> c.getString(i)
                }
                result.add(fila)
            }
        }
        return result
    }
    fun guardar(tabla:String, values:ContentValues, id:Long? = null):Long {
        val db=writableDatabase
        if(id==null) return db.insertOrThrow(seguro(tabla), null, values)
        val pk=columnas(tabla).first{it.pk}.nombre
        db.update(seguro(tabla),values,"\"${seguro(pk)}\" = ?",arrayOf(id.toString()))
        return id
    }
    fun eliminar(tabla:String, id:Long):Int {
        val pk=columnas(tabla).first{it.pk}.nombre
        return writableDatabase.delete(seguro(tabla),"\"${seguro(pk)}\" = ?",arrayOf(id.toString()))
    }
    fun seguro(s:String):String { require(Regex("[A-Za-z_][A-Za-z0-9_]*").matches(s)) {"Identificador SQL inválido"};return s }
}

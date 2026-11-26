-- EJEMPLO: StudyMaster | materias 1:N actividades
PRAGMA foreign_keys = ON;
CREATE TABLE materias (
    id_materia INTEGER PRIMARY KEY,
    nombre TEXT NOT NULL,
    docente TEXT
);
CREATE TABLE actividades (
    id_actividad INTEGER PRIMARY KEY,
    titulo TEXT NOT NULL,
    fecha_entrega TEXT,
    id_materia INTEGER NOT NULL,
    FOREIGN KEY (id_materia) REFERENCES materias(id_materia)
);

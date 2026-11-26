-- EJEMPLO DOCENTE: HomeTask | habitaciones 1:N mantenimientos
PRAGMA foreign_keys = ON;
CREATE TABLE habitaciones (
    id_habitacion INTEGER PRIMARY KEY,
    nombre TEXT NOT NULL,
    ubicacion TEXT NOT NULL
);
CREATE TABLE mantenimientos (
    id_mantenimiento INTEGER PRIMARY KEY,
    descripcion TEXT NOT NULL,
    fecha TEXT,
    id_habitacion INTEGER NOT NULL,
    FOREIGN KEY (id_habitacion) REFERENCES habitaciones(id_habitacion)
);

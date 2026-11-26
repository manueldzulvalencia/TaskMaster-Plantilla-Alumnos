-- EJEMPLO: PetCare | mascotas 1:N vacunas
PRAGMA foreign_keys = ON;
CREATE TABLE mascotas (
    id_mascota INTEGER PRIMARY KEY,
    nombre TEXT NOT NULL,
    especie TEXT NOT NULL
);
CREATE TABLE vacunas (
    id_vacuna INTEGER PRIMARY KEY,
    nombre_vacuna TEXT NOT NULL,
    fecha TEXT,
    id_mascota INTEGER NOT NULL,
    FOREIGN KEY (id_mascota) REFERENCES mascotas(id_mascota)
);

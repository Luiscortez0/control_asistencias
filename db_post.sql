-- ============================================
-- BASE DE DATOS: lccg (versión PostgreSQL)
-- ============================================

DROP TABLE IF EXISTS asistencias, alumnos_clases, clases, materias, profesores, alumnos CASCADE;

-- ========================
-- TABLA: alumnos
-- ========================
CREATE TABLE alumnos (
  no_cuenta INTEGER PRIMARY KEY,
  nombre VARCHAR(100) NOT NULL,
  carrera VARCHAR(100) NOT NULL,
  grado INTEGER NOT NULL,
  grupo VARCHAR(1) NOT NULL,
  edad INTEGER NOT NULL,
  correo VARCHAR(100) NOT NULL
);

-- ========================
-- TABLA: profesores
-- ========================
CREATE TABLE profesores (
  no_cuenta INTEGER PRIMARY KEY,
  nombre VARCHAR(100) NOT NULL,
  facultad VARCHAR(100) NOT NULL,
  carrera VARCHAR(100) NOT NULL,
  correo VARCHAR(100) NOT NULL
);

-- ========================
-- TABLA: materias
-- ========================
CREATE TABLE materias (
  id_materia VARCHAR(8) PRIMARY KEY,
  nombre VARCHAR(50) NOT NULL,
  carrera VARCHAR(100) NOT NULL,
  grado INTEGER NOT NULL,
  creditos INTEGER NOT NULL
);

-- ========================
-- TABLA: clases
-- ========================
CREATE TABLE clases (
  id_clase SERIAL PRIMARY KEY,
  no_cuenta_maestro INTEGER NOT NULL REFERENCES profesores(no_cuenta) ON DELETE CASCADE,
  id_materia VARCHAR(8) NOT NULL REFERENCES materias(id_materia) ON DELETE CASCADE,
  grupo VARCHAR(1)
);

-- ========================
-- TABLA: alumnos_clases
-- ========================
CREATE TABLE alumnos_clases (
  no_cuenta_alumno INTEGER REFERENCES alumnos(no_cuenta) ON DELETE CASCADE,
  id_clase INTEGER REFERENCES clases(id_clase) ON DELETE CASCADE,
  PRIMARY KEY (no_cuenta_alumno, id_clase)
);

-- ========================
-- TABLA: asistencias
-- ========================
CREATE TABLE asistencias (
  id SERIAL PRIMARY KEY,
  no_cuenta_alumno INTEGER REFERENCES alumnos(no_cuenta) ON DELETE CASCADE,
  id_clase INTEGER REFERENCES clases(id_clase) ON DELETE CASCADE,
  fecha DATE NOT NULL,
  hora TIME NOT NULL,
  estado TEXT CHECK (estado IN ('Presente', 'Ausente', 'Justificado')) DEFAULT 'Presente'
);

-- ========================
-- DATOS DE EJEMPLO
-- ========================
INSERT INTO alumnos VALUES
(20206720, 'Luis Carlos Cortez', 'ICI', 5, 'B', 20, 'lcortez8@ucol.mx'),
(20206724, 'Maria Jose', 'Reposteria', 5, 'A', 20, 'mar@ucol.mx'),
(58621421, 'Naye Cortez', 'Reposteria', 4, 'B', 18, 'naye4343@ucol.mx');

INSERT INTO profesores VALUES
(12345678, 'Tono', 'FIME', 'ICI', 'tono7@ucol.mx'),
(12567898, 'Apolinar', 'FIME', 'ICI', 'apo98@ucol.mx'),
(47478989, 'Oswaldo', 'FIME', 'ICI', 'oswaldo123@ucol.mx');

INSERT INTO materias VALUES
('ESRE1234', 'Escalamiento de Redes', 'ICI', 4, 6),
('PROW1234', 'Programación Web', 'ICI', 5, 6),
('PRUEBA00', 'Materia de Prueba', 'ICI', 3, 8);

INSERT INTO clases (no_cuenta_maestro, id_materia, grupo) VALUES
(12345678, 'PRUEBA00', 'A'),
(12567898, 'ESRE1234', 'B');

INSERT INTO alumnos_clases VALUES
(20206720, 1),
(20206724, 1),
(58621421, 2);

INSERT INTO asistencias (no_cuenta_alumno, id_clase, fecha, hora, estado) VALUES
(20206720, 1, '2025-10-19', '10:00:00', 'Presente'),
(20206724, 1, '2025-10-19', '10:00:00', 'Ausente'),
(58621421, 2, '2025-10-19', '12:00:00', 'Presente');
-- ============================================

ALTER TABLE alumnos ADD COLUMN password VARCHAR(255);
ALTER TABLE profesores ADD COLUMN password VARCHAR(255);

-- Asignar contraseñas iniciales (puedes cambiarlas luego)
UPDATE alumnos SET password = '1234';
UPDATE profesores SET password = 'abcd';
-- ============================================

CREATE TABLE administradores (
  id SERIAL PRIMARY KEY,
  nombre VARCHAR(100) NOT NULL,
  usuario VARCHAR(50) UNIQUE NOT NULL,
  password VARCHAR(255) NOT NULL
);

-- Ejemplo de usuario inicial
INSERT INTO administradores (nombre, usuario, password)
VALUES ('Admin General', 'admin', 'xJEQJ');
-- ============================================ 

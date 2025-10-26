import streamlit as st
import psycopg2
import pandas as pd
import bcrypt

# =====================================
# CONFIGURACIÓN
# =====================================
st.set_page_config(page_title="Sistema de Asistencias - UdeC", page_icon="🎓")
st.title("🎓 Sistema de Control de Asistencias")

# =====================================
# CONEXIÓN A LA BASE DE DATOS
# =====================================
def get_connection():
    return psycopg2.connect(st.secrets["postgres"]["url"])

# =====================================
# FUNCIÓN: verificar contraseña
# =====================================
def verificar_password(password_ingresada, password_bd):
    if password_bd is None:
        return False
    try:
        return bcrypt.checkpw(password_ingresada.encode('utf-8'), password_bd.encode('utf-8'))
    except Exception:
        return password_ingresada == password_bd  # fallback si no está cifrada

# =====================================
# LOGIN
# =====================================
rol = st.selectbox("Selecciona tu rol", ["Alumno", "Profesor", "Administrador"])
no_cuenta = st.text_input("Número de cuenta")
password = st.text_input("Contraseña", type="password")

if st.button("Iniciar sesión"):
    try:
        conn = get_connection()
        cursor = conn.cursor()

        tabla = "alumnos" if rol == "Alumno" else "profesores"
        cursor.execute(f"SELECT nombre, password FROM {tabla} WHERE no_cuenta = %s", (no_cuenta,))
        user = cursor.fetchone()

        if not user:
            st.error("❌ Número de cuenta no encontrado.")
        elif verificar_password(password, user[1]):
            st.success(f"✅ Bienvenido {user[0]}")

            if rol == "Administrador":
                st.subheader("⚙️ Panel de Administración")

                opcion = st.sidebar.selectbox(
                    "Selecciona una acción",
                    ["Ver alumnos", "Ver profesores", "Ver materias", "Ver clases", "Agregar registros", "Editar asistencias"]
                )

                if opcion == "Ver alumnos":
                    cursor.execute("SELECT * FROM alumnos ORDER BY no_cuenta")
                    st.dataframe(pd.DataFrame(cursor.fetchall(), columns=["No. Cuenta", "Nombre", "Carrera", "Grado", "Grupo", "Edad", "Correo", "Password"]))
                
                elif opcion == "Ver profesores":
                    cursor.execute("SELECT * FROM profesores ORDER BY no_cuenta")
                    st.dataframe(pd.DataFrame(cursor.fetchall(), columns=["No. Cuenta", "Nombre", "Facultad", "Carrera", "Correo", "Password"]))

                elif opcion == "Ver materias":
                    cursor.execute("SELECT * FROM materias ORDER BY id_materia")
                    st.dataframe(pd.DataFrame(cursor.fetchall(), columns=["ID Materia", "Nombre", "Carrera", "Grado", "Créditos"]))

                elif opcion == "Agregar registros":
                    tabla = st.selectbox("¿A qué tabla deseas agregar?", ["alumnos", "profesores", "materias"])
                    if tabla == "alumnos":
                        with st.form("agregar_alumno"):
                            no_cuenta = st.number_input("Número de cuenta", min_value=10000000, max_value=99999999)
                            nombre = st.text_input("Nombre completo")
                            carrera = st.text_input("Carrera")
                            grado = st.number_input("Grado", min_value=1, max_value=10)
                            grupo = st.text_input("Grupo", max_chars=1)
                            edad = st.number_input("Edad", min_value=15, max_value=100)
                            correo = st.text_input("Correo")
                            password = st.text_input("Contraseña")
                            enviar = st.form_submit_button("Guardar")
                            if enviar:
                                cursor.execute("""
                                    INSERT INTO alumnos (no_cuenta, nombre, carrera, grado, grupo, edad, correo, password)
                                    VALUES (%s,%s,%s,%s,%s,%s,%s,%s)
                                """, (no_cuenta, nombre, carrera, grado, grupo, edad, correo, password))
                                conn.commit()
                                st.success("✅ Alumno agregado correctamente.")

            if rol == "Profesor":
                st.subheader("📚 Tus clases")
                query = """
                    SELECT c.id_clase, m.nombre AS materia, c.grupo
                    FROM clases c
                    JOIN materias m ON c.id_materia = m.id_materia
                    WHERE c.no_cuenta_maestro = %s
                """
                cursor.execute(query, (no_cuenta,))
                clases = pd.DataFrame(cursor.fetchall(), columns=["ID Clase", "Materia", "Grupo"])
                st.dataframe(clases)

                st.subheader("🧾 Editar asistencias")
                clase_id = st.number_input("ID de clase", min_value=1)
                if st.button("Ver alumnos"):
                    cursor.execute("""
                        SELECT a.no_cuenta, a.nombre, asis.estado, asis.fecha
                        FROM asistencias asis
                        JOIN alumnos a ON a.no_cuenta = asis.no_cuenta_alumno
                        WHERE asis.id_clase = %s
                    """, (clase_id,))
                    df = pd.DataFrame(cursor.fetchall(), columns=["No. Cuenta", "Alumno", "Estado", "Fecha"])
                    st.dataframe(df)

                    if not df.empty:
                        alumno_id = st.selectbox("Selecciona alumno", df["No. Cuenta"])
                        nuevo_estado = st.selectbox("Nuevo estado", ["Presente", "Ausente", "Justificado"])
                        if st.button("Actualizar estado"):
                            cursor.execute("""
                                UPDATE asistencias
                                SET estado=%s
                                WHERE no_cuenta_alumno=%s AND id_clase=%s
                            """, (nuevo_estado, alumno_id, clase_id))
                            conn.commit()
                            st.success("✅ Asistencia actualizada.")
            else:
                st.subheader("📘 Tus asistencias")
                query = """
                    SELECT m.nombre AS materia, a.estado, a.fecha, a.hora
                    FROM asistencias a
                    JOIN clases c ON a.id_clase = c.id_clase
                    JOIN materias m ON c.id_materia = m.id_materia
                    WHERE a.no_cuenta_alumno = %s
                """
                cursor.execute(query, (no_cuenta,))
                asistencias = pd.DataFrame(cursor.fetchall(), columns=["Materia", "Estado", "Fecha", "Hora"])
                st.dataframe(asistencias)

        else:
            st.error("❌ Contraseña incorrecta.")
    except Exception as e:
        st.error(f"Error al conectar: {e}")

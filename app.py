import streamlit as st
import psycopg2
import pandas as pd
import bcrypt

# =====================================
# CONFIGURACIÓN INICIAL
# =====================================
st.set_page_config(page_title="Sistema de Asistencias - UdeC", page_icon="🎓")
st.title("🎓 Sistema de Control de Asistencias")

# =====================================
# CONTROL DE SESIÓN
# =====================================
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.rol = None
    st.session_state.user_id = None
    st.session_state.nombre = None


# =====================================
# FUNCIÓN DE CONEXIÓN
# =====================================
def get_connection():
    return psycopg2.connect(st.secrets["postgres"]["url"])


# =====================================
# VERIFICAR CONTRASEÑA
# =====================================
def verificar_password(password_ingresada, password_bd):
    if password_bd is None:
        return False
    try:
        return bcrypt.checkpw(password_ingresada.encode('utf-8'), password_bd.encode('utf-8'))
    except Exception:
        return password_ingresada == password_bd  # fallback si no está cifrada


# =====================================
# SI YA ESTÁ LOGUEADO
# =====================================
if st.session_state.logged_in:
    st.sidebar.write(f"👋 Hola, {st.session_state.nombre}")
    st.sidebar.write(f"Rol: {st.session_state.rol}")

    if st.sidebar.button("Cerrar sesión"):
        st.session_state.logged_in = False
        st.session_state.rol = None
        st.session_state.user_id = None
        st.session_state.nombre = None
        st.rerun()

    rol = st.session_state.rol
    no_cuenta = st.session_state.user_id

    try:
        conn = get_connection()
        cursor = conn.cursor()

        if rol == "Administrador":
            st.subheader("⚙️ Panel de Administración")

            opcion = st.sidebar.selectbox(
                "Selecciona una acción",
                ["Ver alumnos", "Ver profesores", "Ver materias", "Ver clases", "Ver alumnos/clase", "Agregar registros"]
            )

            if opcion == "Ver alumnos":
                cursor.execute("SELECT * FROM alumnos ORDER BY no_cuenta")
                st.dataframe(pd.DataFrame(cursor.fetchall(), columns=["No. Cuenta", "Nombre", "Carrera", "Grado", "Grupo", "Edad", "Correo", "Password"]))

            elif opcion == "Ver profesores":
                cursor.execute("SELECT * FROM profesores ORDER BY no_cuenta")
                st.dataframe(pd.DataFrame(cursor.fetchall(), columns=["No. Cuenta", "Nombre", "Facultad", "Carrera", "Correo", "Password"]))

            elif opcion == "Ver materias":
                cursor.execute("SELECT * FROM materias ORDER BY id_materia")
                st.dataframe(pd.DataFrame(cursor.fetchall(), columns=["ID Materia", "Nombre", "Carrera", "Grado", "Creditos"]))

            elif opcion == "Ver clases":
                cursor.execute("""
                    SELECT c.id_clase, m.nombre AS materia, c.grupo, p.nombre AS profesor
                    FROM clases c
                    JOIN materias m ON c.id_materia = m.id_materia
                    JOIN profesores p ON c.no_cuenta_maestro = p.no_cuenta
                    ORDER BY c.id_clase
                """)
                st.dataframe(pd.DataFrame(cursor.fetchall(), columns=["ID Clase", "Materia", "Grupo", "Profesor"]))

            elif opcion == "Ver alumnos/clase":
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

            elif opcion == "Agregar registros":
                tabla = st.selectbox("¿A qué tabla deseas agregar?", ["alumnos", "profesores", "materias", "clases", "alumnos_clases"])
                if tabla == "alumnos":
                    with st.form("agregar_alumno"):
                        no_cuenta_nuevo = st.number_input("Número de cuenta", min_value=10000000, max_value=99999999)
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
                            """, (no_cuenta_nuevo, nombre, carrera, grado, grupo, edad, correo, password))
                            conn.commit()
                            st.success("✅ Alumno agregado correctamente.")
                if tabla == "profesores":
                    with st.form("agregar_profesor"):
                        no_cuenta_nuevo = st.number_input("Número de cuenta", min_value=10000000, max_value=99999999)
                        nombre = st.text_input("Nombre completo")
                        facultad = st.text_input("Facultad")
                        carrera = st.text_input("Carrera")
                        correo = st.text_input("Correo")
                        password = st.text_input("Contraseña")
                        enviar = st.form_submit_button("Guardar")
                        if enviar:
                            cursor.execute("""
                                INSERT INTO profesores (no_cuenta, nombre, facultad, carrera, correo, password)
                                VALUES (%s,%s,%s,%s,%s,%s)
                            """, (no_cuenta_nuevo, nombre, facultad, carrera, correo, password))
                            conn.commit()
                            st.success("✅ Profesor agregado correctamente.")
                if tabla == "materias":
                    with st.form("agregar_materia"):
                        id_materia = st.text_input("ID de materia", max_chars=8)
                        nombre = st.text_input("Nombre de la materia")
                        carrera = st.text_input("Carrera")
                        grado = st.number_input("Grado", min_value=1, max_value=10)
                        creditos = st.number_input("Créditos", min_value=1, max_value=10)
                        enviar = st.form_submit_button("Guardar")
                        if enviar:
                            cursor.execute("""
                                INSERT INTO materias (id_materia, nombre, carrera, grado, creditos)
                                VALUES (%s,%s,%s,%s,%s)
                            """, (id_materia, nombre, carrera, grado, creditos))
                            conn.commit()
                            st.success("✅ Materia agregada correctamente.")
                if tabla == "clases":
                    with st.form("agregar_clase"):
                        no_cuenta_maestro = st.number_input("Número de cuenta del profesor", min_value=10000000, max_value=99999999)
                        id_materia = st.text_input("ID de materia", max_chars=8)
                        grupo = st.text_input("Grupo", max_chars=1)
                        enviar = st.form_submit_button("Guardar")
                        if enviar:
                            cursor.execute("""
                                INSERT INTO clases (no_cuenta_maestro, id_materia, grupo)
                                VALUES (%s,%s,%s)
                            """, (no_cuenta_maestro, id_materia, grupo))
                            conn.commit()
                            st.success("✅ Clase agregada correctamente.")
                if tabla == "alumnos_clases":
                    with st.form("agregar_alumno_clase"):
                        no_cuenta_alumno = st.number_input("Número de cuenta del alumno", min_value=10000000, max_value=99999999)
                        id_clase = st.number_input("ID de clase", min_value=1)
                        enviar = st.form_submit_button("Guardar")
                        if enviar:
                            cursor.execute("""
                                INSERT INTO alumnos_clases (no_cuenta_alumno, id_clase)
                                VALUES (%s,%s)
                            """, (no_cuenta_alumno, id_clase))
                            conn.commit()
                            st.success("✅ Alumno asignado a la clase correctamente.")

        elif rol == "Profesor":
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

            st.subheader("🧾 Registrar asistencias")

            clase_id = st.number_input("ID de clase", min_value=1)

            # Evita recargar al mostrar alumnos
            if "mostrar_alumnos" not in st.session_state:
                st.session_state.mostrar_alumnos = False

            if st.button("Ver alumnos"):
                st.session_state.mostrar_alumnos = True
                st.session_state.clase_id = clase_id
                st.rerun()

            # Si el profesor ya presionó "Ver alumnos"
            if st.session_state.mostrar_alumnos and "clase_id" in st.session_state:
                clase_id = st.session_state.clase_id
                cursor.execute("""
                    SELECT a.no_cuenta, a.nombre
                    FROM alumnos_clases al_cl
                    JOIN alumnos a ON a.no_cuenta = al_cl.no_cuenta_alumno
                    WHERE al_cl.id_clase = %s
                """, (clase_id,))
                alumnos = pd.DataFrame(cursor.fetchall(), columns=["No. Cuenta", "Alumno"])

                if alumnos.empty:
                    st.warning("⚠️ No hay alumnos asignados a esta clase.")
                else:
                    st.dataframe(alumnos)

                    st.write("### 🗓️ Registrar nueva asistencia")

                    alumno_id = st.selectbox("Selecciona alumno", alumnos["No. Cuenta"])
                    estado = st.selectbox("Estado de asistencia", ["Presente", "Ausente", "Justificado"])
                    fecha = st.date_input("Fecha de asistencia")
                    hora = st.time_input("Hora", pd.Timestamp.now().time())

                    if st.button("Registrar asistencia"):
                        try:
                            cursor.execute("""
                                INSERT INTO asistencias (no_cuenta_alumno, id_clase, fecha, hora, estado)
                                VALUES (%s, %s, %s, %s, %s)
                            """, (alumno_id, clase_id, fecha, hora, estado))
                            conn.commit()
                            st.success("✅ Asistencia registrada correctamente.")
                        except Exception as e:
                            st.error(f"❌ Error al registrar la asistencia: {e}")

        elif rol == "Alumno":
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

    except Exception as e:
        st.error(f"Error al conectar: {e}")


# =====================================
# SI NO ESTÁ LOGUEADO (LOGIN)
# =====================================
else:
    rol = st.selectbox("Selecciona tu rol", ["Alumno", "Profesor", "Administrador"])
    no_cuenta = st.text_input("Número de cuenta")
    password = st.text_input("Contraseña", type="password")

    if st.button("Iniciar sesión"):
        try:
            conn = get_connection()
            cursor = conn.cursor()

            if rol == "Administrador":
                cursor.execute("SELECT nombre, password FROM administradores WHERE usuario = %s", (no_cuenta,))
            else:
                tabla = "alumnos" if rol == "Alumno" else "profesores"
                cursor.execute(f"SELECT nombre, password FROM {tabla} WHERE no_cuenta = %s", (no_cuenta,))
            user = cursor.fetchone()

            if not user:
                st.error("❌ Usuario o número de cuenta no encontrado.")
            elif verificar_password(password, user[1]):
                st.session_state.logged_in = True
                st.session_state.rol = rol
                st.session_state.user_id = no_cuenta
                st.session_state.nombre = user[0]
                st.rerun()
            else:
                st.error("❌ Contraseña incorrecta.")
        except Exception as e:
            st.error(f"Error al conectar: {e}")

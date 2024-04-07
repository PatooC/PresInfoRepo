# Documentación Externa
import psycopg2
from flask import Flask, render_template, request, redirect, url_for, flash, get_flashed_messages
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, DecimalField, DateField, BooleanField
from wtforms.validators import DataRequired, Regexp, Length, ValidationError
from datetime import date
import re
from itertools import cycle

# Acceso DATABASE
db_config = {
    'host': 'postgres',
    'port': '5432',
    'database': 'postgres',
    'user': 'postgres',
    'password': 'pega'
}

# FLASK
app = Flask(__name__, static_folder='static')
app.config['SECRET_KEY'] = 'informatica1234'

#------------------------------------------------------------------------
# FORMULARIOS: RESCTRICCIONES
#------------------------------------------------------------------------


# Restricción: Números Negativos
def positive_number(form, field):
    if field.data is not None and field.data < 0:
        raise ValidationError('El número no puede ser negativo')

# Restricción: Carácteres Correo
def no_special_characters(form, field):
    if not field.data.isalpha() and '.' not in field.data:
        raise ValidationError('Este campo solo permite letras y puntos')

# Restricción: Carácteres Nombre
def only_letters_spaces(form, field):
    if not re.match(r'^[a-zA-Z\s]+$', field.data):
        raise ValidationError('Este campo solo permite letras y espacios.')

# Restricción: Algoritmo RUT
def validar_rut(rut):
    rut = rut.upper().replace("-", "").replace(".", "")
    rut_aux = rut[:-1]
    dv = rut[-1:]

    if not rut_aux.isdigit() or not (1_000_000 <= int(rut_aux) <= 25_000_000):
        return False

    revertido = map(int, reversed(rut_aux))
    factors = cycle(range(2, 8))
    suma = sum(d * f for d, f in zip(revertido, factors))
    residuo = suma % 11

    if dv == 'K':
        return residuo == 1
    if dv == '0':
        return residuo == 11
    return residuo == 11 - int(dv)


#------------------------------------------------------------------------
# BASES FORMULARIOS: ALTERACIÓN DE DATOS
#------------------------------------------------------------------------


# Base Formulario: Préstamo NOTEBOOK
class formulario_prestamoNote(FlaskForm):
    pres_codFunNote = DecimalField('Código de Funcionario', validators=[DataRequired(), positive_number], render_kw={"placeholder": "Sin Ceros al Inicio"})
    pres_equipoIdNote = StringField('Código del Préstamo', validators=[DataRequired(), Regexp('^\d+$', message="Solo se permiten números"), Length(min=3, max=3, message="se deben ingresar 3 carácteres.")], render_kw={"placeholder": "3 Dígitos, Rellene con 0"})
    pres_fechaNote = DateField('Fecha de Entrega', validators=[DataRequired()], default=date.today)
    pres_estimacionNote = DateField('Fecha de Devolución Estimada', validators=[DataRequired()], default=date.today)
    pres_submitNote = SubmitField('Solicitar Préstamo')

# Base Formulario: Préstamo PROYECTOR
class formulario_prestamoProye(FlaskForm):
    pres_codFunProye = DecimalField('Código de Funcionario', validators=[DataRequired(), positive_number], render_kw={"placeholder": "Sin Ceros al Inicio"})
    pres_equipoIdProye = StringField('Serie del Préstamo', validators=[DataRequired()], render_kw={"placeholder": "La Serie del Proyector"})
    pres_fechaProye = DateField('Fecha de Entrega', validators=[DataRequired()], default=date.today)
    pres_estimacionProye = DateField('Fecha de Devolución Estimada', validators=[DataRequired()], default=date.today)
    pres_submitProye = SubmitField('Solicitar Préstamo')

# Base Formulario: Devolución NOTEBOOK
class formulario_devolucionNote(FlaskForm):
    devo_equipoidNote = StringField('Código del Préstamo', validators=[DataRequired(), Regexp('^\d+$', message="Solo se permiten números"), Length(min=3, max=3, message="se deben ingresar 3 carácteres.")], render_kw={"placeholder": "3 Dígitos, Rellene con 0"})
    devo_fechaNote = DateField('Fecha de Devolución', validators=[DataRequired()], default=date.today)
    devo_submitNote = SubmitField('Devolver')

# Base Formulario: Devolución PROYECTOR
class formulario_devolucionProye(FlaskForm):
    devo_equipoidProye = StringField('Serie del Préstamo', validators=[DataRequired()], render_kw={"placeholder": "La Serie del Proyector"})
    devo_fechaProye = DateField('Fecha de Devolución', validators=[DataRequired()], default=date.today)
    devo_submitProye = SubmitField('Devolver')

# Base Formulario: Agregar Notebook
class formulario_ag_note(FlaskForm):
    ag_equipoidNote = StringField('Código del Equipo', validators=[DataRequired(), Regexp('^\d+$', message="Solo se permiten números"), Length(min=3, max=3, message="se deben ingresar 3 carácteres.")], render_kw={"placeholder": "3 Dígitos, Rellene con 0"})
    ag_bolsoNote = BooleanField('Bolso de Transporte')
    ag_estadoNote = BooleanField('Estado del Equipo')
    ag_cargador = BooleanField('¿Tiene Cargador?')
    ag_mouse = BooleanField('¿Tiene Mouse?')
    ag_modeloNote = StringField('¿Cuál es el modelo del Equipo?', validators=[DataRequired(), only_letters_spaces], render_kw={"placeholder": "Modelo Del Equipo"})
    ag_marcaNote = StringField('¿Cuál es la marca del Equipo?', validators=[DataRequired()], render_kw={"placeholder": "Marca Del Equipo"})
    ag_serieNote = StringField('Serie del Equipo', validators=[DataRequired()], render_kw={"placeholder": "Serie Del Equipo"})  
    ag_mantenimientoNote = DateField('Fecha del último mantenimiento', validators=[DataRequired()], default=date.today)
    ag_submitNote = SubmitField('Agregar')

# Base Formulario: Agregar Proyector
class formulario_ag_proye(FlaskForm):
    ag_equipoidProye = StringField('Serie del Equipo', validators=[DataRequired()], render_kw={"placeholder": "La Serie del Proyector"})
    ag_bolsoProye = BooleanField('Bolso de Transporte')
    ag_estadoProye = BooleanField('Estado del Equipo')
    ag_alimentacion = BooleanField('¿Tiene Cable de Alimentacion?')
    ag_hdmi = BooleanField('¿Tiene Cable HDMI?')
    ag_vga = BooleanField('¿Tiene Cable VGA?')
    ag_modeloProye = StringField('¿Cuál es el modelo del Equipo?', validators=[DataRequired()], render_kw={"placeholder": "Modelo del Proyector"})
    ag_marcaProye = StringField('¿Cuál es la marca del Equipo?', validators=[DataRequired()], render_kw={"placeholder": "Marca del Proyector"})
    ag_mantenimientoProye = DateField('Fecha del último mantenimiento', validators=[DataRequired()], default=date.today)
    ag_submitProye = SubmitField('Agregar')

# Base Formulario: Borrar Notebook
class formulario_br_note(FlaskForm):
    br_equipoidNote = StringField('Código del Equipo', validators=[DataRequired(), Regexp('^\d+$', message="Solo se permiten números"), Length(min=3, max=3, message="se deben ingresar 3 carácteres.")], render_kw={"placeholder": "3 Dígitos, Rellene con 0"})
    br_submitNote = SubmitField('Borrar')

# Base Formulario: Borrar Proyector
class formulario_br_proye(FlaskForm):
    br_equipoidProye = StringField('Serie del Equipo', validators=[DataRequired()], render_kw={"placeholder": "La Serie del Proyector"})
    br_submitProye = SubmitField('Borrar')

# Base Formulario: Mantenimiento Notebook
class formulario_mnt_note(FlaskForm):
    mnt_equipoidNote = StringField('Código del Equipo', validators=[DataRequired(), Regexp('^\d+$', message="Solo se permiten números"), Length(min=3, max=3, message="se deben ingresar 3 carácteres.")], render_kw={"placeholder": "3 Dígitos, Rellene con 0"})
    mnt_bolsoNote = BooleanField('Bolso de Transporte')
    mnt_estadoNote = BooleanField('Estado del Equipo')
    mnt_cargador = BooleanField('¿Tiene Cargador?')
    mnt_mouse = BooleanField('¿Tiene Mouse?')
    mnt_mantenimientoNote = DateField('Fecha del último mantenimiento', validators=[DataRequired()], default=date.today)
    mnt_submitNote = SubmitField('Cambiar')

# Base Formulario: Mantenimiento Proyector
class formulario_mnt_proye(FlaskForm):
    mnt_equipoidProye = StringField('Serie del Equipo', validators=[DataRequired()], render_kw={"placeholder": "La Serie del Proyector"})
    mnt_bolsoProye = BooleanField('Bolso de Transporte')
    mnt_estadoProye = BooleanField('Estado del Equipo')
    mnt_alimentacion = BooleanField('¿Tiene Cable de Alimentacion?')
    mnt_hdmi = BooleanField('¿Tiene Cable HDMI?')
    mnt_vga = BooleanField('¿Tiene Cable VGA?')
    mnt_mantenimientoProye = DateField('Fecha del último mantenimiento', validators=[DataRequired()], default=date.today)
    mnt_submitProye = SubmitField('Cambiar')

# Base Formulario: Agregar Funcionario
class formulario_agfun(FlaskForm):
    agfun_codfun = DecimalField('Código de Funcionario', validators=[DataRequired(), positive_number], render_kw={"placeholder": "Sin Ceros al Inicio"})
    agfun_nombre = StringField('Nombre del Funcionario', validators=[DataRequired(), only_letters_spaces], render_kw={"placeholder": "Ej: Felipe Flores"})
    agfun_correo = StringField('Correo del Funcionario', validators=[DataRequired(), no_special_characters], render_kw={"placeholder": "Ej: fflores"})
    agfun_rut = StringField('Rut del Funcionario (Recuerda seguir el formato 11111111-1)', validators=[DataRequired(), Regexp('^([0-9]{1,8}\-[0-9kK]{1})$', message="Solo se permiten números y la letra k"), Length(min=9, max=10, message="además, el RUT debe tener entre 1 y 10 caracteres.")], render_kw={"placeholder": "Ej: 11111111-1"})
    agfun_submitFun = SubmitField('Agregar')

# Base Formulario: Borrar Funcionario
class formulario_brfun(FlaskForm):
    brfun_codfun = DecimalField('Código de Funcionario', validators=[DataRequired(), positive_number], render_kw={"placeholder": "Sin Ceros al Inicio"})
    brfun_submitFun = SubmitField('Borrar')


#------------------------------------------------------------------------
# BASES FILTROS: VISTA DE DATOS
#------------------------------------------------------------------------


# Base Filtro: Funcionarios
class formulario_visfun(FlaskForm):
    visfun_filcodfun = DecimalField('Código de Funcionario', validators=[DataRequired(), positive_number], render_kw={"placeholder": "Sin Ceros al Inicio"})
    visfun_submit = SubmitField('Filtrar')

# Base Filtro: Historial de Préstamos
class formulario_his(FlaskForm):
    his_equipoid = StringField('Código del Equipo', validators=[DataRequired()], render_kw={"placeholder": "Equipo ID"})
    his_submit = SubmitField('Filtrar')

# Base Filtro: Notebooks
class formulario_visNote(FlaskForm):
    visNote_equipoid = StringField('Código del Préstamo', validators=[DataRequired(), Regexp('^\d+$', message="Solo se permiten números"), Length(min=3, max=3, message="se deben ingresar 3 carácteres.")], render_kw={"placeholder": "3 Dígitos, Rellene con 0"})
    visNote_submit = SubmitField('Filtrar')

# Base Filtro: Prestamos Activos
class formulario_visPres(FlaskForm):
    visPres_equipoid = StringField('Código del Equipo', validators=[DataRequired()], render_kw={"placeholder": "Equipo ID"})
    visPres_submit = SubmitField('Filtrar')

# Base Filtro: Proyectores
class formulario_VisProye(FlaskForm):
    VisProye_equipoid = StringField('Código del Equipo', validators=[DataRequired()], render_kw={"placeholder": "La Serie del Proyector"})
    VisProye_submit = SubmitField('Filtrar')


#------------------------------------------------------------------------
# PÁGINA PRINCIPAL: PRÉSTAMOS ACTIVOS & NAVEGACIÓN
#------------------------------------------------------------------------


#------------------------------------------
# Función, Filtro & Vista: INDEX PRÉSTAMOS ACTIVOS
@app.route('/', methods=['GET', 'POST'])
def indexPrestamos():
    # Definición de Variables a Usar
    formVisPres = formulario_visPres()

    # Submit: Filtro
    if formVisPres.validate_on_submit():
        # Obtención de Datos
        visPres_equipoid = formVisPres.visPres_equipoid.data

        # Impresión de la Base de Datos: CON Filtro Aplicado
        connection = psycopg2.connect(**db_config)
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM prestamos WHERE equipoid = %s", (visPres_equipoid,))
        datos = cursor.fetchall()
        cursor.close()
        connection.close()

        # Revisión de Filtro
        if not datos:
            flash('No se encontraron los datos del Prestamo con la ID proporcionado.', 'error')
            return redirect(url_for('indexPrestamos'))

    else:
        # Impresión de la Base de Datos: SIN Filtro Aplicado
        connection = psycopg2.connect(**db_config)
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM prestamos")
        datos = cursor.fetchall()
        cursor.close()
        connection.close()

    # Render del template HTML
    return render_template('index.html', datos=datos, formVisPres=formVisPres)
#------------------------------------------


#------------------------------------------------------------------------
# FUNCIONES PRINCIPALES: ALTERACIÓN DE DATOS
#------------------------------------------------------------------------


#------------------------------------------
# Función: PRESTAMO
@app.route('/prestamo', methods=['GET', 'POST'])
def funcionPrestamo():
    # Definición de Variables a Usar
    formPresNote = formulario_prestamoNote()
    formPresProye = formulario_prestamoProye()

    # Tabla de Datos
    connection = psycopg2.connect(**db_config)
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM notebook WHERE prestado = %s", (False,))
    datos_note = cursor.fetchall()
    cursor.execute("SELECT * FROM proyectores WHERE prestado = %s", (False,))
    datos_proye = cursor.fetchall()
    cursor.close()
    connection.close()

    # Submit: Primer Formulario 
    if request.method == 'POST' and formPresNote.pres_submitNote.data:
        if formPresNote.validate():
            # Obtención de Datos
            pres_codFunNote = formPresNote.pres_codFunNote.data
            pres_equipoIdNote = formPresNote.pres_equipoIdNote.data
            pres_fechaNote = formPresNote.pres_fechaNote.data
            pres_estimacionNote = formPresNote.pres_estimacionNote.data

            # Conexión Base de Datos
            connection = psycopg2.connect(**db_config)
            cursor = connection.cursor()
            
            # Verificación de Datos N°1
            cursor.execute("SELECT COUNT(*) FROM funcionarios WHERE codfun = %s", (pres_codFunNote,))
            pres_verificacionNoteUno = cursor.fetchone()[0]

            if pres_verificacionNoteUno > 0:
                # Verificación de Datos N°2
                cursor.execute("SELECT COUNT(*) FROM notebook WHERE codigo = %s", (pres_equipoIdNote,))
                pres_verificacionNoteDos = cursor.fetchone()[0]
                
                if pres_verificacionNoteDos > 0:
                    
                    # Verificación de Datos N°3
                    cursor.execute("SELECT COUNT(*) FROM prestamos WHERE equipoid = %s", (pres_equipoIdNote,))
                    pres_verificacionNoteTres = cursor.fetchone()[0]
                    
                    if pres_verificacionNoteTres > 0:

                        # Caso de Error
                        flash('El equipo ya está en préstamo.', 'notebook_error')
                    else:

                        # Verificación de Datos N°4
                        cursor.execute("SELECT estado FROM notebook WHERE codigo = %s", (pres_equipoIdNote,))
                        pres_verificacionNoteCuatro = cursor.fetchone()

                        if pres_verificacionNoteCuatro == True:

                            # Ejecución y Modificación de la Base de Datos
                            connection.commit()
                            cursor.execute("SELECT nombre FROM funcionarios WHERE codfun = %s", (pres_codFunNote,))
                            pres_nombrefun = cursor.fetchone()
                            
                            cursor.execute("INSERT INTO prestamos (codfun, equipoid, entrega, estimada, nombrefun) VALUES (%s, %s, %s, %s, %s)", (pres_codFunNote, pres_equipoIdNote, pres_fechaNote, pres_estimacionNote, pres_nombrefun))

                            cursor.execute("UPDATE notebook SET prestado = %s WHERE codigo = %s", (True, pres_equipoIdNote))

                            connection.commit()
                            cursor.close()
                            connection.close()

                            # Redirección Final
                            return redirect(url_for('indexPrestamos'))
                        else:
                            # Caso de Error
                            flash('El equipo no está operativo.', 'notebook_error')
                else:
                    # Caso de Error
                    flash('El equipo no existe.', 'notebook_error')
            else:
                # Caso de Error
                flash('El funcionario no existe.', 'notebook_error')
        else:
            # Caso de Error de Validación
            error_msg = 'Error al agregar el funcionario, '
            if formPresNote.errors:
                for field, errors in formPresNote.errors.items():
                    error_msg += f'{formPresNote[field].label.text}: {", ".join(errors)}. '
            else:
                error_msg += 'El formulario tiene errores.'
            flash(error_msg, 'notebook_error')
    # Submit: Segundo Formulario
    elif request.method == 'POST' and formPresProye.pres_submitProye.data:
        if formPresProye.validate():
            # Obtención de Datos
            pres_codFunProye = formPresProye.pres_codFunProye.data
            pres_equipoIdProye = formPresProye.pres_equipoIdProye.data
            pres_fechaProye = formPresProye.pres_fechaProye.data
            pres_estimacionProye = formPresProye.pres_estimacionProye.data

            # Conexión Base de Datos
            connection = psycopg2.connect(**db_config)
            cursor = connection.cursor()

            # Verificación de Datos N°1
            cursor.execute("SELECT COUNT(*) FROM funcionarios WHERE codfun = %s", (pres_codFunProye,))
            pres_verificacionUno = cursor.fetchone()[0]

            if pres_verificacionUno > 0:
                # Verificación de Datos N°1
                cursor.execute("SELECT COUNT(*) FROM proyectores WHERE serie = %s", (pres_equipoIdProye,))
                pres_verificacionDos = cursor.fetchone()[0]

                if pres_verificacionDos > 0:

                    # Verificación de Datos N°3
                    cursor.execute("SELECT COUNT(*) FROM prestamos WHERE equipoid = %s", (pres_equipoIdProye,))
                    pres_verificacionProyeTres = cursor.fetchone()[0]
                    
                    if pres_verificacionProyeTres > 0:

                        # Caso de Error
                        flash('El equipo ya está en préstamo.', 'notebook_error')
                    else:
                        
                        # Verificación de Datos N°4
                        cursor.execute("SELECT estado FROM proyectores WHERE serie = %s", (pres_equipoIdProye,))
                        pres_verificacionProyeCuatro = cursor.fetchone()

                        if pres_verificacionProyeCuatro == True:
                            # Ejecución y Modificación de la Base de Datos
                            cursor.execute("INSERT INTO prestamos (codfun, equipoid, entrega, estimada) VALUES (%s, %s, %s, %s)", (pres_codFunProye, pres_equipoIdProye, pres_fechaProye, pres_estimacionProye))

                            cursor.execute("UPDATE proyectores SET prestado = %s WHERE serie = %s", (True, pres_equipoIdProye))

                            connection.commit()
                            cursor.close()
                            connection.close()

                            # Redirección Final
                            return redirect(url_for('indexPrestamos'))
                        else:
                            # Caso de Error
                            flash('El equipo no está operativo.', 'proyector_error')
                else:
                    # Caso de Error
                    flash('El equipo no existe.', 'proyector_error')
            else:
                # Caso de Error
                flash('El funcionario no existe.', 'proyector_error')
        else:
            # Caso de Error de Validación
            error_msg = 'Error al agregar el funcionario, '
            if formPresNote.errors:
                for field, errors in formPresNote.errors.items():
                    error_msg += f'{formPresNote[field].label.text}: {", ".join(errors)}. '
            else:
                error_msg += 'El formulario tiene errores.'
            flash(error_msg, 'proyector_error')

    # Render del template HTML
    return render_template('prestamo.html', formPresNote=formPresNote, formPresProye=formPresProye, datos_note=datos_note, datos_proye=datos_proye)
#------------------------------------------


#------------------------------------------
# Función: DEVOLUCIÓN
@app.route('/devolucion', methods=['GET', 'POST'])
def funcionDevolucion():
    # Definición de Variables a Usar
    formDevoNote = formulario_devolucionNote()
    formDevoProye = formulario_devolucionProye()

    # Impresión de la Base de Datos: SIN Filtro Aplicado
    connection = psycopg2.connect(**db_config)
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM prestamos")
    datos = cursor.fetchall()
    cursor.close()
    connection.close()
    
    # Submit:  Primer Formulario
    if request.method == 'POST' and formDevoNote.devo_submitNote.data:
        if formDevoNote.validate():
            # Obtención de Datos
            devo_equipoidNote = formDevoNote.devo_equipoidNote.data
            devo_fechaNote = formDevoNote.devo_fechaNote.data

            # Conexión Base de Datos
            connection = psycopg2.connect(**db_config)
            cursor = connection.cursor()

            try:
                # Verificación de Datos N°1
                cursor.execute("SELECT COUNT(*) FROM notebook WHERE codigo = %s", (devo_equipoidNote,))
                devo_verificacionNoteUno = cursor.fetchone()[0]

                if devo_verificacionNoteUno > 0:
                    # Verificación de Datos N°2
                    cursor.execute("SELECT COUNT(*) FROM prestamos WHERE equipoid = %s", (devo_equipoidNote,))
                    devo_verificacionNoteDos = cursor.fetchone()[0]
                    
                    if devo_verificacionNoteDos > 0:

                        # Modificaciones Efectuadas: Base de Datos
                        cursor.execute("UPDATE prestamos SET devolucion = %s WHERE equipoid = %s", (devo_fechaNote, devo_equipoidNote))

                        cursor.execute("INSERT INTO historial (codfun, equipoid, entrega, estimada, devolucion) SELECT codfun, equipoid, entrega, estimada, devolucion FROM prestamos WHERE equipoid = %s", (devo_equipoidNote,))
                        
                        cursor.execute("DELETE FROM prestamos WHERE equipoid = %s", (devo_equipoidNote,))

                        cursor.execute("UPDATE notebook SET prestado = %s WHERE codigo = %s", (False, devo_equipoidNote))
                        
                        connection.commit()
                        
                        # Redirección Final
                        return redirect(url_for('indexPrestamos'))
                    else:
                        # Caso de Error
                        flash('El préstamo no existe.', 'error')
                else:
                # Caso de Error
                    flash('El equipo no existe.', 'error')
            
            finally:
                # Cierre de Conexión con Base de Datos
                cursor.close()
                connection.close()
    
    # Submit:  Segundo Formulario
    elif request.method == 'POST' and formDevoProye.devo_submitProye.data:
        if formDevoProye.validate():
            # Obtención de Datos
            devo_equipoidProye = formDevoProye.devo_equipoidProye.data
            devo_fechaProye = formDevoProye.devo_fechaProye.data

            # Conexión Base de Datos
            connection = psycopg2.connect(**db_config)
            cursor = connection.cursor()

            try:
                # Verificación de Datos N°1
                cursor.execute("SELECT COUNT(*) FROM proyectores WHERE serie = %s", (devo_equipoidProye,))
                devo_verificacionProyeUno = cursor.fetchone()[0]
                
                if devo_verificacionProyeUno > 0:
                    # Verificación de Datos N°2
                    cursor.execute("SELECT COUNT(*) FROM prestamos WHERE equipoid = %s", (devo_equipoidProye,))
                    devo_verificacionProyeDos = cursor.fetchone()[0]
                    
                    if devo_verificacionProyeDos > 0:

                        # Modificaciones Efectuadas: Base de Datos
                        cursor.execute("UPDATE prestamos SET devolucion = %s WHERE equipoid = %s", (devo_fechaProye, devo_equipoidProye))

                        cursor.execute("INSERT INTO historial (codfun, equipoid, entrega, estimada, devolucion) SELECT codfun, equipoid, entrega, estimada, devolucion FROM prestamos WHERE equipoid = %s", (devo_equipoidProye,))
                        
                        cursor.execute("DELETE FROM prestamos WHERE equipoid = %s", (devo_equipoidProye,))

                        cursor.execute("UPDATE proyectores SET prestado = %s WHERE serie = %s", (False, devo_equipoidProye))
                        
                        connection.commit()
                        
                        # Redirección Final
                        return redirect(url_for('indexPrestamos'))
                    else:
                        # Caso de Error
                        flash('El préstamo no existe.', 'error')
                else:
                    # Caso de Error
                    flash('El proyector no existe.', 'error')
            
            finally:
                # Cierre de Conexión con Base de Datos
                cursor.close()
                connection.close()

    # Render del template HTML
    return render_template('devolucion.html', formDevoNote=formDevoNote, formDevoProye=formDevoProye, datos=datos)
#------------------------------------------


#------------------------------------------
# Función: AGREGAR EQUIPO
@app.route('/agregar', methods=['GET', 'POST'])
def funcionAgregar():
    # Definición de Variables a Usar
    formAgNote = formulario_ag_note()
    formAgProye = formulario_ag_proye()

    # Submit: Primer Formulario
    if request.method == 'POST' and formAgNote.ag_submitNote.data:
        if formAgNote.validate():
            try:
                # Obtención de Datos: Primer Formulario
                ag_equipoidNote = formAgNote.ag_equipoidNote.data
                ag_bolsoNote = formAgNote.ag_bolsoNote.data
                ag_estadoNote = formAgNote.ag_estadoNote.data
                ag_cargador = formAgNote.ag_cargador.data
                ag_mouse = formAgNote.ag_mouse.data
                ag_modeloNote = formAgNote.ag_modeloNote.data
                ag_marcaNote = formAgNote.ag_marcaNote.data
                ag_serieNote = formAgNote.ag_serieNote.data
                ag_mantenimientoNote = formAgNote.ag_mantenimientoNote.data

                # Conxión con Base de Datos
                connection = psycopg2.connect(**db_config)
                cursor = connection.cursor()

                # Verificación de Datos N°1
                cursor.execute("SELECT COUNT(*) FROM notebook WHERE codigo = %s", (ag_equipoidNote,))
                ag_verificacionUnoNote = cursor.fetchone()[0]

                if ag_verificacionUnoNote > 0:
                    # Caso de Error
                    flash('El código ya está en uso.', 'error')
                else:
                    # Verificación de Datos N°2
                    cursor.execute("SELECT COUNT(*) FROM notebook WHERE serie = %s", (ag_serieNote,))
                    ag_verificacionDosNote = cursor.fetchone()[0]

                    if ag_verificacionDosNote > 0:
                        # Caso de Error
                        flash('La serie está duplicada.', 'error')
                    else:
                        # Ejecución y Modificación de la Base de Datos
                        cursor.execute("INSERT INTO notebook (codigo, bolso, estado, cargador, mouse, modelo, marca, mantenimiento, serie, prestado) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)", (ag_equipoidNote, ag_bolsoNote, ag_estadoNote, ag_cargador, ag_mouse, ag_modeloNote, ag_marcaNote, ag_mantenimientoNote, ag_serieNote, False))
                        connection.commit()
                        # Redirección Final
                        return redirect(url_for('funcionVistaNote'))

            finally:
                # Cierre de Conexión con Base de Datos
                cursor.close()
                connection.close()
        # Caso de Error
        else:
            error_msg = 'Error al agregar datos, '
            for field, errors in formAgNote.errors.items():
                error_msg += f'{formAgNote[field].label.text}: {", ".join(errors)}. '
            flash(error_msg, 'error')

    # Submit: Segundo Formulario
    elif request.method == 'POST' and formAgProye.ag_submitProye.data:
        if formAgProye.validate():
            try:
                # Obtención de Datos: Segundo Formulario
                ag_equipoidProye = formAgProye.ag_equipoidProye.data
                ag_bolsoProye = formAgProye.ag_bolsoProye.data
                ag_estadoProye = formAgProye.ag_estadoProye.data
                ag_alimentacion = formAgProye.ag_alimentacion.data
                ag_hdmi = formAgProye.ag_hdmi.data
                ag_vga = formAgProye.ag_vga.data
                ag_modeloProye = formAgProye.ag_modeloProye.data
                ag_marcaProye = formAgProye.ag_marcaProye.data
                ag_mantenimientoProye = formAgProye.ag_mantenimientoProye.data

                # Conxión con Base de Datos
                connection = psycopg2.connect(**db_config)
                cursor = connection.cursor()

                # Verificación de Datos N°1
                cursor.execute("SELECT COUNT(*) FROM proyectores WHERE serie = %s", (ag_equipoidProye,))
                ag_verificacionUno = cursor.fetchone()[0]
                
                if ag_verificacionUno > 0:
                    # Caso de Error
                    flash('La serie está duplicada.', 'error')
                else: 
                    # Verificación de Datos N°3
                    cursor.execute("SELECT COUNT(*) FROM notebook WHERE codigo = %s", (ag_equipoidProye,))
                    ag_verificacionDos = cursor.fetchone()[0]

                    if ag_verificacionDos > 0:
                        # Caso de Error
                        flash('La serie no puede ser igual que el código de un notebook.', 'error')
                    else:
                        # Ejecución y Modificación de la Base de Datos
                        cursor.execute("INSERT INTO proyectores (serie, bolso, estado, alimentacion, hdmi, vga, modelo, marca, mantenimiento, prestado) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)", (ag_equipoidProye, ag_bolsoProye, ag_estadoProye, ag_alimentacion, ag_hdmi, ag_vga, ag_modeloProye, ag_marcaProye, ag_mantenimientoProye, False))
                        connection.commit()
                        # Redirección Final
                        return redirect(url_for('funcionVistaProye'))
                
            finally:
                # Cierre de Conexión con Base de Datos
                cursor.close()
                connection.close()
        # Caso de Error
        else:
            error_msg = 'Error al agregar datos, '
            for field, errors in formAgNote.errors.items():
                error_msg += f'{formAgNote[field].label.text}: {", ".join(errors)}. '
            flash(error_msg, 'error')
    # Render del template HTML
    return render_template('agregar.html', formAgNote=formAgNote, formAgProye=formAgProye)
#------------------------------------------


#------------------------------------------
# Función: BORRAR EQUIPO
@app.route('/borrar', methods=['GET', 'POST'])
def funcionBorrar():
    # Definición de Variables a Usar
    formBrNote = formulario_br_note()
    formBrProye = formulario_br_proye()

    # Tabla de Datos
    connection = psycopg2.connect(**db_config)
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM notebook")
    datos_note = cursor.fetchall()
    cursor.execute("SELECT * FROM proyectores")
    datos_proye = cursor.fetchall()
    cursor.close()
    connection.close()

    # Submit: Primer Formulario
    if request.method == 'POST' and formBrNote.br_submitNote.data:
        if formBrNote.validate():
            # Obtención de Datos: Primer Formulario
            br_equipoidNote = formBrNote.br_equipoidNote.data

            # Verificación de Datos
            connection = psycopg2.connect(**db_config)
            cursor = connection.cursor()
            cursor.execute("SELECT FROM notebook WHERE codigo = %s", (br_equipoidNote,))
            br_equipoNote = cursor.fetchone()
            connection.commit()

            # Método Post Verificación
            if br_equipoNote is not None:
                try:
                    # Ejecución y Modificación de la Base de Datos
                    connection = psycopg2.connect(**db_config)
                    cursor = connection.cursor()
                    cursor.execute("DELETE FROM notebook WHERE codigo = %s", (br_equipoidNote,))
                    connection.commit()

                    # Redirección Final
                    return redirect(url_for('funcionVistaNote'))
                
                finally:
                    # Cierre de Conexión con Base de Datos
                    cursor.close()
                    connection.close()
            else:
                # Caso de Error
                flash('El equipo ingresado no existe.', 'notebook_error')

    # Submit: Segundo Formulario
    elif request.method == 'POST' and formBrProye.br_submitProye.data:
        if formBrProye.validate():
            # Obtención de Datos: Segundo Formulario
            br_equipoidProye = formBrProye.br_equipoidProye.data

            # Verificación de Datos
            connection = psycopg2.connect(**db_config)
            cursor = connection.cursor()
            cursor.execute("SELECT FROM proyectores WHERE serie = %s", (br_equipoidProye,))
            br_equipoProye = cursor.fetchone()
            connection.commit()

            # Método Post Verificación
            if br_equipoProye is not None:
                try:
                    # Ejecución y Modificación de la Base de Datos
                    connection = psycopg2.connect(**db_config)
                    cursor = connection.cursor()
                    cursor.execute("DELETE FROM notebook WHERE codigo = %s", (br_equipoidProye,))
                    connection.commit()

                    # Redirección Final
                    return redirect(url_for('funcionVistaNote'))
                    
                finally:
                    # Cierre de Conexión con Base de Datos
                    cursor.close()
                    connection.close()
            else:
                # Caso de Error
                flash('El equipo ingresado no existe.', 'proyector_error')
    # Render del template HTML
    return render_template('borrar.html', formBrNote=formBrNote, formBrProye=formBrProye, datos_note=datos_note, datos_proye=datos_proye)
#------------------------------------------


#------------------------------------------
# Función: MANTENIMIENTO
@app.route('/mantenimiento', methods=['GET', 'POST'])
def funcionMantenimiento():
    # Definición de Variables a Usar
    formMntNote = formulario_mnt_note()
    formMntProye = formulario_mnt_proye()

    # Tabla de Datos
    connection = psycopg2.connect(**db_config)
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM notebook")
    datos_note = cursor.fetchall()
    cursor.execute("SELECT * FROM proyectores")
    datos_proye = cursor.fetchall()
    cursor.close()
    connection.close()

    # Submit: Primer Formulario
    if request.method == 'POST' and formMntNote.mnt_submitNote.data:
        if formMntNote.validate():
            try:
                # Obtención de Datos: Primer Formulario
                mnt_equipoidNote = formMntNote.mnt_equipoidNote.data
                mnt_bolsoNote = formMntNote.mnt_bolsoNote.data
                mnt_estadoNote = formMntNote.mnt_estadoNote.data
                mnt_cargador = formMntNote.mnt_cargador.data
                mnt_mouse = formMntNote.mnt_mouse.data
                mnt_mantenimientoNote = formMntNote.mnt_mantenimientoNote.data

                # Verificación de Datos
                connection = psycopg2.connect(**db_config)
                cursor = connection.cursor()
                cursor.execute("SELECT COUNT(*) FROM notebook WHERE codigo = %s", (mnt_equipoidNote,))
                mnt_verificadorNote = cursor.fetchone()[0]
            
                if mnt_verificadorNote > 0:
                    # Ejecución y Modificación de la Base de Datos
                    cursor.execute("UPDATE notebook SET bolso = %s, estado = %s, cargador = %s, mouse = %s, mantenimiento = %s WHERE codigo = %s", (mnt_bolsoNote, mnt_estadoNote, mnt_cargador, mnt_mouse, mnt_mantenimientoNote, mnt_equipoidNote))
                    connection.commit()
                    # Redirección Final
                    return redirect(url_for('funcionVistaNote'))
                else:
                    # Caso de Error
                    flash('La ID del notebook no existe.', 'notebook_error')
            finally:
                # Cierre de Conexión con Base de Datos
                cursor.close()
                connection.close()
        # Caso de Error
        else:
            error_msg = 'Error al modificar datos, '
            for field, errors in formMntNote.errors.items():
                error_msg += f'{formMntNote[field].label.text}: {", ".join(errors)}. '
            flash(error_msg, 'notebook_error')

    # Submit: Segundo Formulario
    elif request.method == 'POST' and formMntProye.mnt_submitProye.data:
        if formMntProye.validate():
            try:
                # Obtención de Datos: Segundo Formulario
                mnt_equipoidProye = formMntProye.mnt_equipoidProye.data
                mnt_bolsoProye = formMntProye.mnt_bolsoProye.data
                mnt_estadoProye = formMntProye.mnt_estadoProye.data
                mnt_alimentacion = formMntProye.mnt_alimentacion.data
                mnt_hdmi = formMntProye.mnt_hdmi.data
                mnt_vga = formMntProye.mnt_vga.data
                mnt_mantenimientoProye = formMntProye.mnt_mantenimientoProye.data

                # Verificación de Datos
                connection = psycopg2.connect(**db_config)
                cursor = connection.cursor()
                cursor.execute("SELECT COUNT(*) FROM proyectores WHERE serie = %s", (mnt_equipoidProye,))
                mnt_verificadorProye = cursor.fetchone()[0]

                if mnt_verificadorProye > 0:
                    # Ejecución y Modificación de la Base de Datos
                    cursor.execute("UPDATE proyectores SET bolso = %s, estado = %s, alimentacion = %s, hdmi = %s, vga = %s, mantenimiento = %s WHERE serie = %s", (mnt_bolsoProye, mnt_estadoProye, mnt_alimentacion, mnt_hdmi, mnt_vga, mnt_mantenimientoProye, mnt_equipoidProye ))
                    connection.commit()
                    
                    # Redirección Final
                    return redirect(url_for('funcionVistaProye'))
                else:
                    # Caso de Error
                    flash('La Serie del proyector no existe.', 'proyector_error')

            finally:
                # Cierre de Conexión con Base de Datos
                cursor.close()
                connection.close()
        # Caso de Error
        else:
            error_msg = 'Error al modificar datos, '
            for field, errors in formMntProye.errors.items():
                error_msg += f'{formMntProye[field].label.text}: {", ".join(errors)}. '
            flash(error_msg, 'proyector_error')
    # Render del template HTML
    return render_template('mantenimiento.html', formMntNote=formMntNote, formMntProye=formMntProye, datos_note=datos_note, datos_proye=datos_proye)
#------------------------------------------


#------------------------------------------
# Función: MODIFICACION DE FUNCIONARIOS
@app.route('/modFun', methods=['GET', 'POST'])
def funcionModificacionFun():
    # Definición de Variables a Usar
    formAgFun = formulario_agfun()
    formBrFun = formulario_brfun()

    # Submit: Primer Formulario
    if request.method == 'POST' and formAgFun.agfun_submitFun.data:
        if formAgFun.validate():
            try:
                # Obtención de Datos: Primer Formulario
                agfun_codfun = formAgFun.agfun_codfun.data
                agfun_nombre = formAgFun.agfun_nombre.data
                agfun_correo = formAgFun.agfun_correo.data
                agfun_rut = formAgFun.agfun_rut.data
                
                # Conexión Base de Datos
                connection = psycopg2.connect(**db_config)
                cursor = connection.cursor()
                print(validar_rut(agfun_rut))
                # Validación RUT
                if validar_rut(agfun_rut):
                    # Ejecución y Modificación de la Base de Datos
                    cursor.execute("INSERT INTO funcionarios (codfun, nombre, correo, rut) VALUES (%s, %s, %s, %s)", (agfun_codfun, agfun_nombre, agfun_correo+"@araucania.cl", agfun_rut))
                    connection.commit()
                    # Redirección Final
                    return redirect(url_for('funcionVistaFun'))
                
                else:
                    # Caso de Error
                    flash('RUT inválido.', 'error')
            
            finally:
                # Cierre de Conexión con Base de Datos
                cursor.close()
                connection.close()
        # Caso de Error
        else:
            error_msg = 'Error al agregar el funcionario, '
            for field, errors in formAgFun.errors.items():
                error_msg += f'{formAgFun[field].label.text}: {", ".join(errors)}. '
            flash(error_msg, 'error')

    # Submit: Segundo Formulario
    elif request.method == 'POST' and formBrFun.brfun_submitFun.data:
        if formBrFun.validate():
            try:
                # Obtención de Datos: Segundo Formulario
                brfun_codfun = formBrFun.brfun_codfun.data

                # Verificación de Datos N°1
                connection = psycopg2.connect(**db_config)
                cursor = connection.cursor()
                cursor.execute("SELECT COUNT(*) FROM funcionarios WHERE codfun = %s", (brfun_codfun,))
                brfun_verificacionUno = cursor.fetchone()[0]

                if brfun_verificacionUno > 0:
                    
                    # Verificación de Datos N°2
                    cursor.execute("SELECT COUNT(*) FROM prestamos WHERE codfun = %s", (brfun_codfun,))
                    rfun_verificacionDos = cursor.fetchone()[0]

                    if rfun_verificacionDos > 0:
                        # Caso de Error
                        flash('El funcionario tiene un préstamo pendiente.', 'error')

                    else:
                        # Ejecución y Modificación de la Base de Datos
                        cursor.execute("DELETE FROM funcionarios WHERE codfun = %s", (brfun_codfun,))
                        connection.commit()
                        
                        # Redirección Final
                        return redirect(url_for('funcionVistaFun'))
                else:
                    # Caso de Error
                    flash('El código de funcionario no existe.', 'error')



            finally:
                # Cierre de Conexión con Base de Datos
                cursor.close()
                connection.close()
    # Render del template HTML
    return render_template('modFun.html', formAgFun=formAgFun, formBrFun=formBrFun)
#------------------------------------------


#------------------------------------------------------------------------
# FUNCIONES PRINCIPALES: VISTA DE DATOS
#------------------------------------------------------------------------


#------------------------------------------
# Filtro & Vista: FUNCIONARIOS
@app.route('/Vista-Funcionarios', methods=['GET', 'POST'])
def funcionVistaFun():
    # Definición de Variables a Usar
    formVisFun = formulario_visfun()

    # Submit: Filtro
    if formVisFun.validate_on_submit():
        # Obtención de Datos
        visfun_filcodfun = formVisFun.visfun_filcodfun.data

        # Impresión de la Base de Datos: CON Filtro Aplicado
        connection = psycopg2.connect(**db_config)
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM funcionarios WHERE codfun = %s", (visfun_filcodfun,))
        datos = cursor.fetchall()
        cursor.close()
        connection.close()

        # Revisión de Filtro
        if not datos:
            flash('No se encontraron los datos del Funcionario con el rut proporcionado.', 'error')
            return redirect(url_for('funcionVistaFun'))
        
    else:
        # Impresión de la Base de Datos: SIN Filtro Aplicado
        connection = psycopg2.connect(**db_config)
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM funcionarios")
        datos = cursor.fetchall()
        cursor.close()
        connection.close()

    # Render del template HTML
    return render_template('impresionDatosFuncionarios.html', datos=datos, formVisFun=formVisFun)
#------------------------------------------


#------------------------------------------
# Filtro & Vista: HISTORIAL
@app.route('/Vista-Historial', methods=['GET', 'POST'])
def funcionVistaHis():
    # Definición de Variables a Usar
    formHis = formulario_his()

    # Submit: Filtro
    if formHis.validate_on_submit():
        # Obtención de Datos
        his_equipoid = formHis.his_equipoid.data

        # Impresión de la Base de Datos: CON Filtro Aplicado
        connection = psycopg2.connect(**db_config)
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM historial WHERE equipoid = %s", (his_equipoid,))
        datos = cursor.fetchall()
        cursor.close()
        connection.close()

        # Revisión de Filtro
        if not datos:
            flash('No se encontraron los datos del Prestamo con el Código/Serie proporcionado.', 'error')
            return redirect(url_for('funcionVistaHis'))

    else:
        # Impresión de la Base de Datos: SIN Filtro Aplicado
        connection = psycopg2.connect(**db_config)
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM historial")
        datos = cursor.fetchall()
        cursor.close()
        connection.close()

    # Render del template HTML
    return render_template('impresionDatosHistorial.html', datos=datos, formHis=formHis)
#------------------------------------------


#------------------------------------------
# Filtro & Vista: NOTEBOOKS
@app.route('/Vista-Notebooks', methods=['GET', 'POST'])
def funcionVistaNote():
    # Definición de Variables a Usar
    formVisNote = formulario_visNote()

    # Submit: Filtro
    if formVisNote.validate_on_submit():
        # Obtención de Datos
        visNote_equipoid = formVisNote.visNote_equipoid.data

        # Impresión de la Base de Datos: CON Filtro Aplicado
        connection = psycopg2.connect(**db_config)
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM notebook WHERE codigo = %s", (visNote_equipoid,))
        datos = cursor.fetchall()
        cursor.close()
        connection.close()

        # Revisión de Filtro
        if not datos:
            flash('No se encontraron los datos del Equipo con el Código proporcionado.', 'error')
            return redirect(url_for('funcionVistaNote'))
        
    else:
        # Impresión de la Base de Datos: SIN Filtro Aplicado
        connection = psycopg2.connect(**db_config)
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM notebook")
        datos = cursor.fetchall()
        cursor.close()
        connection.close()

    # Render del template HTML
    return render_template('impresionDatosNote.html', datos=datos, formVisNote=formVisNote)
#------------------------------------------


#------------------------------------------
# Filtro & Vista: PROYECTORES
@app.route('/Vista-Proyectores', methods=['GET', 'POST'])
def funcionVistaProye():
    # Definición de Variables a Usar
    formVisProye = formulario_VisProye()

    # Submit: Filtro
    if formVisProye.validate_on_submit():
        # Obtención de Datos
        VisProye_equipoid = formVisProye.VisProye_equipoid.data

        # Impresión de la Base de Datos: CON Filtro Aplicado
        connection = psycopg2.connect(**db_config)
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM proyectores WHERE serie = %s", (VisProye_equipoid,))
        datos = cursor.fetchall()
        cursor.close()
        connection.close()

        # Revisión de Filtro
        if not datos:
            flash('No se encontraron los datos del Equipo con la Serie proporcionado.', 'error')
            return redirect(url_for('funcionVistaProye'))
        
    else:
        # Impresión de la Base de Datos: SIN Filtro Aplicado
        connection = psycopg2.connect(**db_config)
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM proyectores")
        datos = cursor.fetchall()
        cursor.close()
        connection.close()

    # Render del template HTML
    return render_template('impresionDatosProye.html', datos=datos, formVisProye=formVisProye)
#------------------------------------------

# Ejecución del Servidor FLASK
if __name__ == '__main__':
    app.run(debug=True)
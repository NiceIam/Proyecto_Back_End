from flask import Blueprint, render_template, request, redirect, url_for, session, flash, get_flashed_messages
from sqlalchemy.exc import IntegrityError
from models import db, Usuario, Producto, Pedido, DetallePedido, Comentario

main = Blueprint('main', __name__)

# 🔥 Usuario administrador quemado (no en la DB)
ADMIN_CREDENTIALS = {
    "username": "admin",
    "password": "admin123"
}

# Ruta para la página principal
@main.route('/')
def index():
    productos = Producto.query.all()  # Recuperar productos desde SQLAlchemy
    return render_template('index.html', productos=productos)

# Ruta para ver producto y agregar comentarios
@main.route('/producto/<int:producto_id>', methods=['GET', 'POST'])
def ver_producto(producto_id):
    producto = Producto.query.get_or_404(producto_id)
    comentarios = Comentario.query.filter_by(producto_id=producto_id).order_by(Comentario.fecha.desc()).all()

    if request.method == 'POST':
        usuario = request.form.get('usuario', '').strip()
        comentario_texto = request.form.get('comentario', '').strip()

        if usuario and comentario_texto:
            nuevo_comentario = Comentario(
                producto_id=producto_id,
                usuario_nombre=usuario,
                comentario=comentario_texto
            )
            db.session.add(nuevo_comentario)
            db.session.commit()
            flash('Comentario agregado correctamente.', 'success')
        else:
            flash('Todos los campos son obligatorios.', 'danger')

        return redirect(url_for('main.ver_producto', producto_id=producto_id))

    return render_template('producto.html', producto=producto, comentarios=comentarios)

# Ruta para el login (permite admin quemado y usuarios de la BD)
@main.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '').strip()

        # 🔥 Verificar si el usuario es el admin quemado
        if username == ADMIN_CREDENTIALS["username"] and password == ADMIN_CREDENTIALS["password"]:
            session['user_id'] = None  # No se almacena un ID porque no está en la DB
            session['admin'] = True
            flash("Inicio de sesión exitoso como Administrador.", "success")
            return redirect(url_for('main.admin_dashboard'))

        # 🔐 Verificar si el usuario está en la BD
        usuario = Usuario.query.filter_by(username=username).first()
        if usuario and usuario.check_password(password):
            session['user_id'] = usuario.id
            session['admin'] = usuario.rol == 'admin'
            flash("Inicio de sesión exitoso.", "success")
            return redirect(url_for('main.admin_dashboard' if usuario.rol == 'admin' else 'main.index'))

        flash("Credenciales incorrectas, inténtalo de nuevo.", "danger")

    return render_template('login.html')

# Ruta para el registro de usuarios
@main.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"].strip()
        email = request.form["email"].strip()
        password = request.form["password"].strip()

        # Verificar si el usuario o el correo ya existen
        if Usuario.query.filter_by(username=username).first():
            flash("El usuario ya existe. Prueba otro.", "danger")
            return redirect(url_for("main.register"))

        if Usuario.query.filter_by(email=email).first():
            flash("El correo electrónico ya está registrado. Usa otro.", "danger")
            return redirect(url_for("main.register"))

        # Crear nuevo usuario
        nuevo_usuario = Usuario(username=username, email=email)
        nuevo_usuario.set_password(password)

        db.session.add(nuevo_usuario)
        try:
            db.session.commit()
            flash("Usuario registrado correctamente. Ahora puedes iniciar sesión.", "success")
            return redirect(url_for("main.login"))
        except IntegrityError:
            db.session.rollback()
            flash("Error al registrar el usuario. Intenta con otro correo.", "danger")

    return render_template("register.html")

# Ruta del panel de administración (solo accesible para admin)
@main.route('/admin', methods=['GET', 'POST'])
def admin_dashboard():
    if not session.get('admin'):
        return redirect(url_for('main.login'))

    productos = Producto.query.all()
    messages = get_flashed_messages(with_categories=True)

    return render_template('admin_dashboard.html', productos=productos, messages=messages)

# Ruta para agregar productos (solo admin)
@main.route('/agregar_producto', methods=['POST'])
def agregar_producto():
    if not session.get('admin'):
        flash("Debes iniciar sesión como administrador.", "danger")
        return redirect(url_for('main.login'))

    nombre = request.form.get('nombre', '').strip()
    precio = request.form.get('precio', '').strip()
    descripcion = request.form.get('descripcion', '').strip()
    imagen = request.form.get('imagen', '').strip()

    if any(v is None or v == '' for v in [nombre, precio, descripcion, imagen]):
        flash("Todos los campos son obligatorios.", "danger")
        return redirect(url_for('main.admin_dashboard'))

    try:
        precio = float(precio)
    except ValueError:
        flash("El precio debe ser un número válido.", "danger")
        return redirect(url_for('main.admin_dashboard'))

    nuevo_producto = Producto(nombre=nombre, precio=precio, descripcion=descripcion, imagen=imagen)
    db.session.add(nuevo_producto)
    db.session.commit()
    flash("Producto agregado correctamente.", "success")

    return redirect(url_for('main.admin_dashboard'))

# Ruta para limpiar mensajes flash
@main.route('/clear_flash', methods=['POST'])
def clear_flash():
    session.pop('_flashes', None)
    return '', 204  # Devuelve una respuesta vacía con código 204 (sin contenido)

# Cerrar sesión
@main.route('/logout')
def logout():
    session.pop('user_id', None)
    session.pop('admin', None)
    flash("Sesión cerrada exitosamente.", "success")
    return redirect(url_for('main.login'))

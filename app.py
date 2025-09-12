from flask import Flask, render_template, request, redirect, url_for, flash
from werkzeug.security import generate_password_hash, check_password_hash
<<<<<<< HEAD
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from controladores.models import db, Usuario, Cliente, Categoria
from routes.admin import bp as admin_bp
=======
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from controladores.models import db, Usuario, Cliente
from routes.admin import admin_bp
from routes.clientes import clientes_bp
>>>>>>> 6c4430e (Agregar módulo de seguimiento de pedidos)


# Inicialización de la app
app = Flask(__name__)

# Configuración de la base de datos
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:@127.0.0.1:3306/delicake'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'clave_secreta'

# Inicializar extensiones
db.init_app(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'


# Cargar usuarios para Flask-Login
@login_manager.user_loader
def load_user(user_id):
    return Usuario.query.get(int(user_id))


# Rutas principales
@app.route('/')
def home():
    categorias = Categoria.query.filter_by(Estado="Activa").all()
    return render_template("index.html", categorias=categorias)
                                                                                                                                                                                                                                                                                                                                                                                                            


@app.route('/publica')
def publica():
    return render_template('index-1.html')       


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        nombre = request.form.get('nombre')
        apellido = request.form.get('apellido')
        correo = request.form.get('correo')
        telefono = request.form.get('telefono')
        direccion = request.form.get('direccion')
        contraseña = request.form.get('contraseña')
        confirmar_contraseña = request.form.get('confirmar_contraseña')

        if contraseña != confirmar_contraseña:
            flash('Las contraseñas no coinciden.')
            return redirect(url_for('register'))

        usuario_existente = Usuario.query.filter_by(Correo=correo).first()
        if usuario_existente:
            flash('Este correo ya está registrado.')
            return redirect(url_for('register'))

        hashed_password = generate_password_hash(contraseña)

        nuevo_usuario = Usuario(
            Nombre=nombre,
            Apellido=apellido,
            Correo=correo,
            Contraseña=hashed_password
        )

        try:
            db.session.add(nuevo_usuario)
            db.session.commit()

            nuevo_cliente = Cliente(
                Nombre=nombre,
                Direccion=direccion,
                Telefono=telefono,
                ID_usuario=nuevo_usuario.ID_usuario
            )
            db.session.add(nuevo_cliente)
            db.session.commit()

            flash('Registro exitoso. Ahora puedes iniciar sesión.')
            return redirect(url_for('login'))

        except Exception as e:
            db.session.rollback()
            print(f"Error durante el registro: {e}")
            flash('Ocurrió un error durante el registro.')
            return redirect(url_for('register'))

    return render_template('registro.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        correo = request.form.get('correo')
        contraseña = request.form.get('contraseña')

        usuario = Usuario.query.filter_by(Correo=correo).first()

        if usuario and check_password_hash(usuario.Contraseña, contraseña):
            login_user(usuario)
            flash('Inicio de sesión exitoso.')
            return redirect(url_for('publica'))
        else:
            flash('Correo o contraseña incorrectos.')

    return render_template('clientes/inicio de sesion.html')


@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Has cerrado sesión.')
    return redirect(url_for('publica'))


# Registrar blueprints
app.register_blueprint(admin_bp)
app.register_blueprint(clientes_bp)


# Crear tablas si no existen y ejecutar app
if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)

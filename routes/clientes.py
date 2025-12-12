from flask import Blueprint, render_template, redirect, url_for, flash, request, session, send_file
from reportlab.pdfgen import canvas
from flask_login import login_required, current_user
from werkzeug.security import check_password_hash, generate_password_hash
from controladores.models import db, Usuario, Producto
from controladores.models import db,Categoria,Favorito,Producto, PersonalizacionProducto, Cliente, Pedido, Disponibilidad, DetallePedido,Notificacion, Lanzamiento,Pago
from flask import Blueprint, render_template, request
from flask_login import login_required, current_user
from flask import Flask, render_template, request, redirect, url_for
from flask import Blueprint, render_template, request, redirect, url_for, session, jsonify
from flask import session
from controladores.models import Suscriptor, db
from extensions import mail
from flask_mail import Message
from datetime import date, datetime 
import json  
app = Flask(__name__)


clientes_bp = Blueprint("clientes", __name__, url_prefix="/clientes")

@clientes_bp.route('/mi_cuenta')
@login_required
def mi_cuenta():
    if not current_user.cliente:
        flash("No tienes perfil de cliente.")
        return redirect(url_for("publica"))

    cliente = current_user.cliente
    return render_template(
        "clientes/mi_cuenta.html",
        usuario=current_user,
        cliente=cliente
    )


@clientes_bp.route("/actualizar_datos", methods=["GET", "POST"])
@login_required
def actualizar_datos():
    if not current_user.cliente:
        flash("No tienes perfil de cliente.")
        return redirect(url_for("publica"))

    if request.method == "POST":
        nombre = request.form.get("nombre")
        apellido = request.form.get("apellido")
        correo = request.form.get("correo")
        telefono = request.form.get("telefono")
        direccion = request.form.get("direccion")

        # Verificar si hay cambios
        if (
            nombre == current_user.Nombre and
            apellido == current_user.Apellido and
            correo == current_user.Correo and
            telefono == current_user.cliente.Telefono and
            direccion == current_user.cliente.Direccion
        ):
            flash("No se han realizado cambios", "warning")
            return redirect(url_for("clientes.actualizar_datos"))

        try:
            # Verificar correo duplicado
            if Usuario.query.filter(
                Usuario.Correo == correo,
                Usuario.ID_usuario != current_user.ID_usuario
            ).first():
                flash("Ese correo ya está registrado por otro usuario", "danger")
                return redirect(url_for("clientes.actualizar_datos"))

            # Actualizar datos
            current_user.Nombre = nombre
            current_user.Apellido = apellido
            current_user.Correo = correo
            current_user.cliente.Telefono = telefono
            current_user.cliente.Direccion = direccion

            db.session.commit()
            flash("Datos actualizados correctamente", "success")
            return redirect(url_for("clientes.actualizar_datos"))

        except Exception as e:
            db.session.rollback()
            flash("Ocurrió un error al actualizar: " + str(e), "danger")
            return redirect(url_for("clientes.actualizar_datos"))
    categorias = Categoria.query.all()
    return render_template("clientes/actualizar_dat.html", usuario=current_user, categorias=categorias)


@clientes_bp.route("/cambiar_contrasena", methods=["GET", "POST"])
@login_required
def cambiar_contrasena():
    if request.method == "POST":
        actual = request.form.get("actual")
        nueva = request.form.get("nueva")
        confirmar = request.form.get("confirmar")

        if not check_password_hash(current_user.Contraseña, actual):
            flash("La contraseña actual es incorrecta", "danger")
            return redirect(url_for("clientes.cambiar_contrasena"))

        if nueva != confirmar:
            flash("Las nuevas contraseñas no coinciden", "danger")
            return redirect(url_for("clientes.cambiar_contrasena"))

        current_user.Contraseña = generate_password_hash(nueva)
        db.session.commit()
        flash("Contraseña actualizada con éxito", "success")
        return redirect(url_for("clientes.mi_cuenta"))
    categorias = Categoria.query.all()
    return render_template("clientes/cambiar_con.html",categorias=categorias)

    


#CAMBIOS 3
#
#
# 
#
#
#


@clientes_bp.route("/categoria/<int:id_categoria>")
def productos_por_categoria(id_categoria):
    categorias = Categoria.query.all()
    productos = Producto.query.filter_by(ID_Categoria=id_categoria).all()
    favoritos_ids = []
    if current_user.is_authenticated:
        favoritos_ids = [f.ID_Producto for f in Favorito.query.filter_by(ID_usuario=current_user.ID_usuario).all()]
    return render_template("clientes/catalogo_clien.html",  productos=productos, categorias=categorias, favoritos_ids=favoritos_ids)




@clientes_bp.route("/seguimiento", methods=["GET"])
@login_required
def seguimiento_pedido():
    # 1️⃣ Identificar cliente
    cliente = Cliente.query.filter_by(ID_usuario=current_user.ID_usuario).first()
    if not cliente:
        flash("No tienes un perfil de cliente asociado.", "warning")
        return render_template("clientes/seguimiento_pedido.html", pedidos=[])

    # 2️⃣ Obtener sus pedidos
    pedidos = Pedido.query.filter_by(ID_Cliente=cliente.ID_cliente).all()

    pedidos_data = []
    for pedido in pedidos:
        pedidos_data.append({
            "ID_Pedido": pedido.ID_Pedido,
            "Cliente": f"{current_user.Nombre} {current_user.Apellido}",
            "Fecha_Solicitud": pedido.Fecha_Solicitud.strftime("%Y-%m-%d") if pedido.Fecha_Solicitud else "Pendiente",
            "Fecha_Entrega": pedido.Fecha_Entrega.strftime("%Y-%m-%d") if pedido.Fecha_Entrega else "Pendiente",
            "Total": f"{pedido.Total:.2f}" if pedido.Total else "0.00",
            "Estado_Pedido": pedido.Estado_Pedido
        })

    # 3️⃣ Obtener notificaciones del usuario actual
    notificaciones = Notificacion.query.filter_by(usuario_id=current_user.ID_usuario).order_by(Notificacion.fecha.desc()).all()

    # 4️⃣ Marcar las no leídas como leídas al entrar a la página
    for n in notificaciones:
        if not n.leida:
            n.leida = True
    db.session.commit()

    # 5️⃣ Renderizar vista con pedidos + notificaciones
    categorias = Categoria.query.all()
    return render_template(
        "clientes/seguimiento_pedido.html",
        pedidos=pedidos_data,
        notificaciones=notificaciones,
        categorias=categorias
    )

def esta_en_horario():
    ahora = datetime.now()
    dia = ahora.weekday()
    hora_actual = ahora.hour + ahora.minute / 60

    if 0 <= dia <= 4:  
        return 7 <= hora_actual < 24
    else:  
        return 9 <= hora_actual < 17.5


@clientes_bp.route("/confirmacion_pedido", methods=["GET", "POST"])
@login_required
def confirmacion_pedido():
    carrito = session.get("carrito", [])
    categorias = Categoria.query.all()

    metodo = request.args.get("metodo")

    if not current_user.cliente:
        nuevo_cliente = Cliente(
            Direccion="Por definir",
            Telefono="0000000000",
            usuario=current_user
        )
        db.session.add(nuevo_cliente)
        db.session.commit()

    cliente = current_user.cliente

    if not esta_en_horario():
        flash("⏰ Estamos fuera del horario de atención. Tu pedido será procesado el siguiente día hábil.", "warning")
        return redirect(url_for('clientes.carrito'))

    disponibilidades = Disponibilidad.query.order_by(Disponibilidad.Fecha, Disponibilidad.Hora).all()
    fechas_horas = {}
    for d in disponibilidades:
        if d.Fecha and d.Hora:
            fecha_str = d.Fecha.strftime("%Y-%m-%d")
            hora_str = d.Hora.strftime("%H:%M")
            fechas_horas.setdefault(fecha_str, []).append(hora_str)

    # ✅ POST
    if request.method == "POST":
        direccion = request.form.get("direccion")

        # 🔥 Corrección esencial: asegurar que metodo_pago siempre exista
        metodo_pago = request.form.get("metodo_pago") or metodo

        fecha_entrega = request.form.get("fechaEntrega")
        hora_entrega = request.form.get("horaEntrega")

        carrito_json = request.form.get("carrito_json")
        if carrito_json:
            try:
                carrito = json.loads(carrito_json)
            except:
                carrito = session.get("carrito", [])

        if not carrito:
            carrito = session.get("carrito", [])

        nuevo_pedido = Pedido(
            cliente=cliente,
            Estado_Pedido="Pendiente",
            Total=0,
            Fecha_Solicitud=date.today(),
            Fecha_Entrega=datetime.strptime(fecha_entrega, "%Y-%m-%d").date() if fecha_entrega else None,
            Metodo_Pago=metodo_pago,   # ← YA DEFINIDO SIN ERRORES
            Tiempo_Realizacion="Pendiente"
        )
        db.session.add(nuevo_pedido)
        db.session.commit()

        total_general = 0

        for item in carrito:
            descuento_str = str(item.get("descuento", "0")).replace("%", "").strip()
            try:
                descuento = float(descuento_str)
            except:
                descuento = 0.0

            precio_con_descuento = item["precio"] - (item["precio"] * descuento / 100)
            total_producto = precio_con_descuento * item["cantidad"]
            total_general += total_producto

        nuevo_pedido.Total = total_general
        db.session.commit()

        session["ultimo_pedido_id"] = nuevo_pedido.ID_Pedido
        session["carrito_detalle"] = carrito
        session["total_pedido"] = total_general

        return redirect(url_for("clientes.detalle_pedido", valor=total_general))

    # GET → calcular total
    total = 0
    for item in carrito:
        descuento_str = str(item.get("descuento", "0")).replace("%", "").strip()
        try:
            descuento = float(descuento_str)
        except:
            descuento = 0.0

        precio_con_descuento = item["precio"] - (item["precio"] * descuento / 100)
        total += precio_con_descuento * item["cantidad"]

    return render_template(
        "clientes/confirmacion_pedido.html",
        carrito=carrito,
        total=total,
        cliente=cliente,
        fechas_horas=fechas_horas,
        categorias=categorias,
        metodo_pago_seleccionado=session.get("metodo_pago")
    )




@clientes_bp.route("/pagar_nequi")
def pagar_nequi():

    try:
        valor = float(request.args.get("valor", 0))
    except:
        valor = 0

    # Crear el pago pendiente
    nuevo_pago = Pago(
        Monto=valor,
        Metodo_Pago="Nequi",
        fecha_pago=datetime.now().date(),
        Estado_Pago="Pendiente",
        ID_Cliente=current_user.cliente.ID_cliente,
        ID_Pedido=session.get("ultimo_pedido_id")  
    )

    db.session.add(nuevo_pago)
    db.session.commit()
    session["metodo_pago"] = "Nequi"



    session["ultimo_pago_id"] = nuevo_pago.ID_pago
    
    session["total_pago"] = valor

    
    user_agent = request.headers.get("User-Agent")
    numero = "3143707430"
    descripcion = "Pago pedido DeliCake"

    if "Android" in user_agent or "iPhone" in user_agent:
        return redirect(f"nequi://sendmoney?phone={numero}&amount={valor}")



    return render_template(
    "clientes/pago_nequi_pc.html",
    numero=numero,
    valor=valor,
    descripcion=descripcion,
    pago_id=nuevo_pago.ID_pago  
)



@clientes_bp.route("/estado_pago/<int:id_pago>")
def estado_pago(id_pago):
    pago = Pago.query.get(id_pago)

    if not pago:
        print("⛔ PAGO NO ENCONTRADO")
        return jsonify({"estado": "error", "mensaje": "Pago no encontrado"})

    print("🔍 CONSULTA ESTADO PAGO")
    print("ID:", pago.ID_pago)
    print("Estado_Pago:", pago.Estado_Pago)
    print("Mensaje_Cliente:", pago.Mensaje_Cliente)

    return jsonify({
        "estado": pago.Estado_Pago if pago.Estado_Pago else "Pendiente",
        "mensaje": pago.Mensaje_Cliente if pago.Mensaje_Cliente else ""
    })




@clientes_bp.route("/pagar_daviplata")
def pagar_daviplata():

    try:
        valor = float(request.args.get("valor", 0))
    except:
        valor = 0

    numero = "3143707430"
    descripcion = "Pago pedido DeliCake"

    user_agent = request.headers.get("User-Agent", "")

 
    if "Android" in user_agent or "iPhone" in user_agent:
        return redirect(f"daviplata://sendmoney?phone={numero}&amount={valor}")

    return render_template(
        "clientes/pago_daviplata_pc.html",
        numero=numero,
        valor=valor,
        descripcion=descripcion
    )




@clientes_bp.route("/detalle_pedido", methods=["GET", "POST"])
@login_required
def detalle_pedido():
    pedido_id = session.get("ultimo_pedido_id")
    carrito = session.get("carrito_detalle", [])
    categorias = Categoria.query.all()

    if not pedido_id or not carrito:
        flash("⚠️ No hay pedido para mostrar.", "warning")
        return redirect(url_for("clientes.ver_carrito"))

    pedido = Pedido.query.get(pedido_id)
    cliente = current_user.cliente  

    personalizaciones = PersonalizacionProducto.query.filter_by(ID_Pedido=pedido_id).all()

  
    if not personalizaciones:
        personalizaciones = PersonalizacionProducto.query.filter_by(ID_Cliente=cliente.ID_cliente).all()

    if request.method == "POST":
        for item in carrito:
     
            personalizacion = next(
                (p for p in personalizaciones if p.ID_Producto == item.get("id")), None
            )
            
            detalle = DetallePedido(
                Nombre=current_user.Nombre,
                Cantidad_unidades_producto=item["cantidad"],
                Nombre_producto=item["nombre"],
                Fecha_Solicitud=pedido.Fecha_Solicitud,
                Descuento=item.get("descuento", "0%"),
                Masa=personalizacion.Masa if personalizacion else item.get("masa", "batida"),
                Relleno=personalizacion.Relleno if personalizacion else item.get("relleno", "vainilla"),
                Cobertura=personalizacion.Cobertura if personalizacion else item.get("cobertura", "chocolate"),
                Porciones=personalizacion.Porciones if personalizacion else item.get("porciones", "entero"),
                Adicionales=personalizacion.Adicionales if personalizacion else item.get("adicionales", "ninguno"),
                Precio_Unitario=item["precio"],
                Total=pedido.Total,
                ID_Pedido=pedido.ID_Pedido,
                ID_Producto=item.get("id"),
                ID_Cliente=cliente.ID_cliente,
                ID_Personalizacion=personalizacion.ID_Personalizacion if personalizacion else None
                )
            db.session.add(detalle)
            db.session.commit()
            
            session.pop("carrito_detalle", None)
            session.pop("ultimo_pedido_id", None)
            return redirect(url_for("clientes.gracias"))

    return render_template(
        "clientes/detalle_pedido.html",
        pedido=pedido,
        carrito=carrito,
        cliente=cliente,
        categorias=categorias,
        personalizaciones=personalizaciones
    )








@clientes_bp.route("/personalizar/<int:producto_id>", methods=["GET", "POST"])
def personalizar_producto(producto_id):
    producto = Producto.query.get_or_404(producto_id)
    cliente_id = current_user.cliente.ID_cliente


    # 🔹 Recuperar el pedido actual desde la sesión
    pedido_id = session.get("ultimo_pedido_id")
    pedido_actual = Pedido.query.get(pedido_id) if pedido_id else None

    if not pedido_actual:
        flash("⚠️ No hay un pedido activo para asociar la personalización.", "danger")
        return redirect(url_for("clientes.carrito"))

    if request.method == "POST":
        masa = request.form.get("masa", "").strip()
        relleno = request.form.get("relleno", "").strip()
        cobertura = request.form.get("cobertura", "").strip()
        porciones = request.form.get("porciones", "").strip()
        adicionales = [a.strip() for a in request.form.getlist("adicionales")]
        adicionales_str = ",".join(adicionales) if adicionales else None

        try:
            # 🔹 Verificar si ya existe una personalización previa del mismo producto, cliente y pedido
            personalizacion = PersonalizacionProducto.query.filter_by(
                ID_Producto=producto_id,
                ID_Cliente=cliente_id,
                ID_Pedido=pedido_actual.ID_Pedido
            ).first()

            if personalizacion:
                # 🔄 Actualizar la personalización existente
                personalizacion.Masa = masa
                personalizacion.Relleno = relleno
                personalizacion.Cobertura = cobertura
                personalizacion.Porciones = porciones
                personalizacion.Adicionales = adicionales_str
            else:
                # 🆕 Crear una nueva personalización
                personalizacion = PersonalizacionProducto(
                    ID_Producto=producto_id,
                    ID_Cliente=cliente_id,
                    ID_Pedido=pedido_actual.ID_Pedido,
                    Masa=masa,
                    Relleno=relleno,
                    Cobertura=cobertura,
                    Porciones=porciones,
                    Adicionales=adicionales_str
                )
                db.session.add(personalizacion)

            db.session.commit()

            # 🔹 Actualizar el carrito en sesión
            carrito = session.get("carrito", [])
            for item in carrito:
                if str(item.get("id")) == str(producto_id):
                    item["masa"] = masa
                    item["relleno"] = relleno
                    item["cobertura"] = cobertura
                    item["porciones"] = porciones
                    item["adicionales"] = adicionales_str
                    item["personalizacion_id"] = personalizacion.ID_Personalizacion
                    break

            session["carrito"] = carrito
            session.modified = True

            flash("✅ Personalización guardada con éxito.", "success")
            return redirect(url_for("clientes.confirmacion_pedido"))

        except Exception as e:
            db.session.rollback()
            print(f"Error al guardar personalización: {e}")
            flash("❌ Error al guardar la personalización.", "danger")

    # Mantener los datos de confirmación en la sesión
    datos_confirmacion = session.get("datos_confirmacion", {})
    session["datos_confirmacion"] = datos_confirmacion

    return render_template("clientes/personalizacion_de_producto.html", producto=producto)

          

@clientes_bp.route("/politica_privacidad")
def politica_privacidad():
    return render_template("clientes/politica_privacidad.html")


@clientes_bp.route("/terminos_condiciones")
def terminos_condiciones():
    return render_template("clientes/terminos_condiciones.html")



def get_cart():
    if "carrito" not in session:
        session["carrito"] = []
    return session["carrito"]

@clientes_bp.route("/carrito")
@login_required
def carrito():
    carrito = session.get("carrito", [])
    total = 0

    for item in carrito:

        descuento_str = str(item.get("descuento", "0")).replace("%", "").strip()
        try:
            descuento = float(descuento_str)
        except ValueError:
            descuento = 0.0

      
        precio_con_descuento = item["precio"] - (item["precio"] * descuento / 100)
        total += precio_con_descuento * item["cantidad"]

    
    categorias = Categoria.query.all()


    return render_template("clientes/carrito.html", carrito=carrito, total=total, categorias=categorias)



def carrito():
    carrito = session.get("carrito", [])
    total = sum(item["precio"] * item["cantidad"] for item in carrito)
    categorias = Categoria.query.all()
    return render_template("clientes/carrito.html", categorias=categorias,carrito=carrito, total=total)


@clientes_bp.route("/carrito/agregar", methods=["POST"])
def carrito_agregar():
    data = request.get_json()
    carrito = get_cart()

    
    producto = Producto.query.get(data["id"])
    if not producto:
        return jsonify({"ok": False, "msg": "Producto no encontrado"}), 404


    for item in carrito:
        if str(item["id"]) == str(data["id"]):
            item["cantidad"] += int(data["cantidad"])
            break
    else:
        
        carrito.append({
    "id": str(data["id"]),
    "nombre": data["nombre"],
    "precio": float(data["precio"]),
    "cantidad": int(data["cantidad"]),
    "descuento": float(producto.Descuento or 0),
    "imagen": (
        data["imagen"]
        if data["imagen"].startswith("/static/")
        else url_for('static', filename=f"img/productos/{data['imagen']}")
    ),
})

    
    session["carrito"] = carrito
    session.modified = True

    return jsonify({"ok": True, "msg": "Producto agregado al carrito", "carrito": carrito})

@clientes_bp.route("/carrito/eliminar/<id>")
def carrito_eliminar(id):
    carrito = get_cart()
    carrito = [item for item in carrito if str(item["id"]) != str(id)]
    session["carrito"] = carrito
    session.modified = True
    return redirect(url_for("clientes.carrito"))


@clientes_bp.route("/carrito/vaciar")
def carrito_vaciar():
    session["carrito"] = []
    return redirect(url_for("clientes.carrito"))


@clientes_bp.route("/campanita")
@login_required
def campanita():
    if not current_user.cliente:
        flash("No tienes un perfil de cliente asociado.", "warning")
        return render_template("clientes/campanita.html", notificaciones=[])

    pedidos = current_user.cliente.pedidos

    notificaciones = []
    for pedido in pedidos:
        notificaciones.append(f"Pedido #{pedido.ID_Pedido} está en {pedido.Estado_Pedido}")

    total_notificaciones = len(notificaciones)

    return render_template(
        "clientes/campanita.html",
        notificaciones=notificaciones,
        total_notificaciones=total_notificaciones
    )

@clientes_bp.route('/suscribir1', methods=["POST"])
def suscribir1():
    correo = request.form.get("correo", "").strip()  
    
    if not correo or "@" not in correo or "." not in correo:
        flash("Correo inválido, intente de nuevo", "error")
        return redirect(url_for('publica'))
    existente = Suscriptor.query.filter_by(correo=correo).first()
    if existente:
        flash("Este correo ya está suscrito", "warning")
        return redirect(url_for('publica'))

    nuevo = Suscriptor(correo=correo)
    db.session.add(nuevo)
    db.session.commit()

    msg = Message(
        subject="🎉 ¡Gracias por suscribirte a DeliCake!",
        sender=app.config['MAIL_USERNAME'],
        recipients=[correo]
    )

    msg.html = """
    <div style="text-align:center; font-family: Arial, sans-serif; padding:20px;">
        <img src="cid:logo_delicake" width="150" style="border-radius:50%;"><br>
        <h2 style="color:#d63384;">🎀 Bienvenido a la familia DeliCake 🎀</h2>
        <p style="font-size:16px; color:#333;">
            Gracias por suscribirte a nuestro boletín 💌.<br>
            A partir de ahora recibirás nuestras mejores ofertas, novedades y consejos dulces directamente en tu bandeja de entrada.
        </p>
        <p style="margin-top:20px; color:#d63384; font-weight:bold;">
            ¡Que tu día sea tan dulce como nuestros postres! 🧁
        </p>
    </div>
    """
    with app.open_resource("static/img/nuestrasdelicias.png") as img:
        msg.attach(
            filename="nuestrasdelicias.png",
            content_type="image/png",
            data=img.read(),
            disposition="inline",
            headers={'Content-ID':'<logo_delicake>'}       
            
        )

    
    mail.send(msg)

    flash("¡Gracias por suscribirte! Revisa tu correo 📩", "success")
    return redirect(url_for('publica'))


@clientes_bp.route('/historial-pedidos')
def historial_pedidos():
    if not current_user.cliente:
        flash("Este usuario no tiene perfil de cliente.")
        return redirect(url_for('login'))

    pedidos = current_user.cliente.pedidos
    return render_template('clientes/historial_pedidos.html', pedidos=pedidos)



@clientes_bp.route("/notificaciones_json")
@login_required
def notificaciones_json():
    notificaciones = Notificacion.query.filter_by(
        usuario_id=current_user.ID_usuario,
        leida=False
    ).order_by(Notificacion.fecha.desc()).all()

    data = [{
        "mensaje": n.mensaje,
        "fecha": n.fecha.strftime("%Y-%m-%d %H:%M:%S")
    } for n in notificaciones]

    return jsonify(data)

@clientes_bp.route("/marcar_leidas", methods=["POST"])
@login_required
def marcar_leidas():   
    Notificacion.query.filter_by(usuario_id=current_user.ID_usuario, leida=False).update({"leida": True})
    db.session.commit()
    return jsonify({"success": True})

@clientes_bp.route('/toggle_favorito/<int:producto_id>', methods=['POST'])
@login_required
def toggle_favorito(producto_id):
    favorito = Favorito.query.filter_by(
        ID_usuario=current_user.ID_usuario,
        ID_Producto=producto_id
    ).first()

    if favorito:
        db.session.delete(favorito)
        db.session.commit()
        return jsonify({'favorito': False, 'mensaje': 'Producto eliminado de favoritos 💔'})
    else:
        nuevo = Favorito(ID_usuario=current_user.ID_usuario, ID_Producto=producto_id)
        db.session.add(nuevo)
        db.session.commit()
        return jsonify({'favorito': True, 'mensaje': 'Producto añadido a favoritos 💖'})

@clientes_bp.route('/lanzamientos')
def lanzamientos():
    # Trae todos los lanzamientos ordenados por fecha (opcional)
    lanzamientos = Lanzamiento.query.order_by(Lanzamiento.fecha_catalogo).all()

    return render_template('clientes/lanzamientos.html', lanzamientos=lanzamientos)

@clientes_bp.route("/gracias")
@login_required
def gracias():
    return render_template("clientes/gracias.html")

def marcar_leidas():   
    Notificacion.query.filter_by(usuario_id=current_user.ID_usuario, leida=False).update({"leida": True})
    db.session.commit()
    return jsonify({"success": True})

@clientes_bp.route('/mis_favoritos')
@login_required
def mis_favoritos():
    categorias = Categoria.query.all()
    favoritos = Favorito.query.filter_by(ID_usuario=current_user.ID_usuario).all()
    productos = [f.producto for f in favoritos]
    return render_template('clientes/Favoritos.html', productos=productos, categorias=categorias,favoritos=favoritos)

@clientes_bp.route('/eliminar_favorito/<int:id_favorito>', methods=['POST'])
@login_required
def eliminar_favorito(id_favorito):
    favorito = Favorito.query.filter_by(
        id_favorito=id_favorito,
        ID_usuario=current_user.ID_usuario
    ).first()

    if favorito:
        db.session.delete(favorito)
        db.session.commit()
        flash('Producto eliminado de favoritos 💔', 'success')
    else:
        flash('No se encontró el producto en tus favoritos.', 'danger')

    return redirect(url_for('clientes.mis_favoritos'))

@clientes_bp.route('/buscar')
def buscar_cliente():
    categorias=Categoria.query.all()
    query= request.args.get("q","").strip()
    productos=[]
    
    if query:
        
        productos = Producto.query.filter(
            Producto.Nombre_producto.ilike(f"%{query}%")).all()
    
   
    return render_template('clientes/buscar_cliente.html', productos=productos, query=query, categorias=categorias)


@clientes_bp.route("/lanzamiento")
def lanzamientos_cliente():
    from flask import url_for
    import os

    banner_actual_path = os.path.join("static", "videos", "banner_actual.mp4")
    banner_actual = None

    if os.path.exists(banner_actual_path):
        banner_actual = url_for("static", filename="videos/banner_actual.mp4")

    lanzamientos = Lanzamiento.query.all()
    return render_template("clientes/lanzamientos.html", lanzamientos=lanzamientos, banner_actual=banner_actual)

historial_chat = []  

@clientes_bp.route("/chat", methods=["GET", "POST"])
def chat():
    global historial_chat

    if request.method == "POST":
        pregunta = request.form["pregunta"]


        historial_chat.append({"tipo": "user", "texto": pregunta})

        from chatbot import preguntar_chatbot
        respuesta = preguntar_chatbot(pregunta)


        historial_chat.append({"tipo": "bot", "texto": respuesta})

    return render_template("clientes/chat_bot.html", historial=historial_chat)


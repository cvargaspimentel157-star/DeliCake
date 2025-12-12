from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user 
from controladores.models import FooterConfig, db, Producto, Categoria, Pedido,Favorito, Disponibilidad,DetalleProducto, Calificacion, Reseña, Suscriptor , Notificacion,Lanzamiento,DetallePedido,Pago
from werkzeug.utils import secure_filename
from decimal import Decimal
from sqlalchemy import func, extract
from sqlalchemy import extract, func
from flask import jsonify, request
from datetime import datetime
from datetime import date
from extensions import mysql
import os
import shutil 



admin_bp = Blueprint("admin", __name__, url_prefix="/admin")

VIDEOS_FOLDER = "C:\\Users\\USUARIO\\Desktop\\DeliCake\\DeliCake\\static\\videos"
BANNER_ACTUAL = os.path.join(VIDEOS_FOLDER, "banner_actual.mp4")
UPLOAD_FOLDER = "static/uploads/lanzamientos"




@admin_bp.route("/producto/<int:id>", methods=["GET", "POST"])
def  detalle(id):
    producto = Producto.query.get_or_404(id)
    categorias = Categoria.query.all()
    detalle = DetalleProducto.query.filter_by(ID_producto=id).first()
    
    sugerencias = Producto.query.filter(
        Producto.ID_Categoria == producto.ID_Categoria,
        Producto.ID_Producto != producto.ID_Producto).limit(4).all()    
    
    if request.method =="POST":
        puntuacion = int (request.form['puntuacion'])
        nueva_calificacion = Calificacion(Valor = puntuacion, ID_Producto = id)
        db.session.add(nueva_calificacion)
        db.session.commit()
        return redirect(url_for('admin.detalle', id=id))
    
    calificiones= Calificacion.query.filter_by(ID_Producto=id).all()
    promedio = None
    if calificiones:
        promedio = round(sum(c.Valor for c in calificiones)/len(calificiones),1)
      
    return render_template("clientes/detalle.html", producto=producto, categorias=categorias, detalle=detalle, promedio=promedio, sugerencias=sugerencias, calificiones= calificiones)


@admin_bp.route("/agregar", methods=["GET", "POST"])
def agregar_producto():
    categorias = Categoria.query.all()
    productos = Producto.query.all()
   
    if request.method == "POST":
        nombre = request.form["nombre"]
        descripcion = request.form["descripcion"]
        precio = request.form["precio"]
        descuento = request.form["descuento"]
        id_categoria = request.form["categoria"]
        
        
        producto_existente = Producto.query.filter_by(Nombre_producto=nombre).first()
        if producto_existente:
            flash("❌ El nombre del producto ya existe. Debe ser único.", "danger")
            return redirect(url_for("admin.agregar_producto"))
 
        imagen_file = request.files["imagen"]
        if imagen_file and imagen_file.filename != "":
            imagen_path = imagen_file.filename
            imagen_file.save(os.path.join("static/img", imagen_path))
        else:
            imagen_path = "default.jpg" 

        nuevo = Producto(
            Nombre_producto=nombre,
            Descripcion_producto=descripcion,
            Precio_Unitario =precio,
            Descuento=descuento,
            Imagen=imagen_path,
            ID_Administrador=1,
            ID_Categoria = id_categoria
        )
        db.session.add(nuevo)
        db.session.commit()
        
        ingredientes = request.form['ingredientes']
        tiempo = request.form["tiempo"]
        detalle = DetalleProducto(
            Ingredientes = ingredientes,
            tiempo_preparacion = tiempo,
            ID_producto =nuevo.ID_Producto
        )        
        db.session.add(detalle)
        db.session.commit()
        
        
        flash("Producto agregado con éxito ")
        return redirect(url_for("admin.agregar_producto"))
    categorias = Categoria.query.filter_by().all() 
    return render_template("admin/agregar_producto.html",categorias=categorias,productos=productos)


@admin_bp.route("/categoria/<int:id_categoria>")
def productos_por_categoria(id_categoria):
    categorias = Categoria.query.all()
    productos = Producto.query.filter_by(ID_Categoria=id_categoria).all()
    favoritos_ids = []
    if current_user.is_authenticated:
        favoritos_ids = [f.ID_Producto for f in Favorito.query.filter_by(ID_usuario=current_user.ID_usuario).all()]
    return render_template("clientes/catalogo.html",  productos=productos, categorias=categorias, favoritos_ids=favoritos_ids
                           )

@admin_bp.route("/editar", methods=["GET"])
def editar_producto():
    productos = Producto.query.all()
    categorias = Categoria.query.all()

    for p in productos:

        
        p.Precio_Unitario = float(p.Precio_Unitario)
        p.Descuento = float(p.Descuento) if p.Descuento else 0.0

        
        if p.Descuento > 0:
            p.Precio_descuento = p.Precio_Unitario - (p.Precio_Unitario * (p.Descuento / 100))
        else:
            p.Precio_descuento = p.Precio_Unitario

    return render_template(
        "admin/editar_producto.html",
        productos=productos,
        categorias=categorias
    )

    
@admin_bp.route("/eliminar/<int:id>", methods=["POST"])
def eliminar(id):
    try:
    
        producto = Producto.query.get(id)

        if not producto:
            flash(" El producto no existe", "danger")
            return redirect(url_for("admin.listar_productos"))

        Favorito.query.filter_by(ID_Producto=id).delete(synchronize_session=False)

       
        pedidos_asociados = DetallePedido.query.filter_by(ID_Producto=id).first()

        if pedidos_asociados:
            flash(" No se permite eliminar productos con pedidos registrados o pendientes.", "danger")
            return redirect(url_for("admin.listar_productos"))

        DetalleProducto.query.filter_by(ID_producto=id).delete(synchronize_session=False)

        db.session.delete(producto)
        db.session.commit()

        flash(" Producto eliminado correctamente", "success")

    except Exception as e:
        db.session.rollback()
        flash(f" Error al eliminar producto: {str(e)}", "danger")

    return redirect(url_for("admin.listar_productos"))

@admin_bp.route("/listar_productos")
def listar_productos():
    categorias = Categoria.query.all()
    productos = Producto.query.all()
   
    return render_template("admin/eliminar_producto.html", productos=productos, categorias=categorias)
@admin_bp.route('/buscar')
def buscar():
    categorias=Categoria.query.all()
    query= request.args.get("q","").strip()
    productos=[]
    
    if query:
        
        productos = Producto.query.filter(
            Producto.Nombre_producto.ilike(f"%{query}%")).all()
    
    return render_template('clientes/buscar.html', productos=productos, query=query, categorias=categorias)

@admin_bp.route('/buscar_adm')
def buscar_adm():
    categorias=Categoria.query.all()
    query= request.args.get("q","").strip()
    productos=[]
    
    if query:
        
        productos = Producto.query.filter(
            Producto.Nombre_producto.ilike(f"%{query}%")).all()
    
    return render_template('admin/buscar_admin.html', productos=productos, query=query, categorias=categorias)


@admin_bp.route('/panel')
def panel():
    categorias=Categoria.query.all()
    return render_template("admin/mi_cuenta_ADM.html", categorias=categorias )
    

@admin_bp.route("/seguimiento", methods=["GET"])
def seguimiento_pedidos():
    pedidos = Pedido.query.all()
    categorias=Categoria.query.all()
    return render_template("admin/seguimiento de pedido ADM.html", pedidos=pedidos, categorias=categorias)

@admin_bp.route("/actualizar_estado/<int:pedido_id>", methods=["POST"])
def actualizar_estado(pedido_id):
    nuevo_estado = request.form.get("estado")
    pedido = Pedido.query.get(pedido_id)

    if pedido:
        pedido.Estado_Pedido = nuevo_estado
        db.session.commit()

        cliente = pedido.cliente
        if cliente and cliente.usuario:
            mensaje = f"Tu pedido #{pedido.ID_Pedido} cambió de estado a '{nuevo_estado}'."
            noti = Notificacion(usuario_id=cliente.usuario.ID_usuario, mensaje=mensaje)
            db.session.add(noti)
            db.session.commit()

        flash(f"Estado del pedido {pedido_id} actualizado a {nuevo_estado}", "success")
    else:
        flash("Pedido no encontrado ❌", "danger")

    return redirect(url_for("admin.seguimiento_pedidos"))








# ---------------------- DISPONIBILIDAD ---------------------- #
@admin_bp.route("/disponibilidad", methods=["GET", "POST"])
def gestionar_disponibilidad():
    if request.method == "POST":
        fecha = request.form.get("fecha")
        hora = request.form.get("hora")

        if fecha and hora:
            from datetime import datetime
            fecha_obj = datetime.strptime(fecha, "%Y-%m-%d").date()
            hora_obj = datetime.strptime(hora, "%H:%M").time()

            nueva_disponibilidad = Disponibilidad(Fecha=fecha_obj, Hora=hora_obj)
            db.session.add(nueva_disponibilidad)
            db.session.commit()
            flash("✅ Disponibilidad agregada", "success")
        return redirect(url_for("admin.gestionar_disponibilidad"))

    disponibilidades = Disponibilidad.query.order_by(Disponibilidad.Fecha, Disponibilidad.Hora).all()
    return render_template("admin/disponibilidad.html", disponibilidades=disponibilidades)


@admin_bp.route("/disponibilidad/borrar/<int:id>", methods=["POST"])
def borrar_disponibilidad(id):
    disp = Disponibilidad.query.get_or_404(id)
    db.session.delete(disp)
    db.session.commit()
    flash("🗑️ Disponibilidad eliminada", "success")
    return redirect(url_for("admin.gestionar_disponibilidad"))


@admin_bp.route("/suscriptores")
def lista_suscriptores():
    suscriptores = Suscriptor.query.all()
    categorias = Categoria.query.all()
    return render_template("admin/suscripciones.html", suscriptores=suscriptores,categorias=categorias)

@admin_bp.route("/reseñas")
def lista_reseñas():
    reseñas = Reseña.query.all()
    categorias = Categoria.query.all()
    return render_template("admin/reseñas.html", reseñas=reseñas, categorias=categorias)

@admin_bp.route("/aprobar/<int:id>")
def aprobar_reseña(id):
    reseña = Reseña.query.get_or_404(id)
    reseña.estado = "aprobada"
    db.session.commit()
    return redirect(url_for("admin.lista_reseñas"))




@admin_bp.route("/eliminar/<int:id>")
def eliminar_reseña(id):
    reseña = Reseña.query.get_or_404(id)
    db.session.delete(reseña)
    db.session.commit()
    return redirect(url_for("admin.lista_reseñas"))

@admin_bp.route("/anuncios", methods=["GET", "POST"])
def anuncios():
    banners = [f for f in os.listdir(VIDEOS_FOLDER) if f.endswith((".mp4", ".webm"))]

    if request.method == "POST":
        banner = request.form.get("banner")
        if banner and banner in banners:
            nuevo_banner = os.path.join(VIDEOS_FOLDER, banner)
            shutil.copy(nuevo_banner, BANNER_ACTUAL)
            flash(f'🎥 Banner "{banner}" establecido como actual.', "success")
            return redirect(url_for("admin.anuncios"))

    banner_actual = None
    if os.path.exists(BANNER_ACTUAL):
        banner_actual = url_for("static", filename="videos/banner_actual.mp4")

    return render_template("admin/cambiar_anuncios.html", banners=banners, banner_actual=banner_actual)


@admin_bp.route("/cambiar_banner", methods=["POST"])
def cambiar_banner():
    import os, shutil
    from flask import request, jsonify, current_app

    
    VIDEOS_FOLDER = os.path.join(current_app.root_path, "static", "videos")
    BANNER_ACTUAL = os.path.join(VIDEOS_FOLDER, "banner_actual.mp4")

    
    if "nuevo_banner" not in request.files:
        return jsonify({"error": "No se recibió archivo"}), 400

    file = request.files["nuevo_banner"]

    if file.filename == "":
        return jsonify({"error": "Archivo sin nombre"}), 400

 
    if file and file.filename.lower().endswith((".mp4", ".webm", ".ogg")):
        
        os.makedirs(VIDEOS_FOLDER, exist_ok=True)
        temp_path = os.path.join(VIDEOS_FOLDER, file.filename)
        file.save(temp_path)

       
        if os.path.exists(BANNER_ACTUAL):
            os.remove(BANNER_ACTUAL)
        shutil.move(temp_path, BANNER_ACTUAL)

     
        return jsonify({
            "success": True,
            "message": "✅ Banner actualizado correctamente"
        }), 200

    return jsonify({"error": "Formato no permitido"}), 400

@admin_bp.route("/lanzamientos")
def lanzamientos():
    lanzamientos = Lanzamiento.query.all()
    return render_template("admin/lanzamientos.html", lanzamientos=lanzamientos)


@admin_bp.route("/lanzamientos/agregar", methods=["POST"])
def agregar_lanzamiento():
    descripcion = request.form["descripcion"]
    fecha_catalogo = request.form["fecha_catalogo"]
    imagen = request.files["imagen"]

    if imagen:
        os.makedirs(UPLOAD_FOLDER, exist_ok=True)
        ruta = os.path.join(UPLOAD_FOLDER, imagen.filename)
        imagen.save(ruta)

        nuevo = Lanzamiento(
            descripcion=descripcion,
            fecha_catalogo=fecha_catalogo,
            imagen=imagen.filename
        )
        db.session.add(nuevo)
        db.session.commit()
        flash("✅ Lanzamiento agregado con éxito")

    return redirect(url_for("admin.lanzamientos"))




@admin_bp.route('/reportes/fechas', methods=['GET'])
def fechas_ventas():
    categorias=Categoria.query.all()
    mes_seleccionado = request.args.get('mes', type=int)

    
    query = db.session.query(
        Pedido.Fecha_Solicitud.label('fecha'),
        func.count(Pedido.ID_Pedido).label('cantidad_pedidos'),
        func.sum(Pedido.Total).label('total_vendido')
    )
    if mes_seleccionado:
        query = query.filter(extract('month', Pedido.Fecha_Solicitud) == mes_seleccionado)

    query = query.group_by(Pedido.Fecha_Solicitud).order_by(func.sum(Pedido.Total).desc())

    resultados = query.all()

    total_general = sum([float(r.total_vendido or 0) for r in resultados])

    return render_template(
        'admin/Fechas_ventas.html',
        resultados=resultados,
        total_general=total_general,
        mes_seleccionado=mes_seleccionado,
        categorias =categorias
    )

@admin_bp.route("/lanzamientos/eliminar/<int:id>")
def eliminar_lanzamiento(id):
    lanzamiento = Lanzamiento.query.get_or_404(id)
    db.session.delete(lanzamiento)
    db.session.commit()
    flash("🗑️ Lanzamiento eliminado con éxito")
    return redirect(url_for("admin.lanzamientos"))



@admin_bp.route('/Reportes')
def Reportes():
    categorias=Categoria.query.all()
    return render_template("admin/reportes_ventas.html", categorias=categorias, nombres=[],
    cantidades=[] )


@admin_bp.route('/metodos_pago', methods=["GET"])
@login_required
def metodos_pago():
    
    categorias=Categoria.query.all()
    mes = request.args.get("mes", default=date.today().month, type=int)
    anio = request.args.get("anio", default=date.today().year, type=int)

    
    pagos = Pago.query.filter(
        extract('month', Pago.fecha_pago) == mes,
        extract('year', Pago.fecha_pago) == anio
    ).all()

    
    conteo = {"Tarjeta": 0, "Nequi": 0, "Daviplata": 0,}
    for p in pagos:
        if p.Metodo_Pago in conteo:
            conteo[p.Metodo_Pago] += 1

    total_pagos = sum(conteo.values())
    datos = []


    if total_pagos > 0:
        for metodo, cantidad in conteo.items():
            porcentaje = (cantidad / total_pagos) * 100
            datos.append({"metodo": metodo, "porcentaje": porcentaje})
    else:
        datos = []

    
    return render_template(
        "admin/metodos_pago.html",
        datos=datos,
        mes=mes,
        anio=anio,
        categorias= categorias
    )
   


@admin_bp.route('/ingresos', methods=['GET'])
def ingresos():
    categorias=Categoria.query.all()
    mes = request.args.get('mes', type=int)
    anio = request.args.get('anio', type=int)

    query = (
        db.session.query(
            Categoria.Nombre_categoria,
            func.sum(DetallePedido.Cantidad_unidades_producto * Producto.Precio_Unitario).label('total_ingresos')
        )
        .join(Producto, Producto.ID_Producto == DetallePedido.ID_Producto)
        .join(Categoria, Categoria.ID_Categoria == Producto.ID_Categoria)
        .join(Pedido, Pedido.ID_Pedido == DetallePedido.ID_Pedido)

    )
    
    if anio:
        query = query.filter(extract('year', Pedido.Fecha_Solicitud) == anio)
    if mes:
        query = query.filter(extract('month', Pedido.Fecha_Solicitud) == mes)

    resultados = query.group_by(Categoria.Nombre_categoria).all()

    categorias = [r[0] for r in resultados]
    ingresos = [float(r[1]) for r in resultados]
    total_general = sum(ingresos)
    
    return render_template(
        'admin/ingresos.html',
        categorias=categorias,
        ingresos=ingresos,
        total_general=total_general,
        mes=mes,
        anio=anio,
    )
    
    

@admin_bp.route("/pagos_pendientes")
def pagos_pendientes():
    
    session.pop('_flashes', None)

    pagos = Pago.query.order_by(Pago.ID_pago.desc()).all()

    
    logger.info("----- pagos en BD -----")
    for p in pagos:
        logger.info(f"ID_pago={p.ID_pago} Estado_Pago={p.Estado_Pago} ID_Pedido={getattr(p, 'ID_Pedido', None)} Monto={p.Monto} ID_Cliente={getattr(p, 'ID_Cliente', None)}")

    pagos_view = []
    for p in pagos:
        
        cliente_nombre = "Cliente no disponible"
        if getattr(p, "cliente", None):
            cli = p.cliente
            if getattr(cli, "usuario", None):
                cliente_nombre = f"{cli.usuario.Nombre} {cli.usuario.Apellido}".strip()
            else:
                cliente_nombre = getattr(cli, "Direccion", "Cliente sin nombre")
        elif getattr(p, "pedido", None) and getattr(p.pedido, "cliente", None):
            cli = p.pedido.cliente
            if getattr(cli, "usuario", None):
                cliente_nombre = f"{cli.usuario.Nombre} {cli.usuario.Apellido}".strip()
            else:
                cliente_nombre = getattr(cli, "Direccion", "Cliente")

        try:
            total_val = float(p.Monto) if p.Monto is not None else (float(p.pedido.Total) if getattr(p, "pedido", None) and p.pedido.Total is not None else 0)
        except Exception:
            total_val = 0

        pagos_view.append({
            "ID_pago": p.ID_pago,
            "ID_Pedido": getattr(p, "ID_Pedido", None),
            "cliente_nombre": cliente_nombre,
            "total": total_val,
            "metodo": p.Metodo_Pago,
            "estado": p.Estado_Pago
        })

    return render_template("admin/pagos_pendientes.html", pagos=pagos_view)



@admin_bp.route("/aprobar_pago/<int:id_pago>")
def aprobar_pago(id_pago):
    pago = Pago.query.get(id_pago)
    if not pago:
        flash("❌ Pago no encontrado.", "error")
        return redirect(url_for("admin.pagos_pendientes"))

    
    if pago.Estado_Pago != "Pendiente":
        flash("⚠️ Este pago no está en estado 'Pendiente' (ya fue procesado).", "warning")
        return redirect(url_for("admin.pagos_pendientes"))

    
    nuevo_pedido = Pedido(
        Fecha_Solicitud=datetime.now(),
        Estado_Pedido="Pendiente",
        Total=pago.Monto,
        Metodo_Pago=pago.Metodo_Pago,
        ID_Cliente=pago.ID_Cliente,
        ID_Producto=None   
    )

    db.session.add(nuevo_pedido)
    db.session.flush()   

    
    pago.ID_Pedido = nuevo_pedido.ID_Pedido
    pago.Estado_Pago = "Aprobado"
    pago.Mensaje_Cliente = "✅ Tu pago ha sido aprobado"

    db.session.commit()
    flash("✅ Pago aprobado correctamente.", "success")
    return redirect(url_for("admin.pagos_pendientes"))

@admin_bp.route("/rechazar_pago/<int:id_pago>")
def rechazar_pago(id_pago):
    pago = Pago.query.get(id_pago)
    if pago:
        pago.Estado_Pago = "Rechazado"
        db.session.commit()
    return redirect(url_for("admin.pagos_pendientes"))
from flask import session
import logging

logger = logging.getLogger(__name__)


@admin_bp.route('/admin/footer', methods=['GET', 'POST'])
def editar_footer():
    footer = FooterConfig.query.first()

    if not footer:
        footer = FooterConfig()
        db.session.add(footer)

    if request.method == "POST":
        footer.horario_1 = request.form.get('horario_1')
        footer.horario_2 = request.form.get('horario_2')
        footer.whatsapp_url = request.form.get('whatsapp_url')
        footer.preguntas_text = request.form.get('preguntas_text')
        footer.ubicacion = request.form.get('ubicacion')

        db.session.commit()
        flash("Los cambios fueron guardados correctamente", "success")
        return redirect(url_for('admin.editar_footer'))
    

    return render_template("admin/modificacion_informacion.html", footer=footer)


@admin_bp.route('/productos_mas_vendidos')
def productos_mas_vendidos():
    
    anios = db.session.query(func.extract('year', Pedido.Fecha_Solicitud).label('anio')) \
                      .distinct().order_by('anio').all()
    anios = [int(a.anio) for a in anios]

    
    query = db.session.query(
        Producto.Nombre_producto,
        func.sum(Pedido.Total).label('total_vendido')
    ).join(Pedido).group_by(Producto.ID_Producto).order_by(func.sum(Pedido.Total).desc())

    resultados = query.all()
    nombres = [r[0] for r in resultados]
    cantidades = [float(r[1]) for r in resultados]

    return render_template('admin/productos_mas_vendidos.html',
                           nombres=nombres, cantidades=cantidades, anios=anios)

@admin_bp.route('/admin/actualizar/<int:id>', methods=['POST'])
def actualizar_producto(id):
    producto = Producto.query.get_or_404(id)

    
    producto.Nombre_producto = request.form['nombre']
    producto.Descripcion_producto = request.form['descripcion']
    producto.Precio_Unitario = float(request.form['precio'])


    descuento = request.form.get('descuento', "").strip()
    descuento = float(descuento) if descuento else 0.0
    producto.Descuento = descuento

    
    if descuento > 0:
        producto.Precio_descuento = round(producto.Precio_Unitario * (1 - descuento / 100), 2)
    else:
        producto.Precio_descuento = producto.Precio_Unitario

    producto.ID_Categoria = request.form['categoria']

    imagen = request.files.get('imagen')
    if imagen and imagen.filename != "":
        ruta = os.path.join('static/img', imagen.filename)
        imagen.save(ruta)
        producto.Imagen = imagen.filename


    db.session.commit()

    flash("Producto actualizado correctamente", "success")
    return redirect(url_for('admin.editar_producto'))

from flask import Blueprint, render_template, request, redirect, url_for, flash
from controladores.models import db, Producto, Categoria, Pedido
import os

# Definir el Blueprint
admin_bp = Blueprint("admin", __name__, url_prefix="/admin")

# Ruta: Agregar producto
# ------------------------------
@admin_bp.route("/agregar", methods=["GET", "POST"])
def agregar_producto():
   
    if request.method == "POST":
        nombre = request.form["nombre"]
        descripcion = request.form["descripcion"]
        precio = request.form["precio"]
        descuento = request.form["descuento"]
        id_categoria = request.form["categoria"]

        # Guardar imagen
        imagen_file = request.files["imagen"]
        if imagen_file and imagen_file.filename != "":
            imagen_path = imagen_file.filename
            imagen_file.save(os.path.join("static/img", imagen_path))
        else:
            imagen_path = "default.jpg" 

        # Crear producto
        nuevo = Producto(
<<<<<<< HEAD
            Nombre_producto=nombre,
            Descripcion_producto=descripcion,
            Precio_Unitario =precio,
            Descuento=descuento,
            Imagen=imagen_path,
            ID_Administrador=1,
            ID_Categoria = id_categoria
=======
            nombre=nombre,
            descripcion=descripcion,
            precio=precio,
            descuento=descuento,
            categoria_id=id_categoria,
            imagen=imagen_path
>>>>>>> 6c4430e (Agregar módulo de seguimiento de pedidos)
        )
        db.session.add(nuevo)
        db.session.commit()
        
<<<<<<< HEAD
        
        
        flash("Producto agregado con éxito ")
        return redirect(url_for("admin.agregar_producto"))
    categorias = Categoria.query.filter_by().all() 
    return render_template("admin/agregar_producto.html",categorias=categorias)


@bp.route("/categoria/<int:id_categoria>")
def productos_por_categoria(id_categoria):
    # Buscar categoría
    categoria = Categoria.query.get_or_404(id_categoria)
    productos = Producto.query.filter_by(ID_Categoria=categoria.ID_Categoria).all()
    return render_template("clientes/catalogo.html",  productos=productos)


=======
        flash("Producto agregado con éxito ✅")
        return redirect(url_for("admin.agregar_producto"))

    categorias = Categoria.query.filter_by(Estado="Activa").all()
    return render_template("admin/agregar_producto.html", categorias=categorias)



# ------------------------------
@admin_bp.route("/seguimiento", methods=["GET"])
def seguimiento_pedidos():
    pedidos = Pedido.query.all()
    return render_template("admin/seguimiento_pedido_ADM.html", pedidos=pedidos)




# ------------------------------
@admin_bp.route("/actualizar_estado/<int:pedido_id>", methods=["POST"])
def actualizar_estado(pedido_id):
    nuevo_estado = request.form.get("estado")
    pedido = Pedido.query.get(pedido_id)

    if pedido:
        pedido.Estado_Pedido = nuevo_estado   
        db.session.commit()
        flash(f"Estado del pedido {pedido_id} actualizado a {nuevo_estado}", "success")
    else:
        flash("Pedido no encontrado", "error")

    return redirect(url_for("admin.seguimiento_pedidos"))
>>>>>>> 6c4430e (Agregar módulo de seguimiento de pedidos)

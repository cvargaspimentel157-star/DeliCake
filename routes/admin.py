from flask import Blueprint, render_template, request, redirect, url_for, flash
from controladores.models import db, Producto, Categoria
import os

bp = Blueprint("admin", __name__, url_prefix="/admin")


@bp.route("/agregar", methods=["GET", "POST"])
def agregar_producto():
   
    if request.method == "POST":
        nombre = request.form["nombre"]
        descripcion = request.form["descripcion"]
        precio = request.form["precio"]
        descuento = request.form["descuento"]
        id_categoria = request.form["categoria"]

 
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



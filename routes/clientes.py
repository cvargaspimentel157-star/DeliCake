from flask import Blueprint, render_template
from flask_login import login_required, current_user
from controladores.models import Pedido, Cliente

clientes_bp = Blueprint("clientes", __name__, url_prefix="/clientes")

# Seguimiento de pedidos (solo del cliente logueado)
@clientes_bp.route("/seguimiento", methods=["GET"])
@login_required
def seguimiento_pedidos_cliente():
    # Buscar el cliente asociado al usuario en sesión
    cliente = Cliente.query.filter_by(ID_usuario=current_user.ID_usuario).first()

    if not cliente:
        return render_template("clientes/seguimiento_pedido.html", pedidos=[])

    # Traer solo los pedidos de ese cliente
    pedidos = Pedido.query.filter_by(ID_Cliente=cliente.ID_cliente).all()
    return render_template("clientes/seguimiento_pedido.html", pedidos=pedidos)

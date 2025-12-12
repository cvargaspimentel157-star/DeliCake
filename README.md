# 🍰 DeliCake
![Status](https://img.shields.io/badge/Estado-En%20desarrollo-yellow)
![Python](https://img.shields.io/badge/Python-3.10-pink)
![Flask](https://img.shields.io/badge/Flask-Framework-white)

**DeliCake: Plataforma de ventas en línea de productos de repostería personalizada**

---

## 2. Descripción
DeliCake es un sistema web que permite a los usuarios explorar un catálogo de productos de repostería, personalizarlos y realizar pedidos bajo demanda. La producción se realiza únicamente cuando un cliente hace un pedido, evitando el desperdicio de alimentos. 


   ![Captura de ejemplo de Delicake](static/img/logo_delicake.jpg)

---

## 3. 🚀 Características principales

- Catálogo dinámico de productos.
- Pedidos personalizados según preferencia del cliente.
- Producción bajo demanda (no se fabrican productos para exhibición).
- Interfaz amigable y visual.
- Panel para ver pedidos y estados.
- Flujo de compra claro y rápido.

---

## 4. 🛠️ Tecnologías utilizadas

### *Frontend*
- HTML5  
- CSS3  
- JavaScript (funciones interactivas)

### *Backend*
- Python 3  
- Flask (framework principal)

### *Base de datos*
- MySQL
---

## 📋 Pre-requisitos

Para ejecutar el proyecto necesitas:

- Python 3.10 o superior
- Pip
- Un navegador web
- MySQL

   ```bash
   python --version
   pip --version
---
## 5. Instalación Local (pasos para correrlo)

1. **Clonar el repositorio**
   ```bash
   git clone https://github.com/usuario/delicake.git
   cd delicake

2. **Instalar las dependencias**
   ```bash
   pip install -r requirements.txt

3. **Ejecutar la aplicacion**
   ```bash
   python app.py
4. **Abir en el navegador *
   ```bash
   https://127.0.0.1:5000/
---
## 6. 🌐 Despliegue

El proyecto **Delicake** está desplegado en **Railway**, una plataforma en la nube que permite publicar aplicaciones web usando Python y Flask.

### 🔧 ¿Cómo se realizó el despliegue en Railway?

1. Se creó una cuenta en **Railway.app**.
2. Se subió el repositorio del proyecto a **GitHub**.
3. Desde Railway se seleccionó la opción **"New Project" → "Deploy from GitHub Repo"**.
4. Se conectó Railway con el repositorio del proyecto.
5. En la configuración del servicio se definió:
   - **Build Command:**  
     `pip install -r requirements.txt`
   - **Start Command:**  
     `python app.py`  
6. Railway configuró automáticamente el entorno y generó un dominio público.
7. Cada vez que se actualiza el repositorio, Railway realiza un **deploy automático**.

### 🔗 Enlace del despliegue

👉 **Delicake en línea:**  


---
## 7. Uso 

Una vez la aplicación está en ejecución, el usuario puede navegar por las diferentes secciones del sistema.  
Desde la página principal, es posible explorar los productos disponibles, agregar artículos al carrito, realizar pedidos y verificar su estado.  
La interfaz está diseñada para ser intuitiva, rápida y fácil de usar.

### Flujo básico de uso:
1. Entrar a la página principal.
   ![Captura de ejemplo de Delicake](static/img/img.png)
2. Visualizar el catalogo de productos
   ![Captura de ejemplo de Delicake](static/img/img1.png)
3. Agregar al carrito el producto
   ![Captura de ejemplo de Delicake](static/img/img2.png)
4. Confirmar el pedido llenando la información necesaria.
   ![Captura de ejemplo de Delicake](static/img/img4.png)
5. Listo
   ![Captura de ejemplo de Delicake](static/img/img5.png)

   
---
## 8. 📚 Documentación del Proyecto

A continuación puedes consultar los documentos principales de la aplicación **Delicake**:

- 📘 **Manual de Usuario** — [Ver documento](https://drive.google.com/open?id=1pWFjozwWumGysRNY2XGQ02k8Tni37k5JmoWr1Eh9lOU&usp=drive_copy)
- 🛠️ **Manual Técnico** — [Ver documento](https://drive.google.com/file/d/1VNZufSBROMrCch0fn4eLvPCAkeeaOw0g/view?usp=sharing)
---
## 9. Autores ✒️

Este proyecto fue desarrollado por:

- **Mariana Rojas Rodriguez** 
- **Diana Lucia Ovalle Cardozo**
- **Cesar Alejandro Vargas Pimentel**
  
Participamos conjuntamente en todas las etapas del proyecto: diseño, frontend, backend, documentación, pruebas y despliegue.

#### Agradecemos el esfuerzo colaborativo del equipo para llevar este proyecto a cabo.

---
## Derechos Reservados ⚖️

Todos los archivos, imágenes y código de este proyecto son propiedad del equipo **Delicake**.  
Queda prohibida la copia, modificación, distribución o uso con fines comerciales sin autorización previa de las autoras.

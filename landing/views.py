from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.db.models import Count, Q
from django.contrib import messages
import json

from .models import Pedido, Cliente, Producto


# ─────────────────────────────────────────
#  LANDING PAGE
# ─────────────────────────────────────────

def landing(request):
    productos = Producto.objects.filter(activo=True)[:6]
    return render(request, "index.html", {"productos": productos})


# ─────────────────────────────────────────
#  RECIBIR PEDIDO (API JSON)
# ─────────────────────────────────────────

@csrf_exempt
def order(request):
    if request.method != "POST":
        return JsonResponse({"status": "error"}, status=405)

    data     = json.loads(request.body)
    nombre   = data.get("name", "").strip()
    email    = data.get("email", "").strip()
    telefono = data.get("phone", "").strip()
    producto = data.get("product", "").strip()
    mensaje  = data.get("message", "").strip()

    if not nombre or not telefono or not producto:
        return JsonResponse({"status": "error", "msg": "Faltan datos"}, status=400)

    cliente, _ = Cliente.objects.get_or_create(
        telefono=telefono,
        defaults={"nombre": nombre, "email": email}
    )

    Pedido.objects.create(
        cliente      = cliente,
        nombre       = nombre,
        email        = email,
        telefono     = telefono,
        producto_txt = producto,
        mensaje      = mensaje,
        estado       = "nuevo",
    )

    print(f"\n📦 NUEVO PEDIDO guardado:")
    print(f"  Cliente : {nombre} | Tel: {telefono}")
    print(f"  Producto: {producto}\n")

    return JsonResponse({"status": "success"})


# ─────────────────────────────────────────
#  LOGIN / LOGOUT
# ─────────────────────────────────────────

def admin_login(request):
    if request.user.is_authenticated:
        return redirect("panel_dashboard")

    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            return redirect("panel_dashboard")
        messages.error(request, "Usuario o contraseña incorrectos.")

    return render(request, "admin_panel/login.html")


def admin_logout(request):
    logout(request)
    return redirect("admin_login")


# ─────────────────────────────────────────
#  DASHBOARD
# ─────────────────────────────────────────

@login_required(login_url="admin_login")
def panel_dashboard(request):
    ctx = {
        "pedidos_nuevos":   Pedido.objects.filter(estado="nuevo").count(),
        "pedidos_enviados": Pedido.objects.filter(estado="enviado").count(),
        "contactados":      Pedido.objects.filter(estado="contactado").count(),
        "entregados":       Pedido.objects.filter(estado="entregado").count(),
        "total_clientes":   Cliente.objects.count(),
        "total_pedidos":    Pedido.objects.count(),
        "ultimos_pedidos":  Pedido.objects.select_related("cliente").order_by("-creado")[:8],
    }
    return render(request, "admin_panel/admin.html", ctx)


# ─────────────────────────────────────────
#  PEDIDOS
# ─────────────────────────────────────────

@login_required(login_url="admin_login")
def panel_pedidos(request):
    estado = request.GET.get("estado", "")
    buscar = request.GET.get("q", "")

    pedidos = Pedido.objects.select_related("cliente").all()

    if estado:
        pedidos = pedidos.filter(estado=estado)
    if buscar:
        pedidos = pedidos.filter(
            Q(nombre__icontains=buscar) |
            Q(telefono__icontains=buscar) |
            Q(producto_txt__icontains=buscar)
        )

    ctx = {
        "pedidos": pedidos,
        "estado":  estado,
        "buscar":  buscar,
        "estados": Pedido.ESTADOS,
    }
    return render(request, "admin_panel/pedidos.html", ctx)


# ─────────────────────────────────────────
#  DETALLE / EDITAR PEDIDO
# ─────────────────────────────────────────

@login_required(login_url="admin_login")
def panel_pedido_detalle(request, pk):
    pedido = get_object_or_404(Pedido, pk=pk)

    if request.method == "POST":
        pedido.estado      = request.POST.get("estado", pedido.estado)
        pedido.notas_admin = request.POST.get("notas_admin", pedido.notas_admin)
        pedido.save()
        messages.success(request, "Pedido actualizado ✅")
        return redirect("panel_pedidos")

    ctx = {"pedido": pedido, "estados": Pedido.ESTADOS}
    return render(request, "admin_panel/pedido_detalle.html", ctx)


# ─────────────────────────────────────────
#  CLIENTES
# ─────────────────────────────────────────

@login_required(login_url="admin_login")
def panel_clientes(request):
    buscar   = request.GET.get("q", "")
    clientes = Cliente.objects.annotate(num_pedidos=Count("pedidos")).order_by("-creado")

    if buscar:
        clientes = clientes.filter(
            Q(nombre__icontains=buscar) |
            Q(telefono__icontains=buscar)
        )

    ctx = {"clientes": clientes, "buscar": buscar}
    return render(request, "admin_panel/clientes.html", ctx)


# ─────────────────────────────────────────
#  INVENTARIO / PRODUCTOS
# ─────────────────────────────────────────

@login_required(login_url="admin_login")
def panel_productos(request):
    productos = Producto.objects.all()
    return render(request, "admin_panel/productos.html", {"productos": productos})


@login_required(login_url="admin_login")
def panel_producto_editar(request, pk=None):
    producto = get_object_or_404(Producto, pk=pk) if pk else None

    if request.method == "POST":
        nombre      = request.POST.get("nombre", "").strip()
        categoria   = request.POST.get("categoria", "otro")
        descripcion = request.POST.get("descripcion", "")
        precio      = int(request.POST.get("precio", 0) or 0)
        precio_old  = request.POST.get("precio_old") or None
        stock       = int(request.POST.get("stock", 0) or 0)
        activo      = request.POST.get("activo") == "on"
        destacado   = request.POST.get("destacado") == "on"
        imagen      = request.FILES.get("imagen")

        if producto:
            producto.nombre      = nombre
            producto.categoria   = categoria
            producto.descripcion = descripcion
            producto.precio      = precio
            producto.precio_old  = int(precio_old) if precio_old else None
            producto.stock       = stock
            producto.activo      = activo
            producto.destacado   = destacado
            if imagen:
                producto.imagen  = imagen
            producto.save()
            messages.success(request, "Producto actualizado ✅")
        else:
            nuevo = Producto(
                nombre      = nombre,
                categoria   = categoria,
                descripcion = descripcion,
                precio      = precio,
                precio_old  = int(precio_old) if precio_old else None,
                stock       = stock,
                activo      = activo,
                destacado   = destacado,
            )
            if imagen:
                nuevo.imagen = imagen
            nuevo.save()
            messages.success(request, "Producto creado ✅")

        return redirect("panel_productos")

    ctx = {"producto": producto, "categorias": Producto.CATEGORIAS}
    return render(request, "admin_panel/producto_form.html", ctx)
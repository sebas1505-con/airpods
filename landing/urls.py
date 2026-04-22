from django.urls import path
from . import views

urlpatterns = [
    # ── Landing pública ──────────────────────────
    path("",        views.landing, name="landing"),
    path("order/",  views.order,   name="order"),
    path("panel/login/",  views.admin_login,  name="admin_login"),
    path("panel/logout/", views.admin_logout, name="admin_logout"),
    path("panel/",                          views.panel_dashboard,       name="panel_dashboard"),
    path("panel/pedidos/",                  views.panel_pedidos,         name="panel_pedidos"),
    path("panel/pedidos/<int:pk>/",         views.panel_pedido_detalle,  name="panel_pedido_detalle"),
    path("panel/clientes/",                 views.panel_clientes,        name="panel_clientes"),
    path("panel/productos/",                views.panel_productos,       name="panel_productos"),
    path("panel/productos/nuevo/",          views.panel_producto_editar, name="panel_producto_nuevo"),
    path("panel/productos/<int:pk>/editar/",views.panel_producto_editar, name="panel_producto_editar"),
]
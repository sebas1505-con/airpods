from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
 
 
def landing(request):
    return render(request, "index.html")
 
 
@csrf_exempt
def order(request):
    if request.method == "POST":
        data = json.loads(request.body)
        print(f"\n📦 NUEVO PEDIDO — Usados Importados:")
        print(f"  Cliente : {data.get('name')}")
        print(f"  Email   : {data.get('email')}")
        print(f"  Teléfono: {data.get('phone')}")
        print(f"  Producto: {data.get('product')}")
        print(f"  Mensaje : {data.get('message', 'N/A')}\n")
        return JsonResponse({"status": "success"})
    return JsonResponse({"status": "error"}, status=405)
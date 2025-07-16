from prettytable import PrettyTable
from datetime import datetime
import random
from tqdm import tqdm
import time

def listar_productos_usuario(db): #--tabla para ver los productos D:
    barra_carga("Cargando productos")
    productos = db["productos"]
    pipeline = [
        {"$project": {"_id": 0, "id_producto": 1, "nombre": 1, "descripcion": 1, "precio": 1}}
    ]

    resultados = productos.aggregate(pipeline)
    table = PrettyTable()
    table.field_names = ["ID Producto", "Nombre", "Descripción", "Precio"]

    for prod in resultados:
        table.add_row([
            prod.get("id_producto", "N/A"),
            prod.get("nombre", "N/A"),
            prod.get("descripcion", "N/A"),
            f"${prod.get('precio', 0)}"
        ])

    print("\n--- Lista de Productos ---")
    print(table)

def generar_id_solicitud(reembolsos):  #--ciclo random id_soli
    while True:
        numero = random.randint(1, 99)
        nuevo_id = f"A{numero:02d}"
        if not reembolsos.find_one({"id_solicitud": nuevo_id}):
            return nuevo_id



def crear_solicitud(db, correo_usuario): 
    listar_productos_usuario(db)
    reembolsos = db["reembolsos"]
    productos = db["productos"]

    id_producto = input("Ingrese ID del producto para crear la solicitud: ").strip()
    producto = productos.find_one({"id_producto": id_producto})

    if not producto:
        print(f"No existe el producto con ID '{id_producto}'")
        return

    id_solicitud = generar_id_solicitud(reembolsos)
    descripcion_fallo = input("Describa el fallo del producto: ").strip()

    print("\nSeleccione el tipo de daño:")
    for clave, valor in tipos_dano.items():
        print(f"{clave}. {valor}")

    tipo_dano = ""
    while True:
        opcion = input(f"Opción (1-{len(tipos_dano)}): ").strip()
        if opcion in tipos_dano:
            tipo_dano = tipos_dano[opcion]
            break
        else:
            print("Opcion inválida intente nuevamente")

    opciones_pago = {"EFECTIVO", "DEBITO", "CREDITO"}
    while True:
        medio_pago = input("Ingrese medio de pago usado (Efectivo/Debito/Credito): ").strip().upper()
        if medio_pago in opciones_pago:
            break
        else:
            print("Opcion invalida debe ser EFECTIVO, DEBITO o CREDITO")

    costo_producto = producto.get("precio", 0)
    fecha_solicitud = datetime.now()

    barra_carga("Creando solicitud")

    nueva_solicitud = {
        "id_solicitud": id_solicitud,
        "correo_usuario": correo_usuario,
        "id_producto": id_producto,
        "nombre": producto.get("nombre", ""),
        "descripcion_fallo": descripcion_fallo,
        "tipo_dano": tipo_dano,
        "medio_pago": medio_pago,
        "costo_producto": costo_producto,
        "estado": "pendiente",
        "fecha_solicitud": fecha_solicitud
    }

    reembolsos.insert_one(nueva_solicitud)
    print(f"Solicitud de reembolso creada exitosamente con ID: {id_solicitud}")



def listar_solicitudes_usuario(db, correo_usuario):  # --tabla para ver las solis D:
    barra_carga("Buscando solicitudes")
    reembolsos = db["reembolsos"]
    pipeline = [
        {"$match": {"correo_usuario": correo_usuario}},
        {
            "$project": {
                "_id": 0,
                "id_solicitud": 1,
                "id_producto": 1,
                "nombre": 1,
                "descripcion_fallo": 1,
                "tipo_dano": 1,  
                "costo_producto": 1,
                "medio_pago": 1,
                "estado": 1,
                "fecha_solicitud": 1
            }
        }
    ]

    solicitudes = reembolsos.aggregate(pipeline)

    table = PrettyTable()
    table.field_names = [
        "ID Solicitud",
        "ID Producto",
        "Nombre",
        "Descripción Fallo",
        "Tipo Daño",  
        "Costo",
        "Medio Pago",
        "Estado",
        "Fecha Solicitud"
    ]

    for sol in solicitudes:
        fecha_str = sol.get("fecha_solicitud")
        if fecha_str:
            fecha_str = fecha_str.strftime("%Y-%m-%d")
        else:
            fecha_str = "N/A"

        table.add_row([
            sol.get("id_solicitud", "N/A"),
            sol.get("id_producto", "N/A"),
            sol.get("nombre", "N/A"),
            sol.get("descripcion_fallo", "N/A"),
            sol.get("tipo_dano", "N/A"),  
            f"${sol.get('costo_producto', 0)}",
            sol.get("medio_pago", "N/A"),
            sol.get("estado", "N/A"),
            fecha_str
        ])

    print("\n--- Mis Solicitudes de Reembolso ---")
    print(table)


def ver_solicitudes_aceptadas(db, correo_usuario):  # --tabla para ver las solis aceptadas D:
    reembolsos = db["reembolsos"]
    barra_carga("Consultando solicitudes aceptadas")

    pipeline = [
        {
            "$match": {
                "correo_usuario": correo_usuario,
                "estado": "aceptado"
            }
        },
        {
            "$project": {
                "_id": 0,
                "id_solicitud": 1,
                "id_producto": 1,
                "nombre": 1,
                "descripcion_fallo": 1,
                "tipo_dano": 1,  
                "medio_pago": 1,
                "costo_producto": 1,
                "fecha_solicitud": 1
            }
        }
    ]

    resultados = reembolsos.aggregate(pipeline)

    table = PrettyTable()
    table.field_names = [
        "ID Solicitud",
        "ID Producto",
        "Nombre",
        "Fallo",
        "Tipo Daño",  
        "Medio Pago",
        "Costo",
        "Fecha"
    ]

    encontrados = False
    for sol in resultados:
        encontrados = True
        fecha = sol.get("fecha_solicitud")
        fecha_str = fecha.strftime("%Y-%m-%d") if fecha else "N/A"
        table.add_row([
            sol.get("id_solicitud", "N/A"),
            sol.get("id_producto", "N/A"),
            sol.get("nombre", "N/A"),
            sol.get("descripcion_fallo", "N/A"),
            sol.get("tipo_dano", "N/A"),  
            sol.get("medio_pago", "N/A"),
            f"${sol.get('costo_producto', 0)}",
            fecha_str
        ])

    print("\n--- Solicitudes Aceptadas ---")
    if encontrados:
        print(table)
    else:
        print("No tienes solicitudes aceptadas aun")

def eliminar_solicitud_usuario(db, correo_usuario):
    id_solicitud = input("Ingrese el ID de la solicitud que desea eliminar: ").strip()
    reembolsos = db["reembolsos"]

 
    pipeline = [
        {
            "$match": {
                "id_solicitud": id_solicitud,
                "correo_usuario": correo_usuario
            }
        },
        {
            "$project": {
                "_id": 0,
                "estado": 1
            }
        }
    ]
    resultado = list(reembolsos.aggregate(pipeline))

    if not resultado:
        print("No se encontro una solicitud con ese ID para tu usuario")
        return

    estado = resultado[0]["estado"]
    if estado == "aceptado":
        print("No puedes eliminar una solicitud que ya fue aceptada")
        return

    barra_carga("Eliminando solicitud...")

    result = reembolsos.delete_one({
        "id_solicitud": id_solicitud,
        "correo_usuario": correo_usuario
    })

    if result.deleted_count:
        print(f"Solicitud {id_solicitud} eliminada exitosamente")
    else:
        print("Ocurrio un error al intentar eliminar la solicitud")



def barra_carga(texto="Procesando", pasos=100):
    tiempo_sleep = 2 / pasos 
    for _ in tqdm(range(pasos), desc=texto, ncols=70, bar_format='{l_bar}{bar}| {n_fmt}/{total_fmt}'):
        time.sleep(tiempo_sleep)



tipos_dano = { #--menu para tipo de dañoxd
    "1": "Fallo eléctrico",
    "2": "Daño físico",
    "3": "No enciende",
    "4": "Mal funcionamiento general",
    "5": "Pantalla rota",
    "6": "Problemas de batería",
    "7": "Sobrecalentamiento",
    "8": "Problemas de software",
    "9": "Conectividad fallida",
    "10": "Ruido anormal",
    "11": "Fallo mecánico",
    "12": "Desgaste por uso",
    "13": "Daño por agua",
    "14": "Botones dañados",
    "15": "Problemas de cámara"
}
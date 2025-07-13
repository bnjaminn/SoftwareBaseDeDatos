from datetime import datetime
from prettytable import PrettyTable
from tqdm import tqdm
import time


def listar_usuarios(db):
    barra_carga("Cargando usuarios")
    usuarios = db["usuarios"]
    pipeline = [
        {"$match": {"rol": "cliente"}},
        {"$project": {"_id": 0, "correo": 1, "rol": 1}}
    ]
    clientes = usuarios.aggregate(pipeline)

    table = PrettyTable()
    table.field_names = ["Correo", "Rol"]

    for cliente in clientes:
        table.add_row([cliente["correo"], cliente["rol"]])

    print("\n--- Lista de Clientes ---")
    print(table)

def ver_solicitudes(db, filtro=None):
    barra_carga("Consultando solicitudes")
    reembolsos = db["reembolsos"]
    fecha_captada = {}
    if filtro:
        if "fecha" in filtro:
            fecha_inicio = datetime.strptime(filtro["fecha"], "%Y-%m")
            if fecha_inicio.month == 12:
                fecha_fin = datetime(fecha_inicio.year + 1, 1, 1)
            else:
                fecha_fin = datetime(fecha_inicio.year, fecha_inicio.month + 1, 1)
            fecha_captada["fecha_solicitud"] = {"$gte": fecha_inicio, "$lt": fecha_fin}
        elif "id_producto" in filtro:
            fecha_captada["id_producto"] = filtro["id_producto"]

    pipeline = []
    if fecha_captada:
        pipeline.append({"$match": fecha_captada})

    pipeline.append({
        "$project": {
            "_id": 0,
            "id_solicitud": 1,
            "id_producto": 1,
            "nombre": 1,
            "descripcion_fallo": 1,
            "costo_producto": 1,
            "medio_pago": 1,
            "estado": 1,
            "fecha_solicitud": 1
        }
    })

    resultados = reembolsos.aggregate(pipeline)

    table = PrettyTable()
    table.field_names = ["ID Solicitud", "ID Producto", "Nombre", "Descripción Fallo", "Costo", "Medio Pago", "Estado", "Fecha Solicitud"]

    for sol in resultados:
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
            f"${sol.get('costo_producto', 0)}",
            sol.get("medio_pago", "N/A"),
            sol.get("estado", "N/A"),
            fecha_str
        ])

    print("\n--- Solicitudes de Reembolso ---")
    print(table)

def aceptar_solicitud(db, id_solicitud):
    reembolsos = db["reembolsos"]
    barra_carga(f"Aceptando solicitud {id_solicitud}")
    result = reembolsos.update_one(
        {"id_solicitud": id_solicitud, "estado": "pendiente"},
        {"$set": {"estado": "aceptado"}}
    )
    if result.modified_count:
        print(f"Solicitud {id_solicitud} aceptada")
    else:
        print(f"No se encontró solicitud pendiente con ID {id_solicitud}")

def rechazar_solicitud(db, id_solicitud):
    reembolsos = db["reembolsos"]
    barra_carga(f"Rechazando solicitud {id_solicitud}")
    result = reembolsos.update_one(
        {"id_solicitud": id_solicitud, "estado": "pendiente"},
        {"$set": {"estado": "rechazado"}}
    )
    if result.modified_count:
        print(f"Solicitud {id_solicitud} rechazada.")
    else:
        print(f"No se encontró solicitud pendiente con ID {id_solicitud}")

def eliminar_solicitud(db, id_solicitud):
    reembolsos = db["reembolsos"]
    barra_carga(f"Eliminando solicitud {id_solicitud}")
    result = reembolsos.delete_one({"id_solicitud": id_solicitud})
    if result.deleted_count:
        print(f"Solicitud {id_solicitud} eliminada")
    else:
        print(f"No se encontró solicitud con ID {id_solicitud}")

def listar_productos_admin(db):
    barra_carga("Listando productos")
    productos = db["productos"]
    pipeline = [
        {"$project": {"_id": 0, "id_producto": 1, "nombre": 1, "descripcion": 1, "precio": 1}}
    ]

    resultados = productos.aggregate(pipeline)
    table = PrettyTable()
    table.field_names = ["ID Producto", "Nombre", "Descripción", "Precio"]

    for prod in resultados:
        table.add_row([prod["id_producto"], prod["nombre"], prod["descripcion"], f"${prod['precio']}"])

    print("\n--- Lista de Productos ---")
    print(table)

def contar_solis(db):
    reembolsos = db["reembolsos"]
    barra_carga("Generando estadísticas")
    pipeline = [
        {
            "$group": {
                "_id": "$id_producto",
                "total_solicitudes": {"$sum": 1},
                "costo_total": {"$sum": "$costo_producto"},
                "costo_promedio": {"$avg": "$costo_producto"}
            }
        },
        {"$sort": {"total_solicitudes": -1}}
    ]

    resultados = reembolsos.aggregate(pipeline)

    table = PrettyTable()
    table.field_names = ["ID Producto", "Total Solicitudes", "Costo Total", "Costo Promedio"]

    for doc in resultados:
        table.add_row([
            doc["_id"],
            doc["total_solicitudes"],
            f"${doc['costo_total']:.2f}",
            f"${doc['costo_promedio']:.2f}"
        ])

    print("\n--- Estadísticas de Reembolsos por Producto ---")
    print(table)

def barra_carga(texto="Procesando", pasos=100):
    tiempo_sleep = 2 / pasos 
    for _ in tqdm(range(pasos), desc=texto, ncols=70, bar_format='{l_bar}{bar}| {n_fmt}/{total_fmt}'):
        time.sleep(tiempo_sleep)
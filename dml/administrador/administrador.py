from datetime import datetime
from prettytable import PrettyTable
from tqdm import tqdm
import time


def listar_usuarios(db):  # --tabla para ver a los usuarios D:
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


def ver_solicitudes(db, filtro=None, tipos_dano=None):
    if filtro is None:
        filtro = None
        filtro_opcional = input("¿Filtrar solicitudes? escriba 1 para mes, 2 para producto, 3 para tipo de daño o enter para ver todas: ")
        if filtro_opcional == "1":
            mes = input("Ingrese mes y año (YYYY-MM): ")
            filtro = {"fecha": mes}
        elif filtro_opcional == "2":
            listar_productos_admin(db)
            id_prod = input("Ingrese id_producto: ")
            filtro = {"id_producto": id_prod}
        elif filtro_opcional == "3":
            if tipos_dano is None:
                tipos_dano = {
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
            print("\nSeleccione el tipo de daño:")
            for clave, valor in tipos_dano.items():
                print(f"{clave}. {valor}")
            while True:
                opcion_dano = input(f"Opción (1-{len(tipos_dano)}): ").strip()
                if opcion_dano in tipos_dano:
                    filtro = {"tipo_dano": tipos_dano[opcion_dano]}
                    break
                else:
                    print("Opcion invalida intente nuevamente")
                    
    fecha_captada = {}
    if filtro:
        if "fecha" in filtro:
            from datetime import datetime
            fecha_inicio = datetime.strptime(filtro["fecha"], "%Y-%m")
            if fecha_inicio.month == 12:
                fecha_fin = datetime(fecha_inicio.year + 1, 1, 1)
            else:
                fecha_fin = datetime(fecha_inicio.year, fecha_inicio.month + 1, 1)
            fecha_captada["fecha_solicitud"] = {"$gte": fecha_inicio, "$lt": fecha_fin}
        elif "id_producto" in filtro:
            fecha_captada["id_producto"] = filtro["id_producto"]
        elif "tipo_dano" in filtro:
            fecha_captada["tipo_dano"] = filtro["tipo_dano"]

    barra_carga("Consultando solicitudes")

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
            "tipo_dano": 1,
            "costo_producto": 1,
            "medio_pago": 1,
            "estado": 1,
            "fecha_solicitud": 1
        }
    })

    resultados = db["reembolsos"].aggregate(pipeline)

    from prettytable import PrettyTable
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
            sol.get("tipo_dano", "N/A"),
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


def listar_productos_admin(db):  # --tabla para ver los productos D:
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


def contar_solis(db):  # --tabla contar las solicitudes D:
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


def contar_por_medio_pago(db):
    reembolsos = db["reembolsos"]
    barra_carga("Calculando medios de pago")

    pipeline = [
        {
            "$group": {
                "_id": "$medio_pago",
                "total_solicitudes": {"$sum": 1},
                "costo_promedio": {"$avg": "$costo_producto"}
            }
        },
        {"$sort": {"total_solicitudes": -1}}
    ]

    resultados = reembolsos.aggregate(pipeline)
    tabla = PrettyTable()
    tabla.field_names = ["Medio de Pago", "Total Solicitudes", "Costo Promedio"]

    for r in resultados:
        tabla.add_row([
            r["_id"],
            r["total_solicitudes"],
            f"${r['costo_promedio']:.2f}"
        ])

    print("\n--- Solicitudes por Medio de Pago ---")
    print(tabla)


def ver_clientes_frecuentes(db):
    reembolsos = db["reembolsos"]
    barra_carga("Buscando clientes frecuentes")

    pipeline = [
        {
            "$group": {
                "_id": "$correo_usuario",
                "total_solicitudes": {"$sum": 1},
                "total_gastado": {"$sum": "$costo_producto"}
            }
        },
        {"$sort": {"total_solicitudes": -1}},
        {"$limit": 5}
    ]

    resultados = reembolsos.aggregate(pipeline)
    tabla = PrettyTable()
    tabla.field_names = ["Correo Cliente", "Solicitudes", "Total Gastado"]

    for r in resultados:
        tabla.add_row([
            r["_id"],
            r["total_solicitudes"],
            f"${r['total_gastado']:.2f}"
        ])

    print("\n--- Top 5 Clientes con Más Solicitudes ---")
    print(tabla)


def filtro_personalizado(db):
    from datetime import datetime
    from prettytable import PrettyTable

    barra_carga("Preparando filtros")

    tipos_dano = {
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

    match_filter = {}

    
    mes = input("\nIngrese el mes y año (YYYY-MM) o presione enter para omitir: ").strip()
    dia = input("Ingrese el día (DD) o presione enter para omitir: ").strip()

    if mes:
        try:
            fecha_inicio = datetime.strptime(mes, "%Y-%m")
            if dia:
                fecha_inicio = datetime.strptime(f"{mes}-{dia}", "%Y-%m-%d")
                fecha_fin = fecha_inicio.replace(hour=23, minute=59, second=59)
            else:
                if fecha_inicio.month == 12:
                    fecha_fin = datetime(fecha_inicio.year + 1, 1, 1)
                else:
                    fecha_fin = datetime(fecha_inicio.year, fecha_inicio.month + 1, 1)
            match_filter["fecha_solicitud"] = {"$gte": fecha_inicio, "$lt": fecha_fin}
        except ValueError:
            print("⚠️ Fecha no válida. Se omitirá el filtro de fecha.")

    
    print("\n--- Lista de Productos Disponibles ---")
    listar_productos_admin(db)
    id_producto = input("Ingrese el ID del producto o presione enter para omitir: ").strip()
    if id_producto:
        match_filter["id_producto"] = id_producto

    
    print("\n--- Tipos de Daño Disponibles ---")
    for clave, valor in tipos_dano.items():
        print(f"{clave}. {valor}")
    tipo_dano_opcion = input("Ingrese número del tipo de daño o presione enter para omitir: ").strip()
    if tipo_dano_opcion in tipos_dano:
        match_filter["tipo_dano"] = tipos_dano[tipo_dano_opcion]

    barra_carga("Consultando con filtros personalizados")

    
    pipeline = []
    if match_filter:
        pipeline.append({"$match": match_filter})

    pipeline.append({
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
    })

    resultados = db["reembolsos"].aggregate(pipeline)

    
    tabla = PrettyTable()
    tabla.field_names = [
        "ID Solicitud", "ID Producto", "Nombre", "Descripción Fallo",
        "Tipo Daño", "Costo", "Medio Pago", "Estado", "Fecha Solicitud"
    ]

    encontrados = False
    for doc in resultados:
        encontrados = True
        fecha_str = doc.get("fecha_solicitud")
        fecha_str = fecha_str.strftime("%Y-%m-%d") if fecha_str else "N/A"
        tabla.add_row([
            doc.get("id_solicitud", "N/A"),
            doc.get("id_producto", "N/A"),
            doc.get("nombre", "N/A"),
            doc.get("descripcion_fallo", "N/A"),
            doc.get("tipo_dano", "N/A"),
            f"${doc.get('costo_producto', 0)}",
            doc.get("medio_pago", "N/A"),
            doc.get("estado", "N/A"),
            fecha_str
        ])

    print("\n--- Resultados del Filtro Personalizado ---")
    if encontrados:
        print(tabla)
    else:
        print("No se encontraron resultados con los filtros seleccionados.")



def barra_carga(texto="Procesando", pasos=100):
    tiempo_sleep = 2 / pasos
    for _ in tqdm(range(pasos), desc=texto, ncols=70, bar_format='{l_bar}{bar}| {n_fmt}/{total_fmt}'):
        time.sleep(tiempo_sleep)

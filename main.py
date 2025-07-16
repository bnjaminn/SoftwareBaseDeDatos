#Integrantes: Benjamin Bravo, Carolina Olguin
#Carrera: Analista Programador
#Depedencias a instalar (IMPORTANTE INSTALAR POR FAVOR INSTALAR PARA CORRECTO FUNCIONAMIENTO): pip install pymongo, pip install prettytable, pip install tqdm
from conexion import obtener_conexion
from prettytable import PrettyTable
from tqdm import tqdm
import time
from inicio_sesion import iniciar_sesion, registrar_cliente
from menu import menu_principal, menu_administrador, menu_cliente
from dml.administrador.administrador import (listar_usuarios, ver_solicitudes, aceptar_solicitud,  rechazar_solicitud, eliminar_solicitud, listar_productos_admin, contar_solis, contar_por_medio_pago, ver_clientes_frecuentes, filtro_personalizado, eliminar_usuario, agregar_producto, actualizar_producto)
from dml.usuario.usuario import (crear_solicitud, listar_solicitudes_usuario, ver_solicitudes_aceptadas, eliminar_solicitud_usuario)

def main():
    db = obtener_conexion()

    while True:
        menu_principal()
        opcion = input("Elige una opción: ")

        #----------------inicio opciones generales-------------------------
        if opcion == "1":
            usuario = iniciar_sesion(db)
            if usuario is None:
                continue

            #----------------opciones administrador-------------------------
            if usuario["rol"] == "administrador":
                while True:
                    menu_administrador()
                    admin_opcion = input("Elige una opción: ")

                    if admin_opcion == "0":
                        break
                    elif admin_opcion == "1":
                        listar_usuarios(db)
                    elif admin_opcion == "2":
                        ver_solicitudes(db)
                    elif admin_opcion == "3":
                        id_solicitud = input("Ingrese id_solicitud para aceptar: ")
                        aceptar_solicitud(db, id_solicitud)
                    elif admin_opcion == "4":
                        id_solicitud = input("Ingrese id_solicitud para rechazar: ")
                        rechazar_solicitud(db, id_solicitud)
                    elif admin_opcion == "5":
                        id_solicitud = input("Ingrese id_solicitud para eliminar: ")
                        eliminar_solicitud(db, id_solicitud)
                    elif admin_opcion == "6":
                        contar_solis(db)
                    elif admin_opcion == "7":
                        contar_por_medio_pago(db)
                    elif admin_opcion == "8":
                        ver_clientes_frecuentes(db)  
                    elif admin_opcion == "9":
                        filtro_personalizado(db)
                    elif admin_opcion == "10":
                        eliminar_usuario(db)
                    elif admin_opcion == "11":
                        listar_productos_admin(db)
                    elif admin_opcion == "12":
                        agregar_producto(db)
                    elif admin_opcion == "13":
                        actualizar_producto(db)
                    else:
                        print("Opcion invalida")

            #----------------opciones cliente-------------------------
            elif usuario["rol"] == "cliente":
                while True:
                    menu_cliente()
                    cliente_opcion = input("Elige una opción: ")

                    if cliente_opcion == "0":
                        break
                    elif cliente_opcion == "1":
                        crear_solicitud(db, usuario["correo"])
                    elif cliente_opcion == "2":
                        listar_solicitudes_usuario(db, usuario["correo"])
                    elif cliente_opcion == "3":
                        ver_solicitudes_aceptadas(db, usuario["correo"])
                    elif cliente_opcion == "4":
                        eliminar_solicitud_usuario(db, usuario["correo"])
                    else:
                        print("Opcion invalida")

            else:
                print("Rol no reconocido")

        elif opcion == "2":
            registrar_cliente(db)

        elif opcion == "0":
            print("Cerrando programa")
            break

        else:
            print("Opcion no válida.")

if __name__ == "__main__":
    main()

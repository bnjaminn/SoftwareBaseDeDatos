from pymongo import MongoClient

def obtener_conexion():
    cliente = MongoClient("mongodb://localhost:27017/")
    db = cliente["sistema_reembolsos"]
    return db


if __name__ == "__main__":
    db = obtener_conexion()
    usuarios = db["usuarios"]
    productos = db["productos"]
    reembolsos = db["reembolsos"]

    print("Conexión establecida")

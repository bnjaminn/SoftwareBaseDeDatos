from tqdm import tqdm
import time

def iniciar_sesion(db):
    correo = input("Correo: ").strip()
    contrasena = input("Contraseña: ").strip()

    pipeline = [
        {"$match": {"correo": correo}},
        {"$project": {"_id": 0, "correo": 1, "contrasena": 1, "rol": 1}}
    ]

    resultado = list(db["usuarios"].aggregate(pipeline))

    if not resultado:
        print("Usuario no encontrado")
        return None

    usuario = resultado[0]

    if usuario["contrasena"] != contrasena:
        print("Contraseña incorrecta")
        return None

    animacion()
    print(f"Bienvenido {usuario['correo']}! Rol: {usuario['rol']}")
    return usuario

def registrar_cliente(db):
    correo = input("Correo: ").strip()

    pipeline = [
        {"$match": {"correo": correo}},
        {"$project": {"_id": 0, "correo": 1}}
    ]

    existente = list(db["usuarios"].aggregate(pipeline))
    if existente:
        print("Ya existe una cuenta con ese correo")
        return

    contrasena = input("Contraseña: ").strip()

    nuevo_usuario = {
        "correo": correo,
        "contrasena": contrasena,
        "rol": "cliente"
    }

    db["usuarios"].insert_one(nuevo_usuario)

    animacion("Registrando cliente")
    print("Cliente registrado con éxito")


def animacion(texto="Accediendo al sistema", pasos=100, velocidad=0.02):
    for _ in tqdm(range(pasos), desc=texto, ncols=70, bar_format='{l_bar}{bar}| {n_fmt}/{total_fmt}'):
        time.sleep(velocidad)
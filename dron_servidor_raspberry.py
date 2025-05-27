import socket
import threading

# listas de clientes: usuarios y drones
clientes_usuarios = []
clientes_drones   = []

def manejar_usuario(conn, addr):
    print(f"[USUARIO CONECTADO] {addr}")
    clientes_usuarios.append(conn)
    try:
        # Aviso si ya hay drones conectados
        if clientes_drones:
            for _, nombre_dron in clientes_drones:
                conn.send(f"Dron disponible: {nombre_dron}\n".encode())
        else:
            conn.send("No hay drones disponibles actualmente\n".encode())

        while True:
            data = conn.recv(1024)
            if not data:
                break
            
            # mensaje recibido de cliente usuario
            mensaje = data.decode().strip()
            print(f"Recibido de Usuario {addr}: {mensaje}")
    except:
        # print("### Excepcion en servidor --> manejar_usuario ###")
        pass
    finally:
        print(f"[USUARIO DESCONECTADO] {addr}")
        clientes_usuarios.remove(conn)
        conn.close()

def manejar_dron(conn, addr):
    print(f"[DRON CONECTADO] {addr}")
    clientes_drones.append((conn, addr))
    try:
        conn.send("Nombre del dron:\n".encode())
        nombre_dron = conn.recv(1024).decode().strip()
        
        # Aviso a todos los usuarios que se conectó un nuevo dron
        for usuario in clientes_usuarios:
            usuario.send(f"Nuevo dron conectado: {nombre_dron}\n".encode())

        while True:
            data = conn.recv(1024)
            if not data:
                break      
    except:
        # print("### Excepcion en servidor --> manejar_dron ###")
        pass
    finally:
        print(f"[DRON DESCONECTADO] {addr}")
        try:
            for usuario in clientes_usuarios:
                usuario.send(f"El dron '{addr}' se ha desconectado. . .\n".encode())
        except:
            pass
        clientes_drones.remove((conn, addr))
        conn.close()

def manejar_cliente(conn, addr):
    try:
        rol = conn.recv(1024).decode().strip()
        print(f"[ROL] {rol} desde {addr}")
        if rol == "usuario":
            manejar_usuario(conn, addr)
        elif rol == "dron":
            manejar_dron(conn, addr)
        else:
            conn.send("Rol desconocido\n".encode())
            conn.close()
    except:
        conn.close()

def iniciar_servidor():
    host = '127.0.0.1'
    puerto = 5555
    servidor = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    servidor.bind((host, puerto))
    servidor.listen()
    print(f"[ESCUCHANDO] Servidor en {host}:{puerto}")

    while True:
        conn, addr = servidor.accept()
        thread = threading.Thread(target=manejar_cliente, args=(conn, addr))
        thread.start()

if __name__ == "__main__":
    iniciar_servidor()


import socket

# Creo el cliente y lo conecto al servidor
cliente = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
cliente.connect(("127.0.0.1", 5555))

# Envío rol del dron
cliente.sendall("dron\n".encode())

# El dron se queda conectado
try:
    while True:
        pass
except KeyboardInterrupt:
    cliente.close()

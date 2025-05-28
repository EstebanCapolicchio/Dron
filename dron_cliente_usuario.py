import socket
import threading
import tkinter as tk
from tkinter import scrolledtext

class ClienteUsuarioGUI:
    # Creo la interfaz de usuario
    def __init__(self, master):
        self.master = master
        master.title("Cliente Usuario - Control de Drones")

        # Área para mostrar mensajes
        self.chat_area = scrolledtext.ScrolledText(master, wrap=tk.WORD, width=50, height=15, state='disabled')
        self.chat_area.pack(padx=10, pady=10)

        # Área de botones
        self.boton_frame = tk.Frame(self.master)
        self.boton_frame.pack(pady=20)

        # Diccionario de botones
        self.botones_gui = {}

        # Botones: sus nombres y sus acciones
        botones = [
            ("Avanzar",         lambda: self.enviar_orden("--> Av"),  (1,4)),
            ("Retroceder",      lambda: self.enviar_orden("<-- Re"),  (3,4)),
            ("Subir",           lambda: self.enviar_orden(" A  Sub"), (1,1)),
            ("Bajar",           lambda: self.enviar_orden(" V  Ab"),  (2,1)),
            ("Giro Izquierda",  lambda: self.enviar_orden("--A G_I"), (1,3)),
            ("Giro Derecha",    lambda: self.enviar_orden("--V G_D"), (1,5)),
        ]

        # En diccionario de botones, agregar los botones
        for texto, comando, (fila, columna) in botones:
            btn = tk.Button(self.boton_frame, text=texto, width=18, command=comando)

            btn.grid(row=fila, column=columna, padx=5, pady=5)

            self.botones_gui[texto] = (btn, comando)

        # Asocio teclas a botones y sus respectivas funciones
        self.master.bind("<Up>", lambda e: self.presionar_boton("Avanzar"))
        self.master.bind("<Down>", lambda e: self.presionar_boton("Retroceder"))
        self.master.bind("<w>", lambda e: self.presionar_boton("Subir"))
        self.master.bind("<s>", lambda e: self.presionar_boton("Bajar"))
        self.master.bind("<Left>", lambda e: self.presionar_boton("Giro Izquierda"))
        self.master.bind("<Right>", lambda e: self.presionar_boton("Giro Derecha"))
        
        self.master.focus_set() # Asegura foco para recibir eventos de teclado

        # Conecto el usuario al servidor
        self.conectado = False # Sirve como variable logica para determinar si está conectado al servidor
        self.cliente = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            self.cliente.connect(("127.0.0.1", 5555))
            self.cliente.sendall("usuario\n".encode())
            self.conectado = True
        except Exception as e:
            self.escribir_mensaje(f"[ERROR] No se pudo conectar al servidor: {e}")
            self.conectado = False
            return

        # Inicio hilo para escuchar mensajes del servidor
        self.escuchar_thread = threading.Thread(target=self.escuchar_servidor, daemon=True)
        self.escuchar_thread.start()

    # Presionar botones hace que se desencadenen acciones
    def presionar_boton(self, nombre):
        if nombre in self.botones_gui:
            btn, comando = self.botones_gui[nombre]
            btn.config(relief=tk.SUNKEN, bg="lightblue")
            try:
                comando()
            except Exception as e:
                print("## EXCEPCION --> dron_cliente_usuario --> presionar_boton ##")

            self.master.after(60, lambda: btn.config(relief=tk.RAISED, bg="SystemButtonFace")) # Latencia del botón
            # (no estoy 100% seguro pero el el primer parametro cuando estaba en 100
            #  me iba lento la velocidad de los mensajes de los botones)

    # Enviar ordenes hacia el servidor para que lo reenvie al dron 
    def enviar_orden(self, mensaje):
        try:
            if self.conectado:
                threading.Thread(target=lambda: self.cliente.sendall(mensaje.encode()), daemon=True).start()
            else:
                print("*NO CONECTANDO* pero - "+mensaje+" -")
        except Exception as e:
            print("## EXCEPCION --> dron_cliente_usuario --> enviar_orden ##")

    # Escribir mensajes en la pantalla
    def escribir_mensaje(self, mensaje):
        self.chat_area.config(state='normal')
        self.chat_area.insert(tk.END, mensaje + "\n")
        self.chat_area.config(state='disabled')
        self.chat_area.yview(tk.END)

    # Escuchar mensajes del servidor
    def escuchar_servidor(self):
        while True:
            try:
                mensaje = self.cliente.recv(1024).decode()
                if not mensaje:
                    self.escribir_mensaje("[INFO] Desconectado del servidor.")
                    break
                self.escribir_mensaje("[SERVIDOR] " + mensaje.strip())
            except Exception as e:
                self.escribir_mensaje(f"[ERROR] Conexión perdida: {e}")
                self.conectado = False
                break

if __name__ == "__main__":
    root = tk.Tk()
    app = ClienteUsuarioGUI(root)
    root.mainloop()

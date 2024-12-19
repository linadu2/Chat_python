import socket
import threading
import sys


class ChatServer:
    def __init__(self, host='localhost', port=12345):
        self.host = host
        self.port = port
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server_socket.bind((self.host, self.port))
        self.server_socket.listen(5)

        self.clients = []
        self.clients_lock = threading.Lock()

        print(f"[SERVEUR] Démarré sur {self.host}:{self.port}")

    def broadcast(self, message, sender_socket=None):
        """Envoyer un message à tous les clients sauf l'expéditeur."""
        with self.clients_lock:
            for client in self.clients:
                if client != sender_socket:
                    try:
                        client.send(message.encode('utf-8'))
                    except:
                        self.clients.remove(client)

    def handle_client(self, client_socket):
        """Gérer la communication avec un client."""
        try:
            while True:
                message = client_socket.recv(1024).decode('utf-8')
                if not message:
                    break
                print(f"[REÇU] {message}")
                self.broadcast(message, client_socket)
        except Exception as e:
            print(f"[ERREUR] {e}")
        finally:
            with self.clients_lock:
                if client_socket in self.clients:
                    self.clients.remove(client_socket)
            client_socket.close()

    def start(self):
        """Démarrer le serveur et accepter les connexions des clients."""
        try:
            while True:
                client_socket, address = self.server_socket.accept()
                print(f"[CONNEXION] Nouvelle connexion de {address}")

                with self.clients_lock:
                    self.clients.append(client_socket)

                client_thread = threading.Thread(target=self.handle_client, args=(client_socket,))
                client_thread.daemon = True
                client_thread.start()
        except KeyboardInterrupt:
            print("\n[ARRÊT] Le serveur se ferme...")
        finally:
            self.server_socket.close()


def main():
    server = ChatServer()
    server.start()


if __name__ == "__main__":
    main()
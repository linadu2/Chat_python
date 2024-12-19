import socket
import threading
import sys


class ChatClient:
    def __init__(self, client_id, host='localhost', port=12345):
        self.client_id = client_id
        self.host = host
        self.port = port
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.name = client_id

    def connect(self):
        """Se connecter au serveur."""
        try:
            self.socket.connect((self.host, self.port))
            print(f"[{self.name}] Connecté au serveur")
            return True
        except Exception as e:
            print(f"[{self.name}] Échec de connexion : {e}")
            return False

    def receive_messages(self):
        """Recevoir continuellement des messages du serveur."""
        try:
            while True:
                try:
                    message = self.socket.recv(1024).decode('utf-8')
                    if not message:
                        break
                    print(f"\n[MESSAGE REÇU] {message}")
                    # Réafficher l'invite de saisie après avoir reçu un message
                    print(f"[{self.client_id}] > ", end='', flush=True)
                except:
                    break
        except Exception as e:
            print(f"[{self.client_id} ERREUR] {e}")
        finally:
            self.socket.close()

    def send_messages(self):
        """Envoyer des messages au serveur."""
        print(f"[{self.client_id}] Tapez vos messages. Entrez '/quit' pour quitter.")
        try:
            while True:
                is_command = False
                message = input(f"[{self.name}] > ")

                # Quitter le chat
                if message.lower() == '/quit':
                    break

                # Se renommer
                if message.lower().startswith('/name'):
                    is_command = True
                    #print('new name: ', message.split(' ')[1])
                    if len(message.split(' ')) > 1:
                        if new_name := message.split(' ')[1].strip():
                            self.name = new_name
                        else:
                            print('name non existent')
                    else:
                        print('no name provide')

                if message.strip() and not is_command:
                    try:
                        full_message = f"{self.name}: {message}"
                        self.socket.send(full_message.encode('utf-8'))
                    except Exception as e:
                        print(f"[{self.client_id} ERREUR D'ENVOI] {e}")
                        break
        except KeyboardInterrupt:
            print("\nDéconnexion...")
        finally:
            self.socket.close()

    def start(self):
        """Démarrer le client."""
        if not self.connect():
            return

        receive_thread = threading.Thread(target=self.receive_messages)
        receive_thread.daemon = True
        receive_thread.start()

        self.send_messages()


def main(client_id):
    """Fonction principale pour exécuter un client."""
    client = ChatClient(client_id)
    client.start()


if __name__ == "__main__":
    ip = input('SERVER IP: ')
    port = input('SERVER PORT: ')
    name = input('NAME (empty for anonyme): ')
    if not name:
        name = sys.argv[1]
    try:
        main(name)
    except Exception as e:
        print(e)
import subprocess
import sys
import time
import os
import uuid
import chat_server

def name_connexion(x):
    for n in range(1,x+1):
        yield str(uuid.uuid1())


def launch_in_terminal(script_name, args=None):
    """
    Lance un script Python dans un terminal séparé.
    """
    full_path = os.path.abspath(script_name)

    if sys.platform.startswith('win'):  # Windows
        cmd = ['start']
        cmd.extend(['cmd', '/k', 'python', full_path] + (args or []))
        subprocess.Popen(cmd, shell=True)

    else:  # Linux et autres systèmes Unix
        cmd = ['x-terminal-emulator', '-e', f'python {full_path}']
        if args:
            cmd[2] += ' ' + ' '.join(args)
        subprocess.Popen(cmd)


def main():

    for i in name_connexion(2):
        print(f"Démarrage du client {i}...")
        launch_in_terminal('chat_client.py', [i])

        time.sleep(0.5)

    print("Démarrage du serveur...")
    chat_server.main()

if __name__ == "__main__":
    main()
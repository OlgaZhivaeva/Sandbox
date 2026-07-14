import socket
import sys
import threading


def receive_messages(client_socket):
    """Получает сообщения от сервера."""
    buffer = b""
    try:
        while True:
            data = client_socket.recv(1024)
            if not data:
                break

            buffer += data
            if b'\n' in buffer:
                parts = buffer.split(b'\n')
                messages = parts[:-1]
                buffer = parts[-1]

                for message in messages:
                    print(f"\r{message.decode(errors='replace')}")
                print("> ", end="", flush=True)
    except (KeyboardInterrupt, SystemExit, ConnectionError, OSError):
        pass
    finally:
        client_socket.close()


def send_messages(client_socket, username):
    """Отправляет сообщения на сервер."""
    try:
        while True:
            print("> ", end="", flush=True)
            user_message = input()
            if user_message.strip() == '/quit':
                break
            message_to_send = f"<{username}>: {user_message}\n"
            client_socket.sendall(message_to_send.encode())
    except (KeyboardInterrupt, SystemExit, ConnectionError, OSError):
        pass
    finally:
        client_socket.close()
        sys.exit()

def start_client():
    print("=== Добро пожаловать в Python Chat ===")
    username = input("Введите ваше имя: ").strip()
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect(('127.0.0.1', 8000))

    receive_thread = threading.Thread(target=receive_messages, args=(client_socket,), daemon=True)
    receive_thread.start()

    send_messages(client_socket, username)


if __name__ == '__main__':
    start_client()

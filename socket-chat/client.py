import os
import socket
import sys
import threading

screen_lock = threading.Lock() # Объект блокировки для потокобезопасного вывода на экран (sys.stdout)
input_buffer = [] # Глобальный буфер символов, которые пользователь успел набрать, но ещё не отправил

if os.name == 'nt':
    import msvcrt

    def get_char():
        """Считывание одного символа для Windows."""
        return msvcrt.getwch()
else:
    import termios
    import tty


    def get_char():
        """Считывание одного символа для Linux и macOS."""
        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)
        try:
            tty.setraw(fd)
            return sys.stdin.read(1)
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)


def custom_input(prompt="> "):
    """Посимвольный ввод, сохраняющий набранный текст в input_buffer."""
    global input_buffer
    input_buffer = []

    with screen_lock:
        print(prompt, end="", flush=True)

    while True:
        try:
            ch = get_char()
        except Exception:
            raise KeyboardInterrupt

        if ch in ('\r', '\n'):  # Нажат Enter
            with screen_lock:
                print()
            text = "".join(input_buffer)
            input_buffer = []
            return text

        elif ch in ('\x08', '\x7f'):  # Нажат Backspace
            with screen_lock:
                if input_buffer:
                    input_buffer.pop()
                    current_text = "".join(input_buffer)
                    print(f"\r\033[K{prompt}{current_text}", end="", flush=True)

        elif ch == '\x03':  # Нажато Ctrl+C
            raise KeyboardInterrupt

        else:  # Нажат обычный символ
            with screen_lock:
                input_buffer.append(ch)
                print(ch, end="", flush=True)


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
                    text = message.decode(errors='replace').rstrip('\r')

                    with screen_lock:
                        current_text = "".join(input_buffer)
                        print(f"\r\033[K{text}") # \r — в начало строки, \033[K — очистить текущую строку
                        print(f"> {current_text}", end="", flush=True) # Восстанавливаем недопечатанный текст из буфера
    except (KeyboardInterrupt, SystemExit, ConnectionError, OSError):
        pass
    finally:
        client_socket.close()


def send_messages(client_socket, username):
    """Отправляет сообщения на сервер."""
    try:
        while True:
            user_message = custom_input("> ")
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
    try:
        client_socket.connect(('127.0.0.1', 8000))
    except (SystemExit, ConnectionError, OSError) as e:
        print(f'Подключение не установлено,проверьте запущен ли сервер.')
        client_socket.close()
        sys.exit()

    receive_thread = threading.Thread(target=receive_messages, args=(client_socket,), daemon=True)
    receive_thread.start()

    send_messages(client_socket, username)


if __name__ == '__main__':
    start_client()

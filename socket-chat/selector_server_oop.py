import logging
import selectors
import socket
import sys


logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
logger.addHandler(logging.StreamHandler(stream=sys.stdout))


class ClientConnection:
    def __init__(self, conn, addr):
        self.conn = conn
        self.addr = addr
        self.read_buffer = bytearray()

    def read(self):
        """
        Читает данные из сокета.
        Возвращает:
          - None: если клиент отключился или произошла ошибка
          - list[str]: список распарсенных строк (может быть пустым [])
        """
        try:
            data = self.conn.recv(1024)
        except ConnectionError:
            return None
        if not data:
            return None

        self.read_buffer += data
        text_messages = []

        if b'\n' in self.read_buffer:
            parts = self.read_buffer.split(b'\n')
            self.read_buffer = bytearray(parts[-1])

            for raw_msg in parts[:-1]:
                clean_msg = raw_msg.rstrip(b'\r')
                text = clean_msg.decode('utf-8', errors='replace')
                text_messages.append(text)

        return text_messages

    def send_message(self, msg_str: str):
        """Отправка сообщения клиенту."""
        try:
            self.conn.sendall(msg_str.encode('utf-8'))
        except OSError:
            pass

    def close(self):
        """Закрывает сокет клиента."""
        self.conn.close()


class ChatServer:
    def __init__(self, host='127.0.0.1', port=8000):
        self.host = host
        self.port = port
        self.clients = {}  # {conn: ClientConnection}
        self.selector = selectors.DefaultSelector()
        self.serv_sock = None

    def start(self):
        """
        Запускает чат-сервер: настраивает неблокирующий слушающий сокет,
        регистрирует его в селекторе и запускает бесконечный цикл
        обработки событий ввода-вывода (I/O event loop).
        """
        self.serv_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.serv_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.serv_sock.bind(('127.0.0.1', 8000))
        self.serv_sock.listen()
        self.serv_sock.setblocking(False)

        self.selector.register(self.serv_sock, selectors.EVENT_READ, self.accept_client)
        logger.info('Сервер слушает 127.0.0.1:8000...')

        try:
            while True:
                events = self.selector.select(timeout=1)
                for key, mask in events:
                    callback = key.data
                    callback(key.fileobj)

        except KeyboardInterrupt:
            logger.info('Сервер останавливается пользователем...')
        finally:
            self._cleanup()

    def _cleanup(self):
        """
        Корректно освобождает все ресурсы при остановке сервера:
        отправляет финальное сообщение и закрывает соединения со всеми
        активными клиентами, отключает слушающий сокет и закрывает селектор.
        """
        logger.info('Корректное закрытие ресурсов...')
        for conn in list(self.clients.keys()):
            client = self.clients[conn]
            logger.info(f'Закрываем соединение с клиентом {client.addr[1]}')
            client.send_message('Server has shut down\r\n')
            self.disconnect_client(client)

        logger.info("Закрываем слушающий сокет сервера...")
        if self.serv_sock:
            try:
                self.selector.unregister(self.serv_sock)
            except (KeyError, ValueError):
                pass
            self.serv_sock.close()

        self.selector.close()
        logger.info("Сервер полностью остановлен.")

    def accept_client(self, serv_sock):
        """Принимает новое подключение."""
        conn, addr = self.serv_sock.accept()
        conn.setblocking(False)
        client = ClientConnection(conn, addr)
        self.clients[conn] = client
        client.send_message(f'Welcome to the chat! Your port: {addr[1]}. To exit, enter /quit\r\n')

        chat_msg = f'Client {addr[1]} connected\r\n'
        self.broadcast(chat_msg, sender_client=client)
        logger.info(f'Подключился клиент {addr[1]}')
        self.selector.register(conn, selectors.EVENT_READ, self.handle_client)

    def handle_client(self, conn):
        """Обрабатывает события чтения на сокете конкретного клиента."""
        client = self.clients.get(conn)
        if not client:
            return

        messages = client.read()
        if messages is None:
            self.disconnect_client(client)
            return
        for text in messages:
            if text.strip() == '/quit':
                self.disconnect_client(client)
                return
            if len(text) > 100:
                text = text[:100] + "..."

            logger.info(f'[{client.addr[1]}] {text}')
            chat_msg = f'[{client.addr[1]}] {text}\r\n'
            self.broadcast(chat_msg, sender_client=client)


    def broadcast(self, chat_msg, sender_client):
        """Рассылает байтовое сообщение всем подключенным клиентам, кроме отправителя."""
        for client in list(self.clients.values()):
            if client != sender_client:
                client.send_message(chat_msg)

    def disconnect_client(self, client):
        """
        Корректно отключает клиента от сервера:
        оповещает остальных чат-участников, снимает сокет с регистрации
        в селекторе, закрывает соединение и удаляет клиента из списка активных.
        """
        if client.conn not in self.clients:
            return
        chat_msg = f'Client {client.addr[1]} disconnected\r\n'
        self.broadcast(chat_msg, client)
        logger.info(f'Клиент {client.addr[1]} отключился')

        try:
            self.selector.unregister(client.conn)
        except (KeyError, ValueError):
            pass

        client.close()
        self.clients.pop(client.conn, None)

if __name__ == '__main__':
    server = ChatServer('127.0.0.1', 8000)
    server.start()

import logging
import selectors
import socket
import sys


logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
logger.addHandler(logging.StreamHandler(stream=sys.stdout))


def selector_server():
    selector = selectors.DefaultSelector()
    clients = {}
    read_buffers = {}
    outgoing_buffers = {}

    def disconnect_client(conn):
        """Закрывает соединение, чистит буферы и убирает из селектора."""
        if conn not in clients:
            return
        addr = clients[conn]
        chat_msg = f'Client {addr[1]} disconnected\r\n'
        broadcast(chat_msg.encode(), conn)
        logger.info(f'Клиент {addr[1]} отключился')

        try:
            selector.unregister(conn)
        except KeyError:
            pass
        conn.close()
        clients.pop(conn, None)
        read_buffers.pop(conn, None)
        outgoing_buffers.pop(conn, None)

    def read_client(conn):
        """Читает данные из сокета и формирует сообщения."""
        try:
            data = conn.recv(1024)
        except ConnectionError:
            disconnect_client(conn)
            return
        if not data:
            disconnect_client(conn)
            return

        read_buffers[conn] += data
        if b'\n' in read_buffers[conn]:
            parts = read_buffers[conn].split(b'\n')
            messages = parts[:-1]
            read_buffers[conn] = parts[-1]

            for message in messages:
                clean_msg = message.rstrip(b'\r')
                text = clean_msg.decode('utf-8', errors='replace')
                if text.strip() == '/quit':
                    disconnect_client(conn)
                    return
                if len(text) > 100:
                    text = text[:100] + "..."

                sender_port = clients[conn][1]
                logger.info(f'[{sender_port}] {text}')

                chat_msg = f'[{sender_port}] {text}\r\n'
                broadcast(chat_msg.encode(), conn)

    def write_client(conn):
        """Отправляет накопленные данные клиенту."""
        buffer = outgoing_buffers.get(conn)
        if not buffer:
            return

        try:
            sent = conn.send(buffer)
            del buffer[:sent]

            if len(buffer) == 0:
                selector.modify(conn, selectors.EVENT_READ, handle_client)
        except ConnectionError:
            disconnect_client(conn)

    def handle_client(conn, mask):
        """Определяет какое событие произошло на сокете."""
        if mask & selectors.EVENT_READ:
            read_client(conn)
        if mask & selectors.EVENT_WRITE:
            write_client(conn)

    def accept_client(serv_socket):
        """Принимает новое подключение."""
        conn, addr = serv_socket.accept()
        conn.setblocking(False)
        clients[conn] = addr
        read_buffers[conn] = bytearray()
        outgoing_buffers[conn] = bytearray()

        selector.register(conn, selectors.EVENT_READ, handle_client)

        welcome_msg = f'Welcome to the chat! Your port: {addr[1]}. To exit, enter /quit\r\n'
        add_to_send(conn, welcome_msg.encode())

        chat_msg = f'Client {addr[1]} connected\r\n'
        broadcast(chat_msg.encode(), conn)
        logger.info(f'Подключился клиент {addr[1]}')

    def add_to_send(conn, data: bytes):
        """Добавляет данные в буфер отправки клиента и активирует EVENT_WRITE."""
        if conn not in outgoing_buffers:
            return

        was_empty = len(outgoing_buffers[conn]) == 0
        outgoing_buffers[conn] += data

        if was_empty:
            selector.modify(conn, selectors.EVENT_READ | selectors.EVENT_WRITE, handle_client)

    def broadcast(msg_bytes, sender_conn):
        """Рассылает сообщение всем, кроме отправителя."""
        for client_conn in list(clients.keys()):
            if client_conn != sender_conn:
                add_to_send(client_conn, msg_bytes)

    serv_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    serv_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    serv_sock.bind(('127.0.0.1', 8000))
    serv_sock.listen()
    serv_sock.setblocking(False)
    selector.register(serv_sock, selectors.EVENT_READ, lambda sock, mask: accept_client(sock))
    logger.info('Сервер слушает 127.0.0.1:8000...')

    try:
        while True:
            events = selector.select(timeout=1)
            for key, mask in events:
                callback = key.data
                callback(key.fileobj, mask)
    except KeyboardInterrupt:
        logger.info('Сервер останавливается пользователем...')
    finally:
        logger.info('Корректное закрытие ресурсов...')
        for conn in list(clients.keys()):
            addr = clients[conn]
            logger.info(f'Закрываем соединение с клиентом {addr[1]}')
            try:
                conn.send('Server has shut down\r\n'.encode())
            except ConnectionError:
                pass
            try:
                selector.unregister(conn)
            except KeyError:
                pass
            conn.close()

        logger.info("Закрываем слушающий сокет сервера...")
        try:
            selector.unregister(serv_sock)
        except KeyError:
            pass
        serv_sock.close()
        selector.close()
        logger.info("Сервер полностью остановлен.")


if __name__ == '__main__':
    selector_server()

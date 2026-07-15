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
    buffers = {}

    def disconnect_client(conn):
        """Событие на сокете клиента = клиент отключился"""
        addr = clients[conn]
        chat_msg = f'Client {addr[1]} disconnected\r\n'
        broadcast(chat_msg, conn)
        logger.info(f'Клиент {addr[1]} отключился')
        selector.unregister(conn)
        conn.close()
        buffers.pop(conn)
        clients.pop(conn)

    def read_client(conn):
        """Событие на сокете клиента = пришли данные"""
        try:
            data = conn.recv(1024)
        except ConnectionError:
            disconnect_client(conn)
            return
        if not data:
            disconnect_client(conn)
            return

        buffers[conn] += data
        if b'\n' in buffers[conn]:
            parts = buffers[conn].split(b'\n')
            messages = parts[:-1]
            buffers[conn] = parts[-1]

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
                broadcast(chat_msg, conn)

    def accept_client(serv_socket):
        """Событие на слушающем сокете = новый клиент"""
        conn, addr = serv_socket.accept()
        conn.setblocking(False)
        clients[conn] = addr
        buffers[conn] = b''
        conn.sendall(f'Welcome to the chat! Your port: {addr[1]}. To exit, enter /quit\r\n'.encode())
        chat_msg = f'Client {addr[1]} connected\r\n'
        broadcast(chat_msg, conn)
        logger.info(f'Подключился клиент {addr[1]}')
        selector.register(conn, selectors.EVENT_READ, read_client)

    def broadcast(msg: str, sender_conn):
        """Рассылает сообщение всем, кроме отправителя."""
        for client_conn in list(clients.keys()):
            if client_conn != sender_conn:
                try:
                    client_conn.send(msg.encode())
                except ConnectionError:
                    pass

    serv_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    serv_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    serv_sock.bind(('127.0.0.1', 8000))
    serv_sock.listen()
    serv_sock.setblocking(False)
    selector.register(serv_sock, selectors.EVENT_READ, accept_client)
    logger.info('Сервер слушает 127.0.0.1:8000...')

    try:
        while True:
            events = selector.select(timeout=1)
            for key, mask in events:
                callback = key.data
                callback(key.fileobj)
    except KeyboardInterrupt:
        logger.info('Сервер останавливается пользователем...')
    finally:
        logger.info('Корректное закрытие ресурсов...')
        for conn in clients:
            addr = clients[conn]
            logger.info(f'Закрываем соединение с клиентом {addr[1]}')
            conn.send('Server has shut down\r\n'.encode())
            selector.unregister(conn)
            conn.close()

        logger.info("Закрываем слушающий сокет сервера...")
        selector.unregister(serv_sock)
        serv_sock.close()
        selector.close()
        logger.info("Сервер полностью остановлен.")


if __name__ == '__main__':
    selector_server()

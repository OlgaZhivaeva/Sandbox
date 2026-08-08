import logging
import select
import socket
import sys


logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
logger.addHandler(logging.StreamHandler(stream=sys.stdout))


def broadcast(msg: str, sender_conn, clients: dict):
    """Рассылает сообщение всем, кроме отправителя."""
    for client_conn in clients:
        if client_conn != sender_conn:
            try:
                client_conn.send(msg.encode())
            except ConnectionError:
                pass

def select_server():
    serv_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    serv_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    serv_sock.bind(('127.0.0.1', 8000))
    serv_sock.listen()
    serv_sock.setblocking(False)
    logger.info('Сервер слушает 127.0.0.1:8000...')

    clients = {}
    buffers = {}
    socks_for_read = [serv_sock]

    while True:
        ready, _, _ = select.select(socks_for_read, [], [], 1)
        for sock in ready:
            if sock == serv_sock:
                conn, addr = sock.accept()
                conn.setblocking(False)
                clients[conn] = addr
                buffers[conn] = b''
                socks_for_read.append(conn)
                conn.send(f'Welcome to the chat! Your port: {addr[1]}\r\n'.encode())
                logger.info(f'Welcome to the chat! Your port: {addr[1]}')
                chat_msg = f'Client {addr[1]} connected\r\n'
                broadcast(chat_msg, conn, clients)
                logger.info(f'Подключился клиент {addr[1]}')
                continue

            data = sock.recv(1024)
            if not data:
                addr = clients[sock]
                chat_msg = f'Client {addr[1]} disconnected\r\n'
                broadcast(chat_msg, sock, clients)
                logger.info(f'Клиент {addr[1]} отключился')
                sock.close()
                buffers.pop(sock)
                clients.pop(sock)
                socks_for_read.remove(sock)
                continue

            buffers[sock] += data
            if b'\n' in buffers[sock]:
                parts = buffers[sock].split(b'\n')
                messages = parts[:-1]
                buffers[sock] = parts[-1]

                for message in messages:
                    clean_msg = message.rstrip(b'\r')
                    text = clean_msg.decode('utf-8', errors='replace')

                    sender_port = clients[sock][1]
                    logger.info(f'[{sender_port}]: {text}')

                    chat_msg = f'[{sender_port}]: {text}\r\n'
                    broadcast(chat_msg, sock, clients)


if __name__ == '__main__':
    select_server()

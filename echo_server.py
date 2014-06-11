import socket
import sys


def server(log_buffer=sys.stderr):
    address = ('127.0.0.1', 10000)
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # allow rapid re-use of the socket
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind(address)
    sock.listen(10)

    try:
        while True:
            conn, addr = sock.accept()  # blocking
            try:
                while True:
                    data = conn.recv(16)
                    if data:
                        conn.sendall(data)
                    else:
                        break
            finally:
                conn.close()

    except KeyboardInterrupt:
        sock.close()
        return


if __name__ == '__main__':
    server()
    sys.exit(0)

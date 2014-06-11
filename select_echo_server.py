import select
import socket
import sys

def server(log_buffer=sys.stderr):
    address = ('127.0.0.1', 10000)
    buffsize = 16
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # allow rapid re-use of the socket
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind(address)
    server_socket.listen(5)
    input = [server_socket, sys.stdin]
    running = True
    while running:
        read_ready, write_ready, except_ready = select.select(input, [], [], 0)
        for readable in read_ready:
            # import pdb; pdb.set_trace()
            if readable is server_socket:
                # spin up new handler sockets as clients connect
                handler_socket, address = readable.accept()  # won't block now
                input.append(handler_socket)
            elif readable is sys.stdin:
                # handle any stdin by terminating the server
                sys.stdin.readline()
                running = False
            else:
                # this socket is a handler socket created by a client
                # connection
                data = readable.recv(buffsize)
                if data:
                    #still reading buffers from this handler
                    readable.sendall(data)
                else:
                    readable.close()
                    input.remove(readable)

    server_socket.close()


if __name__ == '__main__':
    server()
    sys.exit(0)

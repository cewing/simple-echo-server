import socket
import sys


def client(msg, log=sys.stderr):
    server_address = ('localhost', 10000)
    sock = socket.socket(
        socket.AF_INET, socket.SOCK_STREAM, socket.IPPROTO_TCP
    )
    print >>log, 'connecting to {0} port {1}'.format(*server_address)
    sock.connect(server_address)
    response = ''
    done = False
    bufsize = 16
    try:
        print >>log, 'sending "{0}"'.format(msg)
        sock.sendall(msg)
        # shut the socket for writing once we are finished.  This will send a
        # 0-byte message to the server and let it know we are done.
        sock.shutdown(socket.SHUT_WR)
        while not done:
            chunk = sock.recv(bufsize)
            if len(chunk) < bufsize:
                done = True
            response += chunk
        print >>log, 'received "{0}"'.format(response)
    finally:
        print >>log, 'closing socket'
        sock.close()
    return response


if __name__ == '__main__':
    if len(sys.argv) != 2:
        usg = '\nusage: python echo_client.py "this is my message"\n'
        print >>sys.stderr, usg
        sys.exit(1)

    msg = sys.argv[1]
    client(msg)

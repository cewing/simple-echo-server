# -*- coding: utf-8 -*-
from cStringIO import StringIO
from echo_client import client
from echo_server import server
import socket
import unittest


def make_buffers(string, buffsize=16):
    for start in range(0, len(string), buffsize):
        yield string[start:start+buffsize]


class EchoTestCase(unittest.TestCase):
    """tests for the echo server and client"""
    connection_msg = 'connecting to localhost port 10000'
    sending_msg = 'sending "{0}"'
    received_msg = 'received "{0}"'
    closing_msg = 'closing socket'

    def setUp(self):
        """set up our tests"""
        if not hasattr(self, 'buff'):
            # ensure we have a buffer for the client to write to
            self.log = StringIO()
        else:
            # ensure that the buffer is set to the start for the next test
            self.log.seek(0)

    def tearDown(self):
        """clean up after ourselves"""
        if hasattr(self, 'buff'):
            # clear our buffer for the next test
            self.log.seek(0)
            self.log.truncate()

    def send_message(self, message):
        """Attempt to send a message using the client and the test buffer

        In case of a socket error, fail and report the problem
        """
        try:
            client(message, self.log)
        except socket.error, e:
            if e.errno == 61:
                msg = "Error: {0}, is the server running?"
                self.fail(msg.format(e.strerror))
            else:
                self.fail("Unexpected Error: {0}".format(str(e)))

    def process_log(self):
        """process the buffer used by the client for logging

        The first and last lines of output will be checked to ensure that the
        client started and terminated in the expected way

        The 'sending' message will be separated from the echoed message
        returned from the server.

        Finally, the sending message, and the list of returned buffer lines
        will be returned
        """
        if self.log.tell() == 0:
            self.fail("No bytes written to buffer")

        self.log.seek(0)
        connect, send, receive, close = [line.strip() for line in self.log]
        self.assertEqual(connect, self.connection_msg,
                         "Unexpected connection message")
        self.assertEqual(close, self.closing_msg,
                         "Unexpected closing message")
        return send, receive

    def test_short_message_echo(self):
        """test that a message short than 16 bytes echoes cleanly"""
        short_message = "short message"
        self.send_message(short_message)
        actual_sent, actual_reply = self.process_log()
        expected_sent = self.sending_msg.format(short_message)
        self.assertEqual(
            expected_sent,
            actual_sent,
            "expected {0}, got {1}".format(expected_sent, actual_sent)
        )

        expected_reply = self.received_msg.format(short_message)
        self.assertEqual(
            expected_reply,
            actual_reply,
            "expected {0} got {1}".format(expected_reply, actual_reply))

    def test_long_message_echo(self):
        """test that a message longer than 16 bytes echoes in 16-byte chunks"""
        long_message = "Four score and seven years ago our fathers did stuff"
        self.send_message(long_message)
        actual_sent, actual_reply = self.process_log()

        expected_sent = self.sending_msg.format(long_message)
        self.assertEqual(
            expected_sent,
            actual_sent,
            "expected {0}, got {1}".format(expected_sent, actual_sent)
        )

        expected_reply = self.received_msg.format(long_message)
        self.assertEqual(
            expected_reply,
            actual_reply,
            "expected {0}, got {1}".format(expected_reply, actual_reply)
        )

    def test_message_exactly_buffsize(self):
        """test that the server is robust to messages exactly 1 buffer long"""
        buf_message = "It's 16 bytes eh"
        self.send_message(buf_message)
        actual_sent, actual_reply = self.process_log()
        expected_sent = self.sending_msg.format(buf_message)
        self.assertEqual(expected_sent, actual_sent)
        expected_reply = self.received_msg.format(buf_message)
        self.assertEqual(expected_reply, actual_reply)


if __name__ == '__main__':
    import multiprocessing
    server_process = multiprocessing.Process(name='daemon', target=server)
    server_process.daemon = True
    server_process.start()
    unittest.main()
    server_process.terminate()

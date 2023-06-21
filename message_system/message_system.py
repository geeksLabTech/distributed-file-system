import socket
import struct
import time
import select
import threading
from socket import SHUT_RDWR


class Message_System:

    def __init__(self):
        self.pendig_send = []
        self.pendig_receive = [
            {'port': "0.0.0.0", "times": -1}
        ]

    def _mc_send(self, hostip, mcgrpip, mcport, msgbuf):
        # This creates a UDP socket
        sender = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM,
                               proto=socket.IPPROTO_UDP, fileno=None)
        # This defines a multicast end point, that is a pair
        #   (multicast group ip address, send-to port nubmer)
        mcgrp = (mcgrpip, mcport)

        # This defines how many hops a multicast datagram can travel.
        # The IP_MULTICAST_TTL's default value is 1 unless we set it otherwise.
        sender.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, 1)

        # This defines to which network interface (NIC) is responsible for
        # transmitting the multicast datagram; otherwise, the socket
        # uses the default interface (ifindex = 1 if loopback is 0)
        # If we wish to transmit the datagram to multiple NICs, we
        # ought to create a socket for each NIC.
        sender.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_IF,
                          socket.inet_aton(hostip))

        # Transmit the datagram in the buffer
        sender.sendto(msgbuf, mcgrp)

        # release the socket resources
        sender.close()

    def stop_listening(self, sock, duration=5):
        threading.Timer(duration, self.close_sock, [sock]).start()

    def close_sock(self, sock: socket):
        print("closing socket", sock)
        try:
            sock.shutdown(SHUT_RDWR)
            sock.close()
        except OSError:
            pass

    def _mc_recv(self, fromnicip, mcgrpip, mcport):
        # print("inside rec")
        bufsize = 1024

        # This creates a UDP socket
        receiver = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM,
                                 proto=socket.IPPROTO_UDP, fileno=None)

        # This configure the socket to receive datagrams sent to this multicast
        # end point, i.e., the pair of
        #   (multicast group ip address, mulcast port number)
        # that must match that of the sender
        print((mcgrpip, mcport))
        bindaddr = (mcgrpip, mcport)
        receiver.bind(bindaddr)

        # This joins the socket to the intended multicast group. The implications
        # are two. It specifies the intended multicast group identified by the
        # multicast IP address.  This also specifies from which network interface
        # (NIC) the socket receives the datagrams for the intended multicast group.
        # It is important to note that socket.INADDR_ANY means the default network
        # interface in the system (ifindex = 1 if loopback interface present). To
        # receive multicast datagrams from multiple NICs, we ought to create a
        # socket for each NIC. Also note that we identify a NIC by its assigned IP
        # address.
        if fromnicip == '0.0.0.0':
            mreq = struct.pack("=4sl", socket.inet_aton(
                mcgrpip), socket.INADDR_ANY)
        else:
            mreq = struct.pack("=4s4s",
                               socket.inet_aton(mcgrpip), socket.inet_aton(fromnicip))
        receiver.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)
        # receiver.timeout(5)
        # ready_to_read, _, _ = select.select([receiver], [], [], 10)

        # print("Listening now...")
        # self.stop_listening(receiver)
        # receiver.shutdown(1)
        buf, senderaddr = receiver.recvfrom(1024)
        # receiver.close()
        # print("GOT IT...")

        msg = buf.decode()

        # msg = senderaddr = None
        # Release resources
        receiver.close()
        print(msg, senderaddr)
        return msg, senderaddr

    def add_to_send(self, msg, times=1, dest=None):
        package = {'message': msg,
                   'times': times}

        if dest == None:
            package['ip'] = None
            package['port'] = None

        self.pendig_send.append(package)

    def send(self):
        self_host = socket.gethostname()
        self_ip = socket.gethostbyname(self_host)
        # self_ip = "192.168.26.1"

        for i in self.pendig_send:
            if i['ip'] == None:
                # print("sending")
                self._mc_send(self_ip, '224.1.1.5', 50001,
                              i['message'].encode())

    def send_heartbeat(self):
        while True:
            self.send()
            time.sleep(0.3)

    def receive(self):
        to_remove = []
        self_host = socket.gethostname()
        self_ip = socket.gethostbyname(self_host)
        # self_ip = "192.168.26.1"
        for idx, i in enumerate(self.pendig_receive):
            if i['times'] > 0:
                i -= 1
            print(f"listening in {self_ip}")
            msg, ip = self._mc_recv(self_ip, '224.1.1.5', 50001)
            if msg:
                print(f">>> Message from {ip}: {msg}\n")

            # process message

            if i['times'] == 0:
                to_remove.append(idx)

        for i in to_remove:
            self.pendig_receive.pop(i)

        return msg

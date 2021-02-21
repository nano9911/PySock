import socket, sys, signal

def signal_handler(signal, frame):
    print("Interrupt by signal SIGINT (Ctrl + C)")
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)

def gateway_out(sock):
    print("[*] gateway_out():\n\tConnection closing...\n\tProgam closing...")
    if sock is not None:
        try:
            sock.shutdown(socket.SHUT_RDWR)
        except OSError as err:
            print("[*] gateway_out(): shutdown() failed with error: %s" % err)

        try:
            sock.close()
        except OSError as err:
            print("[*] gateway_out(): close() failed with error: %s" % err)

    sys.exit(0)

def message_creator(msg):
    message = '''================================================
Start of the message:
%s
End of the message.
================================================''' % msg
    return message

def main(argv):
    target_ip = argv[1]
    target_port = int(argv[2])

    for res in socket.getaddrinfo(target_ip, target_port, socket.AF_UNSPEC, socket.SOCK_STREAM):
        af, socktype, proto, canonname, sa = res
        try:
            s = socket.socket(af, socktype, proto)
            print("[*] socket():\tSocket created succefully.")
        except OSError as err:
            print("> socket():\tSocket creation failed with error %s" % err)
            s = None
            continue

        try:
            s.connect(sa)
            print("[*] connect():\tConnected to %s:%d" % (target_ip,target_port))
        except OSError as err:
            print("> connect():\tConnect to server failed with error: %s" % err)
            s = None
            continue
        break

    if s is None:
        print("> Couldn't open socket")
        sys.exit(0)

    recvbuf = None
    sendbuf = message_creator("Hello Server")
    msg = None
    while True:
        try:
            s.sendall(bytes(sendbuf, encoding="utf8"))
        except OSError as err:
            print("> sendall() failed with error: %s" % err)
            break

        try:
            recvbuf = s.recv(1024)
        except OSError as err:
            print("> recv() failed with error: %s" % err)
            break

        msg = recvbuf.decode()
        if recvbuf == "" or recvbuf == None:
            print("> Empt message received or connection closed")
            break

        print("\n$ Message received from %s:\n%s" % (target_ip, msg))
        recvbuf = None
        
        sendbuf = input("$ Enter a message to send:")
        if len(sendbuf) == 0:
            break

        sendbuf = message_creator(sendbuf)

    print("Closing connection...\nClosing program...")
    s.close()
    sys.exit(0)

main(sys.argv)
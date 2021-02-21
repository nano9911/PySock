import threading, socket, sys, signal

def signal_handler(signal, frame):
    print("> signal():\tInterrupt by signal %s" % signal)
    sys.exit(0)

#signal.SIGEMT | signal.SIGINFO | signal.SIGFPE | signal.SIGILL | signal.SIGINT | signal.SIGSEGV | signal.SIGTERM | signal.SIGBREAK
signal.signal(signal.SIGABRT, signal_handler)
signal.signal(signal.SIGINT, signal_handler)

ip = "0.0.0.0"
port = 12345

class handle_client(threading.Thread) :
    def __init__(self, client_socket, client_address) :
        super(handle_client, self).__init__()
        self.csock = client_socket
        self.addr = client_address
        print("[*] __init__():\tInitialised the handler thread for %s:%s connection" % (self.addr[0], self.addr[1]))
        return

    def run(self):
        print("[*] start()->run():\tStarted the handler thread for %s:%s connection" % (self.addr[0], self.addr[1]))
        recvbuf = "Empty"
        msg = None

        while True:
            recvbuf = None
            try:
                recvbuf = self.csock.recv(1024)
            except (OSError, ConnectionResetError, ConnectionAbortedError, ConnectionError) as err:
                print("> %s:%s recv() failed with error: %s" % (self.addr[0], self.addr[1], err))
                break
            except:
                print("> %s:%s recv() failed with unexpected error: %s" % (self.addr[0], self.addr[1], sys.exc_info() [0]))
                break

            if len(recvbuf) != 0:
                msg = recvbuf.decode()
                print("\n$ Message received from %s:%s (length=%d):\n%s" % (self.addr[0], self.addr[1], len(recvbuf),msg))

                try:
                    self.csock.sendall(bytes(msg, 'utf8'))
                except (OSError, ConnectionResetError, ConnectionAbortedError, ConnectionError) as err:
                    print("> %s:%s sendall() failed with error: %s" % (self.addr[0], self.addr[1], err))
                    break
                except:
                    print("> %s:%s sendall() failed with unexpected error: %s" % (self.addr[0], self.addr[1], sys.exc_info() [0]))
                    break


                print("$ Message received from %s:%s echoed back" % (self.addr[0], self.addr[1]))
                
            else:
                print("> empty message received from %s:%s\n"% (self.addr[0], self.addr[1]))
                break

        print("[*] Closing connection with %s:%s..." % (self.addr[0], self.addr[1]))

        try:
            self.csock.close()
        except OSError as err:
            print("> close() failed with error: %s" % err)

        return


def main():
    s = None
    for res in socket.getaddrinfo(ip, port, socket.AF_UNSPEC, socket.SOCK_STREAM, 0, socket.AI_PASSIVE):
        af, socktype, proto, canoname, sa = res
        try:
            s = socket.socket(af, socktype, proto)
            print("[*] socket():\tSocket created succefully.")
        except socket.error as err:
            print("> socket():\tSocket creation failed with error %s" % err)
            s = None
            continue
        
        try:
            s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        except OSError as err:
            print("> setsockopt():\tSetting option SO_REUSEADDR failed with error: %s" % err)
            s = None
            sys.exit(1)

        try:
            s.bind(sa)
            print("[*] bind():\tSocket binded to port %s" % port)
        except OSError as err:
            print("> bind():\tBinding to port %d failed with error: %s" % (sa.port, err))
            s = None
            continue

        try:
            s.listen(5)
            print("[*] listen():\tListening on port %s" % port)
        except OSError as err:
            print("> listen():\tListening on port %d failed with error: %s" % (sa.port, err))
            s = None
            continue


        break

    if s is None:
        print("> Could't open socket")
        sys.exit(1)

    client_handler = None
    while True:
        client, addr = s.accept()
        print("[*] accept():\tAccepted connection from %s:%d" % (addr[0], addr[1]))
        client_handler = handle_client(client, addr)
        client_handler.start()

main()
import threading, socket, sys

# 0.0.0.0 -> Listens on all interfaces
ip = "0.0.0.0"
port = 12345

# Threading class handler
class handle_client(threading.Thread) :
    def __init__(self, client_socket, client_address) :
        super(handle_client, self).__init__()
        # Defining initial values for thread to start, csock to handle the new socket for the new client
        self.csock = client_socket
        # addr is just to keep track of clients from the output
        self.addr = client_address
        print("[*] __init__():\tInitialised the handler thread for %s:%s connection" % (self.addr[0], self.addr[1]))
        return

    def run(self):
        print("[*] start()->run():\tStarted the handler thread for %s:%s connection" % (self.addr[0], self.addr[1]))
        # Intialising receiving buffer and msg variable which contains the contentof
        # the receiving buffer casted to string
        recvbuf = "Empty"
        msg = None

        while True:
            # Flushing the receiving buffer
            recvbuf = None
            try:
                # recv() returns the message (received data) in bytes object type
                recvbuf = self.csock.recv(1024)
            # handling exceptions
            except (OSError, ConnectionResetError, ConnectionAbortedError, ConnectionError) as err:
                print("> %s:%s recv() failed with error: %s" % (self.addr[0], self.addr[1], err))
                break
            except:
                print("> %s:%s recv() failed with unexpected error: %s" % (self.addr[0], self.addr[1], sys.exc_info() [0]))
                break

            # if the received message is empty this means the clients finished
            # and we should close the socket and exit the thread safely
            if len(recvbuf) != 0:
                # Data in recvbuf are in bytes object type, so decode it to strings so we can read it
                msg = recvbuf.decode()
                print("\n$ Message received from %s:%s (length=%d):\n%s" % (self.addr[0], self.addr[1], len(recvbuf),msg))

                try:
                    # we use the the decoded recvbuf to make sure it wil be sent right
                    self.csock.sendall(bytes(msg, 'utf8'))
                # handling exceptions
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
            # close the socket that is responsible for the clinet handled in that thread
            self.csock.close()
        # handling exceptions
        except OSError as err:
            print("> close() failed with error: %s" % err)

        # the main thread isn't waiting and the thread isn't joinable, so there's no need to specify an exit value
        return


def main():
    # initialising values
    s = None
    # getting the linked list of the possible values that matches our requists in getaddrinfo()
    for res in socket.getaddrinfo(ip, port, socket.AF_UNSPEC, socket.SOCK_STREAM, 0, socket.AI_PASSIVE):
        af, socktype, proto, canoname, sa = res
        try:
            # socket() returns the created socket with required values, else raises an OSError
            s = socket.socket(af, socktype, proto)
            print("[*] socket():\tSocket created succefully.")
        except socket.error as err:
            print("> socket():\tSocket creation failed with error %s" % err)
            s = None
            # it's not critical, so there's no need to end the execution, we can just move on to the next member
            # of the linked list and test it.
            continue
        
        try:
            # setting SO_REUSEADDR option forthe created socket for security reasons
            s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        except OSError as err:
            print("> setsockopt():\tSetting option SO_REUSEADDR failed with error: %s" % err)
            s = None
            # it's critical, and when fails that means it willn't work on any of the member
            # of the linked list, so exit the program and check the error code
            sys.exit(1)

        try:
            # binding the created socket to the specified interface id, ip address and port number
            s.bind(sa)
            print("[*] bind():\tSocket binded to port %s" % port)
        except OSError as err:
            print("> bind():\tBinding to port %d failed with error: %s" % (sa.port, err))
            s = None
            # like socket() it's not critical and you can try the next one
            continue

        try:
            # start listening from the socket on the specified values from bin(), with 5 back log queue length
            s.listen(5)
            print("[*] listen():\tListening on port %s" % port)
        except OSError as err:
            print("> listen():\tListening on port %d failed with error: %s" % (sa.port, err))
            s = None
            # like sockey() and bind() it's not critical, so try the next one
            continue

        # if passed all tries, then you can quit with the current values of s
        break

    # check if the for loop ended because it reaches the end of the linked list of getaddrinfo(),
    # which means that we don't have a socket to listen on and we will exit the program.
    if s is None:
        print("> Could't open socket")
        sys.exit(1)

    # initialising values
    client_handler = None
    # start the loop to receive connections, accept them, create thread to handle the source of the connection (client),
    # move on to the next connection
    while True:
        # accept() returns two values, the first is a socket (client), the second is a list contains
        # the IP address of the source of the connection (client) and the port number
        client, addr = s.accept()
        print("[*] accept():\tAccepted connection from %s:%d" % (addr[0], addr[1]))
        # initialise the client handler thread and pass the new socket for the connection with the client and it's ipaddr:portno
        client_handler = handle_client(client, addr)
        # start the client handler thread
        client_handler.start()

main()
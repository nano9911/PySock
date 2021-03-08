import socket, sys

""" Author: Adnan Hleihel """

# Opritonal signal handler made for testing and fun, you can remove it
'''
import signal
def signal_handler(signal, frame):
    print("Interrupt by signal SIGINT (Ctrl + C)")
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)
'''

# optional cleanup and exit function, another stupid idea from me ^_-
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

# This function I made to put the data user inputs in a form to send.
# We don't use it if the user didn't gave any data (message, input).
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
    # take command line arguments as string for the ip, and cast the port number to an integer
    # to use in getaddrinfo() with                          # IPv4 or IPv6      # TCP Socket
    for res in socket.getaddrinfo(target_ip, target_port, socket.AF_UNSPEC, socket.SOCK_STREAM):
        af, socktype, proto, canonname, sa = res
        try:
            # socket() creates our socket from the data given in getaddrinfo() linked list
            s = socket.socket(af, socktype, proto)
            print("[*] socket():\tSocket created succefully.")
        # when socket() fails it raises an OSError exception
        except OSError as err:
            print("> socket():\tSocket creation failed with error %s" % err)
            s = None
            # not a critical failure, so move on test the next one
            continue
        
        # we don't use the SO_REUSEADDR because the client port will be chosen normally,
        # and it's not the taget for DOS attacks
        try:
            # try connect to the target server [sa is tuple containing (target_ip, targt_port)]
            s.connect(sa)
            print("[*] connect():\tConnected to %s:%d" % (target_ip,target_port))
        # when accept fails it raises an OSError exception
        except OSError as err:
            print("> connect():\tConnect to server failed with error: %s" % err)
            s = None
            # like socket()/bind()/listen() it's not a critical failure, so move on and test the next one
            continue
        break

    # if s == None this means it kept failing in socket() or connect() until the end of the for loop,
    # so we don't have any socket know, exit()
    if s is None:
        print("> Couldn't open socket")
        sys.exit(0)

    # initialising receiving and sending buffers and the msg object which we will use to represent
    # the byte objects by decoding them and save them in msg
    recvbuf = None
    sendbuf = message_creator("Hello Server")
    msg = None
    while True:
        try:
            # convert the message in the sendbuf to an byte abject to send it
            s.sendall(bytes(sendbuf, encoding="utf8"))
        # handling exceptions
        except (OSError, ConnectionResetError, ConnectionAbortedError, ConnectionError) as err:
            print("$ sendall() failed with error: %s" % err)
            break
        except:
            print("$ sendall failed with an unexpected error")
            break

        try:
            # call recv() with 1024 as an argument to take data from the socket queue with a maximum size of 1024 bytes
            recvbuf = s.recv(1024)
        # handling exceptions
        except (OSError, ConnectionResetError, ConnectionAbortedError, ConnectionError) as err:
            print("$ recv() failed with error: %s" % err)
            break
        except:
            print("$ recv() failed with an unexpected error")
            break

        if recvbuf == "" or recvbuf == None:
            print("$ Empt message received or connection closed")
            break

        # decode the received data from byte object to a string to print it as human readable in UTF-8 encoding by default
        msg = recvbuf.decode()
        print("\n> Message received from %s:\n%s" % (target_ip, msg))
        # Flush the received buffer for the next use
        recvbuf = None

        # let the user input the next message to be sent, check if it's empty or not, if so break the loop
        # and close the connection with server
        sendbuf = input("> Enter a message to send:")
        if len(sendbuf) == 0:
            break

        # put the (non empty message) in our form to be sent
        sendbuf = message_creator(sendbuf)

    print("Closing connection...\nClosing program...")
    s.close()
    sys.exit(0)

main(sys.argv)

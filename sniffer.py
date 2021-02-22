import socket

HOST = socket.gethostbyname(socket.gethostname())

s = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_IP)
s.bind((HOST,0))

s.setsockopt(socket.IPPROTO_IP, socket.IP_HDRINCL, 1)
s.ioctl(socket.SIO_RCVALL, socket.RCVALL_ON)

f = open("D:\PyTests\dumped.txt", "ab")
f.write(s.recvfrom(65565).decode())

s.ioctl(socket.SIO_RCVALL, socket.RCVALL_OFF)
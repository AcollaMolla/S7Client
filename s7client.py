import socket
import struct
import time
import sys

TCP_IP = '127.0.0.1'
TCP_PORT = 102
BUFFER_SIZE = 1024
MESSAGE = b'Hello, world!'
RACK = 0
SLOT = 0

if len(sys.argv) > 1:
	conn = sys.argv[1].split("/")
	TCP_IP = conn[0]
	if len(conn) > 1 and conn[1]:
		RACK = conn[1]
	if len(conn) > 2 and conn[2]:
		SLOT = conn[2]

tpdu_value = {
	"7": 128,
	"8": 256,
	"9": 512,
	"10": 1024,
	"11": 2048,
	"12": 4096,
	"13": 8192
}

class TPKT:
	def __init__(self, version=3, reserved=0, length_high=0, length_low=22):
		self.version = version
		self.reserved = reserved
		self.length_high = length_high
		self.length_low = length_low

class COTP:
	def __init__(self, length=17, pdutype=224, destref_high=0, destref_low=0, srcref_high=0, srcref_low=1, cotpclass=0, paramtpdusize=192, paramlength=1, tpdusize=10, srctsap=193, paramlength2=2, srctsap_high=1, srctsap_low=0, paramdsttsap=194, paramlength3=2, dsttsap_high=1, dsttsap_low=int(SLOT)):
		self.length = length
		self.pdutype = pdutype
		self.destref_high = destref_high
		self.destref_low = destref_low
		self.srcref_high = srcref_high
		self.srcref_low = srcref_low
		self.cotpclass = cotpclass
		self.paramtpdusize = paramtpdusize
		self.paramlength = paramlength
		self.tpdusize = tpdusize
		self.srctsap = srctsap
		self.paramlength2 = paramlength2
		self.srctsap_high = srctsap_high
		self.srctsap_low = srctsap_low
		self.paramdsttsap = paramdsttsap
		self.paramlength3 = paramlength3
		self.dsttsap_high = dsttsap_high
		self.dsttsap_low = dsttsap_low

tpkt_msg = []
cotp_msg = []
tpkt = TPKT()
cotp = COTP()
for v in tpkt.__dict__.values():
	tpkt_msg.append(v)

for v in cotp.__dict__.values():
	cotp_msg.append(v)

msg = tpkt_msg + cotp_msg

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((TCP_IP, TCP_PORT))
s.send(bytes(msg))
print("-----------------")
data = s.recv(BUFFER_SIZE)
print("CR Reply:")
tpkt_rep = TPKT(data[0], data[1], data[2], data[3])
print("TPKT header:")
print("TPKT version: " + str(getattr(tpkt_rep, "version")))
print("TPKT reserved: " + str(getattr(tpkt_rep, "reserved")))
print("TPKT length: " + str(getattr(tpkt_rep, "length_high")*256 + getattr(tpkt_rep, "length_low")))
cotp_rep = COTP(length=data[4], tpdusize=data[13])
print("COTP header:")
print("COTP length: " + str(getattr(cotp_rep, "length")))
print("COTP PDU size: " + str(tpdu_value.get(str(getattr(cotp_rep, "tpdusize")))))
#time.sleep(1)
s.close()
exit()
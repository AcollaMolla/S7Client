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

class S7_HEADER:
	def __init__(self, protocol_id=50, rosctr_job=1, red_id_high=0, red_id_low=0, protocol_data_unit_ref_high=0, protocol_data_unit_ref_low=0, parameter_length_high=0, parameter_length_low=8, data_length_high=0, data_length_low=0):
		self.protocol_id = protocol_id
		self.rosctr_job = rosctr_job
		self.red_id_high = red_id_high
		self.red_id_low = red_id_low
		self.protocol_data_unit_ref_high = protocol_data_unit_ref_high
		self.protocol_data_unit_ref_low = protocol_data_unit_ref_low
		self.parameter_length_high = parameter_length_high
		self.parameter_length_low = parameter_length_low
		self.data_length_high = data_length_high
		self.data_length_low = data_length_low

class S7_PARAM:
	def __init__(self, function=240, reserved=0, max_amq_calling_high=0, max_amq_calling_low=1, max_amq_caller_high=0, max_amq_caller_low=1, pdu_length_high=1, pdu_length_low=224):
		self.function = function
		self.reserved = 0
		self.max_amq_calling_high = max_amq_calling_high
		self.max_amq_calling_low = max_amq_calling_low
		self.max_amq_caller_high = max_amq_caller_high
		self.max_amq_caller_low = max_amq_caller_low
		self.pdu_length_high = pdu_length_high
		self.pdu_length_low = pdu_length_low

def SetupCommunication():
	tpkt_msg = []
	cotp_msg = []
	s7_header_msg = []
	s7_param_msg = []
	tpkt = TPKT(length_low=25)
	cotp = COTP(length=2, pdutype=240, destref_high=128) #Seems like only the high bits matter now
	s7_header = S7_HEADER(protocol_id=50, rosctr_job=1, parameter_length_high=0, parameter_length_low=8)
	s7_param = S7_PARAM()

	for v in tpkt.__dict__.values():
		tpkt_msg.append(v)

	for v in s7_header.__dict__.values():
		s7_header_msg.append(v)

	for v in s7_param.__dict__.values():
		s7_param_msg.append(v)

	s7_msg = s7_header_msg + s7_param_msg

	cotp_msg.append(cotp.__dict__.get("length"))
	cotp_msg.append(cotp.__dict__.get("pdutype"))
	cotp_msg.append(cotp.__dict__.get("destref_high"))
	msg = tpkt_msg + cotp_msg + s7_msg
	return msg

def ConnectRequest():
	tpkt_msg = []
	cotp_msg = []
	tpkt = TPKT()
	cotp = COTP()
	for v in tpkt.__dict__.values():
		tpkt_msg.append(v)

	for v in cotp.__dict__.values():
		cotp_msg.append(v)

	msg = tpkt_msg + cotp_msg
	return msg

def VerifyCotp(header, stage):
	if stage == 0:
		if (len(header)-1) == header[0]:
			if header[1] == 208:
				print("PLC accepted connection!")
		else:
			print("Malformed COTP")

def Verify(data, stage):
	tpkt_header = data[:4]
	if tpkt_header[2]*256 + tpkt_header[3] != len(data):
		print("Malformed packet")
	cotp_header = data[4:]
	VerifyCotp(cotp_header, stage)

def SendAndReceive(msg, s, stage):
	s.send(bytes(msg))
	data = s.recv(BUFFER_SIZE)
	Verify(data, stage)
	return data

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((TCP_IP, TCP_PORT))
msg = ConnectRequest()
print("Connecting to PLC...")
SendAndReceive(msg, s, 0)
msg = SetupCommunication() #Set up a S7COMM communication session
print("Initiate S7 communication...")
SendAndReceive(msg, s, 1)

#time.sleep(1)
s.close()
exit()
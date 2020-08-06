import socket
import struct
import time
import sys

TCP_IP = '127.0.0.1'
TCP_PORT = 102
BUFFER_SIZE = 1024

RACK = 0
SLOT = 0
PDU_SIZE = 480

DB = 0
OFFSET = 0
LENGTH = 1

if len(sys.argv) > 1:
	conn = sys.argv[1].split("/")
	TCP_IP = conn[0]
	if len(conn) > 1 and conn[1]:
		RACK = conn[1]
	if len(conn) > 2 and conn[2]:
		SLOT = conn[2]
	if len(sys.argv) > 2:
		addr = sys.argv[2].split(".")
		if len(addr) > 2:
			DB = addr[0]
			OFFSET = addr[1]
			LENGTH = addr[2]
		else:
			print("Warning: Missing parameters for requested address! (<DB>.<OFFSET>.<LENGTH IN BYTES>)")
			print("Warning: Defaulting to DB=0, OFFSET=0, LENGTH=1")


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

class S7_PARAM_READ_VAR:
	def __init__(self, function=4, item_count=1, variable_spec=18, addr_spec_len=10, syntax_id=16, transport_size=2, length_high=0, length_low=1, db_high=0, db_low=63, area=132, addr_high=0, addr_mid=0, addr_low=0):
		self.function = function
		self.item_count = item_count
		self.variable_spec = variable_spec
		self.addr_spec_len = addr_spec_len
		self.syntax_id = syntax_id
		self.transport_size = transport_size
		self.length_high = length_high
		self.length_low = length_low
		self.db_high = db_high
		self.db_low = db_low
		self.area = area
		self.addr_high = addr_high
		self.addr_mid = addr_mid
		self.addr_low = addr_low

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

def ReadVarRequest(msg):
	msg = msg[:len(msg)-8] #Keep the same message as before, but remove S7 Parameters part (ie the last 8 bytes)
	s7_param_msg = []
	s7_param = S7_PARAM()
	msg[14] = 10
	db_high = int(0)
	db_low = int(DB)
	length_high = int(0)
	length_low = int(LENGTH)

	if len(DB) > 128:
		db_high = DB - 128

	if len(LENGTH) > 128:
		db_high = DB - 128

	s7_param = S7_PARAM_READ_VAR(function=4, item_count=1, variable_spec=18, addr_spec_len=10, syntax_id=16, transport_size=2, length_high=length_high, length_low=length_low, db_high=db_high, db_low=db_low, area=132, addr_high=0, addr_mid=0, addr_low=0)
	for v in s7_param.__dict__.values():
		s7_param_msg.append(v)
	msg[14] = len(s7_param_msg)
	msg[3] = len(msg) + len(s7_param_msg)
	msg = msg + s7_param_msg
	return msg


def VerifyS7(header):
	if header[1] == 3:
		print("PLC accepted S7 communication!")
	param_len = (header[6]*256) + header[7]
	params = header[-param_len:]
	pdu_size = (params[len(params)-2]*256) + params[len(params)-1]
	global PDU_SIZE
	PDU_SIZE = pdu_size
	print("PLC accepts a PDU of size: " + str(PDU_SIZE))


def VerifyCotp(header, stage):
	if stage == 0:
		if (len(header)-1) == header[0]:
			if header[1] == 208:
				print("PLC accepted connection!")
		else:
			print("Malformed COTP")
	if stage == 1:
		VerifyS7(header[3:])

def ReadData(data):
	data = data[7:]
	length = (data[8]*256) + data[9]
	data = data[-8:]
	if data[0] == 255:
		print("Successfully read value from PLC")
	length = int(((data[2]*256) + data[3])/8)
	value = data[-length:]
	value = bytes(value)
	value = struct.unpack('>f', value)
	print()
	print("DB" + DB + "." + "DBD" + OFFSET + ": " + str(value))

def Verify(data, stage):
	tpkt_header = data[:4]
	if tpkt_header[2]*256 + tpkt_header[3] != len(data):
		print("Malformed packet")
	cotp_header = data[4:]
	VerifyCotp(cotp_header, stage)
	if stage == 2:
		ReadData(data)

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
print("Sending JOB request...")
msg = ReadVarRequest(msg)
SendAndReceive(msg, s, 2)

#time.sleep(1)
s.close()
exit()
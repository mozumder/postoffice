import asyncio
#import struct
#import bitstruct
#import bitstruct.c as bitstruct
import cbitstruct as bitstruct
import hexdump

from .codes import *

header = bitstruct.compile(header_format)
question = bitstruct.compile(question_format)
answer = bitstruct.compile(answer_format)
opt = bitstruct.compile(opt_format)

#header_format = '!H2B4H'
class DNSServerProtocol:
    def connection_made(self, transport):
        self.transport = transport


    def datagram_received(self, data, addr):
#        message = data.decode()
        print(f'Got datagram from {addr} with length {len(data)}')
        hexdump.hexdump(data)
        print(f'HEADER: Starting byte 1')
        ID_message_id, QR_response, OPCODE_operation, AA_authoritative_answer, TC_truncation, RD_recursion_desired, RA_recursion_available, AD_authentic_data, CD_checking_disabled, RCODE_response_code, QDCOUNT_questions_count, ANCOUNT_answers_count, NSCOUNT_authoritative_answers_count, ARCOUNT_additional_records_count = header.unpack(data)
        print(f'  {ID_message_id=}')
        print(f'  {QR_response=}')
        print(f'  {OPCODE_operation=} ({OPCODE[OPCODE_LOOKUP[OPCODE_operation]]})')
        print(f'  {AA_authoritative_answer=}')
        print(f'  {TC_truncation=}')
        print(f'  {RD_recursion_desired=}')
        print(f'  {RA_recursion_available=}')
        print(f'  {AD_authentic_data=}')
        print(f'  {CD_checking_disabled=}')
        print(f'  {RCODE_response_code=} ({RCODE[RCODE_LOOKUP[RCODE_response_code]]})')
        print(f'  {QDCOUNT_questions_count=}')
        print(f'  {ANCOUNT_answers_count=}')
        print(f'  {NSCOUNT_authoritative_answers_count=}')
        print(f'  {ARCOUNT_additional_records_count=}')
        names = {}
        offset = 12
        question_label_list = []
        answer_label_list = []
        authority_label_list = []
        additional_label_list = []
        question_info = None
        answer_info = None
        authority_info = None
        additional_info = None
        for c in range(QDCOUNT_questions_count):
            print(f'QUESTION NAME: Starting byte {offset+1}')
            question_label_list = []
            namestart = offset
            while data[offset] != 0:
                if data[offset] & 192 == 0:
                    question_label_list.append(data[offset+1:offset+1+data[offset]])
                    offset = offset + data[offset] + 1
            names[namestart] = question_label_list
            print(f'  {question_label_list=}')
            offset = offset + 1
            print(f'QUESTION TYPE & CLASS: Starting byte {offset+1}')
            qtype, qclass = question.unpack(data[offset:offset+4])
            print(f'  {qtype=} ({RR_TYPE[RR_TYPE_LOOKUP[qtype]]})')
            print(f'  {qclass=} ({DNS_CLASS[DNS_CLASS_LOOKUP[qclass]]})')
            offset = offset + 4
        for c in range(ANCOUNT_answers_count):
            print(f'ANSWER NAME: Starting byte {offset+1}')
            answer_label_list = []
            namestart = offset
            while data[offset] != 0 or data[offset]:
                if data[offset] & 192 == 0:
                    label_list.append(data[offset+1:offset+1+data[offset]])
                    offset = offset + data[offset] + 1
            if data[offset] & 192 == 192:
                answer_label_list = names[data[offset] & 63]
            if answer_label_list:
                names[namestart] = answer_label_list
            print(f'  {answer_label_list=}')
            offset = offset + 1
            print(f'ANSWER TYPE & CLASS: Starting byte {offset+1}')
            atype, aclass, attl, alength = answer.unpack(data[offset:offset+10])
            print(f'  {atype=} ({RR_TYPE[RR_TYPE_LOOKUP[atype]]})')
            print(f'  {aclass=} ({DNS_CLASS[DNS_CLASS_LOOKUP[aclass]]})')
            print(f'  {attl=}')
            print(f'  {alength=}')
            offset = offset + 10 + alength
        for c in range(NSCOUNT_authoritative_answers_count):
            print(f'AUTHORITY NAME: Starting byte {offset+1}')
            authority_label_list = []
            namestart = offset
            while data[offset] != 0:
                if data[offset] & 192 == 0:
                    label_list.append(data[offset+1:offset+1+data[offset]])
                    offset = offset + data[offset] + 1
            if data[offset] & 192 == 192:
                authority_label_list = names[data[offset] & 63]
            if authority_label_list:
                names[namestart] = authority_label_list
            print(f'  {authority_label_list=}')
            offset = offset + 1
            print(f'AUTHORITY TYPE & CLASS: Starting byte {offset+1}')
            ntype, nclass, nttl, nlength = answer.unpack(data[offset:offset+10])
            print(f'  {ntype=} ({RR_TYPE[RR_TYPE_LOOKUP[ntype]]})')
            print(f'  {nclass=} ({DNS_CLASS[DNS_CLASS_LOOKUP[nclass]]})')
            print(f'  {nttl=}')
            print(f'  {nlength=}')
            offset = offset + 10 + nlength
        for c in range(ARCOUNT_additional_records_count):
            print(f'ADDITIONAL NAME: Starting byte {offset+1}')
            additional_label_list = []
            namestart = offset
            while data[offset] != 0:
                if data[offset] & 192 == 0:
                    label_list.append(data[offset+1:offset+1+data[offset]])
                    offset = offset + data[offset] + 1
            if data[offset] & 192 == 192:
                additional_label_list = names[data[offset] & 63]
            if additional_label_list:
                names[namestart] = additional_label_list
            print(f'  {additional_label_list=}')
            offset = offset + 1
            print(f'ADDITIONAL TYPE & CLASS: Starting byte {offset+1}')
            xtype, xclass, xttl, xlength = answer.unpack(data[offset:offset+10])
            print(f'  {xtype=} ({RR_TYPE[RR_TYPE_LOOKUP[xtype]]})')
            print(f'  {xlength=}')
            if xtype == 41:
                print(f'OPT EDNS')
                xrcode, EDNS_version, DO_DNSSEC_Answer_OK = opt.unpack(data[offset+4:offset+8])
                OPT_XRCODE = xrcode << 4 | RCODE_response_code
                udp_payload_size = xclass
                print(f'  {udp_payload_size=}')
                print(f'  {xrcode=}')
                print(f'  {EDNS_version=}')
                print(f'  {DO_DNSSEC_Answer_OK=}')
            else:
                print(f'  {xclass=} ({DNS_CLASS[DNS_CLASS_LOOKUP[xclass]]})')
                print(f'  {xttl=}')
            offset = offset + 10 + xlength
        print(f'Processed {offset} bytes')

        print(f'NAMES: {names}' )
        print(f'Sending data to {addr}')
        self.transport.sendto(data, addr)


async def DNSServer(ip_address='127.0.0.1', port=53):
    print("Starting UDP server")

    # Get a reference to the event loop as we plan to use
    # low-level APIs.
    loop = asyncio.get_running_loop()

    # One protocol instance will be created to serve all
    # client requests.
    transport, protocol = await loop.create_datagram_endpoint(
        lambda: DNSServerProtocol(),
        local_addr=(ip_address, port))
#        local_addr=('127.0.0.1', 9999))

    try:
        await asyncio.sleep(3600)  # Serve for 1 hour.
    finally:
        transport.close()



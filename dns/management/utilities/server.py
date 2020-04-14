import asyncio
#import struct
#import bitstruct
#import bitstruct.c as bitstruct
import cbitstruct as bitstruct

#header_format = '!H2B4H'
header_format = '>u16b1u4b1b1b1b1p3u4u16u16u16u16'
header = bitstruct.compile(header_format)
question_format = '>u16u16'
question = bitstruct.compile(question_format)
answer_format = '>u16u16u32u16'
answer = bitstruct.compile(answer_format)

class DNSServerProtocol:
    def connection_made(self, transport):
        self.transport = transport

    def datagram_received(self, data, addr):
#        message = data.decode()
        message = header.unpack(data)
        print(f'Got datagram with length: {len(data)}')
        print(f'HEADER: Starting byte 0')
#        message = struct.unpack(header_format,data[:12])
#        print('Received %r from %s' % (message, addr))

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
        for c in range(message[8]):
            print(f'QUESTION NAME: Starting byte {offset}')
            question_label_list = []
            namestart = offset
            while data[offset] != 0:
                if data[offset] & 192 == 0:
                    question_label_list.append(data[offset+1:offset+1+data[offset]])
                    offset = offset + data[offset] + 1
            names[namestart] = question_label_list
            offset = offset + 1
            print(f'QUESTION TYPE & CLASS: Starting byte {offset}')
            question_info = question.unpack(data[offset:offset+4])
            offset = offset + 4
        for c in range(message[9]):
            print(f'ANSWER NAME: Starting byte {offset}')
            answer_label_list = []
            namestart = offset
            while data[offset] != 0 or data[offset]:
                if data[offset] & 192 == 0:
                    label_list.append(data[offset+1:offset+1+data[offset]])
                    offset = offset + data[offset] + 1
            if data[offset] & 192 == 192:
                answer_label_list = names[data[offset] & 63]
            names[namestart] = answer_label_list
            offset = offset + 1
            print(f'ANSWER TYPE & CLASS: Starting byte {offset}')
            answer_info = answer.unpack(data[offset:offset+10])
            offset = offset + 10
        for c in range(message[10]):
            print(f'AUTHORITY NAME: Starting byte {offset}')
            authority_label_list = []
            namestart = offset
            while data[offset] != 0:
                if data[offset] & 192 == 0:
                    label_list.append(data[offset+1:offset+1+data[offset]])
                    offset = offset + data[offset] + 1
            if data[offset] & 192 == 192:
                authority_label_list = names[data[offset] & 63]
            names[namestart] = authority_label_list
            offset = offset + 1
            print(f'AUTHORITY TYPE & CLASS: Starting byte {offset}')
            authority_info = answer.unpack(data[offset:offset+10])
            offset = offset + 10
        for c in range(message[11]):
            print(f'ADDITIONAL NAME: Starting byte {offset}')
            additional_label_list = []
            namestart = offset
            while data[offset] != 0:
                if data[offset] & 192 == 0:
                    label_list.append(data[offset+1:offset+1+data[offset]])
                    offset = offset + data[offset] + 1
            if data[offset] & 192 == 192:
                additional_label_list = names[data[offset] & 63]
            names[namestart] = additional_label_list
            offset = offset + 1
            print(f'ADDITIONAL TYPE & CLASS: Starting byte {offset}')
            additional_info = answer.unpack(data[offset:offset+10])
            offset = offset + 10
        print(f'Starting byte {offset}')


        print(f'Received from {addr}: {message}' )
        print(f'QUESTION: {question_label_list} {question_info}' )
        print(f'ANSWER: {answer_label_list} {answer_info}' )
        print(f'AUTHORITY: {authority_label_list} {authority_info}' )
        print(f'ADDITIONAL: {additional_label_list} {additional_info}' )
        print(f'NAMES: {names}' )
        print('Send %r to %s' % (message, addr))
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



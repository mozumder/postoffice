import asyncio
import functools
import operator

import hexdump
import cbitstruct as bitstruct
from .db import db_lookup
from .codes import *
from dns.models import A_Record, Domain

header = bitstruct.compile(header_format)
question = bitstruct.compile(question_format)
answer = bitstruct.compile(answer_format)
opt = bitstruct.compile(opt_format)

async def Query(pool, data, addr, transport):
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
    queries = []
    answers = []
    authorities = []
    additionals = []
    options = []
    for c in range(QDCOUNT_questions_count):
        print(f'QUESTION NAME: Starting byte {offset+1}')
        question_label_list = []
        namestart = offset
        while data[offset] != 0:
            if data[offset] & 192 == 0:
                question_label_list.append(data[offset+1:offset+1+data[offset]].decode("utf-8"))
                offset = offset + data[offset] + 1
        print(f'{question_label_list=}')
        names[namestart] = question_label_list
        offset = offset + 1
        print(f'QUESTION TYPE & CLASS: Starting byte {offset+1}')
        qtype, qclass = question.unpack(data[offset:offset+4])
        queries.append((question_label_list, qtype, qclass))
        offset = offset + 4
    for c in range(ANCOUNT_answers_count):
        print(f'ANSWER NAME: Starting byte {offset+1}')
        answer_label_list = []
        namestart = offset
        while data[offset] != 0 or data[offset]:
            if data[offset] & 192 == 0:
                label_list.append(data[offset+1:offset+1+data[offset]].decode("utf-8"))
                offset = offset + data[offset] + 1
        if data[offset] & 192 == 192:
            answer_label_list = names[data[offset] & 63]
        if answer_label_list:
            names[namestart] = answer_label_list
        offset = offset + 1
        print(f'ANSWER TYPE & CLASS: Starting byte {offset+1}')
        atype, aclass, attl, alength = answer.unpack(data[offset:offset+10])
        answers.append((answer_label_list, atype, aclass, attl, alength, data[offset+10:offset+10+alength]))
        offset = offset + 10 + alength
    for c in range(NSCOUNT_authoritative_answers_count):
        print(f'AUTHORITY NAME: Starting byte {offset+1}')
        authority_label_list = []
        namestart = offset
        while data[offset] != 0:
            if data[offset] & 192 == 0:
                label_list.append(data[offset+1:offset+1+data[offset]].decode("utf-8"))
                offset = offset + data[offset] + 1
        if data[offset] & 192 == 192:
            authority_label_list = names[data[offset] & 63]
        if authority_label_list:
            names[namestart] = authority_label_list
        offset = offset + 1
        print(f'AUTHORITY TYPE & CLASS: Starting byte {offset+1}')
        ntype, nclass, nttl, nlength = answer.unpack(data[offset:offset+10])
        authorities.append((authority_label_list, ntype, nclass, nttl, nlength, data[offset+10:offset+10+nlength]))
        offset = offset + 10 + nlength
    for c in range(ARCOUNT_additional_records_count):
        print(f'ADDITIONAL NAME: Starting byte {offset+1}')
        additional_label_list = []
        namestart = offset
        while data[offset] != 0:
            if data[offset] & 192 == 0:
                label_list.append(data[offset+1:offset+1+data[offset]].decode("utf-8"))
                offset = offset + data[offset] + 1
        if data[offset] & 192 == 192:
            additional_label_list = names[data[offset] & 63]
        if additional_label_list:
            names[namestart] = additional_label_list
        offset = offset + 1
        print(f'ADDITIONAL TYPE & CLASS: Starting byte {offset+1}')
        xtype, xclass, xttl, xlength = answer.unpack(data[offset:offset+10])
        additionals.append((additional_label_list, xtype, xclass, xttl, data[offset+4:offset+8], xlength, data[offset+10:offset+10+xlength]))
        offset = offset + 10 + xlength

    for record in additionals:
        if record[1] == 41:
            print(f'OPT EDNS')
            xrcode, EDNS_version, DO_DNSSEC_Answer_OK = opt.unpack(record[4])
            OPT_XRCODE = xrcode << 4 | RCODE_response_code
            options.append((record[2],OPT_XRCODE,EDNS_version,DO_DNSSEC_Answer_OK,record[5],data))

    for record in queries:
        print(f'QUERY:')
        print(f'  label={record[0]}')
        print(f'  type={record[1]} ({RR_TYPE[RR_TYPE_LOOKUP[record[1]]]})')
        print(f'  class={record[2]} ({DNS_CLASS[DNS_CLASS_LOOKUP[record[2]]]})')
    for record in answers:
        print(f'ANSWER')
        print(f'  label={record[0]}')
        print(f'  type={record[1]} ({RR_TYPE[RR_TYPE_LOOKUP[record[1]]]})')
        print(f'  class={record[2]} ({DNS_CLASS[DNS_CLASS_LOOKUP[record[2]]]})')
        print(f'  ttl={record[3]}')
        print(f'  data_length= {record[4]}')
    for record in authorities:
        print(f'AUTHORITY')
        print(f'  label={record[0]}')
        print(f'  type={record[1]} ({RR_TYPE[RR_TYPE_LOOKUP[record[1]]]})')
        print(f'  class={record[2]} ({DNS_CLASS[DNS_CLASS_LOOKUP[record[2]]]})')
        print(f'  ttl={record[3]}')
        print(f'  data_length= {record[4]}')
    for record in additionals:
        print(f'ADDITIONAL')
        print(f'  label={record[0]}')
        print(f'  type=={record[1]} ({RR_TYPE[RR_TYPE_LOOKUP[record[1]]]})')
        print(f'  class={record[2]} ({DNS_CLASS[DNS_CLASS_LOOKUP[record[2]]]})')
        print(f'  ttl={record[3]}')
        print(f'  data_length={record[5]}')
    for record in options:
        print(f'OPTIONS')
        print(f'  udp_payload_size={record[0]}')
        print(f'  OPT_XRCODE={record[1]}')
        print(f'  EDNS_version={record[2]}')
        print(f'  DO_DNSSEC_Answer_OK={record[3]}')
        print(f'  length={record[4]}')
    
    tasks =  [db_lookup(pool,query) for query in queries]
    results = functools.reduce(operator.iconcat, await asyncio.gather(*tasks), [])
    if results == []:
        data = None
    else:
        data = 1
    header_format = '>u16b1u4b1b1b1b1p1b1b1u4u16u16u16u16'
    QR_response = True
    AA_authoritative_answer = True
    QDCOUNT_questions_count = 0
    ANCOUNT_answers_count = len(results)
    data = header.pack(ID_message_id, QR_response, OPCODE_operation, AA_authoritative_answer, TC_truncation, RD_recursion_desired, RA_recursion_available, AD_authentic_data, CD_checking_disabled, RCODE_response_code, QDCOUNT_questions_count, ANCOUNT_answers_count, NSCOUNT_authoritative_answers_count, ARCOUNT_additional_records_count)
    transport.sendto(data, addr)
    print(results)

async def respond(self, query):
    result = await self.responder(query)
    return result

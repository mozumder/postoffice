import asyncio
import functools
import operator

import hexdump
import cbitstruct as bitstruct
from .db import db_lookup
from .codes import *
from dns.models import A_Record, Domain

header_struct = bitstruct.compile(header_format)
question_struct = bitstruct.compile(question_format)
answer_struct = bitstruct.compile(answer_format)
opt_struct = bitstruct.compile(opt_format)
label_struct = bitstruct.compile(label_format)
soa_struct = bitstruct.compile(soa_format)

async def Query(pool, data, addr, transport):
#        message = data.decode()

    # MARK: Header
    # TODO: Handle OPCODE_operation
    # TODO: Handle RD_recursion_desired
    # TODO: Handle QR_response
    # TODO: Handle TC_truncation
    # TODO: Handle AD_authentic_data
    # TODO: Handle CD_checking_disabled
    # FIXME: Check QDCOUNT_questions_count upper and lower limit
    # FIXME: Check ANCOUNT_answers_count upper and lower limit
    # FIXME: Check NSCOUNT_authoritative_answers_count upper and lower limit
    # FIXME: Check ARCOUNT_additional_records_count upper and lower limit
    # FIXME: Check over/under message length
    hexdump.hexdump(data)
    print(f'HEADER: Starting byte 1')
    ID_message_id, QR_response, OPCODE_operation, AA_authoritative_answer, TC_truncation, RD_recursion_desired, RA_recursion_available, AD_authentic_data, CD_checking_disabled, RCODE_response_code, QDCOUNT_questions_count, ANCOUNT_answers_count, NSCOUNT_authoritative_answers_count, ARCOUNT_additional_records_count = header_struct.unpack(data)
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
        qtype, qclass = question_struct.unpack(data[offset:offset+4])
        queries.append((qtype, qclass, data[namestart:offset], question_label_list))
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
        atype, aclass, attl, alength = answer_struct.unpack(data[offset:offset+10])
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
        ntype, nclass, nttl, nlength = answer_struct.unpack(data[offset:offset+10])
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
        xtype, xclass, xttl, xlength = answer_struct.unpack(data[offset:offset+10])
        additionals.append((additional_label_list, xtype, xclass, xttl, data[offset+4:offset+8], xlength, data[offset+10:offset+10+xlength]))
        offset = offset + 10 + xlength

    for record in additionals:
        if record[1] == 41:
            print(f'OPT EDNS')
            xrcode, EDNS_version, DO_DNSSEC_Answer_OK = opt_struct.unpack(record[4])
            OPT_XRCODE = xrcode << 4 | RCODE_response_code
            options.append((record[2],OPT_XRCODE,EDNS_version,DO_DNSSEC_Answer_OK,record[5],data))

    for record in queries:
        print(f'QUERY:')
        print(f'  label={record[2]}')
        print(f'  type={record[0]} ({RR_TYPE[RR_TYPE_LOOKUP[record[0]]]})')
        print(f'  class={record[1]} ({DNS_CLASS[DNS_CLASS_LOOKUP[record[1]]]})')
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
    
    # MARK: DB Lookup
    tasks =  [db_lookup(pool,query) for query in queries]

    results = await asyncio.gather(*tasks)


    # MARK: - Generate Response
    # TODO: Compress labels through referencing
    # TODO: Generate OPT Additional Response
    # TODO: Generate CNAME Resource Record
    # TODO: Generate MX Resource Record
    # TODO: Generate SRV Resource Record
    # TODO: Generate PTR Resource Record
    # TODO: Generate AAAA Resource Record
    # TODO: Generate CAA Resource Record
    # TODO: Generate IXFR Resource Transfer
    # TODO: Generate TXFR Resource Transfer

    questions_data = []
    answers_data = []
    authority_data = []
    additional_data = []

    QR_response = True
    QDCOUNT_questions_count = len(results)
    NSCOUNT_authoritative_answers_count = 0
    ARCOUNT_additional_records_count = 0
    RA_recursion_available = True
    AD_authentic_data = False
    AA_authoritative_answer  = False
    if OPCODE_operation == OPCODE_QUERY:
        offset = 12
        questions = []
        if len(results) > 0:
            if len(results[0]) > 0:
                AA_authoritative_answer = True if results[0][0][3] != None else False
        for i in range(len(queries)):
            query = queries[i]
            question = query[2] + question_struct.pack(query[0], query[1])
            questions_data.append(question)
            if len(results) > 0:
                answer_label = label_struct.pack(offset)
                for r in range(len(results[i])):
                    record = results[i][r]
                    if record[0] == RR_TYPE_A:
                        RLENGTH = 4
                        RDATA = record[2].packed
                        print(f'A IP_Address={RDATA[0]}.{RDATA[1]}.{RDATA[2]}.{RDATA[3]} ttl={record[1]}')
                        response_data = answer_label + answer_struct.pack(record[0], DNS_CLASS_INTERNET, record[1], RLENGTH) + RDATA
                        answers_data.append(response_data)
                    elif record[0] == RR_TYPE_AAAA:
                        RLENGTH = 16
                        RDATA = record[2].packed
                        print(f'A IP_Address={RDATA[0]}.{RDATA[1]}.{RDATA[2]}.{RDATA[3]} ttl={record[1]}')
                        response_data = answer_label + answer_struct.pack(record[0], DNS_CLASS_INTERNET, record[1], RLENGTH) + RDATA
                        answers_data.append(response_data)
                    elif record[0] == RR_TYPE_NS:
                        domainlabel = b''
                        domainnames = record[3].split(".")
                        for label in domainnames:
                            domainlabel = domainlabel + len(label).to_bytes(1, byteorder='big') + bytes(label, 'utf-8')
                        domainlabel = domainlabel + b'\0'
                        domainnameoffset = query[2].find(domainlabel)
                        if domainnameoffset != -1:
                            domainlabel = label_struct.pack(offset+domainnameoffset)
                        nslabel = b''
                        nslabels = record[4].split(".")
                        for label in nslabels:
                            nslabel = nslabel + len(label).to_bytes(1, byteorder='big') + bytes(label, 'utf-8')
                        nslabel = nslabel + b'\0'
                        RLENGTH = len(nslabel)
                        print(f'NS Name={record[4]} ttl={record[1]}')
                        response_data = domainlabel + answer_struct.pack(record[0], DNS_CLASS_INTERNET, record[1], RLENGTH) + nslabel
                        if query[0] == RR_TYPE_NS:
                            answers_data.append(response_data)
                        else:
                            authority_data.append(response_data)
                    elif record[0] == RR_TYPE_SOA:
                        print(record)
                        domainlabel = b''
                        domainnames = record[3].split(".")
                        for label in domainnames:
                            domainlabel = domainlabel + len(label).to_bytes(1, byteorder='big') + bytes(label, 'utf-8')
                        domainlabel = domainlabel + b'\0'
                        domainnameoffset = query[2].find(domainlabel)
                        if domainnameoffset != -1:
                            domainlabel = label_struct.pack(offset+domainnameoffset)
                        nslabel = b''
                        nslabels = record[4].split(".")
                        for label in nslabels:
                            nslabel = nslabel + len(label).to_bytes(1, byteorder='big') + bytes(label, 'utf-8')
                        nslabel = nslabel + b'\0'
                        mailboxlabel = b''
                        mailboxlabels = record[5].replace('@','.').split(".")
                        for label in mailboxlabels:
                            mailboxlabel = mailboxlabel + len(label).to_bytes(1, byteorder='big') + bytes(label, 'utf-8')
                        mailboxlabel = mailboxlabel + b'\0'
                        RLENGTH = len(nslabel) + len(mailboxlabel) + 20
                        response_data = domainlabel + answer_struct.pack(record[0], DNS_CLASS_INTERNET, record[1], RLENGTH) + nslabel + mailboxlabel + soa_struct.pack(record[6],record[7],record[8],record[9],record[10])
                        if query[0] == RR_TYPE_SOA and domainnameoffset == 0:
                            answers_data.append(response_data)
                        else:
                            authority_data.append(response_data)
                offset = offset + len(queries[i]) + 4

    ANCOUNT_answers_count = len(answers_data)
    NSCOUNT_authoritative_answers_count = len(authority_data)
    data = header_struct.pack(ID_message_id, QR_response, OPCODE_operation, AA_authoritative_answer, TC_truncation, RD_recursion_desired, RA_recursion_available, AD_authentic_data, CD_checking_disabled, RCODE_response_code, QDCOUNT_questions_count, ANCOUNT_answers_count, NSCOUNT_authoritative_answers_count, ARCOUNT_additional_records_count)
    for question in questions_data:
        data = data + question
    for answer in answers_data:
        data = data + answer
    for authority in authority_data:
        data = data + authority
    transport.sendto(data, addr)


async def respond(self, query):
    result = await self.responder(query)
    return result

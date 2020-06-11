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
optanswer_struct = bitstruct.compile(optanswer_format)
label_struct = bitstruct.compile(label_format)
soa_struct = bitstruct.compile(soa_format)
mx_struct = bitstruct.compile(mx_format)
caa_flags_struct = bitstruct.compile(caa_flags_format)
srv_struct = bitstruct.compile(srv_format)

async def Query(pool, data):
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
#    hexdump.hexdump(data)
#    print(f'HEADER: Starting byte 1')
    ID_message_id, QR_response, OPCODE_operation, AA_authoritative_answer, TC_truncation, RD_recursion_desired, RA_recursion_available, AD_authentic_data, CD_checking_disabled, RCODE_response_code, QDCOUNT_questions_count, ANCOUNT_answers_count, NSCOUNT_authoritative_answers_count, ARCOUNT_additional_records_count = header_struct.unpack(data)
    test = False
    if test == True:
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
    dictionary = {}
    for c in range(QDCOUNT_questions_count):
#        print(f'QUESTION NAME: Starting byte {offset+1}')
        labels = []
        namestart = offset
        labeloffset = offset
        while data[offset] != 0:
            if data[offset] & 192 == 0:
                labels.append(data[offset+1:offset+1+data[offset]].decode("utf-8"))
                offset = offset + data[offset] + 1
#        print(f'{labels=}')
        names[namestart] = labels
        for i in range(len(labels)):
            dictionary[".".join(labels[i:len(labels)])] = labeloffset
            labeloffset = labeloffset + len(labels[i]) + 1
        offset = offset + 1
#        print(f'QUESTION TYPE & CLASS: Starting byte {offset+1}')
        qtype, qclass = question_struct.unpack(data[offset:offset+4])
        queries.append((qtype, qclass, data[namestart:offset], ".".join(labels)))
        offset = offset + 4
    for c in range(NSCOUNT_authoritative_answers_count):
#        print(f'AUTHORITY NAME: Starting byte {offset+1}')
        labels = []
        namestart = offset
        labeloffset = offset
        while data[offset] != 0:
            if data[offset] & 192 == 0:
                labels.append(data[offset+1:offset+1+data[offset]].decode("utf-8"))
                offset = offset + data[offset] + 1
#        print(f'{labels=}')
        names[namestart] = labels
        for i in range(len(labels)):
            dictionary[".".join(labels[i:len(labels)])] = labeloffset
            labeloffset = labeloffset + len(labels[i]) + 1
        offset = offset + 1
#        print(f'AUTHORITY TYPE & CLASS: Starting byte {offset+1}')
        ntype, nclass, nttl, nlength = answer_struct.unpack(data[offset:offset+10])
        authorities.append((authority_label_list, ntype, nclass, nttl, nlength, data[offset+10:offset+10+nlength]))
        offset = offset + 10 + nlength
    for c in range(ARCOUNT_additional_records_count):
#        print(f'ADDITIONAL NAME: Starting byte {offset+1}')
        labels = []
        namestart = offset
        labeloffset = offset
        while data[offset] != 0:
            if data[offset] & 192 == 0:
                labels.append(data[offset+1:offset+1+data[offset]].decode("utf-8"))
                offset = offset + data[offset] + 1
#        print(f'{labels=}')
        names[namestart] = labels
        for i in range(len(labels)):
            dictionary[".".join(labels[i:len(labels)])] = labeloffset
            labeloffset = labeloffset + len(labels[i]) + 1
        offset = offset + 1
#        print(f'ADDITIONAL TYPE & CLASS: Starting byte {offset+1}')
        xtype, xclass, xttl, xlength = answer_struct.unpack(data[offset:offset+10])
        additionals.append((additional_label_list, xtype, xclass, xttl, data[offset+4:offset+8], xlength, data[offset+10:offset+10+xlength]))
        offset = offset + 10 + xlength
    for record in additionals:
        if record[1] == 41:
#            print(f'OPT EDNS')
            xrcode, EDNS_version, DO_DNSSEC_Answer_OK = opt_struct.unpack(record[4])
            OPT_XRCODE = xrcode << 4 | RCODE_response_code
            options.append((record[2],OPT_XRCODE,EDNS_version,DO_DNSSEC_Answer_OK,record[5],data))
    if test == True:
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
            print(f'  data_length={record[6]}')
        for record in options:
            print(f'OPTIONS')
            print(f'  udp_payload_size={record[0]}')
            print(f'  OPT_XRCODE={record[1]}')
            print(f'  EDNS_version={record[2]}')
            print(f'  DO_DNSSEC_Answer_OK={record[3]}')
            print(f'  length={record[4]}')
    
    # MARK: DNS Lookup
    if QR_response == False:
        if len(queries)>0:
            data = await DNSLookup(pool, queries, dictionary, ID_message_id, OPCODE_operation, TC_truncation, RD_recursion_desired, CD_checking_disabled, options)
        else:
            data = header_struct.pack(ID_message_id, QR_response, OPCODE_operation, AA_authoritative_answer, TC_truncation, RD_recursion_desired, RA_recursion_available, AD_authentic_data, CD_checking_disabled, RCODE_response_code, 0, 0, 0, ARCOUNT_additional_records_count)
    else:
        RCODE_response_code = 4
        data = header_struct.pack(ID_message_id, QR_response, OPCODE_operation, AA_authoritative_answer, TC_truncation, RD_recursion_desired, RA_recursion_available, AD_authentic_data, CD_checking_disabled, RCODE_response_code, 0, 0, 0, ARCOUNT_additional_records_count)
    return data

async def DNSLookup(pool, queries, dictionary, ID_message_id, OPCODE_operation, TC_truncation, RD_recursion_desired, CD_checking_disabled, options):
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

    # MARK: - Lookup Database
    tasks =  [db_lookup(pool,query) for query in queries]
    results = await asyncio.gather(*tasks)

    question_results = []
    answer_results = []
    authority_results = []
    additional_results = []

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
        if results[0] != -1:
            if len(results) > 0:
                if len(results[0]) > 0:
                    AA_authoritative_answer = True if results[0][0][3] != None else False
        RCODE_response_code = 3
        for i in range(len(queries)):
            query = queries[i]
            if results[0] == -1:
                RCODE_response_code = 4
            elif len(results) > 0:
                answer_label = label_struct.pack(offset)
                for r in range(len(results[i])):
                    record = results[i][r]
                    if record[1] == True:
                        RCODE_response_code = 0
                    if record[0] == RR_TYPE_A or record[0] == RR_TYPE_AAAA:
                        RDATA = record[12].packed
                        print(f' name={record[11]} IP_Address={record[12]}')
                        if query[0] == RR_TYPE_MX or query[0] == RR_TYPE_SRV:
                            additional_results.append((record[0], record[3], record[11], RDATA))
                        elif record[11] != None:
                            answer_results.append((record[0], record[3], record[11], RDATA))
                        else:
                            answer_results.append((record[0], record[3], query[3], RDATA))
                    elif record[0] == RR_TYPE_CNAME:
                        print(f'  CNAME Name={record[11]}')
                        answer_results.append((record[0], record[3], query[3], record[11]))
                    elif record[0] == RR_TYPE_PTR:
                        print(f'  PTR Name={record[11]}')
                        answer_results.append((record[0], record[3], query[3], record[11]))
                    elif record[0] == RR_TYPE_CAA:
                        print(f'  CAA Tag={record[12]} Value={record[11]}')
                        rdata = caa_flags_struct.pack(record[13])
                        rdata = rdata + len(record[12]).to_bytes(1, byteorder='big') + bytes(record[12], 'utf-8') + bytes(record[11], 'utf-8')
                        answer_results.append((record[0], record[3], query[3], rdata))
                    elif record[0] == RR_TYPE_TXT:
                        print(f'  TXT Name={record[11]}')
                        string = b''
                        strings = [record[11][i:i+255] for i in range(0, len(record[11]), 255)]
                        for label in strings:
                            string = string + len(label).to_bytes(1, byteorder='big') + bytes(label, 'utf-8')
                        answer_results.append((record[0], record[3], query[3], string))
                    elif record[0] == RR_TYPE_SRV:
                        print(f'  SRV Name={record[11]}')
                        answer_results.append((record[0], record[3], query[3], record[11], record[13], record[14], record[15]))
                    elif record[0] == RR_TYPE_MX:
                        print(f'  MX Host={record[11]}')
                        answer_results.append((record[0], record[3], query[3], record[11], record[13]))
                    elif record[0] == RR_TYPE_NS:
                        if query[0] == RR_TYPE_NS:
                            answer_results.append((record[0], record[3], record[2], record[4]))
                        else:
                            authority_results.append((record[0], record[3], record[2], record[4]))
                    elif record[0] == RR_TYPE_SOA:
                        print(f'  SOA Domain={record[2]} NS={record[4]} Mailbox={record[5]}')
                        mbox = record[5].replace('@','.')
                        info = soa_struct.pack(record[6],record[7],record[8],record[9],record[10])
                        if query[0] == RR_TYPE_SOA:
                            answer_results.append((record[0], record[3], record[2], record[4], mbox, info))
                        else:
                            authority_results.append((record[0], record[3], record[2], record[4], mbox, info))
                offset = offset + len(queries[i]) + 4
            question = query[2] + question_struct.pack(query[0], query[1])
            questions_data.append(question)

    # MARK: - Generate Response

    ANCOUNT_answers_count = len(answer_results)
    NSCOUNT_authoritative_answers_count = len(authority_results)
    ARCOUNT_additional_records_count = len(additional_results)
    if len(options) > 0:
        ARCOUNT_additional_records_count += 1
    data = header_struct.pack(ID_message_id, QR_response, OPCODE_operation, AA_authoritative_answer, TC_truncation, RD_recursion_desired, RA_recursion_available, AD_authentic_data, CD_checking_disabled, RCODE_response_code, QDCOUNT_questions_count, ANCOUNT_answers_count, NSCOUNT_authoritative_answers_count, ARCOUNT_additional_records_count)
    for question in questions_data:
        data = data + question
    offset = len(data)
    for record in answer_results + authority_results + additional_results:
        response = b''
        if record[0] == RR_TYPE_A:
            name, offset = decode_name(record[2], dictionary, offset)
            response = name + answer_struct.pack(record[0], DNS_CLASS_INTERNET, record[1], 4) + record[3]
            offset = offset + 14
        elif record[0] == RR_TYPE_AAAA:
            name, offset = decode_name(record[2], dictionary, offset)
            response = name + answer_struct.pack(record[0], DNS_CLASS_INTERNET, record[1], 16) + record[3]
            offset = offset + 26
        elif record[0] == RR_TYPE_NS:
            name, offset = decode_name(record[2], dictionary, offset)
            dname, offset = decode_name(record[3], dictionary, offset + 10)
            response = name + answer_struct.pack(record[0], DNS_CLASS_INTERNET, record[1], len(dname)) + dname
        elif record[0] == RR_TYPE_CNAME:
            name, offset = decode_name(record[2], dictionary, offset)
            dname, offset = decode_name(record[3], dictionary, offset + 10)
            response = name + answer_struct.pack(record[0], DNS_CLASS_INTERNET, record[1], len(dname)) + dname
        elif record[0] == RR_TYPE_MX:
            name, offset = decode_name(record[2], dictionary, offset)
            dname, offset = decode_name(record[3], dictionary, offset + 12)
            response = name + mx_struct.pack(record[0], DNS_CLASS_INTERNET, record[1], len(dname) + 2, record[4]) + dname
        elif record[0] == RR_TYPE_PTR:
            name, offset = decode_name(record[2], dictionary, offset)
            dname, offset = decode_name(record[3], dictionary, offset + 10)
            response = name + answer_struct.pack(record[0], DNS_CLASS_INTERNET, record[1], len(dname)) + dname
        elif record[0] == RR_TYPE_TXT:
            name, offset = decode_name(record[2], dictionary, offset)
            rlength = len(record[3])
            response = name + answer_struct.pack(record[0], DNS_CLASS_INTERNET, record[1], rlength) + record[3]
            offset = offset + 10 + rlength
        elif record[0] == RR_TYPE_SRV:
            name, offset = decode_name(record[2], dictionary, offset)
            dname, offset = decode_name(record[3], dictionary, offset + 16)
            response = name + srv_struct.pack(record[0], DNS_CLASS_INTERNET, record[1], len(dname)+6, record[4], record[5], record[6]) + dname
        elif record[0] == RR_TYPE_CAA:
            name, offset = decode_name(record[2], dictionary, offset)
            response = name + answer_struct.pack(record[0], DNS_CLASS_INTERNET, record[1], len(record[3])) + record[3]
            offset = offset + 10 + len(record[3])
        elif record[0] == RR_TYPE_SOA:
            name, offset = decode_name(record[2], dictionary, offset)
            nsname, offset = decode_name(record[3], dictionary, offset + 10)
            mbname, offset = decode_name(record[4], dictionary, offset)
            names = nsname + mbname
            response = name + answer_struct.pack(record[0], DNS_CLASS_INTERNET, record[1], len(names) + 20) + names + record[5]
            offset = offset + 20
        data = data + response
    if len(options) > 0:
        data = data + add_OPT_data(options)

#    hexdump.hexdump(data)
    return data
def add_OPT_data(options):
    for record in options:
        data = optanswer_struct.pack(41, record[0], record[1] >> 4, record[2], record[3], 0)
    return data
    
def decode_name(name, dictionary, offset):
    labels = name.split(".")
    encoded_name = b''
    compress = False
    for i in range(len(labels)):
        index = ".".join(labels[i:len(labels)])
        if index in dictionary:
            encoded_name = encoded_name + label_struct.pack(dictionary[index])
            compress = True
#            print(f' - Found reference to {name} at: {dictionary[index]}')
            offset = offset + 2
            break
        else:
            dictionary[index] = offset
#            print(f'Added {index} at: {offset}')
            offset = offset + len(labels[i]) + 1
            encoded_name = encoded_name + len(labels[i]).to_bytes(1, byteorder='big') + bytes(labels[i], 'utf-8')
    if compress == False:
        encoded_name = encoded_name + b'\0'
        offset = offset + 1
    return encoded_name, offset

async def respond(self, query):
    result = await self.responder(query)
    return result

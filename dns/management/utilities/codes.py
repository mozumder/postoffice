header_format = '>u16b1u4b1b1b1b1p3u4u16u16u16u16'
question_format = '>u16u16'
answer_format = '>u16u16u32u16'
opt_format = '>u8u8b1p15'

OPCODE_QUERY=0
OPCODE_IQUERY=1
OPCODE_STATUS=2
OPCODE = {
    OPCODE_QUERY:'QUERY',
    OPCODE_IQUERY:'IQUERY',
    OPCODE_STATUS:'STATUS'}
RCODE_OK=0
RCODE_FORMAT_ERROR=1
RCODE_SERVER_FAILURE=2
RCODE_NAME_ERROR=3
RCODE_NOT_IMPLEMENTED=4
RCODE_REFUSED=5
RCODE = {
    RCODE_OK:'No error',
    RCODE_FORMAT_ERROR:'Format Error',
    RCODE_SERVER_FAILURE:'Server Failure',
    RCODE_NAME_ERROR:'Name Error',
    RCODE_NOT_IMPLEMENTED:'Not Implemented',
    RCODE_REFUSED:'Refused'
}
DNS_CLASS_RESERVED = 0
DNS_CLASS_INTERNET = 1
DNS_CLASS_UNASSIGNED = 2
DNS_CLASS_CHAOS = 3
DNS_CLASS_HESIOD = 4
DNS_CLASS_QCLASS_NONE = 254
DNS_CLASS_QCLASS_ANY = 255
DNS_CLASS_RESERVED_FOR_PRIVATE_USE = 65280
DNS_CLASS = {
    DNS_CLASS_RESERVED:'Reserved',
    DNS_CLASS_INTERNET:'Internet (IN)',
    DNS_CLASS_UNASSIGNED:'Unassigned',
    DNS_CLASS_CHAOS:'Chaos (CH)',
    DNS_CLASS_HESIOD:'Hesoid (HS)',
    DNS_CLASS_QCLASS_NONE:'QCLASS NONE',
    DNS_CLASS_QCLASS_ANY:'QCLASS * (ANY)',
    DNS_CLASS_RESERVED_FOR_PRIVATE_USE:'Reserved for Private Use',
}
DNS_CLASS_LOOKUP = (
    (DNS_CLASS_RESERVED,
     DNS_CLASS_INTERNET,
     DNS_CLASS_UNASSIGNED,
     DNS_CLASS_CHAOS,
     DNS_CLASS_HESIOD,) +
     tuple(DNS_CLASS_UNASSIGNED for i in range(5,254)) +
     (DNS_CLASS_QCLASS_NONE,
     DNS_CLASS_QCLASS_ANY,) +
     tuple(DNS_CLASS_UNASSIGNED for i in range(256,65280)) +
     tuple(DNS_CLASS_RESERVED_FOR_PRIVATE_USE for i in range(65280,65535)) +
     (DNS_CLASS_RESERVED,)
)


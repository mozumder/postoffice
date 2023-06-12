header_format = '>u16b1u4b1b1b1b1p1b1b1u4u16u16u16u16'
question_format = '>u16u16'
answer_format = '>u16u16u32u16'
label_format = '>P2u14'
soa_format = '>u32u32u32u32u32'
opt_format = '>u8u8b1p15'
mx_format = '>u16u16u32u16u16'
caa_flags_format = '>b1p7'
srv_format = '>u16u16u32u16u16u16u16'
optanswer_format = '>p8u16u16u8u8b1p15u16'
tcp_length_format = '>u16'
ip_address_format = '>u8u8u8u8'

OPCODE_QUERY=0
OPCODE_IQUERY=1
OPCODE_STATUS=2
OPCODE_UNASSIGNED=3
OPCODE_NOTIFY=4
OPCODE_UPDATE=5
OPCODE_DSO=6

OPCODE = {
    OPCODE_QUERY:'QUERY',
    OPCODE_IQUERY:'IQUERY',
    OPCODE_STATUS:'STATUS',
    OPCODE_UNASSIGNED:'UNASSIGNED',
    OPCODE_NOTIFY:'NOTIFY',
    OPCODE_UPDATE:'UPDATE',
    OPCODE_DSO:'DSO',
}

OPCODE_LOOKUP=(
    (OPCODE_QUERY,
    OPCODE_IQUERY,
    OPCODE_STATUS,
    OPCODE_UNASSIGNED,
    OPCODE_NOTIFY,
    OPCODE_UPDATE,
    OPCODE_DSO,) +
    tuple(OPCODE_UNASSIGNED for i in range(7,16))
)

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

RCODE_NOERROR=0
RCODE_FORMERROR=1
RCODE_SERVEFAIL=2
RCODE_NXDOMAIN=3
RCODE_NOTIMP=4
RCODE_REFUSED=5
RCODE_YXDOMAIN=6
RCODE_YXRRSET=7
RCODE_NXRRSET=8
RCODE_NOTAUTH=9
RCODE_NOTZONE=10
RCODE_DSOTYPENI=11
RCODE_UNASSIGNED=12
RCODE_BADVERS=16
RCODE_BADSIG=16
RCODE_BADKEY=17
RCODE_BADTIME=18
RCODE_BADMODE=19
RCODE_BADNAME=20
RCODE_BADALG=21
RCODE_BADTRUNC=22
RCODE_BADCOOKIE=3841
RCODE_PRIVATE=4096
RCODE_RESERVED=65535

RCODE = {
    RCODE_NOERROR:'NoError',
    RCODE_FORMERROR:'FormErr',
    RCODE_SERVEFAIL:'ServFail',
    RCODE_NXDOMAIN:'NXDomain',
    RCODE_NOTIMP:'NotImp',
    RCODE_REFUSED:'Refused',
    RCODE_YXDOMAIN:'YXDomain',
    RCODE_YXRRSET:'YXRRSet',
    RCODE_NXRRSET:'NXRRSet',
    RCODE_NOTAUTH:'NotAuth',
    RCODE_NOTZONE:'NotZone',
    RCODE_DSOTYPENI:'DSOTYPENI',
    RCODE_UNASSIGNED:'Unassigned',
    RCODE_BADVERS:'BADVERS',
    RCODE_BADSIG:'BADSIG',
    RCODE_BADKEY:'BADKEY',
    RCODE_BADTIME:'BADTIME',
    RCODE_BADMODE:'BADMODE',
    RCODE_BADNAME:'BADNAME',
    RCODE_BADALG:'BADALG',
    RCODE_BADTRUNC:'BADTRUNC',
    RCODE_BADCOOKIE:'BADCOOKIE',
    RCODE_PRIVATE:'Private',
    RCODE_RESERVED:'Reserved',
    }

RCODE_LOOKUP = (
    (RCODE_NOERROR,
    RCODE_FORMERROR,
    RCODE_SERVEFAIL,
    RCODE_NXDOMAIN,
    RCODE_NOTIMP,
    RCODE_REFUSED,
    RCODE_YXDOMAIN,
    RCODE_YXRRSET,
    RCODE_NXRRSET,
    RCODE_NOTAUTH,
    RCODE_NOTZONE,
    RCODE_DSOTYPENI,
    RCODE_UNASSIGNED,) +
    tuple(RCODE_UNASSIGNED for i in range(12,16))
)

OPT_RCODE_LOOKUP = (
    (RCODE_NOERROR,
    RCODE_FORMERROR,
    RCODE_SERVEFAIL,
    RCODE_NXDOMAIN,
    RCODE_NOTIMP,
    RCODE_REFUSED,
    RCODE_YXDOMAIN,
    RCODE_YXRRSET,
    RCODE_NXRRSET,
    RCODE_NOTAUTH,
    RCODE_NOTZONE,
    RCODE_DSOTYPENI,
    RCODE_UNASSIGNED,) +
    tuple(RCODE_UNASSIGNED for i in range(12,16)) +
    (RCODE_BADVERS,
    RCODE_BADKEY,
    RCODE_BADTIME,
    RCODE_BADMODE,
    RCODE_BADNAME,
    RCODE_BADALG,
    RCODE_BADTRUNC,
    RCODE_BADCOOKIE,) +
    tuple(RCODE_PRIVATE for i in range(24,3841)) +
    tuple(RCODE_RESERVED for i in range(3841,4096)) +
    tuple(RCODE_PRIVATE for i in range(4096,65535)) +
    (RCODE_RESERVED,)
)

SIG_RCODE_LOOKUP = (
    (RCODE_NOERROR,
    RCODE_FORMERROR,
    RCODE_SERVEFAIL,
    RCODE_NXDOMAIN,
    RCODE_NOTIMP,
    RCODE_REFUSED,
    RCODE_YXDOMAIN,
    RCODE_YXRRSET,
    RCODE_NXRRSET,
    RCODE_NOTAUTH,
    RCODE_NOTZONE,
    RCODE_DSOTYPENI,
    RCODE_UNASSIGNED,) +
    tuple(RCODE_UNASSIGNED for i in range(12,16)) +
    (RCODE_BADSIG,
    RCODE_BADKEY,
    RCODE_BADTIME,
    RCODE_BADMODE,
    RCODE_BADNAME,
    RCODE_BADALG,
    RCODE_BADTRUNC,
    RCODE_BADCOOKIE,) +
    tuple(RCODE_PRIVATE for i in range(24,3841)) +
    tuple(RCODE_RESERVED for i in range(3841,4096)) +
    tuple(RCODE_PRIVATE for i in range(4096,65535)) +
    (RCODE_RESERVED,)
)

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

RR_TYPE_RESERVED = 0
RR_TYPE_A = 1
RR_TYPE_NS = 2
RR_TYPE_MD = 3
RR_TYPE_MF = 4
RR_TYPE_CNAME = 5
RR_TYPE_SOA = 6
RR_TYPE_MB = 7
RR_TYPE_MG = 8
RR_TYPE_MR = 9
RR_TYPE_NULL = 10
RR_TYPE_WKS = 11
RR_TYPE_PTR = 12
RR_TYPE_HINFO = 13
RR_TYPE_MINFO = 14
RR_TYPE_MX = 15
RR_TYPE_TXT = 16
RR_TYPE_RP = 17
RR_TYPE_AFSDB = 18
RR_TYPE_X25 = 19
RR_TYPE_ISDN = 20
RR_TYPE_RT = 21
RR_TYPE_NSAP = 22
RR_TYPE_NSAPPTR = 23
RR_TYPE_SIG = 24
RR_TYPE_KEY = 25
RR_TYPE_PX = 26
RR_TYPE_GPOS = 27
RR_TYPE_AAAA = 28
RR_TYPE_LOC = 29
RR_TYPE_NXT = 30
RR_TYPE_EID = 31
RR_TYPE_NIMLOC = 32
RR_TYPE_SRV = 33
RR_TYPE_ATMA = 34
RR_TYPE_NAPTR = 35
RR_TYPE_KX = 36
RR_TYPE_CERT = 37
RR_TYPE_A6 = 38
RR_TYPE_DNAME = 39
RR_TYPE_SINK = 40
RR_TYPE_OPT = 41
RR_TYPE_APL = 42
RR_TYPE_DS = 43
RR_TYPE_SSHFP = 44
RR_TYPE_IPSECKEY = 45
RR_TYPE_RRSIG = 46
RR_TYPE_NSEC = 47
RR_TYPE_DNSKEY = 48
RR_TYPE_DHCID = 49
RR_TYPE_NSEC3 = 50
RR_TYPE_NSEC3PARAM = 51
RR_TYPE_TLSA = 52
RR_TYPE_SMIMEA = 53
RR_TYPE_UNASSIGNED = 54
RR_TYPE_HIP = 55
RR_TYPE_NINFO = 56
RR_TYPE_RKEY = 57
RR_TYPE_TALINK = 58
RR_TYPE_CDS = 59
RR_TYPE_CDNSKEY = 60
RR_TYPE_OPENPGPKEY = 61
RR_TYPE_CSYNC = 62
RR_TYPE_ZONEMD = 63
RR_TYPE_SPF = 99
RR_TYPE_UINFO = 100
RR_TYPE_UID = 101
RR_TYPE_GID = 102
RR_TYPE_UNSPEC = 103
RR_TYPE_NID = 104
RR_TYPE_L32 = 105
RR_TYPE_L64 = 106
RR_TYPE_LP = 107
RR_TYPE_EUI48 = 108
RR_TYPE_EUI64 = 109
RR_TYPE_TKEY = 249
RR_TYPE_TSIG = 250
RR_TYPE_IXFR = 251
RR_TYPE_AXFR = 252
RR_TYPE_MAILB = 253
RR_TYPE_MAILA = 254
RR_TYPE_ANY = 255
RR_TYPE_URI = 256
RR_TYPE_CAA = 257
RR_TYPE_AVC = 258
RR_TYPE_DOA = 259
RR_TYPE_AMTRELAY = 260
RR_TYPE_TA = 32768
RR_TYPE_DLV = 32769
RR_TYPE_PRIVATE_USE = 65280


RR_TYPE = {
    RR_TYPE_RESERVED:'Reserved',
    RR_TYPE_A:'A',
    RR_TYPE_NS:'NS',
    RR_TYPE_MD:'MD',
    RR_TYPE_MF:'MF',
    RR_TYPE_CNAME:'CNAME',
    RR_TYPE_SOA:'SOA',
    RR_TYPE_MB:'MB',
    RR_TYPE_MG:'MG',
    RR_TYPE_MR:'MR',
    RR_TYPE_NULL:'NULL',
    RR_TYPE_WKS:'WKS',
    RR_TYPE_PTR:'PTR',
    RR_TYPE_HINFO:'HINFO',
    RR_TYPE_MINFO:'MINFO',
    RR_TYPE_MX:'MX',
    RR_TYPE_TXT:'TXT',
    RR_TYPE_RP:'RP',
    RR_TYPE_AFSDB:'AFSDB',
    RR_TYPE_X25:'X25',
    RR_TYPE_ISDN:'ISDN',
    RR_TYPE_RT:'RT',
    RR_TYPE_NSAP:'NSAP',
    RR_TYPE_NSAPPTR:'NSAP-PTR',
    RR_TYPE_SIG:'SIG',
    RR_TYPE_KEY:'KEY',
    RR_TYPE_PX:'PX',
    RR_TYPE_GPOS:'GPOS',
    RR_TYPE_AAAA:'AAAA',
    RR_TYPE_LOC:'LOC',
    RR_TYPE_NXT:'NXT',
    RR_TYPE_EID:'EID',
    RR_TYPE_NIMLOC:'NIMLOC',
    RR_TYPE_SRV:'SRV',
    RR_TYPE_ATMA:'ATMA',
    RR_TYPE_NAPTR:'NAPTR',
    RR_TYPE_KX:'KX',
    RR_TYPE_CERT:'CERT',
    RR_TYPE_A6:'A6',
    RR_TYPE_DNAME:'DNAME',
    RR_TYPE_SINK:'SINK',
    RR_TYPE_OPT:'OPT',
    RR_TYPE_APL:'APL',
    RR_TYPE_DS:'DS',
    RR_TYPE_SSHFP:'SSHFP',
    RR_TYPE_IPSECKEY:'IPSECKEY',
    RR_TYPE_RRSIG:'RRSIG',
    RR_TYPE_NSEC:'NSEC',
    RR_TYPE_DNSKEY:'DNSKEY',
    RR_TYPE_DHCID:'DHCID',
    RR_TYPE_NSEC3:'NSEC3',
    RR_TYPE_NSEC3PARAM:'NSEC3PARAM',
    RR_TYPE_TLSA:'TLSA',
    RR_TYPE_SMIMEA:'SMIMEA',
    RR_TYPE_UNASSIGNED:'Unassigned',
    RR_TYPE_HIP:'HIP',
    RR_TYPE_NINFO:'NINFO',
    RR_TYPE_RKEY:'RKEY',
    RR_TYPE_TALINK:'TALINK',
    RR_TYPE_CDS:'CDS',
    RR_TYPE_CDNSKEY:'CDNSKEY',
    RR_TYPE_OPENPGPKEY:'OPENPGPKEY',
    RR_TYPE_CSYNC:'CSYNC',
    RR_TYPE_ZONEMD:'ZONEMD',
    RR_TYPE_SPF:'SPF',
    RR_TYPE_UINFO:'UINFO',
    RR_TYPE_UID:'UID',
    RR_TYPE_GID:'GID',
    RR_TYPE_UNSPEC:'UNSPEC',
    RR_TYPE_NID:'NID',
    RR_TYPE_L32:'L32',
    RR_TYPE_L64:'L64',
    RR_TYPE_LP:'LP',
    RR_TYPE_EUI48:'EUI48',
    RR_TYPE_EUI64:'EUI64',
    RR_TYPE_TKEY:'TKEY',
    RR_TYPE_TSIG:'TSIG',
    RR_TYPE_IXFR:'IXFR',
    RR_TYPE_AXFR:'AXFR',
    RR_TYPE_MAILB:'MAILB',
    RR_TYPE_MAILA:'MAILA',
    RR_TYPE_ANY:'ANY',
    RR_TYPE_URI:'URI',
    RR_TYPE_CAA:'CAA',
    RR_TYPE_AVC:'AVC',
    RR_TYPE_DOA:'DOA',
    RR_TYPE_AMTRELAY:'AMTRELAY',
    RR_TYPE_TA:'TA',
    RR_TYPE_DLV:'DLV',
    RR_TYPE_PRIVATE_USE:'Private Use',
}

RR_TYPE_LOOKUP = (
    (RR_TYPE_RESERVED,
    RR_TYPE_A,
    RR_TYPE_NS,
    RR_TYPE_MD,
    RR_TYPE_MF,
    RR_TYPE_CNAME,
    RR_TYPE_SOA,
    RR_TYPE_MB,
    RR_TYPE_MG,
    RR_TYPE_MR,
    RR_TYPE_NULL,
    RR_TYPE_WKS,
    RR_TYPE_PTR,
    RR_TYPE_HINFO,
    RR_TYPE_MINFO,
    RR_TYPE_MX,
    RR_TYPE_TXT,
    RR_TYPE_RP,
    RR_TYPE_AFSDB,
    RR_TYPE_X25,
    RR_TYPE_ISDN,
    RR_TYPE_RT,
    RR_TYPE_NSAP,
    RR_TYPE_NSAPPTR,
    RR_TYPE_SIG,
    RR_TYPE_KEY,
    RR_TYPE_PX,
    RR_TYPE_GPOS,
    RR_TYPE_AAAA,
    RR_TYPE_LOC,
    RR_TYPE_NXT,
    RR_TYPE_EID,
    RR_TYPE_NIMLOC,
    RR_TYPE_SRV,
    RR_TYPE_ATMA,
    RR_TYPE_NAPTR,
    RR_TYPE_KX,
    RR_TYPE_CERT,
    RR_TYPE_A6,
    RR_TYPE_DNAME,
    RR_TYPE_SINK,
    RR_TYPE_OPT,
    RR_TYPE_APL,
    RR_TYPE_DS,
    RR_TYPE_SSHFP,
    RR_TYPE_IPSECKEY,
    RR_TYPE_RRSIG,
    RR_TYPE_NSEC,
    RR_TYPE_DNSKEY,
    RR_TYPE_DHCID,
    RR_TYPE_NSEC3,
    RR_TYPE_NSEC3PARAM,
    RR_TYPE_TLSA,
    RR_TYPE_SMIMEA,
    RR_TYPE_UNASSIGNED,
    RR_TYPE_HIP,
    RR_TYPE_NINFO,
    RR_TYPE_RKEY,
    RR_TYPE_TALINK,
    RR_TYPE_CDS,
    RR_TYPE_CDNSKEY,
    RR_TYPE_OPENPGPKEY,
    RR_TYPE_CSYNC,
    RR_TYPE_ZONEMD,) +
    tuple(RR_TYPE_UNASSIGNED for i in range(64,99)) +
    (RR_TYPE_SPF,
    RR_TYPE_UINFO,
    RR_TYPE_UID,
    RR_TYPE_GID,
    RR_TYPE_UNSPEC,
    RR_TYPE_NID,
    RR_TYPE_L32,
    RR_TYPE_L64,
    RR_TYPE_LP,
    RR_TYPE_EUI48,
    RR_TYPE_EUI64,) +
    tuple(RR_TYPE_UNASSIGNED for i in range(110,249)) +
    (RR_TYPE_TKEY,
    RR_TYPE_TSIG,
    RR_TYPE_IXFR,
    RR_TYPE_AXFR,
    RR_TYPE_MAILB,
    RR_TYPE_MAILA,
    RR_TYPE_ANY,
    RR_TYPE_URI,
    RR_TYPE_CAA,
    RR_TYPE_AVC,
    RR_TYPE_DOA,
    RR_TYPE_AMTRELAY,) +
    tuple(RR_TYPE_UNASSIGNED for i in range(261,32768)) +
    (RR_TYPE_TA,
    RR_TYPE_DLV,) +
    tuple(RR_TYPE_UNASSIGNED for i in range(32770,65280)) +
    tuple(RR_TYPE_PRIVATE_USE for i in range(65280,65535)) +
    (RR_TYPE_RESERVED,)
)



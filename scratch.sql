
select
    6 as type,
    dns_soa_record.ttl as ttl,
    NULL::inet as ip_address,
    dns_domain.name as domainname,
    dns_soa_record.nameserver as nsname,
    dns_soa_record.rname as rname,
    dns_soa_record.serial as serial,
    dns_soa_record.refresh as refresh,
    dns_soa_record.retry as retry,
    dns_soa_record.expiry as expiry,
    dns_soa_record.nxttl as nxttl
from
    dns_domain
inner join
    dns_aaaa_record
on
    dns_domain.id = dns_aaaa_record.domain_id
left outer join
    dns_soa_record
on
    dns_domain.id = dns_soa_record.domain_id
where
    dns_aaaa_record.fqdn != 'la.mozumder.net' AND
    'la.mozumder.net' LIKE '%' || dns_domain.name ;
;
select
    24 as type,
    dns_aaaa_record.ttl as ttl,
    ip_address,
    dns_domain.name as domainname,
    NULL::varchar(255) as nsname,
    NULL::varchar(255) as rname,
    NULL::int as serial,
    NULL::int as refresh,
    NULL::int as retry,
    NULL::int as expiry,
    NULL::int as nxttl
from
    dns_aaaa_record
left outer join
    dns_domain
on
    dns_domain.id = dns_aaaa_record.domain_id
where
    dns_aaaa_record.fqdn = 'la.mozumder.net'
;

select
    6 as type,
    dns_aaaa_record.name as name,
    ip_address,
    dns_aaaa_record.ttl as ttl,
    dns_domain.name as domainname,
    dns_soa_record.id as soa_id,
    dns_soa_record.nameserver as nsname,
    dns_soa_record.rname as rname,
    dns_soa_record.serial as serial,
    dns_soa_record.refresh as refresh,
    dns_soa_record.retry as retry,
    dns_soa_record.expiry as expiry,
    dns_soa_record.nxttl as nxttl,
    dns_soa_record.domain_id,
    dns_aaaa_record.domain_id
from
    dns_aaaa_record, dns_domain, dns_soa_record
where
    (dns_aaaa_record.fqdn != 'mozumder.net' AND
    'mozumder.net' LIKE '%' || dns_domain.name AND
    dns_aaaa_record.domain_id = dns_domain.id AND
    dns_soa_record.domain_id = dns_domain.id ) OR
    (dns_aaaa_record.fqdn != 'mozumder.net' AND
    'mozumder.net' LIKE '%' || dns_domain.name AND
    dns_aaaa_record.domain_id = dns_domain.id AND
    dns_soa_record.domain_id = dns_domain.id ) OR

    dns_soa_record.domain_id != dns_aaaa_record.domain_id AND
;
    AND
;


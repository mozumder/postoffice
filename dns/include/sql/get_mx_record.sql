DROP FUNCTION IF EXISTS get_mx_record(character varying);
CREATE OR REPLACE FUNCTION get_mx_record(
    search varchar(255)
    )
RETURNS TABLE (
    type INT,
    nxdomain BOOLEAN,
    domainname VARCHAR(255),
    ttl INT,
    nsname VARCHAR(255),
    rname VARCHAR(255),
    serial INT,
    refresh INT,
    retry INT,
    expiry INT,
    nxttl INT,
    out_hostname VARCHAR(255),
    out_ip_address INET,
    out_preference INT
)
AS
$BODY$
DECLARE
    mx_check RECORD;
BEGIN

SELECT
    dns_mx_record.hostname as hostname,
    dns_mx_record.preference as preference,
    dns_mx_record.ttl as ttl,
    dns_domain.id as founddomain_id,
    dns_domain.name as domainname
INTO
    mx_check
FROM
    dns_mx_record
LEFT OUTER JOIN
    dns_domain
ON
    dns_domain.id = dns_mx_record.domain_id
WHERE
    dns_mx_record.searchname = search
ORDER BY
    length(dns_domain.name) DESC
LIMIT 1
;

IF FOUND THEN
-- MX and NS records must never point to CNAME
    RETURN QUERY
    SELECT
        {RR_TYPE_MX} as type,
        true as nxdomain,
        mx_check.domainname as domainname,
        mx_check.ttl as ttl,
        NULL::varchar(255) as nsname,
        NULL::varchar(255) as rname,
        NULL::int as serial,
        NULL::int as refresh,
        NULL::int as retry,
        NULL::int as expiry,
        NULL::int as nxttl,
        mx_check.hostname as hostname,
        NULL::inet as ip_address,
        mx_check.preference as preference
    UNION
    SELECT
        {RR_TYPE_NS} as type,
        true as nxdomain,
        mx_check.domainname as domainname,
        dns_ns_record.ttl as ttl,
        dns_ns_record.name as nsname,
        NULL::varchar(255) as rname,
        NULL::int as serial,
        NULL::int as refresh,
        NULL::int as retry,
        NULL::int as expiry,
        NULL::int as nxttl,
        NULL::varchar(255) as hostname,
        NULL::inet as ip_address,
        NULL::int as preference
    FROM
        dns_ns_record
    WHERE
        mx_check.founddomain_id = dns_ns_record.domain_id
    UNION
    SELECT
        {RR_TYPE_A} as type,
        true as nxdomain,
        mx_check.domainname as domainname,
        dns_a_record.ttl as ttl,
        NULL::varchar(255) as nsname,
        NULL::varchar(255) as rname,
        NULL::int as serial,
        NULL::int as refresh,
        NULL::int as retry,
        NULL::int as expiry,
        NULL::int as nxttl,
        NULL::varchar(255) as hostname,
        dns_a_record.ip_address as ip_address,
        NULL::int as preference
    FROM
        dns_a_record
    WHERE
        dns_a_record.searchname = mx_check.hostname
    UNION
    SELECT
        {RR_TYPE_AAAA} as type,
        true as nxdomain,
        mx_check.domainname as domainname,
        dns_aaaa_record.ttl as ttl,
        NULL::varchar(255) as nsname,
        NULL::varchar(255) as rname,
        NULL::int as serial,
        NULL::int as refresh,
        NULL::int as retry,
        NULL::int as expiry,
        NULL::int as nxttl,
        NULL::varchar(255) as hostname,
        dns_aaaa_record.ip_address as ip_address,
        NULL::int as preference
    FROM
        dns_aaaa_record
    WHERE
        dns_aaaa_record.searchname = mx_check.hostname
    ;
ELSE
    RETURN QUERY
    SELECT
        {RR_TYPE_SOA} as type,
    exists(
        SELECT 1
        FROM
            dns_a_record,
            dns_aaaa_record,
            dns_cname_record
        WHERE
            dns_a_record.searchname = search OR
            dns_aaaa_record.searchname = search OR
            dns_cname_record.searchname = search
        ) as nxdomain,
        dns_domain.name as domainname,
        dns_soa_record.ttl as ttl,
        dns_soa_record.nameserver as nsname,
        dns_soa_record.rname as rname,
        dns_soa_record.serial as serial,
        dns_soa_record.refresh as refresh,
        dns_soa_record.retry as retry,
        dns_soa_record.expiry as expiry,
        dns_soa_record.nxttl as nxttl,
        NULL::varchar(255) as hostname,
        NULL::inet as ip_address,
        NULL::int as preference
    FROM
        dns_domain, dns_soa_record
    WHERE
        '.' || search LIKE '%.' || dns_domain.name AND
        dns_domain.id = dns_soa_record.domain_id
    ORDER BY
        length(dns_domain.name) DESC
    LIMIT 1
    ;
END IF;
RETURN ;
END
$BODY$
LANGUAGE plpgsql;
;
PREPARE get_mx_record(VARCHAR(255)) AS
SELECT * from get_mx_record($1) ;


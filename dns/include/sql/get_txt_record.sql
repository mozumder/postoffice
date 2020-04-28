DROP FUNCTION IF EXISTS get_txt_record(character varying(255));
CREATE OR REPLACE FUNCTION get_txt_record(
    searchname varchar(65535)
    )
RETURNS TABLE (
    type INT,
    nonexstent BOOLEAN,
    domainname VARCHAR(255),
    ttl INT,
    nsname VARCHAR(255),
    rname VARCHAR(255),
    serial INT,
    refresh INT,
    retry INT,
    expiry INT,
    nxttl INT,
    out_value VARCHAR(65535)
)
AS
$BODY$
DECLARE
    result RECORD;
BEGIN

SELECT
    dns_domain.name as domainname,
    dns_domain.id as founddomain_id
INTO
    result
FROM
    dns_txt_record,
    dns_domain
WHERE
    dns_domain.id = dns_txt_record.domain_id AND
    dns_txt_record.fqdn = searchname
ORDER BY
    length(dns_domain.name) DESC
LIMIT 1
;
IF FOUND THEN
    RETURN QUERY
    SELECT
        {RR_TYPE_TXT} as type,
        NULL::bool as nonexistent,
        result.domainname as domainname,
        dns_txt_record.ttl as ttl,
        NULL::varchar(255) as nsname,
        NULL::varchar(255) as rname,
        NULL::int as serial,
        NULL::int as refresh,
        NULL::int as retry,
        NULL::int as expiry,
        NULL::int as nxttl,
        dns_txt_record.value as value
    FROM
        dns_txt_record,
        dns_domain
    WHERE
        dns_domain.id = result.founddomain_id AND
        dns_txt_record.fqdn = searchname
    UNION
    SELECT
        {RR_TYPE_NS} as type,
        NULL::bool as nonexistent,
        dns_domain.name as domainname,
        dns_ns_record.ttl as ttl,
        dns_ns_record.name as nsname,
        NULL::varchar(255) as rname,
        NULL::int as serial,
        NULL::int as refresh,
        NULL::int as retry,
        NULL::int as expiry,
        NULL::int as nxttl,
        NULL::varchar(255) as value
    FROM
        dns_domain, dns_txt_record, dns_ns_record
    WHERE
        dns_txt_record.fqdn = searchname AND
        dns_domain.id = dns_txt_record.domain_id AND
        dns_domain.id = dns_ns_record.domain_id
    ;
ELSE
    RETURN QUERY
    SELECT
        {RR_TYPE_SOA} as type,
        NULL::bool as nonexistent,
        dns_domain.name as domainname,
        dns_soa_record.ttl as ttl,
        dns_soa_record.nameserver as nsname,
        dns_soa_record.rname as rname,
        dns_soa_record.serial as serial,
        dns_soa_record.refresh as refresh,
        dns_soa_record.retry as retry,
        dns_soa_record.expiry as expiry,
        dns_soa_record.nxttl as nxttl,
        NULL::varchar(255) as value
    FROM
        dns_domain, dns_soa_record
    WHERE
        '.' || searchname LIKE '%.' || dns_domain.name AND
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
PREPARE get_txt_record(VARCHAR(255)) AS
SELECT * from get_txt_record($1) ;

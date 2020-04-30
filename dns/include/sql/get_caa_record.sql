DROP FUNCTION IF EXISTS get_caa_record(character varying(255));
CREATE OR REPLACE FUNCTION get_caa_record(
    search varchar(65535)
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
    out_value VARCHAR(65535),
    out_tag VARCHAR(16),
    issuer_critical BOOLEAN
)
AS
$BODY$
DECLARE
    domain_check RECORD;
BEGIN

SELECT
    dns_domain.name as domainname,
    dns_domain.id as founddomain_id
INTO
    domain_check
FROM
    dns_caa_record,
    dns_domain
WHERE
    dns_domain.id = dns_caa_record.domain_id AND
    dns_caa_record.searchname = search
ORDER BY
    length(dns_domain.name) DESC
LIMIT 1
;
IF FOUND THEN
    RETURN QUERY
    SELECT
        {RR_TYPE_CAA} as type,
        true as nxdomain,
        domain_check.domainname as domainname,
        dns_caa_record.ttl as ttl,
        NULL::varchar(255) as nsname,
        NULL::varchar(255) as rname,
        NULL::int as serial,
        NULL::int as refresh,
        NULL::int as retry,
        NULL::int as expiry,
        NULL::int as nxttl,
        dns_caa_record.value as out_value,
        dns_caa_record.tag as out_tag,
        dns_caa_record.issuer_critical as issuer_critical
    FROM
        dns_caa_record
    WHERE
        dns_caa_record.searchname = search
    UNION
    SELECT
        {RR_TYPE_NS} as type,
        true as nxdomain,
        domain_check.domainname as domainname,
        dns_ns_record.ttl as ttl,
        dns_ns_record.name as nsname,
        NULL::varchar(255) as rname,
        NULL::int as serial,
        NULL::int as refresh,
        NULL::int as retry,
        NULL::int as expiry,
        NULL::int as nxttl,
        NULL::varchar(65535) as value,
        NULL::varchar(255) as tag,
        NULL::boolean as issuer_critical
    FROM
        dns_ns_record
    WHERE
        domain_check.founddomain_id = dns_ns_record.domain_id
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
        NULL::varchar(65535) as value,
        NULL::varchar(255) as tag,
        NULL::boolean as issuer_critical
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
PREPARE get_caa_record(VARCHAR(255)) AS
SELECT * from get_caa_record($1) ;


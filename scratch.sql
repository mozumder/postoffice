./manage.py createmodel -app polls Question question_text:varchar(200) pub_date:datetime
./manage.py createmodel -app polls Choice question=CharField(max-length=200) pub_date=DateTimeField('date published')
./manage.py createadmin -app polls -model [
./manage.py crateview
./manage.py createtemplate


SELECT exists(
        SELECT 1
        FROM
            dns_cname_record
        WHERE
            dns_cname_record.fqdn = 'mail2.mozumder.net'
        ) as found
;


SELECT
    dns_cname_record.canonical_name as cname,
    dns_domain.id as domain_id,
    dns_domain.name as domainname
FROM
    dns_cname_record
LEFT OUTER JOIN
    dns_domain
ON
    dns_domain.id = dns_cname_record.domain_id
WHERE
    dns_cname_record.fqdn = 'mail2.mozumder.net'
;

    SELECT
        dns_a_record.fqdn,
        dns_aaaa_record.fqdn,
        dns_cname_record.fqdn,
        dns_cname_record.canonical_name,
        1 as existing,
        COALESCE(dns_cname_record.canonical_name, 'mail.mozumder.net') as cname
    FROM
        dns_domain,
        dns_a_record,
        dns_aaaa_record,
        dns_cname_record
    WHERE
        (dns_domain.id = dns_a_record.domain_id AND
        dns_a_record.fqdn = 'mail.mozumder.net') OR
        (dns_domain.id = dns_aaaa_record.domain_id AND
        dns_aaaa_record.fqdn = 'mail.mozumder.net') OR
        (dns_domain.id = dns_cname_record.domain_id AND
        dns_cname_record.fqdn = 'mail.mozumder.net')
;

SELECT
    *
FROM
    dns_domain,
    dns_soa_record
WHERE
    '.''mozumder.net' LIKE '%.' || dns_domain.name AND
    dns_domain.id = dns_soa_record.domain_id ;

SELECT
    dns_soa_record.ttl as ttl,
    dns_domain.name as domainname,
    dns_soa_record.nameserver as nsname,
    dns_soa_record.rname as rname,
    dns_soa_record.serial as serial,
    dns_soa_record.refresh as refresh,
    dns_soa_record.retry as retry,
    dns_soa_record.expiry as expiry,
    dns_soa_record.nxttl as nxttl
INTO
    result
FROM
    dns_domain, dns_soa_record
WHERE
    'mozumder.net' LIKE '%.' || dns_domain.name AND
    dns_domain.id = dns_soa_record.domain_id
;

DROP FUNCTION IF EXISTS get_aaaa_record(character varying);
CREATE OR REPLACE FUNCTION get_aaaa_record(
    searchname varchar(255)
    )
RETURNS TABLE (
    type INT,
    ttl INT,
    out_ip_address INET,
    domainname VARCHAR(255),
    nsname VARCHAR(255),
    rname VARCHAR(255),
    serial INT,
    refresh INT,
    retry INT,
    expiry INT,
    nxttl INT
)
AS
$BODY$
DECLARE
    result RECORD;
BEGIN

SELECT
    dns_aaaa_record.ttl as ttl,
    ip_address,
    dns_domain.name as domainname
INTO
    result
FROM
    dns_aaaa_record,
    dns_domain
WHERE
    dns_domain.id = dns_aaaa_record.domain_id AND
    dns_aaaa_record.fqdn = searchname
;
IF FOUND THEN
    RETURN QUERY SELECT
        {RR_TYPE_AAAA} as type,
        result.ttl as ttl,
        result.ip_address as ip_address,
        result.domainname as domainname,
        NULL::varchar(255) as nsname,
        NULL::varchar(255) as rname,
        NULL::int as serial,
        NULL::int as refresh,
        NULL::int as retry,
        NULL::int as expiry,
        NULL::int as nxttl
    UNION
    SELECT
        {RR_TYPE_NS} as type,
        dns_ns_record.ttl as ttl,
        NULL::inet as ip_address,
        dns_domain.name as domainname,
        dns_ns_record.name as nsname,
        NULL::varchar(255) as rname,
        NULL::int as serial,
        NULL::int as refresh,
        NULL::int as retry,
        NULL::int as expiry,
        NULL::int as nxttl
    FROM
        dns_domain, dns_aaaa_record, dns_ns_record
    WHERE
        dns_aaaa_record.fqdn = searchname AND
        dns_domain.id = dns_aaaa_record.domain_id AND
        dns_domain.id = dns_ns_record.domain_id
    ;
ELSE
    RETURN QUERY SELECT
        {RR_TYPE_SOA} as type,
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
    FROM
        dns_domain, dns_soa_record
    WHERE
        searchname LIKE '%' || dns_domain.name AND
        dns_domain.id = dns_soa_record.domain_id
    ;
END IF;
RETURN ;
END
$BODY$
LANGUAGE plpgsql;
;

PREPARE get_aaaa_record(VARCHAR(255)) AS
SELECT * from get_aaaa_record($1) ;


    SELECT t.banned FROM check_ip_address(ip) as t
      INTO banned ;
    IF banned = TRUE THEN
        RETURN QUERY SELECT 403,
                            null::varchar,
                            null::timestamptz,
                            '{}'::json,
                            null::integer,
                            FALSE;
        RETURN;
    END IF;
    SELECT t.bot FROM check_user_agent(user_agent) as t
      INTO bot ;
    IF bot = TRUE THEN
        RETURN QUERY SELECT 200,
                            null::varchar,
                            null::timestamptz,
                            '{}'::json,
                            null::integer,
                            FALSE;
        RETURN;
    END IF;
    -- Get session data
    WITH t AS (
        SELECT
            "django_session"."expire_date" as session_expire_date,
            substr(
                encode(
                    decode(
                        "django_session"."session_data",
                        'base64'),
                    'escape'),
                42)::json as session_data
        FROM "django_session"
        WHERE
            "django_session"."session_key" = request_session_key
        AND "django_session"."expire_date" > request_timestamp::timestamptz
    )
    SELECT request_session_key::varchar as session_key,
           t.session_expire_date as session_expire_date,
           t.session_data as session_data_field,
           (t.session_data->>'_auth_user_id')::integer as user_id,
            FALSE as new_session
    FROM t
    INTO session ;

    IF NOT FOUND THEN
        json := '{"session_start_time":"'|| request_timestamp || '"}' ;
        expire := request_timestamp::timestamptz + interval '14 days' ;
        data := encode(
            decode(
                encode(
                    hmac(
                        json,
                        session_secret,
                        'sha1'::text
                        ),
                    'hex'::text) || ':' || json,
                    'escape'::text),
                'base64') ;
        LOOP
            WITH t AS (
            INSERT INTO "django_session"
                        (
                        session_key,
                        expire_date,
                        session_data
                        )
                 VALUES (
                        random_string(32)::varchar,
                        expire,
                        data
                        )
                ON CONFLICT DO NOTHING
                RETURNING
                        "django_session"."session_key"::varchar(40) as session_key,
                        expire_date as session_expire_date,
                        substr(encode(decode(session_data,
                        'base64'), 'escape'), 42)::json as session_data_field
            )
            SELECT
                t.session_key as session_key,
                t.session_expire_date as session_expire_date,
                t.session_data_field as session_data_field,
                (t.session_data_field->>'_auth_user_id')::integer as user_id,
                TRUE as new_session
            FROM t
            INTO session;
            EXIT WHEN FOUND;
        END LOOP;
    END IF;

    -- Return Session and Page data
    RETURN QUERY SELECT 200,
                        session.session_key,
                        session.session_expire_date,
                        session.session_data_field,
                        session.user_id,
                        session.new_session;
    RETURN ;
 END
$BODY$
LANGUAGE plpgsql;

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
    dns_aaaa_record.ttl as ttl,
    dns_domain.name as domainname,
    dns_soa_record.id as soa_id,
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
    ('mozumder.net' NOT LIKE '%' || dns_aaaa_record.fqdn AND
    'mozumder.net' LIKE '%' || dns_domain.name AND
    dns_aaaa_record.domain_id = dns_domain.id AND
    dns_soa_record.domain_id = dns_domain.id
    )


select
    6 as type,
    dns_aaaa_record.name as name,
    dns_aaaa_record.ttl as ttl,
    dns_domain.name as domainname,
    dns_soa_record.id as soa_id,
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

    ('la.mozumder.net' NOT LIKE '%' || dns_aaaa_record.fqdn AND
    'la.mozumder.net' LIKE '%' || dns_domain.name AND
    dns_aaaa_record.domain_id = dns_domain.id AND
    dns_soa_record.domain_id = dns_domain.id
    )


    ('la.mozumder.net' NOT LIKE '%' || dns_aaaa_record.fqdn AND
    'la.mozumder.net' LIKE '%' || dns_domain.name AND
    dns_aaaa_record.domain_id = dns_domain.id AND
    dns_soa_record.domain_id = dns_domain.id
    )
    AND NOT
    'mozumder.net' NOT LIKE '%' || dns_aaaa_record.fqdn AND
    OR
    (dns_aaaa_record.fqdn != 'mozumder.net' AND
    'mozumder.net' LIKE '%' || dns_domain.name AND
    dns_aaaa_record.domain_id = dns_domain.id AND
    dns_soa_record.domain_id = dns_domain.id ) OR

    dns_soa_record.domain_id != dns_aaaa_record.domain_id AND
;
    AND
;


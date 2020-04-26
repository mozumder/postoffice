#/bin/sh
./manage.py createdomain --email dns@dnsmadeeasy.com mozumder.net 108.51.234.125 ns0.dnsmadeeasy.com ns1.dnsmadeeasy.com ns2.dnsmadeeasy.com ns3.dnsmadeeasy.com ns4.dnsmadeeasy.com
./manage.py addhost -dyn mozumder.net 108.51.234.125 admin
./manage.py addhost -dyn mozumder.net 108.51.234.125 api
./manage.py addhost -dyn mozumder.net 108.51.234.125 beta
./manage.py addhost -dyn mozumder.net 108.51.234.125 blog
./manage.py addhost -dyn mozumder.net 108.51.234.125 bobby
./manage.py addhost -dyn mozumder.net 108.51.234.125 cdn
./manage.py addredundantadddress mozumder.net 83.136.180.204 cdn
./manage.py addhost -dyn mozumder.net 108.51.234.125 db
./manage.py addhost -dyn mozumder.net 108.51.234.125 django
./manage.py addhost -dyn mozumder.net 108.51.234.125 ftp
./manage.py addhost -dyn mozumder.net 108.51.234.125 git
./manage.py addhost -dyn mozumder.net 108.51.234.125 gitlab
./manage.py addhost -dyn mozumder.net 108.51.234.125 home
./manage.py addhost -dyn mozumder.net 108.51.234.125 imap
./manage.py addhost -6 fe80::216:3eff:fe46:abc3 mozumder.net 83.136.180.204 la
./manage.py addhost -mx -dyn mozumder.net 108.51.234.125 mail
./manage.py addhost -dyn mozumder.net 108.51.234.125 mohammed
./manage.py addhost -dyn mozumder.net 108.51.234.125 news
./manage.py addhost -dyn mozumder.net 108.51.234.125 ns
./manage.py addhost -dyn mozumder.net 108.51.234.125 ns0
./manage.py addhost -dyn mozumder.net 108.51.234.125 ns1
./manage.py addhost -dyn mozumder.net 108.51.234.125 ns2
./manage.py addhost -dyn mozumder.net 108.51.234.125 ns3
./manage.py addhost -dyn mozumder.net 108.51.234.125 ns4
./manage.py addhost -dyn mozumder.net 108.51.234.125 ns5
./manage.py addhost -dyn mozumder.net 108.51.234.125 ntp
./manage.py addhost -dyn mozumder.net 108.51.234.125 ntp0
./manage.py addhost -dyn mozumder.net 108.51.234.125 ntp1
./manage.py addhost -dyn mozumder.net 108.51.234.125 omar
./manage.py addhost -dyn mozumder.net 108.51.234.125 pop
./manage.py addhost -dyn mozumder.net 108.51.234.125 redis
./manage.py addhost -dyn mozumder.net 108.51.234.125 roohi
./manage.py addhost -dyn mozumder.net 108.51.234.125 rspamd
./manage.py addhost -dyn mozumder.net 108.51.234.125 shahryar
./manage.py addhost -6 fe80::216:3eff:fe46:abc3 mozumder.net 83.136.180.204 smtp
./manage.py addhost -dyn mozumder.net 108.51.234.125 stats
./manage.py addhost -dyn mozumder.net 108.51.234.125 uwsgi
./manage.py addhost -dyn mozumder.net 108.51.234.125 vpn
./manage.py addhost -dyn mozumder.net 108.51.234.125 www
./manage.py addhost -dyn mozumder.net 108.51.234.125 zinnia
./manage.py createredirect mozumder.net la mail2
./manage.py addtxtrecord mozumder.net 'Sendinblue-code:3fe1ac48ac4588d17c0515b589b70bf4'
./manage.py addtxtrecord mozumder.net 'v=spf1 a mx ptr include:spf.sendinblue.com +ip4:108.51.234.125 +ip4:83.136.180.204 -all'
./manage.py addtxtrecord mozumder.net 'google-site-verification=Fi4VXVWVF8D0njI1JTUbXzKpQRGwYbPw6tgYUCdW5xc'
./manage.py addtxtrecord -n 2019102201._domainkey mozumder.net 'v=DKIM1; k=rsa; p=MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEA0kIjkMO4lXDTvmtiYdAv7ieKOQJXAKp+2wfXfvAG0Jex7APqKWnl816b4/voyyy8JcsrFph2Ug1EAKlSp9Rx/BomZM8aT1HmWeU4yIBvziexOTIsyRD5L6cweu38l7oIaruPJma4t8rHqQZfqLnHNWSO4lrkXKrGUYWTEN58DVjOmKAWSeTR6IPreb2qHiY2KVb5iJOv/zhR322yf5BC3JvxZ56BDXATaMjjVYpDNTslQp7jbu1wwxlmh2S5xx7VNqs7Zv90Yb2dIGQmgsJnh3YQhwibWK2CUbzeD9jXXq1RIs/wzTrK4cgutzHvOPTHoEMaB7RfbdGU9PTYWAmAbwIDAQAB'
./manage.py addtxtrecord -n _dmarc mozumder.net 'v=DMARC1; p=reject; sp=reject; rua=mailto:dmarcrua@mozumder.net!10m; ruf=mailto:dmarcruf@mozumder.net!10m; rf=afrf; pct=100; ri=86400'

./manage.py createdomain --email dns@dnsmadeeasy.com futureclaw.com  108.51.234.125 ns0.dnsmadeeasy.com ns1.dnsmadeeasy.com ns2.dnsmadeeasy.com ns3.dnsmadeeasy.com ns4.dnsmadeeasy.com
./manage.py addhost -dyn futureclaw.com 108.51.234.125 www
./manage.py addmailexchange futureclaw.com mail.mozumder.net

./manage.py createzone --email info@mozumder.net 10.IN-ADDR.ARPA ns.mozumder.net

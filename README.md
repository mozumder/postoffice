# Postoffice

Postoffice is a DNS origin server written in Python and Django using Postgres as the back-end database. You can administer it from the web interface, or you can use it from the command line shell:

    % ./manage.py createdomain --email admin@example.com example.com 123.123.123.123 ns0.example.com ns1.example.com
    % ./manage.py addhost example.com 123.123.123.123 www
    % ./manage.py addhost example.com 123.123.123.123 mail
    % ./manage.py rundnsserver --processes 4

## Installation

First, download and install Postgresql. Instructions for that are platform-specific and outside of the scope of this document, so please visit [https://www.postgresql.org/download/](https://www.postgresql.org/download/ "Postgresql")  to download for your platform.

Once you have Postgresql installed and running, create a Postgresql user as well as a database for Postoffice. This can be done with Postgresql's psql command shell by logging in as a Postgres administrator:

    % psql -U postgres
    postgres=# create role postmaster with login passowrd 'pick-a-password';
    postgres=# create database postoffice with owner postmaster;
    postgres=# exit

Next, download Postffice by cloning this repository:

    % git clone https://github.com/mozumder/postoffice.git
    % cd postoffice

Then, install all the Python components, including Django, by running installing from the pip requirements.txt file:

    % pip install -r requirements.txt
    
(Hint: use a Python virtualenvironment so you don't clobber the base python instlalation)

Inside this directory, create a .env vile with some basic information to run Django:

    % vi .env
    
Add the following lines to the .env file:
    
    DJANGO_SETTINGS_MODULE=postoffice.settings
    DJANGO_RUN_ENV=prod
    SECRET_KEY='random-52-byte-string'
    DEBUG=False
    ALLOWED_HOSTS=127.0.0.1
    LOG_DIR=log
    POSTGRES_HOST=127.0.0.1
    POSTGRES_PORT=
    POSTGRES_USER=postmaster
    POSTGRES_PW=postgres-passwprd
    POSTGRES_DB=postoffice
    
You then initialize the Django database 

    % ./manage.py makemigrations
    % ./manage.py migrate
    % ./manage.py createsuperuser

At this point you can start to administer and run Postoffice.

You first create a domain that it should serve:

    % ./manage.py createdomain --email admin@example.com example.com 123.123.123.123 nameserver0.example.com nameserver1.example.com

Then you can add individual hosts to that domain:

    % ./manage.py addhost example.com 123.123.123.123 mail
    % ./manage.py addhost example.com 123.123.123.123 www

Finally you would run the DNS server for your domain:

    % ./manage.py rundnsserver 

Note that you need to run this dns server on two machines, and have them connect to the same database. This is a requirement for the DNS system for redundancy purposes.

To actualy serve DNS requests from the world, tell your DNS registrar the IP address of the two DNS servers you are running Postoffice.

## Web Interface

The web interface to edit the database can be run with the standard Django web server::

    % ./manage.py runesrver
    
And the database can be accessed under http://localhost/admin

## Commands

There are several additional commands to configure your DNS server available to you. You can find a list of these commands through the Django help system:

    % ./manage.py help

This will give the following list of commands:
    
    [dns]
    addcaarecord
    adddyndnsrecord
    addhost
    addmailexchange
    addredundantadddress
    addreversednsptr
    addsrvrecord
    addtxtrecord
    createdomain
    createdyndnsaccount
    createredirect
    createzone
    deletecanonicalalias
    deletedomain
    deletedyndnsrecord
    deletehost
    dnsclient
    listarecords
    listdomains
    listhosts
    monitordynamicip
    rundnsserver
    updatearecords
    updatedynamicip

You can find help on each individual command with:

    % ./manage.py [command] --help

## Notes and To-do

Postoffice is in the prototype phase, so use at your own risk. As of now Postoffice is not a DNS recursive resolver. You wouldn't use it for your personal computer's DNS server. Instead, Postoffice is an origin server. You would use it when you register a domain name, and you want the rest of the world to find all the hosts for your domain.  Eventually this will include being a recursive resolver, as well as being secure with DNSSEC and other fun features.

Ultimately, this project will include an IMAP/SMTP mail server to replace the incredibly complicated Dovecot and Postfix, which is why this project is nameed Postoffice. The DNS server is only the first step to get things going. But that's a long-term goal.

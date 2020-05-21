# Postoffice

Postoffice is a modern simplified DNS origin server written in Python 3.8 and Django using Postgres as the back-end database. You can administer it from the web interface or from the command line shell:

    $ ./manage.py createdomain --email admin@example.com example.com 123.45.67.89 ns0.mynameservers.com ns1.mynameservers.com
    $ ./manage.py addhost example.com 123.45.67.89 www
    $ ./manage.py addhost -mx example.com 123.45.67.90 mail
    $ ./manage.py rundnsserver --processes 4
    
It even includes a DNS-over-HTTP server under the url /dns/query?dns
    
## Installation

First, download and install Postgresql. Instructions for that are platform-specific and outside of the scope of this document, so please visit [https://www.postgresql.org/download/](https://www.postgresql.org/download/ "Postgresql")  to download for your platform.

Once you have Postgresql installed and running, create a Postgresql user as well as a database for Postoffice. This can be done with Postgresql's psql command shell by logging in as a Postgres administrator:

    $ psql -U postgres
    postgres=# create role postmaster with login passowrd 'pick-a-password';
    postgres=# create database postoffice with owner postmaster;
    postgres=# exit

Next, download Postffice by cloning this repository:

    $ git clone https://github.com/mozumder/postoffice.git
    $ cd postoffice

Then, install all the Python components, including Django, by running installing from the pip requirements.txt file:

    $ pip install -r requirements.txt
    
(Hint: use a Python virtualenvironment so you don't clobber the base python instlalation)

Inside this directory, create a .env vile with some basic information to run Django:

    $ vi .env
    
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

    $ ./manage.py makemigrations
    $ ./manage.py migrate
    $ ./manage.py createsuperuser

At this point you can start to administer and run Postoffice.

You first create a domain that it should serve:

    $ ./manage.py createdomain --email admin@example.com example.com 123.45.67.89 ns0.mynameservers.com ns1.mynameservers.com
    
This creates the Start-of-authority record as well listing the names of two name servers that this are the origin name servers for the domain.

Then you can add individual hosts to that domain:

    $ ./manage.py addhost example.com 123.45.67.89 www
    $ ./manage.py addhost -mx example.com 123.45.67.90 mail
    
You can configure all sorts of things for your domain, incuding adding TXT and other domain name records.

Finally you would run the DNS server for your domain by logging into your dns server machine that has access to the install directory and starting the DNS server:

    $ ssh ns0.mynameservers.com
    postmaster@ns0 $ cd install-directory
    postmaster@ns0 install-directory$ ./manage.py rundnsserver 

Note that you need to run this dns server on two machines, and have them connect to the same database. This is a requirement for the DNS system for redundancy purposes. To do that you will have to log into another system that has the install directory available, and run another DNS server:

    $ ssh ns1.mynameservers.com
    postmaster@ns1 $ cd install-directory
    postmaster@ns1 install-directory$ ./manage.py rundnsserver 

To actualy serve DNS requests from the world, tell your DNS registrar the IP address of the two DNS servers you are running Postoffice.

## Web Interface

The web interface to edit the database can be run with the standard Django web server::

    % ./manage.py runesrver
    
And the database can be accessed under http://localhost/admin

## Commands

There are several additional commands to configure your DNS server available to you. You can find a list of these commands through the Django help system:

    % ./manage.py help

This will list all available commands, with the DNS commands in the DNS section:
    
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

Postoffice is in the concept prototype phase, so use at your own risk. The database and interfaces are continuously redesigned. 

As of now Postoffice is not a DNS edge server with a recursive resolver. You wouldn't use it for your personal computer's DNS server. Instead, Postoffice is an origin server. You would use it when you register a domain name, and you want the rest of the world to find all the hosts for your domain.  Eventually this will also be an edge server, as well as adding security through DNSSEC and other fun features, but right now it's specifically a basic origin server.

Ultimately, this project will include an IMAP/SMTP mail server to replace the incredibly complicated Dovecot and Postfix, which is why I started this project and named Postoffice. The DNS server is only the first step to get things going. But that's a long-term goal.

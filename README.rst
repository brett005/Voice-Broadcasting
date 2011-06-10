.. image:: https://github.com/Star2Billing/newfies/raw/master/newfies/resources/images/newfies.png


Newfies is a bulk dialer application which was commissioned by a charity named
Kubatana (http://www.kubatana.net) based in Zimbabwe, which sponsors the 
Freedomfone project (http://www.freedomfone.org/) dedicated to providing 
information via phone technology.

In less economically developed countries, Internet is often limited, but there
is usually comprehensive mobile phone coverage. Freedomfone will use Newfies 
to dial up people’s phones and offer health information on Cholera, Malaria 
and so many other avoidable health issues in the third world, which may be 
alleviated by education. Newfies was so named after the Newfoundland Dog 
which is used by sea rescue services around the world.

Newfies has been built using a messaging system so that it can support 
distributed processing on cloud servers. The platform is focused on real-time
operations and task call distributions to clustered brokers and workers 
meaning that many millions of calls can be processed daily.

Newfies can be installed on a standalone server for smaller deployments. 
It currently utilises the Freeswitch Telephony engine 
(http://www.freeswitch.org) to process the the outbound calls however support
for other telephony engines, such as Asterisk may be added in the future.

Newfies is written in Python using the Django Framework, and operates with
message brokers such as RabbitMQ and Redis using the emerging open standard
for messaging middleware, AMPQ (Advance Messaging Queuing Processing). 
Beanstalk, MongoDB, CouchDB and DBMS can also be supported.

In order to communicate with external systems, Newfies has been released with 
comprehensive set of API's to easily integrate the platform with third-party 
applications. Furthermore, Newfies is supplied with a comprehensive 
administrative and user interface which allow you and your customers to create
outbound call campaigns, add phonebooks, subscribers, as well as record audio 
messages and design more complex IVR (Interactive Voice Response) applications.
When ready and tested, the campaign can be launched from the interface.


Who is it for ?
---------------

NGOs :

    - Newfies was commissioned by the Kubatana NGO Alliance (kubatana.net).
      They needed a platform on which to deliver large numbers of messages to
      different communities. The platform can be used to offer complex data 
      collection, voting applications and notification for availability of 
      supplies.

Marketing :

    - Newfies is a strong telephony based marketing tool to deliver 
      advertising to your company's contacts.

Emergency :

    - Provide a message delivery platform to quickly and efficiently send 
      messages to communities.

Finance :    

    - Debt Recovery and Reminders, this can be easily integrated with call 
      centre software and processes. 

Health & Welfare :
    
    - Deliver appointment reminders to patients of dentists, doctors and 
      other organisations.


Terminology
-----------

**User :** The Person configuring the campaigns and wishing to deliver 
messages.

**Subscriber :** Person who will receive the message.

**Administrator :** Person administering the platform, usually with root 
permission.

**Gateway :** Peer which will outbound a call and deliver the message to 
the subscriber.

**Phonebook :** Group of subscribers, this is used to define the subset of 
subscribers that will receive the message.

**CDR :** Call Detail Record, keep track of the calls performed by the 
system, eventually can be used for monitoring and billing purposes.

**Call Request :** Describes the request to the system to run a call to a 
subscriber.

**Audio Application :** This can be a simple audio delivery, a routing to 
another gateway, forwarded to a Call-Centre, in fact, any to any 
application that can be built on Freeswitch.


Installation
------------

Newfies is a django based application, so the major requirements are :

    - python >= 2.4
    - Apache / http server with WSGI modules
    - Django Framework >= 1.3
    - Celery >= 2.2
    
The rest of the requirement can easily be installed with PIP 
(http://pypi.python.org/pypi/pip) :

    - https://github.com/Star2Billing/newfies/blob/master/newfies/requirements.txt


Newfies takes advantage of  messaging systems such as RabbitMQ or Redis. Other 
alternatives provided by Celery (http://celeryproject.org) are also supported.

    - Install RabbitMQ : https://github.com/Star2Billing/newfies/raw/master/newfies/docs/install_rabbitmq.txt
    - or Install Redis : https://github.com/Star2Billing/newfies/raw/master/newfies/docs/install_redis.txt

An installation script can be found here : https://github.com/Star2Billing/newfies/blob/master/scripts/install-newfies.sh


Installation Script
~~~~~~~~~~~~~~~~~~~

An installation script is provided to install the web interface, this doesn't 
include the install and configuration of RabbitMQ or Redis.

    - https://github.com/Star2Billing/newfies/raw/master/scripts/install-newfies.sh
   

Documentation
-------------

General documentation :

    - https://github.com/Star2Billing/newfies/blob/master/docs/

RestFul API :

    - https://github.com/Star2Billing/newfies/raw/master/docs/api_doc.pdf


Applications
------------

* User Interface :
    http://localhost:8000/
    This application provides a User interface for restricted management of 
    the User's Campaign, Phonebook, Subscriber. It also provides detailed 
    Reporting of calls and message delivery.

* Admin Interface :
    http://localhost:8000/admin/
    This interface provides user (ACL) management, a full control of all 
    Campaigns, Phonebooks, Subscribers, Gateway, configuration of the 
    Audio Application.


Screenshot
----------

.. image:: https://github.com/Star2Billing/newfies/raw/master/docs/_static/images/admin_screenshot.png


Coding Conventions
------------------

This project is PEP8 compilant and please refer to these sources for the Coding 
Conventions :

    - http://docs.djangoproject.com/en/dev/internals/contributing/#coding-style

    - http://www.python.org/dev/peps/pep-0008/
    

Additional information
-----------------------

Fork the project on GitHub : https://github.com/Star2Billing/newfies

License : AGPL (https://github.com/Star2Billing/newfies/blob/master/COPYING)

Website : http://www.newfies-dialer.org


Support 
-------

Star2Billing S.L. (http://www.star2billing.com) offers consultancy including 
installation, training and customization 

Please email us at sales@star2billing.com for more information


# Weladee - Odoo 



![Weladee logo](https://vgy.me/jlVton.png)![odoo](https://goo.gl/D9uZDJ)

## What is Weladee?

Weladee is a "In The Cloud" service to manage employee attendance.
It's developed to be simple, fast and cheap to use for any small company (or even big ones).
The primary market of this service is Thailand for now (2017).

Take a look: https://www.weladee.com


## Description

Odoo module for Weladee

This Odoo module create the link between Weladee and your Odoo instance.

You will be able to synchronize departments, employees and attendance.

## Technical

### gRPC

[gRPC](https://grpc.io) is used to communicate with [weladee](https://www.weladee.com) server.
The http2 protocol and stream push between client and server offer excellent performances.
The communication between Odoo & Weladee is encrypted by TLS 1.3


### API Key

To connect your Odoo instance to [weladee](https://www.weladee.com) server you need an api key.
The api key is available when you create an account at http://www.weladee.com/register

Weladee is free to subscribe with 3 months trial period or even 100% free for company with less than 5 employees.

--------------------------------------------------------------
(c) 2017 [Frontware International](https://www.frontware.co.th)
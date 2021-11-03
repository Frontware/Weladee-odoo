# Weladee - Odoo

[![Gitter chat](https://badges.gitter.im/gitterHQ/gitter.png)](https://gitter.im/weladee)
[![Coverage Status](https://coveralls.io/repos/github/Frontware/Weladee-odoo/badge.svg?branch=odoo11)](https://coveralls.io/github/Frontware/Weladee-odoo?branch=odoo11)

![Weladee logo](https://vgy.me/jlVton.png)![odoo](https://vgy.me/5KoRp0.png)

## What is Weladee?

Weladee is a service "In The Cloud" to manage employee attendance.
It's developed to be **simple**, **fast** and **cheap** to use for any small company (or even big ones).
The primary market of this service is **Thailand** for now (2018), we started to deploy customers in Cambodia too.

Take a look at https://www.weladee.com

### Why using Weladee?

Because employee lateness and absenteeism cost a lot of money to your company.
Weladee provides a very easy way to reduce it.

See how much lateness costs you with our simulation page: https://www.weladee.com/simulation

## Description

[Odoo](https://www.odoo.co.th) module for Weladee

This Odoo module create the link between Weladee and your Odoo 11.0 instance.

You will be able to synchronize departments, employees and attendance.

## Technical

### gRPC

[gRPC](https://grpc.io) is used to communicate with [weladee](https://www.weladee.com) server.
The http2 protocol and stream push between client and server offer excellent performances.
The communication between Odoo & Weladee is encrypted with SSL3 and TLS 1.3 certificate.

Sample calls:

![uml](https://goo.gl/AFpwfs)

### API Key

To connect your Odoo instance to [weladee](https://www.weladee.com) server you need an api key.
The api key is available when you create an account at https://www.weladee.com/register

Weladee is free to subscribe with 3 months trial period or even 100% free for company with less than 5 employees.

## Sample Code for gRPC API

It's ready for Odoo 11. gRPC code is compatible python 2 & 3.

### Connect to server

```python
    import grpc
    import . from weladee_pb2
    import . from weladee_pb2_grpc
  

    # Weladee grpc server address is grpc.weladee.com:22443
    address = "grpc.weladee.com:22443"

    # Define a secure channel with embedded public certificate

    creds = grpc.ssl_channel_credentials(certificate)
    channel = grpc.secure_channel(address, creds)
```

### Provide api-key and get some data

This code retrieve the list of departments and add a holiday to Weladee.

```python
    # Connect from Odoo
    # Place here the token specific to each company. It's called api_key in table company

    authorization = [("authorization", "bc7f3c00-bfa4-4ac2-810b-a11dca5ec48e")]

    stub = weladee_pb2_grpc.OdooStub(channel)

    # List all departments
    print("Departments")
    for dept in stub.GetDepartments(myrequest, metadata=authorization):
        print(dept)

    # Add new holiday
    newHoliday = weladee_pb2.HolidayOdoo()
    newHoliday.Holiday.date = 20170918
    newHoliday.Holiday.name_english = "Company holiday"
    newHoliday.odoo.odoo_id = 9
    try:
        result = stub.AddHoliday(newHoliday, metadata=authorization)

        print (result.id)
    except Exception as e:
        print("Add holiday failed",e)
```

### Get all logs from Weladee not yet sync with Odoo

Simple code parsing a stream of log events that need to be synchronized with Odoo.

```python
    # List of attendance to sync
    print("Attendance to sync")
    i=0
    for att in stub.GetNewAttendance(weladee_pb2.Empty(), metadata=authorization):
        i+=1
        logging.log(i,att)
```

--------------------------------------------------------------
(c) 2021 [Frontware International Co,Ltd.](https://www.frontware.co.th)
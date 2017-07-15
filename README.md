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
The communication between Odoo & Weladee is encrypted with SSL3 and TLS 1.3 certificate.

Sample calls:

![uml](https://goo.gl/3xyzN5)


### API Key

To connect your Odoo instance to [weladee](https://www.weladee.com) server you need an api key.
The api key is available when you create an account at https://www.weladee.com/register

Weladee is free to subscribe with 3 months trial period or even 100% free for company with less than 5 employees.


## Sample Code for gRPC API

### Connect to server

```python
    import grpc
    import weladee_pb2
    import weladee_pb2_grpc
  
   
    # Weladee grpc server address is hrpc.weladee.com:22443
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
    for dept in stub.GetDepartments(myrequest, metadata=token):
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
   
      

--------------------------------------------------------------
(c) 2017 [Frontware International](https://www.frontware.co.th)
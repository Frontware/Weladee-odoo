command for set grpc

Example code :
address = "grpc.weladee.com:22443"
creds = grpc.ssl_channel_credentials(certificate) <- certificate is grpc certificate
channel = grpc.secure_channel(address, creds)

 authorization = [("authorization", "[ authorization from weladee ]")]
 for dept in stub.GetDepartments(myrequest, metadata=authorization):
    print(dept)

if you want to get datas from DEV and run on your local then go to /etc/hosts and add command :

192.168.1.28  grpc.weladee.com
echo run from folder weladee
echo
echo example:
echo
echo "./tools/proto.sh ~/git/odoo/weladee ~/go/src/frontware.com/weladee/proto"
echo 
echo will get proto from $2 to $1

cd $2
git pull gitlab develop

cp python/* "$1/Modules/Weladee_Attendances/models/grpcproto/"

cd $1
echo patching code at Modules/Weladee_Attendances/models/grpcproto...
echo
node tools/update_proto.js
echo 
echo done

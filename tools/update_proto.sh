echo !*****************************!
echo !                             
echo !! must run at folder weladee
echo !                             
echo !*****************************!
echo

cd ..
echo
# update git
if [ -d "weladee-proto" ]; then
    echo pull...
    cd weladee-proto
    git pull
    git checkout develop
    git pull gitlab develop
else
    echo cloning...
    git clone -o gitlab --depth 1 git@gitlab.com:frontware_International/Weladee/proto.git weladee-proto
    cd weladee-proto
fi

echo
echo update..
cp python/* ../weladee/Modules/Weladee_Attendances/models/grpcproto

echo
echo fix...
# fix import  
for file in ../weladee/Modules/Weladee_Attendances/models/grpcproto/*
do
    echo change $file ..
    sed -i "s|import weladee_pb2 as|from . import weladee_pb2 as|g" $file
    sed -i "s|import timesheet_pb2 as|from . import timesheet_pb2 as|g" $file
    sed -i "s|import expense_pb2 as|from . import expense_pb2 as|g" $file
    sed -i "s|import approval_pb2 as|from . import approval_pb2 as|g" $file
    sed -i "s|import skill_pb2 as|from . import skill_pb2 as|g" $file
    sed -i "s|import job_pb2 as|from . import job_pb2 as|g" $file
    sed -i "s|import odoo_pb2 as|from . import odoo_pb2 as|g" $file

done

echo 
echo copying...done
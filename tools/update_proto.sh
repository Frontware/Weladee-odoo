echo !*****************************!
echo !                             
echo !! must run at folder weladee/odoo
echo !                             
echo !*****************************!
echo

branch=$1

if [ "$1" = "" ]
then
    $branch=develop
fi

cd ..
echo get $branch
# update git
if [ -d "weladee-proto" ]; then
    echo pull...
    cd weladee-proto
    git pull gitlab $branch
else
    echo cloning...
    git clone -o gitlab --depth 1 git@gitlab.com:frontware_International/Weladee/proto.git weladee-proto
    cd weladee-proto
    git checkout $branch
fi

echo
echo update..
rm -R -f ../odoo/Modules/Weladee_Attendances/models/grpcproto/*
cp python/* ../odoo/Modules/Weladee_Attendances/models/grpcproto


echo 
echo copying...done
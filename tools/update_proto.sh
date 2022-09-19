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
    git pull gitlab master
else
    echo cloning...
    git clone -o gitlab --depth 1 git@gitlab.com:frontware_International/Weladee/proto.git weladee-proto
    cd weladee-proto
fi

echo
echo update..
rm -R -f ../weladee/Modules/Weladee_Attendances/models/grpcproto/*
cp python/* ../weladee/Modules/Weladee_Attendances/models/grpcproto


echo 
echo copying...done
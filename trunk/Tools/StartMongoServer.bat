@echo off

set MY_SLEEP=ping 1.1.1.1 -n 1 -w

echo Create mongod server data directory
md _mongo_data_dir 2>nul
attrib +H _mongo_data_dir

echo Start monogod server
start "MongoServer" /MIN mongod --bind_ip 127.0.0.1 --port 27017 --dbpath ./_mongo_data_dir --logpath mongo.log --logappend

if %ERRORLEVEL% NEQ 0 echo "failed to start mongod"
%MY_SLEEP% 1000 >nul
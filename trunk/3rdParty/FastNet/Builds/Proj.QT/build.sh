debug=$1
clean=$2

qmake FastNet.pro

if [ $clean == 'clean' ]
then                 
	make clean
fi 


if [ $debug == 'debug' ]
then
	make debug -j16
fi	

if [ $debug == 'release' ]
then
	make release -j16
fi

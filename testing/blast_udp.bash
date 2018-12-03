while true
do
    #random=$(dd if=/dev/urandom bs=65000 count=1 status=noxfer)
    #echo $random | nc -w 0 -u $1 9005 
    nc -w 0 -u 192.168.1.220 9005 < /dev/urandom
done

ncat -l -k -p 4444 > /dev/null & ncat_pid=$!

n=3
for i in $(seq 1 $n)
do
    dd if=/dev/zero status=noxfer count=5 bs=100M | pv -L 200M | ncat localhost 4444 # 500Mb
    sleep 1
    dd if=/dev/zero status=noxfer count=4 bs=500M | pv -L 500M | ncat localhost 4444 #2Gb
    sleep 3
    dd if=/dev/zero status=noxfer count=5 bs=200M | pv -L 100M | ncat localhost 4444 # 1Gb
    dd if=/dev/zero status=noxfer count=50 bs=10M | pv -L 50M | ncat localhost 4444 # 500Mb
    sleep 2
    echo "epoch $i out of $n"

done

kill $ncat_pid

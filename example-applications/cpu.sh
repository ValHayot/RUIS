n=3
for i in $(seq 1 $n)
do
    stress --quiet --cpu $(nproc) --timeout 3
    sleep 2
    stress --quiet --cpu $(($(nproc) / 5)) --timeout 1
    stress --quiet --cpu $(($(nproc) / 2)) --timeout 2
    stress --quiet --cpu $(($(nproc))) --timeout 3
    stress --quiet --cpu $(($(nproc) / 2)) --timeout 2
    stress --quiet --cpu $(($(nproc) / 5)) --timeout 1
    sleep 2
    stress --quiet --cpu $(nproc) --timeout 3
    sleep 1
    echo "epoch $i out of $n"

done

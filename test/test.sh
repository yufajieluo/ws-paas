index=1
while [ $index -le 10 ]
do
    echo $index
    index=$(($index + 1))
    sleep 1
done

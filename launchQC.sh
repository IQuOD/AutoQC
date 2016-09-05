# bash launchQC.sh <number of profiles> <number of processes>

QUEUE=$(($1 / $2))

for i in `seq 0 $(($2 - 2))`
do
  echo python AutoQC.py demo $(($i * $QUEUE)) $(($(($i + 1)) * $QUEUE)) &
done

echo python AutoQC.py demo $(( $(($i + 1)) * $QUEUE)) $1 &


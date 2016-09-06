# bash launchQC.sh <database table> <number of profiles> <number of processes>

QUEUE=$(($2 / $3))

for i in `seq 0 $(($3 - 2))`
do
  python AutoQC.py $1 $(($i * $QUEUE)) $(($(($i + 1)) * $QUEUE)) &
done

python AutoQC.py $1 $(( $(($i + 1)) * $QUEUE)) $2 &

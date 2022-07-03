#!/bin/bash

#ALGS="fuzzy kapusta rfid"
ALGS="kapusta"
DIRS="improvement improvement-affected runtime tls-mean tls-total timeloss" 
#DIRS="improvement improvement-affected runtime timeloss" 
LOCATION=$1
BASEFOLDER=$2
EV=$3
NOPREEMPT="no-preemption"

for l in $LOCATION; do
	for i in $ALGS; do
		for j in $DIRS; do
			echo "./plot-$i.sh $LOCATION $BASEFOLDER/$j/$i $EV"
			./plot-$i.sh $LOCATION $BASEFOLDER/$j/$i $EV
		done 
	done
	echo "./plot-ttt.sh $LOCATION $BASEFOLDER/ttt $EV"
	./plot-ttt.sh $LOCATION $BASEFOLDER/ttt $EV
	echo "./plot-$NOPREEMPT.sh $LOCATION $BASEFOLDER/runtime/$NOPREEMPT $EV"
	./plot-$NOPREEMPT.sh $LOCATION $BASEFOLDER/runtime/$NOPREEMPT $EV
done



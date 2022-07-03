#!/bin/bash

ALGS="fuzzy kapusta rfid"
DIRS="improvement improvement-affected runtime tls-mean tls-total timeloss" 
LOCATION=$1
BASEFOLDER=$2
NOPREEMPT="no-preemption"

for l in $LOCATION; do
	for i in $ALGS; do
		for j in $DIRS; do
			echo "./plot-$i.sh $l $BASEFOLDER/$j/$i"
			./plot-$i.sh $l $BASEFOLDER/$j/$i
		done 
	done
	echo "./plot-ttt.sh $l $BASEFOLDER/ttt"
	./plot-ttt.sh $l $BASEFOLDER/ttt
	echo "./plot-$NOPREEMPT.sh $l $BASEFOLDER/runtime/$NOPREEMPT"
	./plot-$NOPREEMPT.sh $l $BASEFOLDER/runtime/$NOPREEMPT
done



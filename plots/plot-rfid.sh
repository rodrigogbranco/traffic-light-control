#!/bin/bash

LOCATION=$1
FOLDER=$2

LABELS=($(cat ${FOLDER}/${LOCATION}-labels.dat))
NVEC=($(cat ${FOLDER}/${LOCATION}-nvec.dat))
INDEXES=($(cat ${FOLDER}/${LOCATION}-indexes.dat))

declare -a ARGS=()
j=0

IFS=$'\n'
for i in `cat ${FOLDER}/${LOCATION}-args.dat`
do
   ARGS[j]=$i
   let "j++"
done


gnuplot << EOF

	set lmargin at screen 0.15

	set key font ",19"
	set xtics font ",20" 
	set ytics font ",24" 
	set xlabel font ",28"  
	set ylabel font ",22" 

	set terminal png size 640,480 enhanced
	set output "${FOLDER}/${ARGS[3]}-${ARGS[0]}-${LOCATION}.png"
	set style fill solid border lc rgb "black"

	set key top right
	set xlabel "Number of vehicles"
	set ylabel "${ARGS[1]}"
	set boxwidth 0.3
	set grid
	set xrange [-1.5:13.6]
	set yrange [0:${ARGS[2]}]

	set xtics ("${NVEC[0]}" ${INDEXES[0]}, "${NVEC[1]}" ${INDEXES[1]}, "${NVEC[2]}" ${INDEXES[2]}, "${NVEC[3]}" ${INDEXES[3]}, "${NVEC[4]}" ${INDEXES[4]})

	plot \
		"${FOLDER}/${LOCATION}-${LABELS[0]}.dat" u (column(1)-1.2):2:3 w boxerrorbar lt rgb "#90EE90" fs pattern 2 title "${LABELS[0]}", \
		"${FOLDER}/${LOCATION}-${LABELS[1]}.dat" u (column(1)-0.9):2:3 w boxerrorbar lt rgb "#90EE90" fs pattern 1  title "${LABELS[1]}", \
		"${FOLDER}/${LOCATION}-${LABELS[2]}.dat" u (column(1)-0.6):2:3 w boxerrorbar lt rgb "#90EE90" fs pattern 3 title "${LABELS[2]}", \
		"${FOLDER}/${LOCATION}-${LABELS[3]}.dat" u (column(1)-0.3):2:3 w boxerrorbar lt rgb "#90EE90" fs pattern 4 title "${LABELS[3]}", \
		"${FOLDER}/${LOCATION}-${LABELS[4]}.dat" u (column(1)):2:3 w boxerrorbar lt rgb "#FF0000" fs pattern 5 title "${LABELS[4]}", \
		"${FOLDER}/${LOCATION}-${LABELS[5]}.dat" u (column(1)+0.3):2:3 w boxerrorbar lt rgb "#FF0000" fs pattern 3 title "${LABELS[5]}", \
		"${FOLDER}/${LOCATION}-${LABELS[6]}.dat" u (column(1)+0.6):2:3 w boxerrorbar lt rgb "#FF0000" fs pattern 4 title "${LABELS[6]}", \
		"${FOLDER}/${LOCATION}-${LABELS[7]}.dat" u (column(1)+0.9):2:3 w boxerrorbar lt rgb "#FF0000" fs pattern 7 title "${LABELS[7]}", \
		"${FOLDER}/${LOCATION}-${LABELS[8]}.dat" u (column(1)+1.2):2:3 w boxerrorbar lt rgb "#000000" fs pattern 8 title "${LABELS[8]}" 

EOF

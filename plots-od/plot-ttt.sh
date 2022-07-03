#!/bin/bash

LOCATION=$1
FOLDER=$2
EV=$3

NVEC=($(cat ${FOLDER}/${LOCATION}-nvec.dat))

gnuplot << EOF

	set lmargin at screen 0.18

	set key font ",14"
	set xtics font ",16" 
	set ytics font ",21" 
	set y2tics font ",21"
	set xlabel font ",27"  
	set ylabel font ",21" 
	set y2label font ",19" 
				

	set terminal png size 640,480 enhanced
	set output "${FOLDER}/nopreemption-${LOCATION}-${EV}-gnuplot.png"
	set style fill solid border lc rgb "black"

	set key top left
	set xlabel "Number of vehicles"
        set ylabel "Time Loss (s)" textcolor rgb "blue" offset -1
        set y2label "Time Loss / Actual Travel Time (%)"        textcolor rgb "red"
				set grid

        set xrange [${NVEC[0]}-1000:${NVEC[4]}+1000]
        set yrange [800:3100]
	      set y2range [0:100]
        set xtics nomirror
        set ytics nomirror  textcolor rgb "blue"
        set y2tics nomirror textcolor rgb "red"

        plot \
                "${FOLDER}/file-${LOCATION}-${EV}.dat" 	u 1:4:5 w yerrorlines lt rgb "blue" dt solid t "Timeloss", \
                ""             	u 1:2:3 w yerrorlines lt rgb "red" dt solid t "Time Loss / Actual Travel Time" axes x1y2, \
                #""             	u 1:(column(2)+5.5):2 with labels notitle tc rgb "red" axes x1y2, \
                #""             	u 1:(column(4)-4):4 with labels notitle tc rgb "blue"
EOF

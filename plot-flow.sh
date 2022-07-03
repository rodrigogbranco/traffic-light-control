#!/bin/bash

FOLDER=$2

QUEUELENGTH=($(cat /home/rodrigo/queue.dat))

gnuplot << EOF

	set lmargin at screen 0.18

	set key font ",14"
	set xtics font ",16" 
	set ytics font ",21" 
	set xlabel font ",27"  
	set ylabel font ",21" 
				

	set terminal png size 640,480 enhanced
	set output "/home/rodrigo/flow-gnuplot.png"
	set style fill solid border lc rgb "black"

	set key top left
	set xlabel "Queue Length (m)"
    set ylabel "Supported Flow (veh/s)"
	set grid

	#set xrange [${QUEUELENGTH[0]}-1000:${QUEUELENGTH[4]}+1000]
	#set yrange [-60:100]
	set xtics nomirror
	set ytics nomirror  textcolor rgb "blue"

	set style line 1 \
		linecolor rgb '#0060ad' \
		linetype 1 linewidth 1 \
		pointtype 7 pointsize 1.5
	set style line 2 \
		linecolor rgb '#dd181f' \
		linetype 1 linewidth 1 \
		pointtype 5 pointsize 1.5
	set style line 3 \
		linecolor rgb '#00ff00' \
		linetype 1 linewidth 1 \
		pointtype 5 pointsize 1.5
	set style line 4 \
		linecolor rgb '#ff00ff' \
		linetype 1 linewidth 1 \
		pointtype 5 pointsize 1.5
	set style line 5 \
		linecolor rgb '#707070' \
		linetype 1 linewidth 1 \
		pointtype 5 pointsize 1.5
	set style line 6 \
		linecolor rgb '#bebebe' \
		linetype 1 linewidth 1 \
		pointtype 5 pointsize 1.5										

	plot '/home/rodrigo/flow.dat' using 1:2 with linespoints linestyle 2 t "kapusta:v=50km/h,ct=60s", \
	     '' using 1:3 with linespoints linestyle 1 t "kapusta:v=75km/h,ct=90s", \
		 '' using 1:4 with linespoints linestyle 3 t "kapusta:v=100km/h,ct=120s", \
		 '' using 1:5 with linespoints linestyle 4 t "tpn:v=50km/h", \
		 '' using 1:6 with linespoints linestyle 5 t "tpn:v=75km/h", \
		 '' using 1:7 with linespoints linestyle 6 t "tpn:v=100km/h"

EOF

        

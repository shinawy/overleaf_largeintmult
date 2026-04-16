#!/bin/bash
ScatterDir="Scatter"
BarDir="Bar"
BubbleDir="Bubble"

Mul1024="Mul1024"
RealSize="RealSize"

# create all directories
mkdir -p $ScatterDir 
mkdir -p $BarDir 
mkdir -p $BubbleDir 

# cp files into the specified directory 
find . -maxdepth 1 -name "*scatter_*" -exec cp '{}' $ScatterDir/ \;
find . -maxdepth 1 -name "*bar*" -exec cp '{}' $BarDir/ \;
find . -maxdepth 1 -name "*bubble*" -exec cp '{}' $BubbleDir/ \;


find . -maxdepth 1 -name "*.pdf" -exec rm '{}' \;
tree .

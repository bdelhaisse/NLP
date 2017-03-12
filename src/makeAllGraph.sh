#!/bin/bash
# Script that automatically produces the tree<i>.png files from the tree<i>.ps files
# @author: Brian Delhaisse

echo "Producing tree<i>.png files from the tree<i>.ps files..."
for i in `ls tree*.ps`
do
   filename=`echo "${i%.*}"`
   file=`echo tree${filename:4}`

   echo "Producing $file.png"
   convert $file.ps $file.png 
   rm $file.ps
done
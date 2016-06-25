#! /bin/bash

for file in $@; do
    filename="${file%.*}"
    pdfcrop $file
    convert "$filename"-crop.pdf "$filename"-crop.png 
done

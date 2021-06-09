#!/bin/bash

src_res=50
dst_res=1000

for i in *_$src_res.asc
do
  gdal_translate -tr $dst_res $dst_res -r nearest -of AAIGrid $i `basename $i _$src_res.asc`_$dst_res.asc
done

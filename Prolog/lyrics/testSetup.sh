#!/bin/bash
for i 
do
    ls lyrics-${i}/ | shuf -n 20 | xargs -I {} -t cp lyrics-${i}/{} ./testAggregate/{}
done
./testSingle.sh testAggregate/
./testCorr.sh testAggregate/


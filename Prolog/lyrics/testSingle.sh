#!/bin/sh
FILES=${1}*
mkdir /tmp/test/
rm testSingle*.txt
for FILE1 in $FILES
do
    cp ${FILE1} /tmp/test/
    tar cvzf test.tar.gz /tmp/test/
    FILESIZETAR=$(stat -c%s "test.tar.gz")
    echo "single($FILE1,${FILESIZETAR})." >> testSingleTar.txt
    rm test.tar.gz
    lrztar -o ./test2.lrz -L 2 /tmp/test/
    FILESIZELR2=$(stat -c%s "test2.lrz")
    echo "single($FILE1,${FILESIZELR2})." >> testSingleLr2.txt
    rm test2.lrz
    lrztar -o ./test9.lrz -L 9 /tmp/test/
    FILESIZELR9=$(stat -c%s "test9.lrz")
    echo "single($FILE1,${FILESIZELR9})." >> testSingleLr9.txt
    rm test9.lrz
    lrztar -o ./testz.lrz -z /tmp/test/
    FILESIZEZP=$(stat -c%s "testz.lrz")
    echo "single($FILE1,${FILESIZEZP})." >> testSingleZpaq.txt
    rm testz.lrz
    rm /tmp/test/*
done
perl -i -p -e's/(.*\//(/g' testSingle*.txt
        

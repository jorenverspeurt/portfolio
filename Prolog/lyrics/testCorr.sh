#!/bin/sh
FILES=${1}*
mkdir /tmp/test/
rm testCorr*.txt
for FILE1 in $FILES
do
    for FILE2 in $FILES
    do
        cp ${FILE1} /tmp/test/
        cp ${FILE2} /tmp/test/
        tar cvzf test.tar.gz /tmp/test/
        FILESIZETAR=$(stat -c%s "test.tar.gz")
        echo "combination($FILE1,$FILE2,${FILESIZETAR})." >> testCorrTar.txt
        rm test.tar.gz
        lrztar -o ./test2.lrz -L 2 /tmp/test/
        FILESIZELR2=$(stat -c%s "test2.lrz")
        echo "combination($FILE1,$FILE2,${FILESIZELR2})." >> testCorrLr2.txt
        rm test2.lrz
        lrztar -o ./test9.lrz -L 9 /tmp/test/
        FILESIZELR9=$(stat -c%s "test9.lrz")
        echo "combination($FILE1,$FILE2,${FILESIZELR9})." >> testCorrLr9.txt
        rm test9.lrz
        lrztar -o ./testz.lrz -z /tmp/test/
        FILESIZEZP=$(stat -c%s "testz.lrz")
        echo "combination($FILE1,$FILE2,${FILESIZEZP})." >> testCorrZpaq.txt
        rm testz.lrz
        rm /tmp/test/*
    done
done


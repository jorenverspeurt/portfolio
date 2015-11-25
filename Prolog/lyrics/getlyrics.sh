#!/bin/bash
HS=""
US=""
for i
do
    HS=$HS"-"$i
    US=${US}$i
done
wget -r --no-parent -A "*-lyrics${HS}.html" www.lyrics.com/${US}
find www.lyrics.com/ -type f -exec grep -l "Submit Lyrics" {} \;| xargs rm
perl extractlyrics.pl www.lyrics.com/*.html
perl -i -p -e's/[\-]{3}.*//g' www.lyrics.com/*.html
rename "lyrics-" "" www.lyrics.com/*
rename .html .txt www.lyrics.com/*
mv www.lyrics.com/ lyrics${HS}

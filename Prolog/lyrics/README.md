# Compression Clustering with Prolog
For an assignment for the Capita Selecta of AI course I took in 2013-2014 I had to experiment (with a partner) with compression clustering. This is a clustering technique that uses normalized compression distance as metric.
I chose to try it on song lyrics. I wanted to see whether the clustering algorithm would be able to be used to recognize which band wrote a lyric, so whether it would cluster lyrics by the same artist together. The baseline requirement was that it would cluster lyrics in different languages as far apart as possible, so I picked 1 French-singing band and 2 English-singing bands as examples.
The code is written in Prolog and Bash scripts. I had only just learned Prolog and didn't have a lot of time to write this so the code is pretty rough... I was interested to see whether something like this was easy to write in Prolog and I found it reasonably intuitive. The fact that I could store the data from the compression distance calculation as Prolog factbases and just read them in with a single line was very handy.
I do think using Prolog had a significant impact on execution time and memory use, so if I had to write it again I probably wouldn't use Prolog.
I'd write up which file does what but I don't really remember too well...


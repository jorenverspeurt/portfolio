#!/usr/bin/perl

use strict;
use warnings;

use HTML::TreeBuilder::XPath;

for(@ARGV){
    my $root = HTML::TreeBuilder::XPath->new_from_file($_);
    my $id="lyric_space";
    my @divs=$root->findnodes(qq{//div[\@id="$id"]});
    open(OUTFILE,">$_");
    print OUTFILE $divs[0]->as_text;
}


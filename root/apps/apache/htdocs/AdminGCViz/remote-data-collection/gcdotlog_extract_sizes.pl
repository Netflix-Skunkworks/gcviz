#!/usr/bin/perl -w

# $Id: //depot/cloud/rpms/nflx-webadmin-gcviz/root/apps/apache/htdocs/AdminGCViz/remote-data-collection/gcdotlog_extract_sizes.pl#2 $
# $DateTime: 2013/05/15 18:34:23 $
# $Change: 1838706 $
# $Author: mooreb $

use strict;

my $num_args = $#ARGV + 1;

if($num_args != 1) {
    die "Usage: $0 output-dir";
}

my $outputdir = $ARGV[0];
my $fname = "${outputdir}/gcdotlog_extract_sizes_rejected_lines"; 
open(REJECTS, ">$fname") or die "cannot open $fname for writing";

print "datetimestamp,secs_since_jvm_boot,young_begin_k,young_end_k,young_total_k,whole_heap_begin_k,whole_heap_end_k,whole_heap_total_k\n";
while(<STDIN>) {
    my $line = $_;
    chomp($line);

    if(0) {
        # make all the lines elsif to make moving blocks easier
    }
    elsif($line =~ m/->.*->.*->/) {
        # reject lines with three arrows
        print REJECTS "$line\n";
    }
    elsif($line =~ m/^([0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}[.][0-9]{3}[+]0000): ([0-9]+[.][0-9]{3}): .* ([0-9]+)K->([0-9]+)K\(([0-9]+)K\).* ([0-9]+)K->([0-9]+)K\(([0-9]+)K\)/) {
        print "$1,$2,$3,$4,$5,$6,$7,$8\n";
    }
    else {
        print REJECTS "$line\n";
    }
}

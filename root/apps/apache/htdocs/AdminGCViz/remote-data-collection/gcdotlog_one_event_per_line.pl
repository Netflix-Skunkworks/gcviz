#!/usr/bin/perl -w

# $Id: //depot/cloud/rpms/nflx-webadmin-gcviz/root/apps/apache/htdocs/AdminGCViz/remote-data-collection/gcdotlog_one_event_per_line.pl#3 $
# $DateTime: 2013/11/05 12:09:10 $
# $Change: 2024106 $
# $Author: mooreb $

use strict;

sub flush_previous_record {
    my ($previous_record) = @_;
    if ("" ne "$previous_record") {
        print "$previous_record\n";
    }
}

my $previous_record = "";
while(<STDIN>) {
    my $line = $_;
    chomp($line);
    # -XX:+PrintGCDateStamps
    if($line =~ m/^[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}/) {
        # starting a new record
        flush_previous_record($previous_record);
        $previous_record = $line;
    }
    elsif($line =~ m/^[0-9]+[.][0-9]+: /) {
        # starting a new record
        flush_previous_record($previous_record);
        $previous_record = $line;
    }
    elsif($line =~ m/(^.*[0-9]+[.][0-9]+ secs])([0-9]+[.][0-9]+: .*$)/) {
        # two records are conflated 
        $previous_record = $previous_record . $1;
        flush_previous_record($previous_record);
        $previous_record = $2;
    }
    elsif($line =~ m/(^.*)([0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}.*)/) {
        # two records (with -XX:+PrintGCDateStamps) are conflated 
        $previous_record = $previous_record . $1;
        flush_previous_record($previous_record);
        $previous_record = $2;
    }
    else {
        # append to the previous record
        $previous_record = $previous_record . $line;
    }
}
flush_previous_record($previous_record);


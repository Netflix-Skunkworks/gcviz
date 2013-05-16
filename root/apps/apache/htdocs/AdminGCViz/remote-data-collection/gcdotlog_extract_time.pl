#!/usr/bin/perl -w

# $Id: //depot/cloud/rpms/nflx-webadmin-gcviz/root/apps/apache/htdocs/AdminGCViz/remote-data-collection/gcdotlog_extract_time.pl#2 $
# $DateTime: 2013/05/15 18:34:23 $
# $Change: 1838706 $
# $Author: mooreb $

use strict;

sub classify_gc_event_type {
    my ($line) = @_;

    if(0) {
        # make all the lines "elsif" so that they are interchangable
    }
    elsif($line =~ m/Full GC/) {
        return "FullGC";
    }
    elsif($line =~ m/\(concurrent mode failure\)/) {
        return "concurrent-mode-failure";
    }
    elsif($line =~ m/\(promotion failed\)/) {
        return "promotion-failed";
    }
    elsif($line =~ m/ParNew/) {
        return "ParNew";
    }
    elsif($line =~ m/CMS-initial-mark/) {
        return "CMS-initial-mark";
    }
    elsif($line =~ m/CMS-concurrent-mark/) {
        return "CMS-concurrent-mark";
    }
    elsif($line =~ m/CMS-concurrent-abortable-preclean/) {
        return "CMS-concurrent-abortable-preclean";
    }
    elsif($line =~ m/CMS-concurrent-preclean/) {
        return "CMS-concurrent-preclean";
    }
    elsif($line =~ m/CMS-remark/) {
        return "CMS-remark";
    }
    elsif($line =~ m/CMS-concurrent-sweep/) {
        return "CMS-concurrent-sweep";
    }
    elsif($line =~ m/CMS-concurrent-reset/) {
        return "CMS-concurrent-reset";
    }
    elsif($line =~ /PSYoungGen/) {
        return "ParallelScavengeYoungGen";
    }
    elsif($line =~ /DefNew/) {
        return "DefNew";
    }
    else {
        return "unknown";
    }
}

sub mayne {
    my $num_args = $#ARGV + 1;

    if($num_args != 1) {
        die "Usage: $0 output-dir";
    }

    my $outputdir = $ARGV[0];
    my $fname = "${outputdir}/gcdotlog_extract_time_rejected_lines"; 
    open(FP, ">$fname") or die "cannot open $fname";

    print "datetimestamp,secs_since_jvm_boot,gc_event_type,gc_event_duration_in_seconds\n";
    while(<STDIN>) {
        my $line = $_;
        chomp($line);
        # -XX:+PrintGCDateStamps
        if($line =~ m/^([0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}[.][0-9]{3}[+]0000): ([0-9]+[.][0-9]+): .*real=([0-9][0-9]*[.][0-9][0-9]*) secs\]\s*$/) {
            my $datestamp = $1;
            my $secs_since_jvm_boot = $2;
            my $gctime_in_seconds = $3;
            my $gc_event_type = classify_gc_event_type($line);
            print "${datestamp},${secs_since_jvm_boot},${gc_event_type},${gctime_in_seconds}\n";
        }
        else {
            print FP "$line\n";
        }
    }
    close(FP);
}

mayne()

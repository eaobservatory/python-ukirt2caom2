#!/usr/bin/env perl

use lib '../omp-perl';

use DateTime;
use OMP::DateTools;

use strict;

local $\ = "\n";
my $year_plus_day = DateTime::Duration->new(
    years => 1, hours => 23, minutes => 59, seconds => 59);

while (<>) {
    chomp;

    # Code modified from JSA::EnterData.

    my $semester = OMP::DateTools->determine_semester(
        date => $_, tel => 'UKIRT');
    my ($sem_begin, $sem_end) = OMP::DateTools->semester_boundary(
        semester => $semester, tel => 'UKIRT');

    my $release_date = DateTime->from_epoch(
        epoch => $sem_end->epoch, time_zone => 'UTC') + $year_plus_day;

    print $release_date->strftime('%Y%m%d %H:%M:%S');
    flush STDOUT;
}

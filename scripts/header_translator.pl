#!/usr/bin/env perl

use JSON;

use Astro::FITS::HdrTrans qw/translate_from_FITS/;

use strict;

my $json = new JSON();
$json->allow_blessed(1);

my $buff = '';

while (<>) {
    unless (/^###/) {
        $buff .= $_;
        next;
    }

    my $translated = eval {
        my $header = $json->decode($buff);
        my %translated = translate_from_FITS($header);
        \%translated;
    };

    unless (defined $translated) {
        $translated = {__ERROR__ => $@};
    }

    print $json->encode($translated);
    print "\n###\n";
    flush STDOUT;

    $buff = '';
}

#!/usr/bin/env tcsh

source sourceme.csh

set OPTS='-v --out xml -r'

foreach INST (cgs3 cgs4 ircam michelle ufti uist)
    scripts/ukirt2caom2 $OPTS -i $INST -c control/${INST}.txt >&! log/${INST}.txt &
end

wait

#!/usr/bin/env tcsh

source sourceme.csh

set OPTS='-v -r'
set LOGDIR='log'

foreach INST (cgs3 cgs4 ircam michelle ufti uist)
    scripts/ukirt2caom2 $OPTS -i $INST -c control/${INST}.txt >&! ${LOGDIR}/${INST}.txt &
end

wait

#!/usr/bin/env sh

#
### get curent information for stdinput nation on corona virus stats
#


# check if $1 is empty string, if it is, set location to germany -> TODO: curent location
[[ -z $1 ]] && nation='Germany' || nation=$1

# get current date and time for file timestamp
ddt=$(date -d now +%d-%m-%y_%H-%M)

# get stats and grep stdinput nation and header line and convert it to csv (and sed magic)
curl -v --silent https://corona-stats.online\?source\=2 2> /dev/null | grep -- "Rank\|$nation\|Update" | sed $'s/[^[:print:]\t]//g; s/\[[0-9].m//g; s/│/;/g; s/▲//g; s/║//g ' | sed 's/\[//g' > corona_$nation_$ddt.csv


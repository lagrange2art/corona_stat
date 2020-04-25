#!/usr/bin/env sh

######################################################################
# @author      : pdaynoe@github.com/lagrange2art/corona_stat
# @file        : corona-stats2CSV.sh
# @created     : Saturday Apr 25, 2020
#
# @description : Get curent information for a nation on corona virus stats from stdinput
#                multiple inputs possible, example: "Germany\|France\|USA" (" needed as input)
######################################################################


#### check if $1 is empty string, if it is, set location to current location
[[ -z $1 ]] && nation=$(curl -v --silent  ifconfig.co/country 2> /dev/null) || nation=$1


#### get current date and time for file timestamp
## short timestamp: 12-31-20
timestamp=$(date -d today +%m-%d-%y)

## full timestamp: 31-12-1999_23-58
# timestamp=$(date -d today +%d-%m-%Y_%H-%M)


#### get stats and sed-magic of nations and convert it to csv
echo -e  "### Current corona stats for:  $(echo $nation | sed -E 's/\\\|/, /g')" > corona\_$timestamp.csv
echo -e  "### Fetched from corona-stats.online. See: https://corona-stats.online" >> corona\_$timestamp.csv
echo -e  "### Last updated on:  $(curl -v --silent https://corona-stats.online\?source\=2 2> /dev/null | grep -- "Update" | sed $'s/[^[:print:]\t]//g' | cut -c 26-) \n" >> corona\_$timestamp.csv
curl -v --silent https://corona-stats.online\?source\=2 2> /dev/null | grep -- "Rank\|$nation" | sed $'s/[^[:print:]\t]//g; s/\[[0-9].m//g; s/│/;/g; s/▲//g; s/║//g ' | sed 's/\[//g' >> corona\_$timestamp.csv


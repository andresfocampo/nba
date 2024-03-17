#!/bin/bash

if [ $# -eq 0 ];
then
  echo "$0: Missing vf_dev name"
  exit 1
else
    vf_dev=$1;
    dp=$(sudo tc -g -s qdisc ls dev $vf_dev | sed -e '1,4d' | head -n -1 | sed -e 's/.*dropped \(.*\), overlimits.*/\1/');
    sp=$(sudo tc -g -s qdisc ls dev $vf_dev | sed -e '1,4d' | head -n -1 | sed -e 's/.*bytes \(.*\) pkt.*/\1/');
    bl=$(sudo tc -g -s qdisc ls dev $vf_dev | sed -e '1,5d' -e 's/.*b \(.*\)p .*/\1/');
fi
echo $dp $sp $bl

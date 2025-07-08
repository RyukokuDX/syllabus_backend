#!/bin/bash
# JSONを整形して出力
if [ $# -eq 0 ]; then
    jq .
else
    jq . "$1"
fi 
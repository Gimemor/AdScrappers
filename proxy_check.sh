#!/bin/bash
cat ips-zone-processed.txt | while read line; do
response=`curl -L http://avito.ru/robots.txt -x $line  --write-out %{http_code} --silent --output /dev/null`
if [ $response <> 502 ]
then
	echo  $line;
fi;
done

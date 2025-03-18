#! /bin/sh

reportDate="2024-01-05 14:54:32 +0100"
# init database
echo "Initializing database"
cd neo4j-mdr-db && pipenv run init_neo4j
# import neodash reports
mkdir -p neodash_reports/import && FILES="neodash/neodash_reports/*.json"

for f in $FILES
do
    echo "Processing $f file..."
    filename=`basename $f`
    content=`cat $f`
    title=`jq -r .title $f`
    uuid=`jq -r .uuid $f`
    version=`jq -r .version $f`
    echo "$title" "$uuid" "$version"
    jq -n --slurpfile content $f --arg title "$title" --arg uuid "$uuid" --arg version "$version" --arg date "$reportDate" '. += {"content": $content, "title": $title, "uuid": $uuid, "version": $version, "date": $date, "user": "OpenStudyBuilder@gmail.com"}' > neodash_reports/import/$filename
done 

python -m pipenv run import_reports neodash_reports/import 
# imports
echo "Importing data"
cd ../mdr-standards-import && pipenv run bulk_import "IMPORT" "packages" 
# update CT package stats
echo "Updating CT package stats"
cd ../neo4j-mdr-db && pipenv run update_ct_stats 
# start API
cd ../clinical-mdr-api
echo "Starting API"
pipenv run uvicorn --host 127.0.0.1 --port 8000 --log-level info clinical_mdr_api.main:app
# wait until 8000/tcp is open
while ! netstat -tna | grep 'LISTEN>' | grep -q '8000>'
do 
    sleep 2
done 
# && set -x 
# imports
sleep 10 && cd ../studybuilder-import
echo "Importing data"
pipenv run import_all
# pipenv run import_dummydata
pipenv run import_feature_flags
pipenv run activities 
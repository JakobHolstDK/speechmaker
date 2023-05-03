curl -X POST   https://speechmakerapi.openknowit.com/events   -H 'Content-Type: application/json'   -d '{
"token": "demo",
"name": "The wedding of Mary and George",
"situation": "We are at a weeding, Mary 27 years and George 28 Years, They are are from New York, have known each other since higscool. Mary has a twin brother and her father and mother are from Ireland, and lives en New Jersey. George has divorsed parent. His fater lives in Paris France and his mother lives in Brooklyn. The couple have a daughter , June 1 year old. We are at a wedding in Dublin Ireland"
}'

curl   https://speechmakerapi.openknowit.com/events 
clear
while [[ 1 == 1 ]];
do
  curl -X PUT https://speechmakerapi.openknowit.com/randomstatement/demo
  curl   https://speechmakerapi.openknowit.com/events 
  curl   https://speechmakerapi.openknowit.com/statements
  curl   https://speechmakerapi.openknowit.com/speeches
  sleep 60
done






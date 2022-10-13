docker build -f dockerfile -t moneylogger_app .
docker-compose -f docker-compose.yml up --remove-orphans -d
sleep 10
docker exec -i moneylogger_app python -m flask db migrate
docker exec -i moneylogger_app python -m flask db upgrade
docker cp moneylogger_app:/srv/application/migrations/ .\application\
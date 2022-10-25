docker build -f dockerfile-back -t moneylogger_back .
docker build -f dockerfile-front -t moneylogger_front .
docker-compose -f docker-compose.yml up --remove-orphans -d
sleep 10
docker exec -i moneylogger_back python -m flask db migrate
docker exec -i moneylogger_back python -m flask db upgrade
docker cp moneylogger_back:/srv/application/migrations/ .\application\
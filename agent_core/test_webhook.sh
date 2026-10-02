echo -n "brute_force "
curl -s -o /dev/null -w "%{http_code}" \
  -X POST -H "Content-Type: application/json" \
  -d '{"rule":"brute_force"}' http://127.0.0.1:5001/webhook
echo
echo -n "password_spraying "
curl -s -o /dev/null -w "%{http_code}" \
  -X POST -H "Content-Type: application/json" \
  -d '{"rule":"password_spraying"}' http://127.0.0.1:5001/webhook
echo
echo -n "night_login "
curl -s -o /dev/null -w "%{http_code}" \
  -X POST -H "Content-Type: application/json" \
  -d '{"rule":"night_login"}' http://127.0.0.1:5001/webhook
echo

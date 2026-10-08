curl -s -X POST -H "Content-Type: application/json" \
  -d '{"rule":"brute_force"}' http://127.0.0.1:5001/webhook
echo
curl -s -X POST -H "Content-Type: application/json" \
  -d '{"rule":"night_login"}' http://127.0.0.1:5001/webhook
echo

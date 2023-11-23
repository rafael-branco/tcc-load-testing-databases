# tcc-load-testing-databases

AppServer: http://[IP_ADDRESS]:5000

Command for starting AppServer:
gunicorn -w 12 -b 0.0.0.0:5000 app:app

Command for Locust Load Testing:
locust -f .\load.py

web: gunicorn joog_ecommerce.wsgi:application --log-file - --workers 3
worker: celery -A joog_ecommerce worker --loglevel=info
beat: celery -A joog_ecommerce beat --loglevel=info
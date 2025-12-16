include .env
export

worker:
	find . -type f -name "*.py" | entr -r celery -A django_shop worker -l INFO

server:
	python manage.py runserver

flower:
	celery -A django_shop flower

stripe-cli:
	stripe listen --forward-to localhost:8000/payment/webhook/ --api-key ${STRIPE_CLI_API_KEY}

redis-ui:
	open /Applications/Another\ Redis\ Desktop\ Manager.app

compose-up:
	docker compose -f .docker/compose.yml --env-file .env up -d

compose-down:
	docker compose -f .docker/compose.yml down

compile-i18n:
	find . -type f -name "django.po" | entr -r python manage.py compilemessages
	
makemessages:
	python manage.py makemessages --all

django-shell:
	python manage.py shell -i ipython
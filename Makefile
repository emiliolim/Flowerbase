build:
	docker build --force-rm $(options) -t flowershop-website:latest .

build-prod:
	$(MAKE) build options="--target production"

compose-start: # begin website
	docker-compose up --remove-orphans $(options)

compose-stop: # stop container processes
	docker-compose down --remove-orphans $(options)

compose-manage-py: # make compose-manage-py cmd="makemigrations"
	docker-compose run --rm $(options) website python manage.py $(cmd)
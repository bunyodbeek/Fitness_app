mig:
	python3 manage.py makemigrations
	python3 manage.py migrate

user:
	python3 manage.py createsuperuser

loaddata:
	python3 manage.py loaddata program edition exercises

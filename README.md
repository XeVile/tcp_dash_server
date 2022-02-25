# tcp_dash_server
Multithreaded server class with a Dashboard to access DB of server-client comms.

Django part extended from -> [This repo as per collab](https://github.com/Sadnan-Sakib1407/Blog_App_Django)

### Requirements:
>	* Python 3.9
>	* Django 4.0.2

### To run:
Run the Django test server using:

	python3 manage.py runserver

Run IoT/Device server core.py using:

	python3 core.py

Finally to connect to the server:

	python3 client.py


### Issues:
* The Django Dashboard view updates only after a restart
	> Probably something to do with the database (protected.db) being statically linked rather than dynamically
* The Client communication archive is inaccessible -> Feature not implemented yet

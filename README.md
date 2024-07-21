# Forescout MAR Manager

This app maintains a list of MAR Entries to sync to Forescout (via API calls in an associated Connect App) and adds RBAC controls around the MAR entries and Smartcard authentication.

## Tech Used

- [Python](https://python.org) for codebase
- [Django](https://www.djangoproject.com/) for database, ORM, admin interface
- [Django Ninja](https://django-ninja.dev/) for API
- [Ninja JWT](https://eadwincode.github.io/django-ninja-jwt/) library to create JWTs for API authentication/authorization
- [PostgreSQL](https://www.postgresql.org/) for Database
- [Docker](https://www.docker.com/) for packaging everything up and running

## Setup

### Environment
Read `.env.example` to determine available Environment variables that can/should be set

### Manually running without Docker

Install dependencies:
`pip install -r requirements.txt`

Setup .env

Make sure PostgreSQL is running

Run server:
`python manage.py runserver`

### Random Information

- The data model used in this app allows for the same MAC address to be entered into the system multiple times over, but this is incompatible with adding a MAC address to the MAR in Forescout. Therefore, API responses will only include a single MAC address if there are duplicates -- the most recent (not exceeding `now()`) `effective_date` then the soonest `expire_date`. This is expressed by the following ORM statement: `Mac.objects.filter(Q(Q(expire_date__gte=now) | Q(expire_date__isnull=True))).filter(effective_date__lte=now).order_by('mac', '-effective_date', 'expire_date', 'mac').distinct('mac')`

  - IMPORTANT NOTE: This behavior places an explicit dependency on PostgresSQL as the DB. The Combo of `.order_by` and `.distinct` in the SQL allows for this behavior wihtout wasted compute.

### Create MAR Managers

- Login as a Super Admin, go to 'AUTHENTICATION AND AUTHORIZATION' > 'Users' > 'ADD USER'.
- Entering the username and password and select "Save and continue editing".
- Enable 'Staff status' and add them to the "MAR Manager ..." Group.
- *NOTE: The MAR Manager group has full CRUD to the MAC Address Repository > MAC table however Row Level Security by MAC Address Group is implemented and will prevent the user from having full access to the table. We will create this access in the next steps.
- Go to 'MAC ADDRESS REPOSITORY' > 'MAC Address Groups: User & Permissions Assignment' > 'ADD MAC ADDRESS GROUP: USER & PERMISSIONS ASSIGNMENT'
- Here you can select the user (created earlier), which MAC Address Group to give them access to and what level of access (Create, Read, Update, Delete)

### API

- API docs are at http://[localhost|host]/api/docs
- API Docs require an active Django Admin Session (unless in DEBUG mode)
- API queries require a JWT token which uses the username & password of a Django User to convert to a JWT 
- For the Forescout Connect App user, it is recommended that the Forescout Django user is Super Admin

# Forescout MAR Manager

This app maintains a list of MAR Entries to sync to Forescout (via API calls in an associated Connect App) and adds RBAC controls around the MAR entries and Smartcard authentication.

## GitHub Codespaces ♥️ Django

Welcome to your shiny new Codespace running Django! We've got everything fired up and running for you to explore Django.

You've got a blank canvas to work on from a git perspective as well. There's a single initial commit with what you're seeing right now - where you go from here is up to you!

Everything you do here is contained within this one codespace. There is no repository on GitHub yet. If and when you’re ready you can click "Publish Branch" and we’ll create your repository and push up your project. If you were just exploring then and have no further need for this code then you can simply delete your codespace and it's gone forever.

## Tech Used

- [Django](https://www.djangoproject.com/) for database, ORM, admin interface
- [Django Ninja](https://django-ninja.dev/) for API
- [Ninja JWT](https://eadwincode.github.io/django-ninja-jwt/) library to create JWTs for API authentication/authorization
- Postgresql for Database
- Docker for packaging everything up

## Setup

### Random FYSAs

- The data model allows for the same MAC address to be entered into the system multiple times over. Forescout doesn't like duplicate MACs. Therefore, API responses will only include a single MAC address if there are duplicates -- the most recent (not exceeding `now()`) `effective_date` then the soonest `expire_date`. This is expressed by the following ORM statement: `Mac.objects.filter(Q(Q(expire_date__gte=now) | Q(expire_date__isnull=True))).filter(effective_date__lte=now).order_by('mac', '-effective_date', 'expire_date', 'mac').distinct('mac')`

  - IMPORTANT NOTE: This behavior places an explicit dependency on PostgresSQL as the DB. The Combo of `.order_by` and `.distinct` in the SQL allows for this behavior wihtout wasted compute.

### Create MAR Managers

- Login as a Super Admin, go to 'AUTHENTICATION AND AUTHORIZATION' > 'Users' > 'ADD USER'.
- Entering the username and password and select "Save and continue editing".
- Enable 'Staff status' and add them to the "MAR Manager ..." Group.
- *NOTE: The MAR Manager group has full CRUD to the MAC Address Repository > MAC table however Row Level Security by MAC Address Group is implemented and will prevent the user from having full access to the table. We will create this access in the next steps.
- Go to 'MAC ADDRESS REPOSITORY' > 'MAC Address Groups: User & Permissions Assignment' > 'ADD MAC ADDRESS GROUP: USER & PERMISSIONS ASSIGNMENT'
- Here you can select the user (created earlier), which MAC Address Group to give them access to and what level of access (Create, Read, Update, Delete)

### API

- API docs are at http://HOST/api/docs
- API Docs require an active Django Admin Session
- API queries require a JWT token which uses the username & password of a Django User to convert to a JWT
- For the Forescout Connect App user, it is recommended that the Forescout Django user is Super Admin

## Handy Commands

### To collect static files

```python
python manage.py collectstatic
```

### To run this application

```python
python manage.py runserver
```

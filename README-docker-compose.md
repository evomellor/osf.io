
## Docker and OS Setup

1. Install the Docker Client
  - OSX: https://www.docker.com/products/docker#/mac
  - Windows: https://www.docker.com/products/docker#/windows
2. Grant the docker client additional memory and cpu (minimum of 4GB and 2 CPU)
   - OSX: https://docs.docker.com/docker-for-mac/#/preferences
   - Windows: https://docs.docker.com/docker-for-windows/#advanced
3. Setup the Operating System
  - OSX
    - Alias the loopback interface

      `$ sudo cp com.runlevel1.lo0.192.168.168.167.plist /Library/LaunchDaemons`

      `$ sudo chmod 0644 /Library/LaunchDaemons/com.runlevel1.lo0.192.168.168.167.plist`

      `$ sudo chown root:wheel /Library/LaunchDaemons/com.runlevel1.lo0.192.168.168.167.plist`

      `$ sudo launchctl load /Library/LaunchDaemons/com.runlevel1.lo0.192.168.168.167.plist`

  - Windows
    - Install Microsoft Loopback Adapter (Windows 10 follow community comments as the driver was renamed)
      https://technet.microsoft.com/en-us/library/cc708322(v=ws.10).aspx
    - Rename the new Loopback Interface (typically called 'Ethernet 2')
      - List interfaces

        `netsh interface show interface`
      - Rename the interface

        `netsh inteface set interface "Ethernet 2" newname="Loopback"`
      - Assign the Loopback interface an IP address

        `netsh interface ip add address "Loopback" 192.168.168.167 255.255.255.255`
      - Allow Docker to access to Drive your project is stored on

        Open the Docker Client -> Settings -> Shared Drives -> e.g. C -> Apply



## Application Configuration
_NOTE: After making changes to `Environment Variables` or `Volume Mounts` (e.g. docker-sync) you will need to recreate the container(s)._

  - `$ docker-compose up --force-recreate --no-deps preprints`

1. Application Settings
 - e.g. OSF & OSF API local.py

    `$ cp ./website/settings/local-dist.py ./website/settings/local.py`

    `$ cp ./api/base/settings/local-dist.py ./api/base/settings/local.py`

2. OPTIONAL (uncomment the below lines if you will use remote debugging) Environment variables (incl. remote debugging)
  - e.g. .docker-compose.env

    ```bash
    WEB_REMOTE_DEBUG=192.168.168.167:11000
    API_REMOTE_DEBUG=192.168.168.167:12000
    WORKER_REMOTE_DEBUG=192.168.168.167:13000
    ```

      _NOTE: Similar docker-compose.\<name\>.env environment configuration files exist for services._

3. OPTIONAL (skip if you do not need to modify services, e.g. mfr and waterbutler): Mounting Service Code
  - By modifying docker-compose.override.yml and docker-sync.yml you can specify the relative path to your service code directories. e.g.
    - This makes it so your local changes will be reflected in the docker containers. Until you do this none of your changes will have any effect.

  - In `docker-compose.override.yml`:

    ```yml
    services:
      wb:
        volumes_from:
          - container:wb-sync
    ```

  - In `docker-sync.yml`:

    ```yml
    syncs:
      wb-sync:
        src: '../waterbutler'
        dest: '/code'
        sync_strategy: 'unison'
        sync_excludes_type: 'Name'
        sync_excludes: ['.DS_Store', '*.pyc', '*.tmp', '.git', '.idea']
        watch_excludes: ['.*\.DS_Store', '.*\.pyc', '.*\.tmp', '.*/\.git', '.*/\.idea']
    ```

## Docker Sync

1. Install Docker Sync
  - [Instructions](http://docker-sync.io)

2. If you have problems trying installing macfsevents
  - `$ sudo pip install macfsevents`

3. Running Docker Sync

    _NOTE: Wait for Docker Sync to fully start before running any docker-compose commands._
  - `$ docker-sync start`


## Application Runtime
1. Application Environment

  - `$ docker-compose up requirements mfr_requirements wb_requirements`

    _NOTE: When the various requirements installations are complete these containers will exit. You should only need to run these containers after pulling code that changes python requirements or if you update the python requirements._

2. Start Core Component Services
  - `$ docker-compose up elasticsearch postgres tokumx rabbitmq`

3. Remove your existing node_modules and start the assets watcher
  - `$ rm -Rf ./node_modules`
  - `$ docker-compose up assets`

    _NOTE: The first time the assets container is run it will take Webpack/NPM up to 15 minutes to compile resources.
    When you see the BowerJS build occurring it is likely a safe time to move forward with starting the remaining
    containers._
4. Start the Services
  - `$ docker-compose up mfr wb fakecas sharejs`
5. Run migrations and create preprint providers
  - When starting with an empty database you will need to run migrations and populate preprint providers. See the [Running arbitrary commands](#running-arbitrary-commands) section below for instructions.
6. Run Django migrations
  - `$ docker-compose run --rm web python manage.py migrate`
7. Start the OSF Web, API Server, and Preprints
  - `$ docker-compose up worker web api preprints`
8. View the OSF at [http://localhost:5000](http://localhost:5000).


## Quickstart: Running all OSF services in the background

- Once the requirements have all been installed, you can start the OSF in the background with

  ```
  $ docker-sync start
  # Wait until you see "Nothing to do: replicas have not changed since last sync."
  $ docker-compose up -d assets elasticsearch postgres tokumx mfr wb fakecas sharejs worker web api preprints
  ```

- To view the logs for a given container: 

  ```
  $ docker-compose logs -f -t 100 web
  ```

## Running arbitrary commands

- View logs: `$ docker-compose -f --tail 100 <container_name>`
    - _NOTE: CTRL-c will exit_
- Run migrations:
  - After creating migrations, resetting your database, or starting on a fresh install you will need to run migrations to make the needed changes to database. This command looks at the migrations on disk and compares them to the list of migrations in the `django_migrations` database table and runs any migrations that have not been run.
    - `docker-compose run --rm web python manage.py migrate`
- Populate preprint providers:
  - After resetting your database or with a new install you will need to populate the table of preprint providers. **You must have run migrations first.**
    - `docker-compose run --rm web python -m scripts.update_taxonomies`
    - `docker-compose run --rm web python -m scripts.populate_preprint_providers`
- Create migrations:
  - After changing a model you will need to create migrations and apply them. Migrations are python code that changes either the structure or the data of a database. This will compare the django models on disk to the database, find the differences, and create migration code to change the database. If there are no changes this command is a noop.
    - `docker-compose run --rm web python manage.py makemigrations`
- Destroy and recreate an empty database:
  - **WARNING**: This will delete all data in your database.
    - `docker-compose run --rm web python manage.py reset_db --noinput`

## Application Debugging
- Console Debugging with IPDB
  - `docker attach [projectname]_web_1`

    _NOTE: You can detach from a container and leave it running using the CTRL-p CTRL-q key sequence._
- Remote Debugging with PyCharm
  - Add a Python Remote Debugger per container
    - Name: `Remote Debug (web)`
    - Local host name: `192.168.168.167`
    - Port: `11000`
    - Path mappings:
      - `~/Projects/cos/osf : /code`
      - `~/.virtualenvs/osf/lib/python2.7/site-packages : /usr/local/lib/python2.7/site-packages`
    - `Single Instance only`
  - Configure `.docker-compose.env` `<APP>_REMOTE_DEBUG` environment variables to match these settings.

## Managing Container State

Restart a container:
  - `$ docker-compose restart -t 0 assets`

Recreate a container _(useful to ensure all environment variables/volume changes are in order)_:
  - `$ docker-compose up --force-recreate --no-deps assets`

Delete a container _(does not remove volumes)_:
  - `$ docker-compose stop -t 0 assets`
  - `$ docker-compose rm assets`

## Cleanup & Docker Reset

Resetting the Environment:

  **WARNING: All volumes and containers are destroyed**
  - `$ docker-compose down -v`

Delete a persistent storage volume:

  **WARNING: All postgres data will be destroyed.**
  - `$ docker-compose stop -t 0 postgres`
  - `$ docker-compose rm postgres`
  - `$ docker volume rm osf_postgres_data_vol`

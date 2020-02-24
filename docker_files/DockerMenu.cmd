@ECHO OFF

:startscript

CLS

:: Load in config properties
For /F "tokens=1,2 delims==" %%G IN (DockerScriptConfig.properties) DO (set %%G=%%H)

ECHO Morpheus Docker Menu
ECHO.
ECHO Enter a choice from the list below:
ECHO. 
:: Remove the line below to get rid of the option of installing docker
ECHO [1] Install Docker For Windows
ECHO [2] Build and Run Docker Containers
ECHO [3] Stop Running Containers
ECHO [4] Start Previously Stopped Containers
ECHO [5] Restart App Container
ECHO [6] Stop and Remove Containers from Hard Drive
ECHO [7] Dump Postgres DB
ECHO.

SET choice='0'
SET /p choice=Enter the number for your choice. 
:: Remove the line below to get rid of the option of installing docker
IF '%choice%'=='1' GOTO installdocker
IF '%choice%'=='2' CALL :checkfordocker buildruncontainers
IF '%choice%'=='3' CALL :checkfordocker stopcontainers
IF '%choice%'=='4' CALL :checkfordocker startcontainers
IF '%choice%'=='5' CALL :checkfordocker restartserver
IF '%choice%'=='6' CALL :checkfordocker stopremovecontainers
IF '%choice%'=='7' CALL :checkfordocker dumpdatabase
IF '%choice%'=='0' GOTO startscript

GOTO end

:: Install Docker
:installdocker

:: This script downloads the Docker install, installs it, and then starts it.

ECHO Downloading the Docker install file...

:: Download the install file for docker
powershell -c "Start-BitsTransfer -Source https://download.docker.com/win/stable/Docker%%20Desktop%%20Installer.exe -Destination ./DockerInstaller.exe"

ECHO Installing Docker. An install window will open to begin the process. Follow the prompts to the end then click the button that says close.

:: Start the install exe
START /WAIT DockerInstaller.exe

ECHO Starting Docker.

:: Ensure docker for desktop has started
START "" "C:\Program Files\Docker\Docker\Docker Desktop.exe"

ECHO Done!

DEL DockerInstaller.exe

PAUSE

GOTO startscript

:: Build Containers
:buildruncontainers

ECHO Docker is running. Building the docker container and starting up the server...

docker-compose -f Docker-Compose.yml up -d --build

ECHO Containers have started and the App can be found at http://127.0.0.1:%exposedPort%

PAUSE

GOTO end

:: Stop running containers
:stopcontainers

ECHO Stopping the docker containers...

docker-compose -f Docker-Compose.yml stop

ECHO Done!

PAUSE

GOTO end

:: Start previously stopped containers
:startcontainers

ECHO Docker is running. Starting the docker containers...

docker-compose -f Docker-Compose.yml up -d

ECHO Containers have started and the App can be found at http://127.0.0.1:%exposedPort%

PAUSE

GOTO end

:: Restart server container
:restartserver

ECHO Docker is running. Restarting the server container...

docker stop %appContainerName%
docker start %appContainerName%

ECHO App has been restarted...

PAUSE

GOTO end

:: Stop and remove containers
:stopremovecontainers

ECHO Stopping the docker containers...

docker-compose -f Docker-Compose.yml down --rmi all -v
docker system prune -a -f
docker system prune --volumes -f

ECHO Done!

PAUSE

GOTO end

:: Create a new dump.pgdata file
:dumpdatabase

ECHO Dumping the database into dump.pgdata...

docker exec %databaseContainerName% pg_dump -U %databaseUser% --format custom %database% > ../database/dump.pgdata

ECHO Done!

PAUSE

GOTO end

:: Restore MongoDB
:restoremongodb

ECHO Restoring MongoDB...

docker cp dump.gz %databaseContainerName%:/dump/dump.gz
docker exec -t %databaseContainerName% mongorestore --username %databaseUser% --password %databasePassword% --authenticationDatabase admin --archive=/dump/dump.gz --gzip --db %database%

ECHO Done!

PAUSE

GOTO end

:: Ensures docker is running
:checkfordocker
ECHO  Checking to see if Docker is running...

:: Find the service name
SETLOCAL EnableExtensions
set EXE=Docker.Watchguard.exe
FOR /F %%x IN ('tasklist /NH /FI "IMAGENAME eq %EXE%"') DO IF %%x == %EXE% GOTO %~1

:: Docker is not running so start the service
:dockernotrunning

ECHO Docker is not running. Starting Docker now...

START "" "C:\Program Files\Docker\Docker\Docker Desktop.exe"

ECHO Docker is starting. Wait for the 'Docker Desktop is running' prompt to appear on the taskbar then continue...

PAUSE

GOTO %~1

:: Wait for user to exit
:end
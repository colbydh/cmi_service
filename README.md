# CMFI Service README

## Setup

### Clone Project

1. Navigate to a folder where the files will be stored.
2. In the terminal type: "git clone git@github.boozallencsn.com:cmfi/cmi_service.git"
    * Note: You should have already setup github with your SSH key.

### Setup Coding Environment

1. Setup Anaconda
    * Follow directions here to setup Anaconda: https://docs.anaconda.com/anaconda/install/
    * Open an Anaconda terminal and create/activate a new environment.
        * Type: "conda create -n django python=3.7 pip"
        * Select "y" to create the new environment.
        * Type: "conda activate django" to activate the environment.
2. Install requirements
    * Navigate to the folder with "requirements.txt"
    * In the anaconda terminal type: "pip install -r requirements.txt" this should install all the packages.
3. Install the npm packages for frontend development, mainly used for SCSS compiling.
    * In the anaconda terminal type: "npm install -g sass"
    
### Setup PyCharm

1. Install PyCharm by following the guide here: https://www.jetbrains.com/help/pycharm/installation-guide.html
2. In the main folder where this README is located right-click and select "Open folder as PyCharm Project" if on windows.
3. Setup the interpreter, this will allow the code to run inside the anaconda environment created above.
    * In the bottom right-hand corner click on "<No interpreter>" and select "Add Interpreter".
    * On the next screen, click on "Conda Environment" from the left-hand side.
    * Select the "Existing environment" radio button.
    * If the django environment is not in the "Interpreter" input box then click on the folder icon to the right to navigate to the correct file.
        * In the pop up toggle the eye toggle to show hidden folders.
        * Next navigate to the conda environment folder for the django environment created earlier. This is usually located at "C:\User\<employee number>\AppData\Local\Continuum\anaconda3\envs\django\python3.exe"
    * Click "OK".
4. Setup SCSS file watchers to auto compile into CSS on changes.
    * Press "CTL-ALT-S" to bring up the settings menu.
    * Under "Tools-File Watchers" Click the "+" button.
    * Select the "SCSS" template
    * On the window that pops up enter the values below:
        * Arguments: --update $FileName$:$ProjectFileDir$/CMFI_Service/static/css/$FileNameWithoutExtension$.css
        * Output paths to refresh: $ProjectFileDir$/CMFI_Service/static/css/$FileNameWithoutExtension$.css
    * Click "OK".  
    
### Starting the App

1. On a fresh database and clone of the project you first need to migrate the database and collect the static files. This is for development only, a Dockerfile will do all this for production.
    * In the main folder in a terminal type: "python manage.py makemigrations" then "python manage.py migrate"
    * In the terminal in the main folder type: "python manage.py collectstatic"
2. Start the app by clicking the debug symbol in the top right of PyCharm. Then navigate http://127.0.0.1:8000
    * Because it is in dev mode you can make changes to the code and html and see live updates.
# CMI Service README

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
    
### Starting the App

1. run "python manage.py runserver".
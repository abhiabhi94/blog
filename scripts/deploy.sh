# This script is used to pull in the latest changes and update the server in production.

# exit if any command fails
set -e

# this function redirects and prints error when an error is encountered
exit_on_error(){
        exit_code=$1
        last_command=$2
        if [ $exit_code -ne 0 ]; then
                >&2 echo "\"${last_command}\" command failed with exit code ${exit_code}."
                exit $exit_code
        fi
}

trap 'exit_on_error $? $BASH_COMMAND' EXIT

# Set these variables before executing this file
project_dir=~/blog/
virtual_env_dir=~/.virtualenvs/hackadda

# navigate to project folder
echo Navigating to project directory
cd $project_dir

# pull in the latest changes
echo Pulling in the latest changes from the git repository
git pull --ff

# activate project environment
echo Activating virtual environment
source $virtual_env_dir/bin/activate

# Install requirements
echo Installing Requirements
python -m pip install --upgrade pip
pip install -r requirements.txt

# Updating database
echo Updating database, if required
python manage.py migrate

# Update static files
echo Copying static files
python manage.py collectstatic --noinput

# Restarting Apache
echo Restarting Apache Server
# Set the sudo password as an environment variable
echo $SUDO_PASS | sudo -S service apache2 restart

echo Deployed Successfully!!!!

# deactivate the virtual environment
deactivate

# this file can be used to run cron jobs using crontab
# as of now, it is used to fill in the trending score column for the Post model.


# exit if any command fails
set -e

clean_up(){
        deactivate
        exit_code=$1
        last_command=$2
        if [ $exit_code -ne 0 ]; then
                >&2 echo "\"${last_command}\" command failed with exit code ${exit_code}."
                exit $exit_code
        fi
}

trap 'clean_up $? $BASH_COMMAND' EXIT

# Set these variables before executing this file
PROJECT_DIR=~/blog/
VIRTUAL_ENV_DIR=~/.virtualenvs/hackadda

cd $PROJECT_DIR
source $VIRTUAL_ENV_DIR/bin/activate

python manage.py runjobs daily

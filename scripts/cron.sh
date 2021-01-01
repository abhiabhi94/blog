# this file can be used to run cron jobs using crontab
# as of now, it is used to fill in the trending score column for the Post model.


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

cd $project_dir
source $virtual_env_dir/bin/activate

python manage.py runjobs daily

deactivate

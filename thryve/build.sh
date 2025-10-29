set -o errexit

pip install -r requirements.txt
python ./thryve/manage.py collectstatic --noinput
python ./thryve/manage.py makemigrations
python ./thryve/manage.py migrate
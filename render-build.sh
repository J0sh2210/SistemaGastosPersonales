
set -o errexit



apt-get update
apt-get install -y curl gnupg2


curl https://packages.microsoft.com/keys/microsoft.asc | apt-key add -
curl https://packages.microsoft.com/config/debian/10/prod.list > /etc/apt/sources.list.d/mssql-release.list


ACCEPT_EULA=Y apt-get install -y msodbcsql17


pip install -r requirements.txt
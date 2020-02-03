# Three Person Team

Este proyecto es para manejar toda la interfaz de TreePersonTeam

# Instalar Proyecto
```[bash]
git clone https://github.com/jgmc3012/dashboard_go_shop.git threepersonteam
cd threepersonteam

python -m venv venv
source venv/source/activate

python -m pip install -r requirements.txt

git clone https://github.com/jgmc3012/AdminLTE.git static/vendor/adminLTE


cp .env_example .env
#Configurar las variables de entorno


python manage.py migrate
python manage.py runserver
```

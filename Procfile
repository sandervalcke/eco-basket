web: uwsgi uwsgi.ini
init: python3 manage.py db init
upgrade: python3 manage.py db upgrade
init_gdv: python3 scripts/populate_grains_de_vie.py
clear_all_the_orders_in_the_database: python3 -m scripts.remove_order_items

# eco-basket 

# Heroku
heroku status
heroku logs
heroku logs --source startup
heroku config:set APP_SETTINGS=bread.config.heroku.HerokuConfig

heroku run init
heroku run upgrade
heroku run python3 scripts/populate_orders_gaspipa.py 

git push heroku master

import sqlite3

from flask import Flask, jsonify, json, render_template, request, url_for, redirect, flash
from werkzeug.exceptions import abort
from datetime import datetime
import logging
import sys 

connection_count = 0
# Function to get a database connection.
# This function connects to database with the name `database.db`
def get_db_connection():
        connection = sqlite3.connect('database.db')
        connection.row_factory = sqlite3.Row
        global connection_count
        connection_count = connection_count + 1
        return connection

# Function to get a post using its ID
def get_post(post_id):
        connection = get_db_connection()
        post = connection.execute('SELECT * FROM posts WHERE id = ?',
                                                (post_id,)).fetchone()            
        connection.close()
        return post

# Define the Flask application
app = Flask(__name__)
app.config['SECRET_KEY'] = 'your secret key'

# Define the main route of the web application 
@app.route('/')
def index():
        connection = get_db_connection()
        posts = connection.execute('SELECT * FROM posts').fetchall()
        connection.close()
        return render_template('index.html', posts=posts)

# Define how each individual article is rendered 
# If the post ID is not found a 404 page is shown
@app.route('/<int:post_id>')
def post(post_id):
        post = get_post(post_id)
        if post is None:
            app.logger.error('Non-existing article accessed')
            return render_template('404.html'), 404
        else:
            app.logger.info('Article "{0}" retrieved !'.format(post['title']))
            return render_template('post.html', post=post)

# Define the About Us page
@app.route('/about')
def about():
    app.logger.info('About Us` page retrieved successfully')
    return render_template('about.html')

# Define the post creation functionality 
@app.route('/create', methods=('GET', 'POST'))
def create():
        if request.method == 'POST':
                title = request.form['title']
                content = request.form['content']

                if not title:
                        flash('Title is required!')
                else:
                        connection = get_db_connection()
                        connection.execute('INSERT INTO posts (title, content) VALUES (?, ?)',
                                                 (title, content))
                        app.logger.info('New article with title "{0}" created !'.format(title))
                        connection.commit()
                        connection.close()

                        return redirect(url_for('index'))

        return render_template('create.html')

# Healthcheck endpoint
@app.route('/healthz')
def healthcheck():
    try:
        connection = get_db_connection()
        posts = connection.execute('SELECT * FROM posts').fetchall()
        connection.close()
        response = app.response_class(
            response = json.dumps({"result":"OK - healthy"}),
            status = 200,
            mimetype = 'application/json'
            )
        app.logger.info('Health status successful')
    except Exception:
        response = app.response_class(
            response = json.dumps({"result":"NOT OK - Unhealthy"}),
            status = 500,
            mimetype = 'application/json'
            )
        app.logger.info('Health status Unsuccessful')
    return response


#Metric Endpoint
@app.route('/metrics')
def metrics():
    connection = get_db_connection()
    all_posts = connection.execute('SELECT * FROM posts').fetchall()
    posts_count = len(all_posts)
    response = app.response_class(
                response=json.dumps({"status":"success","code":200,"data":{"db_connection_count":connection_count,"post_count":posts_count}}),
                status=200,
                mimetype='application/json'
            )

    app.logger.info('Metrics request successful')
    return response 
        

# start the application on port 3111
if __name__ == "__main__":
     logger = logging.getLogger(__name__) 
     stdout_handler = logging.StreamHandler(sys.stdout)
     stdout_handler.setLevel(logging.DEBUG)
     stderr_handler = logging.StreamHandler(sys.stderr)
     stderr_handler.setLevel(logging.ERROR)
     handlers = [stderr_handler, stdout_handler]
     for handler in handlers:
        logger.addHandler(handler)
     logging.basicConfig(format='%(asctime)s : %(levelname)s ::  %(message)s',datefmt='%d-%m-%Y , %H:%M:%S', level=logging.DEBUG)
     app.run(host='0.0.0.0', port='3111')

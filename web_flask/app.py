#!/usr/bin/env python3
from web_flask import create_app, babel, socketio
import psutil
import os
import pstats
import click
import cProfile
from werkzeug.serving import run_simple
from flask import request
"""
    This is the entry point of the application.
    It creates the application instance and runs it.
"""

app = create_app('default')
#migrate = Migrate(app, db)



"""
    babel.localeselector decorator registers the decorated function as a
    local selector function. The function is invoked for each request to
    select a language translation to use for that request.
    The function returns the best match language.
"""
@babel.localeselector
def get_locale():
    return request.accept_languages.best_match(app.config['LANGUAGES'])

@app.route('/test')
def make_shell_context():
    return dict(db=db)

"""
    The app.cli decorator registers a new command with the flask script.
    function runs a Source Code Profiling on the application and displays
    the result. The profiler measures the execution time of the functions
    in the application and the number of times each function was called.
    and saves the stats in a file.
"""
@app.cli.command()
@click.option('--length', default=25, help='Number of functions to include in the profiler report.')
@click.option('--profile-dir', default=None, help='Directory where profiler data files are saved.')
def profile(length, profile_dir):
    """Start the application under the code profiler."""
    profiler = cProfile.Profile()
    profiler.enable()

    profiler.disable()
    stats = pstats.Stats(profiler)
    stats.strip_dirs()
    stats.sort_stats('cumulative')
    stats.print_stats(length)
    if profile_dir:
        stats.dump_stats(os.path.join(profile_dir, 'myapp_profile.out'))

if __name__ == '__main__':
    process = psutil.Process()
    print(f'Initial memory usage: {process.memory_info().rss / 1024 / 1024} MB')
    #app.run(port=5000, debug=False)
    socketio.run(app)
    #cProfile.run('main()', filename='myapp_profile.out')

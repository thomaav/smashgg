import logging
from GGClient import GGClient
from flask import Flask, render_template, redirect, request, jsonify
from flask.logging import create_logger
from flask_caching import Cache
from tournament import BracketType


app = Flask(__name__)
app.logger.setLevel(logging.INFO)

cache_config = \
        {'CACHE_TYPE': 'simple'} if __name__ == '__main__' else \
        {'CACHE_TYPE': 'uwsgi', 'CACHE_UWSGI_NAME': 'smashggcache', 'CACHE_DEFAULT_TIMEOUT': 60}
cache = Cache(app, config=cache_config)
cache.init_app(app)


@app.errorhandler(ValueError)
def handle_value_error(error):
    return 'bee boo poo pee fucko boingo in the backend' + \
        f'<br><br>{str(error)}'


@app.route('/')
def search():
    return render_template('search.jinja2')


@app.route('/tournaments')
@cache.memoize(timeout=60*60)
def coming_tournaments():
    client = GGClient(logger=app.logger)
    t = client.get_coming_tournaments()
    return render_template('coming_tournaments.jinja2', coming_tournaments=t)


@app.route('/bracket/search/<string:search>')
def choose_tournament(search):
    client = GGClient(logger=app.logger)
    tournaments = client.search_for_tournaments(search)
    if len(tournaments) == 1:
        tournament_id = list(tournaments.keys())[0]
        return redirect(f'/bracket/{tournament_id}')
    return render_template('tournament.jinja2', url_path='/bracket', tournaments=tournaments, search=search)


@app.route('/bracket/<int:tournament_id>')
@cache.memoize(timeout=10*60)
def choose_event(tournament_id):
    client = GGClient(logger=app.logger)
    events = client.get_melee_events(tournament_id)
    smashggurl = client.get_smashgg_url(tournament_id, 0, 0, 0)

    if len(events) == 1:
        event_id = list(events.keys())[0]
        return redirect(f'{request.path}/{event_id}')
    return render_template('event.jinja2', url_path=request.path, events=events, smashggurl=smashggurl)


@app.route('/bracket/<int:tournament_id>/<int:event_id>')
@cache.memoize(timeout=10*60)
def choose_phase(tournament_id, event_id):
    client = GGClient(logger=app.logger)
    phases = client.get_event_phases(event_id)
    smashggurl = client.get_smashgg_url(tournament_id, event_id, 0, 0)

    if len(phases) == 1:
        phase_id = list(phases.keys())[0]
        return redirect(f'{request.path}/{phase_id}')
    return render_template('phase.jinja2', url_path=request.path, phases=phases, smashggurl=smashggurl)


@app.route('/bracket/<int:tournament_id>/<int:event_id>/<int:phase_id>')
@cache.memoize(timeout=10*60)
def choose_phase_group(tournament_id, event_id, phase_id):
    client = GGClient(logger=app.logger)
    phase_groups = client.get_phase_groups(phase_id)
    smashggurl = client.get_smashgg_url(tournament_id, event_id, phase_id, 0)

    if len(phase_groups) == 1:
        phase_group_id = phase_groups[0]['id']
        return redirect(f'{request.path}/{phase_group_id}')
    return render_template('phase_group.jinja2', url_path=request.path, phase_groups=phase_groups, smashggurl=smashggurl)


@app.route('/bracket/<int:tournament_id>/<int:event_id>/<int:phase_id>/<int:phase_group_id>')
@cache.memoize(timeout=1*60)
def render_bracket(tournament_id, event_id, phase_id, phase_group_id):
    client = GGClient(logger=app.logger)
    bracket = client.get_phase_group_bracket(phase_group_id, tournament_id)
    bracket.finalize()
    smashggurl = client.get_smashgg_url(tournament_id, event_id, phase_id, phase_group_id)

    if bracket.type in [BracketType.DOUBLE_ELIMINATION, BracketType.SINGLE_ELIMINATION]:
        return render_template('bracket.jinja2', bracket=bracket, smashggurl=smashggurl)
    elif bracket.type == BracketType.ROUND_ROBIN:
        return render_template('pool.jinja2', bracket=bracket, smashggurl=smashggurl)


@app.route('/user/<int:user_id>')
def user_tournaments(user_id):
    client = GGClient(logger=app.logger)
    user = client.get_user(user_id)
    return render_template('user.jinja2', user=user)

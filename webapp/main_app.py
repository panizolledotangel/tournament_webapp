import logging
import signal
import sys
import os
from flask import Flask, jsonify, render_template
from apscheduler.schedulers.background import BackgroundScheduler
from werkzeug.serving import run_simple

from sources.services.google_drive_service import GoogleDriveService
from sources.logic.tournament import Tournament
from sources.logic.tsp_problem import TSPProblem


logging.basicConfig(level=logging.DEBUG)

gdrive = GoogleDriveService()
problem = TSPProblem()
t = Tournament(gdrive, problem)

def check_for_new_results():
    logging.getLogger("acotournament").debug("Checking for new results...")
    t.check_for_new_results()

scheduler = BackgroundScheduler()
scheduler.add_job(check_for_new_results, 'interval', seconds=60)
scheduler.start()

def signal_handler(sig, frame):
    print('Performing shutdown tasks...')
    t.save_ranking(os.getenv('RANKING_PATH'))
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/rankings')
def get_rankings():
    scores = t.ranking.get_scores()
    
    ranks = list(scores.items())
    ranks = sorted(ranks, key=lambda x: x[1]['best'], reverse=False)
    ranks = [{'name': e[0], 'best': f"{e[1]['best']:.4f}", 'last': f"{e[1]['last'][-1]:.4f}", "status": e[1]["status"]} for e in ranks]

    return jsonify(ranks)

@app.route('/statuses')
def show_statuses():
    contestants = t.ranking.get_messages()
    return render_template('status.html', contestants=contestants)

if __name__ == '__main__':
    #app.run(debug=True, use_reloader=False, host='0.0.0.0', port=8897)
    run_simple('0.0.0.0', 8888, app, shutdown_hooks=[t.save_ranking])

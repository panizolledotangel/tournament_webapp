import logging
import signal
import sys
import os
from flask import Flask, jsonify, render_template
from apscheduler.schedulers.background import BackgroundScheduler
from werkzeug.serving import run_simple

from sources.services.google_drive_service import GoogleDriveService
from sources.logic import Tournament

def get_problem_class():
    problem_class = os.getenv("PROBLEM_CLASS")
    mod = __import__('sources.logic', fromlist=[problem_class])
    klass = getattr(mod, problem_class)
    return klass

logging.basicConfig(level=logging.DEBUG)

gdrive = GoogleDriveService()
problem = get_problem_class()()
maximize = bool(os.getenv("PROBLEM_MAXIMIZE"))
restore_snapshot = bool(os.getenv("RESTORE_SNAPSHOT"))
t = Tournament(gdrive, problem, maximize=maximize, restore_snapshot=restore_snapshot)

def check_for_new_results():
    logging.getLogger("acotournament").info("Checking for new results...")
    t.check_for_new_results()
    logging.getLogger("acotournament").info("Done!")

def save_snapshot():
    logging.getLogger("acotournament").debug("Saving snapshot...")
    t.save_snapshot(os.getenv('SNAPSHOT_FOLDER_PATH'))
    logging.getLogger("acotournament").debug("Done!")

scheduler = BackgroundScheduler()
scheduler.add_job(check_for_new_results, 'interval', seconds=60)
scheduler.add_job(save_snapshot, 'interval', seconds=int(60*1.8))
scheduler.start()

def signal_handler(sig, frame):
    print('Performing shutdown tasks...')
    save_snapshot()
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
    last_checked = t.last_checked.strftime('%H:%M:%S')
    
    ranks = list(scores.items())
    ranks = sorted(ranks, key=lambda x: x[1]['best'], reverse=maximize)
    ranks = [{'name': e[0], 'best': f"{e[1]['best']:.4f}", 'last': f"{e[1]['last'][-1]:.4f}", "status": e[1]["status"]} for e in ranks]

    data = {
        'last_checked': last_checked,
        'ranks': ranks
    }

    return jsonify(data)

@app.route('/statuses')
def show_statuses():
    contestants = t.ranking.get_messages()
    return render_template('status.html', contestants=contestants)

@app.route('/score-evolution')
def show_score_evolution():
    return render_template('graph.html')

@app.route('/api/score-evolution')
def get_score_evolution():
    data = t.ranking.get_scores_evolution()
    return jsonify(data)

if __name__ == '__main__':
    #app.run(debug=True, use_reloader=False, host='0.0.0.0', port=8897)
    run_simple('0.0.0.0', 8888, app, shutdown_hooks=[t.save_ranking])

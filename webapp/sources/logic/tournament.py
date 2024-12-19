import logging
import os
import json
import pytz
from datetime import datetime

from sources.services.google_drive_service import GoogleDriveService
from sources.logic.ranking import Ranking
from sources.logic.problem import Problem

class Tournament:

    def __init__(self, g_drive, problem: Problem, maximize: bool = False):
        self.gdrive = g_drive
        self.logger = logging.getLogger("acotournament")
        self.tz_info = pytz.timezone(os.environ["TIMEZONE"])
        self.last_checked = datetime.now(self.tz_info).time()
        self.tournament_name = os.getenv('TOURNAMENT_NAME')

        snapshot = None
        if os.environ.get("RESTORE_SNAPSHOT") == 1:
            snapshot =  self._restore_last_snapshot()
        
        self.needs_snapshot = snapshot is None
        self.contestants = self._load_contestants(snapshot=snapshot)
        self.last_contestant_checked = self._load_last_checked(snapshot=snapshot)
        self.last_md5 = self._load_last_md5(snapshot=snapshot)
        self.ranking =  self._load_ranking(problem, maximize, snapshot=snapshot)

    def check_for_new_results(self):
        self.last_checked = datetime.now(self.tz_info).time()
        for contestant in self.contestants.keys():
            try:
                new_result, f_name = self._check_contestant(contestant)
                if new_result:
                    self.needs_snapshot = True
                    self.ranking.update(contestant, f_name, new_result)
                    self.logger.debug(f"New result for {contestant}: {new_result}")
            except Exception as e:
                self.ranking.set_error(contestant, f"Error: {e}")
                self.logger.error(f"Error checking contestant {contestant}: {e}")

    def save_snapshot(self, path=None):
        if self.needs_snapshot:
            file_name = f"{datetime.now(self.tz_info).strftime('%Y-%m-%d_h%H_m%M')}_{self.tournament_name}_snapshot.json"
            path = file_name if path is None else os.path.join(path, file_name)
            data = {
                "contestants": self.contestants,
                "last_contestant_checked": self._serialize_contestands_check(),
                "last_md5": self.last_md5,
                "ranking": self.ranking.get_scores()
            }
            with open(path, "w") as f:
                json.dump(data, f)
            
            self.logger.debug(f"Snapshot saved to {path}")
            self.needs_snapshot = False

    def _restore_last_snapshot(self):
        self.logger.info("Restoring last snapshot...")

        folder_path = os.environ.get("SNAPSHOT_FOLDER_PATH")
        
        files = [os.path.join(folder_path, f) for f in os.listdir(folder_path) if os.path.isfile(os.path.join(folder_path, f))]
        if not files:
            self.logger.warning("No snapshot found even though RESTORE_SNAPSHOT is set to True")
            return None
        
        last_file = max(files, key=os.path.getmtime)
        self.logger.info(f"Restored snapshot from {last_file}")
        with open(last_file, "r") as f:
            return json.load(f)

    def _serialize_contestands_check(self):
        return {k: v.strftime('%Y-%m-%d %H:%M:%S') for k, v in self.last_contestant_checked.items()}
    
    def _load_contestants(self, snapshot=None):
        if snapshot:
            return snapshot["contestants"]
        
        file_id = os.getenv('ROOT_FOLDER_ID')
        folders = self.gdrive.list_files(file_id)
        return {f["name"]:f["id"] for f in folders if f['mimeType'] == 'application/vnd.google-apps.folder'}
    
    def _load_ranking(self, problem: Problem, maximize: bool, snapshot=None):
        ranking = Ranking(self.contestants.keys(), problem, maximize)
        if snapshot:
            ranking.load_scores(snapshot["ranking"])
        return ranking

    def _load_last_checked(self, snapshot=None):
        if snapshot:
            return {k: datetime.strptime(v, '%Y-%m-%d %H:%M:%S') for k, v in snapshot["last_contestant_checked"].items()}
        
        return {c: datetime(1970, 1, 1, tzinfo=self.tz_info) for c in self.contestants.keys()}

    def _load_last_md5(self, snapshot=None):
        if snapshot:
            return snapshot["last_md5"]
        
        return {c: None for c in self.contestants.keys()}
    
    def _check_contestant(self, name):
        files = self.gdrive.list_files(self.contestants[name])
        
        files = list(filter(lambda f: f['mimeType'] == 'application/json', files))
        for i in range(len(files)):
            files[i]['modifiedTime'] = GoogleDriveService.convert_to_date(files[i]['modifiedTime'])

        if self.ranking.get_status(name) == Ranking.OK_STATUS:
            files = list(filter(lambda f: self._is_file_valid(f, name), files))

        if len(files) > 0:
            files.sort(key=lambda f: f["modifiedTime"], reverse=True)

            f = files[0]
            self.last_contestant_checked[name] = f['modifiedTime']
            self.last_md5[name] = f['md5Checksum']

            return self.gdrive.load_json(f['id']), f['name']
        else:
            return None, ""
        
    def _is_file_valid(self, file, contestant):
        
        if file["modifiedTime"] <= self.last_contestant_checked[contestant]:
            return False
        
        if file['md5Checksum'] == self.last_md5[contestant]:
            return False
        
        return True
    
    


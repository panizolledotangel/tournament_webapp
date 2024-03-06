import logging
import os
import json
from datetime import datetime

from sources.services.google_drive_service import GoogleDriveService
from sources.logic.ranking import Ranking
from sources.logic.problem import Problem

class Tournament:

    def __init__(self, g_drive, problem: Problem):
        self.gdrive = g_drive
        self.tournament_name = os.getenv('TOURNAMENT_NAME')
        self.contestants = self._load_contestants()
        self.last_checked = self._load_last_checked()
        self.last_md5 = self._load_last_md5()
        self.ranking =  self._load_ranking(problem)
        self.logger = logging.getLogger("acotournament")

    def check_for_new_results(self):
        for contestant in self.contestants.keys():
            try:
                new_result, f_name = self._check_contestant(contestant)
                if new_result:
                    self.ranking.update(contestant, f_name, new_result)
                    self.logger.debug(f"New result for {contestant}: {new_result}")
            except Exception as e:
                self.ranking.set_error(contestant, f"Error: {e}")
                self.logger.error(f"Error checking contestant {contestant}: {e}")

    def save_ranking(self, path=None):
        file_name = f"{datetime.now().strftime('%Y-%m-%d_h%H')}_{self.tournament_name}.json"
        path = file_name if path is None else os.path.join(path, file_name)
        with open(path, "w") as f:
            json.dump(self.ranking.get_scores(), f)
    
    def _load_contestants(self):
        file_id = os.getenv('ROOT_FOLDER_ID')
        folders =self. gdrive.list_files(file_id)
        return {f["name"]:f["id"] for f in folders if f['mimeType'] == 'application/vnd.google-apps.folder'}
    
    def _load_ranking(self, problem: Problem):
        return Ranking(self.contestants.keys(), problem)

    def _load_last_checked(self):
        return {c: datetime(1970, 1, 1) for c in self.contestants.keys()}

    def _load_last_md5(self):
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
            self.last_checked[name] = f['modifiedTime']
            self.last_md5[name] = f['md5Checksum']

            return self.gdrive.load_json(f['id']), f['name']
        else:
            return None, ""
        
    def _is_file_valid(self, file, contestant):
        
        if file["modifiedTime"] <= self.last_checked[contestant]:
            return False
        
        if file['md5Checksum'] == self.last_md5[contestant]:
            return False
        
        return True
    
    


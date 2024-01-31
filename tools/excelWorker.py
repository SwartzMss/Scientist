import pandas as pd
import os
from datetime import datetime

class excelWorker:
    def __init__(self, project_name, logger):
        self.project_name = project_name
        target_path = r"\\192.168.3.142\SuperWind\Study"
        self.filename = os.path.join(target_path, f"aridropList_{datetime.now().year}_{str(datetime.now().month).zfill(2)}.xlsx")
        self.lockfile = os.path.join(target_path, "excel_is_ongoing1234567890.lock")
        self.cached_data = []
        self.logger = logger
        self.create_lockfile()

    def create_lockfile(self):
        # Create a lock file to indicate that the process is ongoing
        with open(self.lockfile, 'w') as file:
            file.write("This file indicates that an Excel operation is in progress.")

    def remove_lockfile(self):
        # Remove the lock file to indicate that the process is complete
        if os.path.exists(self.lockfile):
            os.remove(self.lockfile)

    def update_info(self, name, msg):
        self.cached_data.append({"name": name, "msg": msg})

    def save_msg_and_stop_service(self):
        try:
            sheet_name = f"{self.project_name}_{datetime.now().strftime('%Y_%m_%d_%H_%M')}"
            if not os.path.exists(self.filename):
                with pd.ExcelWriter(self.filename, engine='openpyxl') as writer:
                    df = pd.DataFrame(self.cached_data)
                    df.to_excel(writer, sheet_name=sheet_name, index=False)
            else:
                with pd.ExcelWriter(self.filename, engine='openpyxl', mode='a') as writer:
                    df = pd.DataFrame(self.cached_data)
                    df.to_excel(writer, sheet_name=sheet_name, index=False)
            self.cached_data = []  # Clear cached data
            self.remove_lockfile()  # Remove the lock file once the process is complete
            self.logger(f"Saving data to {self.filename} in sheet {sheet_name}")
        except Exception as e:
            self.logger(f"Error saving self.filename， msg: {e}")

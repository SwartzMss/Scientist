import pandas as pd
import os
from datetime import datetime
import glob
class excelWorker:
    def __init__(self, project_name, logger):
        self.project_name = project_name
        # 设置文件路径
        self.target_path = r"\\192.168.3.142\SuperWind\Study"
        self.filename = os.path.join(self.target_path, f"{project_name}_{datetime.now().year}_{str(datetime.now().month).zfill(2)}.xlsx")
        # 锁文件名现在包含项目名称
        self.lockfile = os.path.join(self.target_path, f"{project_name}_excel_is_ongoing1234567890.lock")
        self.cached_data = []
        self.logger = logger
        self.create_lockfile()

    def maintain_log_files(self):
        # 定义要保留的最新日志文件数量
        max_files = 3
        # 构造日志文件搜索模式
        log_pattern = os.path.join(self.target_path, f"{self.project_name}_*.log")
        # 获取所有匹配的日志文件
        files = glob.glob(log_pattern)
        # 按修改时间排序，最新的先
        files.sort(key=os.path.getmtime, reverse=True)
        # 删除超过数量限制的旧文件
        for file in files[max_files:]:
            os.remove(file)
            self.logger(f"Removed old log file: {file}")

    def create_lockfile(self):
        with open(self.lockfile, 'w') as file:
            file.write("This file indicates that an Excel operation is in progress for project " + self.project_name + ".")

    def remove_lockfile(self):
        if os.path.exists(self.lockfile):
            os.remove(self.lockfile)

    def update_info(self, name, msg, column_name="msg"):
        # 查找是否已经有相同name的数据条目
        existing_item = None
        for item in self.cached_data:
            if item['name'] == name:
                existing_item = item
                break

        if existing_item:
            # 如果找到了现有的条目，更新或添加列信息
            existing_item[column_name] = msg
        else:
            # 如果没有找到现有的条目，创建一个新条目
            new_item = {"name": name, column_name: msg}
            self.cached_data.append(new_item)

    def save_msg_and_stop_service(self):
        if not self.cached_data: 
            self.logger("no cached_data. no need save file")
            return
        # 在保存Excel之前维护日志文件
        self.maintain_log_files()
        try:
            # 工作表名称现在包括日期和时间
            sheet_name = datetime.now().strftime('%d_%H_%M')
            if not os.path.exists(self.filename):
                with pd.ExcelWriter(self.filename, engine='openpyxl') as writer:
                    df = pd.DataFrame(self.cached_data)
                    df.to_excel(writer, sheet_name=sheet_name, index=False)
            else:
                with pd.ExcelWriter(self.filename, engine='openpyxl', mode='a', if_sheet_exists='replace') as writer:
                    df = pd.DataFrame(self.cached_data)
                    df.to_excel(writer, sheet_name=sheet_name, index=False)
            self.cached_data = []  # 清空缓存数据
            self.remove_lockfile()  # 进程完成后移除锁文件
            self.logger(f"Saving data to {self.filename} in sheet {sheet_name}")
        except Exception as e:
            self.logger(f"Error saving {self.filename}, msg: {e}")

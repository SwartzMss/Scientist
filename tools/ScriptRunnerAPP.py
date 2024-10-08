import configparser
import subprocess
import os
import time
from datetime import datetime, timedelta

class ScriptRunner:
    def __init__(self, config_path, flag_file, check_interval=60,log_max_size_mb=10, log_duration_hours=10):
        self.config_path = config_path
        self.flag_file = flag_file
        self.check_interval = check_interval
        self.config = configparser.ConfigParser()
        self.log_max_size_mb = log_max_size_mb
        self.log_duration_hours = log_duration_hours
        self.log_file_path = self.create_log_file()


    def create_log_file(self):
        current_time = datetime.now().strftime("%Y_%m_%d_%H_%M_%S")
        log_file_path = rf'\\192.168.3.142\SuperWind\Study\ScriptRunner{current_time}.log'
        self.log_creation_time = datetime.now()
        return log_file_path

    def check_and_manage_log_file(self):
        if os.path.exists(self.log_file_path):
            file_size_mb = os.path.getsize(self.log_file_path) / (1024 * 1024)
            if file_size_mb > self.log_max_size_mb or (datetime.now() - self.log_creation_time) > timedelta(hours=self.log_duration_hours):
                os.remove(self.log_file_path)
                self.log_file_path = self.create_log_file()
                self.log_and_print("由于大小或时间限制，日志文件已重置。")

    def log_message(self, text):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        return f"{timestamp} - {text}"

    def log_and_print(self, text):
        self.check_and_manage_log_file()
        message = self.log_message(text)
        with open(self.log_file_path, 'a', encoding='utf-8') as log_file:
            print(message)
            log_file.write(message + '\n')

    def load_config(self):
        self.config.read(self.config_path)

    def get_task_name(self):
        with open(self.flag_file, 'r') as file:
            return file.read().strip()

    def create_ongoing_file(self, task_name):
        ongoing_file = rf'\\192.168.3.142\SuperWind\Study\task_{task_name}.ongoing'
        with open(ongoing_file, 'w') as file:
            file.write("Task is running.")
        return ongoing_file

    def cleanup(self, ongoing_file):
        if os.path.exists(ongoing_file):
            os.remove(ongoing_file)
        # 清空 task_flag.txt 的内容
        with open(self.flag_file, 'w') as file:
            file.write("")

    def run(self):
        while True:
            if os.path.exists(self.flag_file):
                task_name = self.get_task_name()
                if task_name:
                    ongoing_file = self.create_ongoing_file(task_name)  # 正确的创建.ongoing文件
                    self.load_config()
                    if task_name in self.config:
                        task_type = self.config[task_name].get('type')
                        if task_type == 'python':
                            self.run_python_task(task_name)
                        elif task_type == 'gitbash':
                            self.run_gitbash_task(task_name)
                    else:
                        self.log_and_print(f"No task named '{task_name}' found in configuration.")
                    self.cleanup(ongoing_file)  # 清理时传递正确的.ongoing文件
                else:
                    self.log_and_print(f"Task flag file '{self.flag_file}' is empty, waiting for the next task...")
            else:
                self.log_and_print(f"Task flag file '{self.flag_file}' not found.")

            self.log_and_print(f"Waiting for {self.check_interval} seconds before next check...")
            time.sleep(self.check_interval)

    def run_python_task(self, task_name):
        python_interpreter = self.config[task_name].get('python_interpreter')
        script_name = self.config[task_name].get('script_name')
        run_directory = self.config[task_name].get('run_directory')
        
        self.log_and_print(f"Changing directory to: {run_directory}")
        os.chdir(run_directory)  # 切换到脚本所在目录
        
        script_path = os.path.join(run_directory, script_name)
        self.log_and_print(f"Running Python task: {script_path}")
        
        try:
            subprocess.run([python_interpreter, script_path], check=True)
        except subprocess.CalledProcessError as e:
            self.log_and_print(f"Python task execution failed: {e}")

    def run_gitbash_task(self, task_name):
        directory = self.config[task_name].get('directory')
        command = self.config[task_name].get('command', 'pull')  # 如果未指定命令，则默认为 'pull'
        
        # 先改变当前工作目录
        os.chdir(directory)
        self.log_and_print(f"Changed directory to: {directory}")
        
        # 然后执行 git 命令
        self.log_and_print(f"Running Git Bash task: git {command}")
        try:
            subprocess.run(['git', command], check=True)
        except subprocess.CalledProcessError as e:
            self.log_and_print(f"Git Bash task execution failed: {e}")


if __name__ == "__main__":
    config_path = rf'\\192.168.3.142\SuperWind\Study\account_config\ScriptRunnerConfig.ini'
    flag_file = rf'\\192.168.3.142\SuperWind\Study\account_config\task_flag.txt'
    runner = ScriptRunner(config_path, flag_file)
    runner.run()

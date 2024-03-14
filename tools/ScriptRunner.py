import configparser
import subprocess
import os
import time
from datetime import datetime

class ScriptRunner:
    def __init__(self, config_path, flag_file, check_interval=60):
        self.config_path = config_path
        self.flag_file = flag_file
        self.check_interval = check_interval
        self.config = configparser.ConfigParser()
        current_time = datetime.now().strftime("%Y_%m_%d_%H_%M_%S")
        self.log_file_path = rf'\\192.168.3.142\SuperWind\Study\ScriptRunner{current_time}.log'
        self.ongoing_file = 'task.ongoing'

    def log_message(self, text):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        return f"{timestamp} - {text}"

    def log_and_print(self, text):
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
        ongoing_file = f'task_{task_name}.ongoing'
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
        git_bash_path = self.config[task_name].get('git_bash_path', "C:/Program Files/Git/git-bash.exe")  # Use default if not specified
        directory = self.config[task_name].get('directory')
        command = self.config[task_name].get('command')
        
        self.log_and_print(f"Changing directory to: {directory}")
        
        # 构建执行Git命令的完整命令
        full_command = f'git -C "{directory}" {command}'
        self.log_and_print(f"Running Git Bash task: {full_command} in {directory}")
        
        try:
            subprocess.run([git_bash_path, '-c', full_command], check=True)
        except subprocess.CalledProcessError as e:
            self.log_and_print(f"Git Bash task execution failed: {e}")


if __name__ == "__main__":
    config_path = "ScriptRunnerConfig.ini"
    flag_file = "task_flag.txt"
    runner = ScriptRunner(config_path, flag_file)
    runner.run()

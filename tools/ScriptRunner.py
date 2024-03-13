import configparser
import subprocess
import os
import time

class ScriptRunner:
    def __init__(self, config_path, check_interval=60):
        self.config_path = config_path
        self.check_interval = check_interval  # 检查配置文件的间隔时间，单位为秒
        self.ongoing_file = config_path + '.ongoing'  # 基于配置文件路径创建ongoing文件的路径

    def run(self):
        """周期性检查配置文件并根据配置执行脚本。"""
        while True:
            try:
                self.config = self.load_config()
                self.create_ongoing_file()
                self.run_script()
                self.cleanup_files()
            except Exception as e:
                print(f"发生错误：{e}")
            finally:
                print(f"等待{self.check_interval}秒后重新检查配置文件...")
                time.sleep(self.check_interval)

    def load_config(self):
        """从INI配置文件加载配置信息。如果文件不存在或格式错误，抛出异常。"""
        if not os.path.exists(self.config_path):
            raise FileNotFoundError(f"配置文件 {self.config_path} 未找到。")
        config = configparser.ConfigParser()
        config.read(self.config_path)
        return config

    def create_ongoing_file(self):
        """创建一个标记文件，表示任务正在进行中。"""
        open(self.ongoing_file, 'w').close()

    def cleanup_files(self):
        """删除ongoing标记文件和配置文件，表示任务已完成。"""
        os.remove(self.ongoing_file)
        os.remove(self.config_path)

    def run_script(self):
        """根据配置信息运行脚本。"""
        python_path = self.config['Paths']['python_interpreter']
        script_path = self.config['Paths']['script_directory']
        run_path = self.config['Paths']['run_directory']
        script_name = self.config['Script']['name']

        self.check_file_exists(python_path, "Python解释器")
        script_full_path = os.path.join(script_path, script_name)
        self.check_file_exists(script_full_path, "Python脚本")

        os.chdir(run_path)
        subprocess.run([python_path, script_full_path])

    def check_file_exists(self, file_path, description):
        """检查文件是否存在，如果不存在抛出异常。"""
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"{description} {file_path} 未找到。")

def main():
    config_path = "script_config.ini"
    check_interval = 60  # 检查配置文件的间隔时间（秒）

    runner = ScriptRunner(config_path, check_interval)
    runner.run()

if __name__ == "__main__":
    main()

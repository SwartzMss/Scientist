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
        """根据配置信息运行脚本，增加字段读取保护和执行停止功能。"""
        # 检查是否存在停止标志
        if os.path.exists("stop_script.flag"):
            print("检测到停止标志文件，脚本执行被停止。")
            return

        # 使用.get()避免KeyError，可以指定默认值作为第二个参数
        python_path = self.config['Paths'].get('python_interpreter', '/usr/bin/python3')
        script_path = self.config['Paths'].get('script_directory')
        run_path = self.config['Paths'].get('run_directory')
        script_name = self.config['Script'].get('name')

        # 确保必要的配置信息存在
        if not script_path or not run_path or not script_name:
            print("配置文件中缺少必要的路径信息或脚本名称。")
            return

        self.check_file_exists(python_path, "Python解释器")
        script_full_path = os.path.join(script_path, script_name)
        self.check_file_exists(script_full_path, "Python脚本")

        # 更改当前工作目录并执行脚本
        os.chdir(run_path)
        try:
            subprocess.run([python_path, script_full_path], check=True)
        except subprocess.CalledProcessError as e:
            print(f"脚本执行失败: {e}")


def main():
    config_path = "script_config.ini"
    check_interval = 60  # 检查配置文件的间隔时间（秒）

    runner = ScriptRunner(config_path, check_interval)
    runner.run()

if __name__ == "__main__":
    main()

import os
import stat
import shutil
import sys
import time
import warnings
import git
from multiprocessing import Process
from PIL import Image
from pathlib import Path

from app.utils import MD5
import subprocess
from subprocess import CalledProcessError
from app.models.errors import DirAnalyzeError, GitFetchError, ProjectNotFound, GitRepoNotExist, CommandRunError, \
    GitFetchingError, GitCheckoutError


class DealFile:
    base_path = "./assets/projects/"
    cal_path = "./assets/calculation/"

    @classmethod
    def compress(cls, path: str):
        img = Image.open(path)
        img.save(path)

    @classmethod
    def allowed_file(cls, filename: str):
        return '.' in filename and \
               filename.rsplit('.', 1)[1].lower() in {'png', 'jpg', 'py'}

    @classmethod
    def rename(cls, filename: str) -> str:
        return MD5.encode_file(filename) + '.jpg'

    @classmethod
    def deal_img(cls, f):
        folder_path = Path.joinpath(Path(__file__).absolute().parent.parent.parent, 'img')
        img_path = Path.joinpath(folder_path, f.filename)
        f.save(str(img_path))
        # 压缩
        DealFile().compress(str(img_path))

        # 重命名
        name = MD5.encode_file(str(img_path)) + '.jpg'
        os.rename(
            str(img_path),
            str(Path.joinpath(folder_path, name))
        )
        return name

    @classmethod
    def save_file(cls, path, py_f):
        paths = path.rsplit('/', 1)
        file_message = py_f.filename.rsplit('/', 1)
        file_name = file_message[1] if len(file_message) == 2 else file_message[0]
        if len(paths) == 2:
            if paths[1] == file_name:
                file_path = paths[0] + '/'
            else:
                file_path = path
        else:
            if paths[0] == file_name:
                file_path = ''
            else:
                file_path = path
        proj_path = cls.base_path + file_path
        if os.path.exists(proj_path) is not True:
            os.makedirs(proj_path)
        py_f.save(proj_path + file_name)

    @classmethod
    def get_dirs(cls, file_path):
        proj_path = cls.base_path + file_path
        if os.path.exists(os.path.join(proj_path)) is not True:
            raise ProjectNotFound('Project Not Found')
        try:
            for _, dirs, files in os.walk(proj_path, topdown=True):
                return dirs, files
        except Exception:
            raise DirAnalyzeError('DirAnalyzeError')
        # dir_list = []
        # file_list = []
        # for item in dirs:
        #     temp = os.path.join(proj_path, item)
        #     if os.path.isdir(temp):
        #         dir_list.append(item)
        #     else:
        #         file_list.append(item)

    @classmethod
    def git_fetch(cls, repo_url):
        warnings.warn("please use git_fetch_re", DeprecationWarning)
        git_target, git_url = cls.git_url_deal(repo_url)
        project_repo = git_url.strip('/').split('/', 1)
        project_master = project_repo[0]
        project_name = project_repo[1]
        encode_project_name = project_master + '-' + project_name
        fetch_command = 'cd ' + cls.base_path + ' && git clone ' + git_target + git_url + ' ' + encode_project_name
        project_path = cls.base_path + encode_project_name
        if os.path.exists(project_path):
            dirs, files = cls.get_dirs(encode_project_name)
            if len(dirs) + len(files) > 1:
                return project_path, project_name, encode_project_name
            else:
                shutil.rmtree(project_path, onerror=cls.rm_read_only)
        try:
            res = cls.command_run(fetch_command)
        except Exception:
            raise GitFetchError('获取项目失败')
        if res:
            return project_path, project_name, encode_project_name
        else:
            shutil.rmtree(project_path)
            raise GitFetchError('获取项目失败')

    @classmethod
    def git_url_deal(cls, git_url: str):
        if git_url.find("github.com/") != -1:
            # return "https://github.com.cnpmjs.org/", git_url.split("github.com/", 1)[1]
            return "https://github.com/", git_url.split("github.com/", 1)[1]
        elif git_url.find("gitee.com") != -1:
            return "https://gitee.com/", git_url.split("gitee.com/", 1)[1]
        else:
            raise GitRepoNotExist('Repo not Exist')

    @classmethod
    def command_run(cls, command: str):
        try:
            ret = subprocess.run(command, shell=True, check=True, encoding="utf-8")
            return ret.returncode == 0
        except CalledProcessError:
            raise CommandRunError

    @classmethod
    def rm_read_only(cls, fn, tmp, info):
        try:
            os.chmod(tmp, stat.S_IWRITE)
            fn(tmp)
        except PermissionError:
            raise GitFetchingError

    @classmethod
    def git_fetch_re(cls, git_url, repo_path, ver: str = ''):
        project_master = repo_path.strip('/').split('/', 1)[0]
        project_name = repo_path.strip('/').split('/', 1)[1]
        encode_project_name = project_master + '-' + project_name
        project_path = cls.base_path + encode_project_name
        if os.path.exists(project_path):
            # 判断是否已经存在项目文件夹
            dirs, files = cls.get_dirs(encode_project_name)
            repo = git.Repo(project_path)
            if len(dirs) + len(files) > 1:
                # size = cls.monitor_size(encode_project_name)
                # if size <= 32*1024*2:
                #     with open(f"{cls.base_path}/log.txt", 'a', newline='') as f:
                #         f.write(encode_project_name+'\n')
                #     raise GitFetchError(f"获取项目失败{git_url + repo_path}")
                return project_path, project_name, encode_project_name, repo.commit().hexsha
            else:
                shutil.rmtree(project_path)
                print("Delete " + encode_project_name)
        # res = cls.repo_clone(url=git_url + repo_path, to_path=project_path)
        p = Process(target=cls.repo_clone, args=(git_url + repo_path, project_path))
        p.start()
        if cls.check_clone_status(encode_project_name) == 1:
            p.terminate()
            while True:
                time.sleep(5)
                print("检测存活喵.")
                if not p.is_alive():
                    break
            p.close()
            raise GitFetchError(f"获取项目失败{git_url + repo_path}")
        p.join()
        if p.exitcode == 1:
            if Path(project_path).exists():
                # shutil.rmtree(project_path)
                print("Delete(exit=1) " + encode_project_name)
            raise GitFetchError(f"获取项目失败{git_url + repo_path}")
        else:
            res = git.Repo(project_path)
            if ver is not None and ver != '':
                cls.repo_repair(encode_project_name, ver)
            commit_head = res.commit().hexsha
            with open(f"{cls.base_path}/log.txt", mode='a', newline='', encoding='utf-8') as f:
                f.write(encode_project_name + '克隆更新成功' + '\n')
        return project_path, project_name, encode_project_name, commit_head

    @classmethod
    def repo_clone(cls, url, to_path, count=0):
        if count == 5:
            sys.exit(1)
            # raise GitFetchError(f"获取项目失败{url}")
        try:
            print("cloning from " + url)
            return git.Repo.clone_from(url, to_path)
        except Exception:
            print(f"Failed to clone from {url}, retry" + str(count + 1))
            return cls.repo_clone(url, to_path, count + 1)

    @classmethod
    def repo_repair(cls, project_encodename: str, ver: str, count=0):
        if count == 5:
            raise GitCheckoutError("跳转版本失败")
        repo = git.Repo(cls.base_path + project_encodename)
        try:
            repo.git.checkout(ver)
        except Exception:
            print(f"{project_encodename}跳转版本失败，重试中" + str(count + 1))
            cls.repo_repair(project_encodename, ver, count + 1)

    @classmethod
    def check_clone_status(cls, project_encodename, pre_size=-1, delay=20):
        time.sleep(delay)
        print("检测clone状态ing...")
        exit_code = 0
        size = cls.monitor_size(project_encodename)
        print(f"repo size={str(size)}, pre_size={pre_size}")
        if pre_size == -1:
            if size <= 32 * 1024:
                exit_code = cls.check_clone_status(project_encodename, size, delay=120)
        else:
            if size <= pre_size:
                exit_code = 1
        return exit_code

    @classmethod
    def get_cal_steps(cls, project_encodename):
        """
        保留旧的step记录方式，因为数据库中的step可能可以修改为其他记录方式(exp.最后分析完成日期)
        """
        res = 0
        info = Path(cls.cal_path + project_encodename + '/info.txt')
        if info.exists():
            with open(info, 'r') as file:
                res = int(file.readline())
            return res
        if Path(cls.cal_path + project_encodename + '/TypingTimeLine.csv').exists():
            res = 5
        return res

    @classmethod
    def status_signal(cls, project_encodename, signal, hint: str = ""):
        print("set signal=" + str(signal) + f",{hint}")
        info = Path(cls.cal_path + project_encodename + '/info.txt')
        if signal == -1:
            if info.exists():
                os.remove(info)
            from app.daos.project import DaoProject
            from app.models.modify_project import modify_project
            modify_project(DaoProject().query_project_by_encode_name(project_encodename), {"step": 5})
        else:
            if not Path(cls.cal_path + project_encodename).exists():
                os.mkdir(Path(cls.cal_path + project_encodename))
            with open(info, 'w') as file:
                file.write(str(signal))

    @classmethod
    def monitor_size(cls, project_encodename):
        dir_path = cls.base_path + project_encodename
        size = 0
        if os.path.exists(dir_path):
            for root, dirs, files in os.walk(dir_path):
                size += sum([os.path.getsize(os.path.join(root, name)) for name in files])
        return size

    @classmethod
    def set_running(cls, project_encodename, status: bool):
        running_info = Path(cls.cal_path + project_encodename + '/running.txt')
        if status:
            with open(running_info, 'w') as file:
                file.write("running")
        else:
            if running_info.exists():
                os.remove(running_info)

    @classmethod
    def get_running(cls, project_encodename):
        running_info = Path(cls.cal_path + project_encodename + '/running.txt')
        return running_info.exists()

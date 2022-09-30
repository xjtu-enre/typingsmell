import subprocess
from subprocess import CalledProcessError
from app.models.errors import CommandRunError


class Command:
    @classmethod
    def command_run(cls, command: str):
        try:
            ret = subprocess.run(command, shell=True, check=True, encoding="utf-8")
            return ret.returncode == 0
        except CalledProcessError:
            raise CommandRunError

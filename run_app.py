from sys import platform
from subprocess import call

if platform == "linux" or platform == "linux32":
    call("chmod","+x","run_client.sh")
    call("./run_client.sh")
elif platform == "win32":
    call("run_client.bat")
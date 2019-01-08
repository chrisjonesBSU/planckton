import argparse
import gsd
import hoomd
import hoomd.md
import hoomd.deprecated
import os
import sys

def main():
    parser = argparse.ArgumentParser()
    args, dir_list = parser.parse_known_args()
    if len(dir_list) == 0:
        dir_list = [os.path.abspath(os.path.join("workspace", dir_name)) for dir_name in os.listdir("./workspace")]
    else:
        dir_list = [os.path.abspath(dir_name) for dir_name in dir_list]
    for dir_name in dir_list:
        hoomd.context.initialize()
        dir_name = "".join(dir_name.split("restart.gsd"))
        restart_gsd = os.path.join(dir_name, "restart.gsd")
        system = hoomd.init.read_gsd(filename=restart_gsd)
        hoomd.deprecated.dump.xml(
            group=hoomd.group.all(),
            filename=os.path.join(dir_name, "restart.xml"), all=True
        )


if __name__ == "__main__":
    main()

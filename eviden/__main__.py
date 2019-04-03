import argparse
import sys
from . import core
from getpass import getpass


class Validator:
    NOT_REQUIRED_ARGUMENTS_MESSAGE = "不必要な引数が指定されています！"

    def __init__(self, option):
        self.option = option

    def login_validation(self):
        if len(self.option) > 1:
            print(self.NOT_REQUIRED_ARGUMENTS_MESSAGE)

        try:
            user_id = self.option[0]
        except IndexError:
            sys.exit("ユーザIDが指定されていません\nusage: cli.py login <user_id>")

        return user_id

    def no_args_validation(self):
        if len(self.option) != 0:
            print(self.NOT_REQUIRED_ARGUMENTS_MESSAGE)

    def select_project_validation(self):
        if len(self.option) > 1:
            print(self.NOT_REQUIRED_ARGUMENTS_MESSAGE)

        try:
            name = self.option[0]
        except IndexError:
            sys.exit("プロジェクト名が指定されていません\nusage: cli.py select <project_name>")

        return name

    def post_issue_validation(self):
        if len(self.option) > 2:
            print(self.NOT_REQUIRED_ARGUMENTS_MESSAGE)

        try:
            title, text = self.option[0:2]
        except IndexError:
            sys.exit("タイトルと本文を入力してください\nusage: cli.py post <title> <text>")

        return (title, text)


def main():
    command_parser = argparse.ArgumentParser(add_help=False)
    command_parser.add_argument(
        "command",
        choices=["setup", "reset", "login", "list", "select", "issues", "post"],
        help="実行されるコマンド"
    )

    option_parser = argparse.ArgumentParser(parents=[command_parser])
    option_parser.add_argument("option", nargs="*")

    args = option_parser.parse_args()
    validator = Validator(args.option)

    if args.command in ["setup", "reset", "list", "issues"]:
        validator.no_args_validation()
        if args.command in ["setup", "reset"]:
            core.setup()
        elif args.command == "list":
            core.list_projects()
        else:
            core.list_issues()
    elif args.command == "login":
        user_id = validator.login_validation()
        password = getpass("passwordを入力してください:")
        core.login(user_id, password)
    elif args.command == "select":
        name = validator.select_project_validation()
        core.select_project(name)
    elif args.command == "post":
        title, text = validator.post_issue_validation()
        core.post_issue(title, text)


if __name__ == "__main__":
    main()

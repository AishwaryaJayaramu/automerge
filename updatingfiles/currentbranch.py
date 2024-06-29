import os
import subprocess

def get_current_branch_name():
    result = subprocess.run(['git', 'rev-parse', '--abbrev-ref', 'HEAD'], check=True, stdout=subprocess.PIPE, text=True)

    print(result.stdout.strip())

    if result.stdout.strip() == 'main':
        new_branch_name = input("You are in main, please enter your own branch name: ")
        subprocess.run(['git', 'checkout', new_branch_name])


    return result.stdout.strip()
get_current_branch_name()

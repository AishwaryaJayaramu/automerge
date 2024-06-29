import os

def automate_commit_push(commit_message):
    # Add all changes to the staging area
    os.system('git add .')

    # Commit the changes with the provided commit message
    os.system(f'git commit -m "{commit_message}"')

    # Push the changes to the remote repository
    os.system('git push')


    

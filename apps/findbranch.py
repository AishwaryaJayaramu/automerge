import os
import subprocess

def get_current_branch_name():
    result = subprocess.run(['git', 'rev-parse', '--abbrev-ref', 'HEAD'], check=True, stdout=subprocess.PIPE, text=True)
    return result.stdout.strip()

# def get_branches_containing_file(file_name):
#     result = subprocess.run(['git', 'branch', '--contains', file_name], check=True, stdout=subprocess.PIPE, text=True)
#     branches = [branch.strip() for branch in result.stdout.split('\n') if branch.strip()]
#     return branches



def overwrite_file_in_apps_folder(file_name, new_content, commit_message):
    # Define the directory and file path
    folder_path = 'apps' 
    file_path = os.path.join(folder_path, file_name)

    
    
    # # Create the folder if it doesn't exist
    # os.makedirs(folder_path, exist_ok=True)
    
    # Open the file in write mode, which clears its current content
    with open(file_path, 'w') as file:
        # Write the new content to the file
        file.write(new_content)
    
    # Add the file to the staging area
    subprocess.run(['git', 'add', file_path], check=True)
    
    # Commit the changes
    subprocess.run(['git', 'commit', '-m', commit_message], check=True)
    
    # Get the current branch name
    branch_name = get_current_branch_name()
    print(f"Current branch name: {branch_name}")
    
    # Push the changes to the remote repository
    subprocess.run(['git', 'push', 'origin', branch_name], check=True)
    
    # Find branches containing the file
    branches_containing_file = get_branches_containing_file(file_name)
    print(f"The branches containing the file '{file_name}' are:")
    for branch in branches_containing_file:
        print(branch)

# Example usage
file_name = 'script.txt'
new_content = '''This is the new content. hhhhh
It will replace the old content in the file.'''
commit_message = 'Updated content of example.txt'
overwrite_file_in_apps_folder(file_name, new_content, commit_message)

import os
import subprocess

def overwrite_file(file_name, new_content, commit_message):
    folder_path = 'apps'
    file_path = os.path.join(folder_path, file_name)

    # Open the file in write mode, which clears its current content
    with open(file_path, 'w') as file:
        # Write the new content to the file
        file.write(new_content)

    
    # Add the file to the staging area
    subprocess.run(['git', 'add', file_path ], check=True)
    
    # Commit the changes
    subprocess.run(['git', 'commit', '-m', commit_message], check=True)
    
    # Push the changes to the remote repository
    subprocess.run(['git', 'push'], check=True)

# Example usage
file_path = 'script.txt'
new_content = '''This is the new content.
It will replace the old content in the file.'''
commit_message = 'Automerged commit'
overwrite_file(file_path, new_content, commit_message)
save_location = 'automerge/apps/script2.txt'


def overwrite_files(file_path, new_content):
    # Read the contents of the file
    with open(file_path, 'w') as file:
        
        file.write(new_content)

# Example usage
file_path = 'script.txt'
new_content = 'Hackathon is so fun'
overwrite_files(file_path, new_content)

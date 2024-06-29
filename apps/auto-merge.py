import os
import sys
import argparse
from github import Github
import difflib

# GitHub authentication
github_token = os.getenv('GITHUB_TOKEN')
print(f"Token available: {'Yes' if github_token else 'No'}")
if not github_token:
    print("Error: GITHUB_TOKEN environment variable not set.")
    sys.exit(1)

g = Github(github_token)

def get_file_content(repo, path, ref):
    try:
        content = repo.get_contents(path, ref=ref)
        return content.decoded_content.decode('utf-8')
    except Exception as e:
        print(f"Error fetching content for {path} from {ref}: {str(e)}")
        return None

def get_conflict_content(master_content, pr_content):
    differ = difflib.Differ()
    diff = list(differ.compare(master_content.splitlines(), pr_content.splitlines()))
    conflict_content = []
    in_conflict = False
    for line in diff:
        if line.startswith('- '):
            if not in_conflict:
                conflict_content.append("<<<<<<< HEAD")
                in_conflict = True
            conflict_content.append(line[2:])
        elif line.startswith('+ '):
            if in_conflict:
                conflict_content.append("=======")
                in_conflict = False
            conflict_content.append(line[2:])
        elif line.startswith('  '):
            if in_conflict:
                conflict_content.append("=======")
                conflict_content.append(">>>>>>> PR")
                in_conflict = False
            conflict_content.append(line[2:])
    if in_conflict:
        conflict_content.append("=======")
        conflict_content.append(">>>>>>> PR")
    return '\n'.join(conflict_content)

def get_pr_data(repo_name, pr_number):
    try:
        repo = g.get_repo(repo_name)
        pr = repo.get_pull(pr_number)
        
        pr_data = {
            'title': pr.title,
            'body': pr.body,
            'state': pr.state,
            'created_at': pr.created_at,
            'updated_at': pr.updated_at,
            'base': pr.base.ref,
            'head': pr.head.ref,
            'user': pr.user.login,
        }
        
        files_changed = list(pr.get_files())
        pr_data['files_changed'] = [file.filename for file in files_changed]
        
        file_contents = {}
        conflicting_files = []
        for file in files_changed:
            master_content = get_file_content(repo, file.filename, pr.base.ref)
            pr_content = get_file_content(repo, file.filename, pr.head.ref)
            file_contents[file.filename] = {
                'master_content': master_content,
                'pr_content': pr_content
            }
            if master_content != pr_content:
                conflicting_files.append(file.filename)
                file_contents[file.filename]['conflict_content'] = get_conflict_content(master_content, pr_content)
        
        pr_data['file_contents'] = file_contents
        pr_data['conflicting_files'] = conflicting_files
        
        return pr_data
    
    except Exception as e:
        print(f"An error occurred: {str(e)}")
        return None

def main():
    parser = argparse.ArgumentParser(description="Fetch GitHub PR data")
    parser.add_argument("repo", help="Repository name in the format 'owner/repo'")
    parser.add_argument("pr_number", type=int, help="Pull Request number")
    args = parser.parse_args()

    pr_data = get_pr_data(args.repo, args.pr_number)
    if pr_data:
        print(f"PR Data for {args.repo} #{args.pr_number}:")
        for key, value in pr_data.items():
            if key not in ['file_contents', 'conflicting_files']:
                print(f"{key}: {value}")
        
        print("\nConflicting files:")
        print(pr_data['conflicting_files'])
        
        print("\nFile contents:")
        for filename, contents in pr_data['file_contents'].items():
            print(f"\n{filename}:")
            if filename in pr_data['conflicting_files']:
                print("Conflict content:")
                print(contents['conflict_content'])
            else:
                print("Master branch content:")
                print(contents['master_content'][:500] + "..." if contents['master_content'] and len(contents['master_content']) > 500 else contents['master_content'])
                print("\nPR branch content:")
                print(contents['pr_content'][:500] + "..." if contents['pr_content'] and len(contents['pr_content']) > 500 else contents['pr_content'])
    else:
        print(f"Failed to fetch PR data for {args.repo} #{args.pr_number}")

if __name__ == "__main__":
    main()
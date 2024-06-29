import os
import sys
import argparse
from github import Github
import json

def get_pr_data(repo_name, pr_number):
    github_token = os.getenv('GITHUB_TOKEN')
    if not github_token:
        print("Error: GITHUB_TOKEN environment variable not set.")
        sys.exit(1)

    g = Github(github_token)

    try:
        repo = g.get_repo(repo_name)
        pr = repo.get_pull(pr_number)
        print(pr_number)
        pr_data = {
            'title': pr.title,
            'body': pr.body,
            'state': pr.state,
            # 'created_at': pr.created_at,
            # 'updated_at': pr.updated_at,
            'base': pr.base.ref,
            'head': pr.head.ref,
            'user': pr.user.login,
        }
        
        files_changed = list(pr.get_files())
        pr_data['files_changed'] = [file.filename for file in files_changed]
        
        file_contents = {}
        for file in files_changed:
            if file.status == 'added':
                master_content = None
                pr_content = file.patch
            elif file.status == 'removed':
                master_content = repo.get_contents(file.filename, ref=pr.base.ref).decoded_content.decode('utf-8')
                pr_content = None
            else:
                master_content = repo.get_contents(file.filename, ref=pr.base.ref).decoded_content.decode('utf-8')
                pr_content = repo.get_contents(file.filename, ref=pr.head.sha).decoded_content.decode('utf-8')
            
            file_contents[file.filename] = {
                'status': file.status,
                'master_content': master_content,
                'pr_content': pr_content,
                'patch': file.patch
            }
        
        pr_data['file_contents'] = file_contents
        
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
        output_data = {
            "conflicting_files": [],
            "master_files": [],
            "pr_files": [],
            "added_files": [],
            "deleted_files": []
        }

        for filename, contents in pr_data['file_contents'].items():
            file_path = f"/{args.repo}/blob/main/{filename}"  # Assuming main branch
            
            if contents['status'] == 'modified':
                if contents['master_content'] != contents['pr_content']:
                    output_data["conflicting_files"].append({
                        "path": file_path,
                        "content": contents['patch']
                    })
                output_data["master_files"].append({
                    "path": file_path,
                    "content": contents['master_content']
                })
                output_data["pr_files"].append({
                    "path": file_path,
                    "content": contents['pr_content']
                })
            elif contents['status'] == 'added':
                output_data["added_files"].append({
                    "path": file_path,
                    "content": contents['patch']
                })
                output_data["pr_files"].append({
                    "path": file_path,
                    "content": contents['pr_content']
                })
            elif contents['status'] == 'removed':
                output_data["deleted_files"].append({
                    "path": file_path,
                    "content": contents['master_content']
                })
                output_data["master_files"].append({
                    "path": file_path,
                    "content": contents['master_content']
                })

        # Print the JSON data
        print(json.dumps(output_data, indent=2))

        # Return the JSON data
        return json.dumps(output_data)
    else:
        print(f"Failed to fetch PR data for {args.repo} #{args.pr_number}")
        return None

if __name__ == "__main__":
    main()
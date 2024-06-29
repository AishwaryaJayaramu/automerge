import os
import sys
import json
import argparse
from github import Github, InputGitTreeElement

def update_pr(repo_name, pr_number, llm_output):
    github_token = os.environ.get('GITHUB_TOKEN')
    if not github_token:
        print("Error: GITHUB_TOKEN environment variable not set.")
        sys.exit(1)

    g = Github(github_token)
    print(f"Authenticated as {g.get_user().login}")

    try:
        repo = g.get_repo(repo_name)
        print(f"Repository: {repo.full_name}")

        pr = repo.get_pull(pr_number)
        print(f"Pull Request: #{pr_number}")

        branch = pr.head.ref
        print(f"Branch: {branch}")

        # Parse LLM output
        llm_data = json.loads(llm_output)

        # Create blobs for each file
        blobs = []
        for file in llm_data['files']:
            blob = repo.create_git_blob(file['content'], 'utf-8')
            blobs.append((file['path_to_file'], blob))
            print(f"Created blob for {file['path_to_file']}")

        # Create a new tree with our blobs
        base_tree = repo.get_branch(branch).commit.tree
        tree_elements = [
            InputGitTreeElement(
                path=path,
                mode="100644",
                type="blob",
                sha=blob.sha
            ) for path, blob in blobs
        ]
        new_tree = repo.create_git_tree(tree_elements, base_tree)
        print(f"Created new tree: {new_tree.sha}")

        # Create a new commit
        base_commit = repo.get_branch(branch).commit
        commit = repo.create_git_commit(
            message="Auto-merge: Apply LLM suggestions",
            tree=new_tree,
            parents=[base_commit]
        )
        print(f"Created new commit: {commit.sha}")

        # Update the branch reference
        ref = repo.get_git_ref(f"heads/{branch}")
        ref.edit(sha=commit.sha)
        print(f"Updated branch {branch} to point to new commit")

        print("Successfully updated the pull request with LLM suggestions.")

    except Exception as e:
        print(f"An error occurred: {str(e)}")
        sys.exit(1)

def main():
    parser = argparse.ArgumentParser(description="Update GitHub PR with LLM suggestions")
    parser.add_argument("repo", help="Repository name in the format 'owner/repo'")
    parser.add_argument("pr_number", type=int, help="Pull Request number")
    parser.add_argument("llm_output", help="LLM output in JSON format")
    args = parser.parse_args()

    update_pr(args.repo, args.pr_number, args.llm_output)

if __name__ == "__main__":
    main()
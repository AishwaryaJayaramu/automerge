import os
import sys
import json
import argparse
import traceback
from github import Github, InputGitTreeElement, GithubException
from dotenv import load_dotenv
load_dotenv()

def log_error(message):
    print(f"ERROR: {message}", file=sys.stderr)

def log_debug(message):
    print(f"DEBUG: {message}")

def get_file_content(repo, path, ref):
    try:
        content = repo.get_contents(path, ref=ref)
        return content.decoded_content.decode('utf-8')
    except:
        return None

def update_pr(repo_name, pr_number, llm_output):
    github_token = os.environ.get('GITHUB_TOKEN')
    if not github_token:
        log_error("GITHUB_TOKEN environment variable not set.")
        sys.exit(1)

    g = Github(github_token)
    log_debug(f"Authenticated as {g.get_user().login}")

    try:
        repo = g.get_repo(repo_name)
        log_debug(f"Repository: {repo.full_name}")

        pr = repo.get_pull(pr_number)
        log_debug(f"Pull Request: #{pr_number}")

        base_branch = pr.base.ref
        head_branch = pr.head.ref
        log_debug(f"Base branch: {base_branch}, Head branch: {head_branch}")

        # Get the latest commit on the base branch (usually master)
        base_commit = repo.get_branch(base_branch).commit
        log_debug(f"Latest commit on {base_branch}: {base_commit.sha}")

        # Get the commits in the PR
        pr_commits = list(pr.get_commits())
        log_debug(f"Number of commits in PR: {len(pr_commits)}")

        # Parse LLM output
        llm_data = json.loads(llm_output)

        # Rebase PR commits on top of the latest base commit
        new_base_tree = repo.get_git_tree(base_commit.sha)
        current_tree = new_base_tree
        new_commits = []
        for commit in pr_commits:
            # Recreate each commit on top of the new base
            commit_tree = repo.get_git_tree(commit.sha)
            new_tree_elements = [
                InputGitTreeElement(
                    path=element.path,
                    mode=element.mode,
                    type=element.type,
                    sha=element.sha
                )
                for element in commit_tree.tree
            ]
            new_tree = repo.create_git_tree(new_tree_elements, base_tree=current_tree)
            parent_commit = repo.get_git_commit(new_commits[-1].sha if new_commits else base_commit.sha)
            new_commit = repo.create_git_commit(
                message=commit.commit.message,
                tree=new_tree,
                parents=[parent_commit]
            )
            new_commits.append(new_commit)
            current_tree = new_tree
            log_debug(f"Rebased commit: {commit.sha} -> {new_commit.sha}")

        # Apply LLM changes
        new_tree_elements = []
        for file in llm_data.get('files', []):
            file_path = file['path_to_file']
            llm_content = file['content']
            current_content = get_file_content(repo, file_path, new_commits[-1].sha)
            
            if llm_content != current_content:
                blob = repo.create_git_blob(llm_content, 'utf-8')
                new_tree_elements.append(InputGitTreeElement(
                    path=file_path,
                    mode="100644",
                    type="blob",
                    sha=blob.sha
                ))
                log_debug(f"Applied LLM changes to {file_path}")
            else:
                log_debug(f"No changes needed for {file_path}")

        if new_tree_elements:
            final_tree = repo.create_git_tree(new_tree_elements, base_tree=current_tree)
            parent_commit = repo.get_git_commit(new_commits[-1].sha)
            final_commit = repo.create_git_commit(
                message="Apply LLM suggestions for conflict resolution",
                tree=final_tree,
                parents=[parent_commit]
            )
            log_debug(f"Created final commit with LLM changes: {final_commit.sha}")
        else:
            final_commit = new_commits[-1]
            log_debug("No LLM changes to apply")

        # Update the PR branch
        head_ref = repo.get_git_ref(f"heads/{head_branch}")
        head_ref.edit(sha=final_commit.sha, force=True)
        log_debug(f"Updated branch {head_branch} to point to final commit")

        log_debug("Successfully rebased PR and applied LLM suggestions.")

    except Exception as e:
        log_error(f"An unexpected error occurred: {str(e)}")
        log_error(traceback.format_exc())
        sys.exit(1)

def main():
    parser = argparse.ArgumentParser(description="Rebase GitHub PR and apply LLM suggestions")
    parser.add_argument("repo", help="Repository name in the format 'owner/repo'")
    parser.add_argument("pr_number", type=int, help="Pull Request number")
    parser.add_argument("llm_output", help="LLM output in JSON format")
    args = parser.parse_args()

    update_pr(args.repo, args.pr_number, args.llm_output)

if __name__ == "__main__":
    main()
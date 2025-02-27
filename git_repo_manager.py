#!/usr/bin/env python3
import os
import subprocess
import argparse
import sys

# Global GitHub URL variables
mainGitHubURL = "https://github.com/SE1020-IT2070-OOP-DSA-25/project-Bashitha-Weerapperuma.git"
subGitHubURL = "https://github.com/Bashitha-Weerapperuma/AF-SE1020-Production.git"


def run_command(command, cwd=None):
    """Run a shell command and return the output."""
    try:
        result = subprocess.run(
            command,
            shell=True,
            check=True,
            text=True,
            capture_output=True,
            cwd=cwd
        )
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        print(f"Error executing command: {command}")
        print(f"Error message: {e.stderr}")
        sys.exit(1)


def setup_repositories(main_repo_url, sub_repo_url, main_repo_dir="main_repo", sub_repo_dir="sub_repo"):
    """Clone/setup both repositories."""
    # Create directories if they don't exist
    os.makedirs(main_repo_dir, exist_ok=True)
    os.makedirs(sub_repo_dir, exist_ok=True)

    # Use global URLs if no URLs are provided
    if not main_repo_url and mainGitHubURL:
        main_repo_url = mainGitHubURL
        print(f"Using main repository URL from global variable: {main_repo_url}")

    if not sub_repo_url and subGitHubURL:
        sub_repo_url = subGitHubURL
        print(f"Using sub repository URL from global variable: {sub_repo_url}")

    # Clone or initialize main repository
    if os.path.exists(os.path.join(main_repo_dir, ".git")):
        print(f"Main repository already exists in {main_repo_dir}")
    else:
        if main_repo_url:
            print(f"Cloning main repository from {main_repo_url}...")
            run_command(f"git clone {main_repo_url} {main_repo_dir}")
        else:
            print(f"Initializing new main repository in {main_repo_dir}...")
            run_command(f"git init", cwd=main_repo_dir)

    # Clone sub repository
    if os.path.exists(os.path.join(sub_repo_dir, ".git")):
        print(f"Sub repository already exists in {sub_repo_dir}")
    else:
        if sub_repo_url:
            print(f"Cloning sub repository from {sub_repo_url}...")
            run_command(f"git clone {sub_repo_url} {sub_repo_dir}")
        else:
            print("Error: No sub repository URL provided")
            sys.exit(1)

    return main_repo_dir, sub_repo_dir


def add_sub_repo_as_remote(main_repo_dir, sub_repo_dir, remote_name="subrepo"):
    """Add the sub repo as a remote to the main repo."""
    # Get absolute path to sub repo
    sub_repo_abs_path = os.path.abspath(sub_repo_dir)

    # Check if remote already exists
    remotes = run_command("git remote", cwd=main_repo_dir)
    if remote_name in remotes.split():
        print(f"Remote '{remote_name}' already exists, updating URL...")
        run_command(f"git remote set-url {remote_name} {sub_repo_abs_path}", cwd=main_repo_dir)
    else:
        print(f"Adding sub repository as remote '{remote_name}'...")
        run_command(f"git remote add {remote_name} {sub_repo_abs_path}", cwd=main_repo_dir)


def commit_changes(repo_dir, message="Update from script"):
    """Commit changes in the repository."""
    print(f"Committing changes in {repo_dir}...")
    run_command("git add .", cwd=repo_dir)
    result = run_command(f"git commit -m '{message}'", cwd=repo_dir)
    print(result)
    return result


def push_to_repo(source_dir, remote="origin", branch="main"):
    """Push changes to a repository."""
    print(f"Pushing changes from {source_dir} to {remote}/{branch}...")
    result = run_command(f"git push {remote} {branch}", cwd=source_dir)
    print(result)
    return result


def pull_from_repo(target_dir, remote="origin", branch="main"):
    """Pull changes from a repository."""
    print(f"Pulling changes into {target_dir} from {remote}/{branch}...")
    result = run_command(f"git pull {remote} {branch}", cwd=target_dir)
    print(result)
    return result


def merge_branches(repo_dir, source_branch, target_branch="main"):
    """Merge branches in a repository."""
    print(f"Merging {source_branch} into {target_branch} in {repo_dir}...")
    run_command(f"git checkout {target_branch}", cwd=repo_dir)
    result = run_command(f"git merge {source_branch}", cwd=repo_dir)
    print(result)
    return result


def sync_repos(main_repo_dir, sub_repo_dir, remote_name="subrepo", branch="main"):
    """Sync changes from main repo to sub repo."""
    # Push changes from main repo to sub repo
    push_to_repo(main_repo_dir, remote_name, branch)

    # Pull changes into sub repo
    run_command(f"git checkout {branch}", cwd=sub_repo_dir)
    pull_from_repo(sub_repo_dir)


def main():
    parser = argparse.ArgumentParser(description="Manage Git repositories and sync between them")
    parser.add_argument("--main-repo", help="URL of the main repository (overrides global variable)")
    parser.add_argument("--sub-repo", help="URL of the sub repository to clone/duplicate (overrides global variable)")
    parser.add_argument("--action", choices=["setup", "commit", "push", "pull", "merge", "sync"],
                        default="setup", help="Action to perform")
    parser.add_argument("--message", default="Update from script", help="Commit message")
    parser.add_argument("--branch", default="main", help="Branch name to work with")
    parser.add_argument("--source-branch", help="Source branch for merge operation")
    parser.add_argument("--main-dir", default="main_repo", help="Directory for main repository")
    parser.add_argument("--sub-dir", default="sub_repo", help="Directory for sub repository")

    args = parser.parse_args()

    # Use command line arguments if provided, otherwise use global variables
    main_repo = args.main_repo if args.main_repo else mainGitHubURL
    sub_repo = args.sub_repo if args.sub_repo else subGitHubURL

    if args.action == "setup":
        if not sub_repo:
            print(
                "Error: No sub repository URL provided. Please either set the global subGitHubURL or provide --sub-repo")
            sys.exit(1)

        main_repo_dir, sub_repo_dir = setup_repositories(main_repo, sub_repo, args.main_dir, args.sub_dir)
        add_sub_repo_as_remote(main_repo_dir, sub_repo_dir)
        print("Repositories setup complete!")

    elif args.action == "commit":
        commit_changes(args.main_dir, args.message)

    elif args.action == "push":
        push_to_repo(args.main_dir, "subrepo", args.branch)

    elif args.action == "pull":
        pull_from_repo(args.main_dir, "origin", args.branch)

    elif args.action == "merge":
        if not args.source_branch:
            print("Error: --source-branch is required for merge operation")
            sys.exit(1)
        merge_branches(args.main_dir, args.source_branch, args.branch)

    elif args.action == "sync":
        sync_repos(args.main_dir, args.sub_dir, "subrepo", args.branch)


if __name__ == "__main__":
    main()
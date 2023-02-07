import click
from plumbum import local, ProcessExecutionError
from typing import List

git = local['git']
grep = local['grep']


@click.group()
def cli():
    """ A simple python script to delete unwanted branches from a remote repository """


@cli.command()
@click.option('--branch-to-keep', multiple=True, required=False)
@click.option('--confirm', default=False)
def delete_branches(branch_to_keep, confirm):
    """ delete all branches except these:\n
     - current branch\n
     - main branch\n
     - branches given as parameters with --branch-to-keep\n
     param --confirm: confirm deletion """
    if branch_to_keep:
        # <branch-to-keep> is a tuple
        for branch in branch_to_keep:
            other_branches = (git['branch'] | grep['-v', branch])()
    else:
        other_branches = (git['branch'] | grep['-v', 'main'])()
    if confirm:
        other_branches = other_branches.split()
        # dont delete current branch
        if '*' in other_branches:
            other_branches.remove('*')
        for branch in other_branches:
            print(f'deleting branch {branch} from local and remote')
            try:
                git('branch', '-D', branch)
                git('push', 'origin', '-d', branch)
            except ProcessExecutionError as e:
                if 'remote ref does not exist' in e.stderr:
                    print(f'branch {branch} doesnt exist on remote')
                elif 'refusing to delete the current branch' in e.stderr:
                    print(
                        f'github refuses to delete branch {branch}. maybe you tried to delete a protected/default branch?')
                else:
                    raise

    else:
        print(
            f'about to delete {other_branches}, not actually deleting anything. pass in --confirm=True to actually delete')


if __name__ == '__main__':
    cli()

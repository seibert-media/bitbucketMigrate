#!/usr/bin/env python3
"""
bitucketMigrate for mirroring projects from source to target system
"""

import configparser
import requests
import git, os, shutil


def get_projects(system, auth):
    """
    This returns an array of projects
    """
    req = requests.get("{}/projects".format(system),
                       auth=auth, verify=SSL_VERIFY)
    result = req.json()
    return result['values']


def get_project(system, auth, project):
    """
    This returns a single project
    """
    req = requests.get("{}/projects/{}".format(system, project.get('key')),
                       auth=auth, verify=SSL_VERIFY)
    result = req.json()
    if req.status_code == 200:
        return result


def add_project(system, auth, project):
    """
    This creates the passed in project in system
    """
    print('Creating Project {}'.format(project))
    if get_project(system, auth, project):
        print("Project {} exists, skipping creation")
        return 1
    payload = {'key': project.get('key'), 'name': project.get('name'),
               'description': project.get('description')}
    req = requests.post("{}/projects".format(system),
                        auth=auth, verify=SSL_VERIFY, json=payload)
    result = req.json()
    return result


def get_project_groups(system, auth, project):
    """
    This returns an array of groups and permissions for project
    """
    req = requests.get("{}/projects/{}/permissions/groups".format(system, project.get('key')),
                       auth=auth, verify=SSL_VERIFY)
    result = req.json()
    return result['values']


def add_project_group(system, auth, project, group):
    """
    This adds the passed in group permissions to project in system
    """
    print('Add Group Permission {} for {} in {}'.format(group.get('permission'),
                                                        group.get('group').get(
                                                            'name'),
                                                        project.get('key')))
    payload = {'name': group.get('group').get(
        'name'), 'permission': group.get('permission')}
    req = requests.put("{}/projects/{}/permissions/groups".format(system, project.get('key')),
                       auth=auth, verify=SSL_VERIFY, params=payload)
    return req.status_code


def get_project_users(system, auth, project):
    """
    This returns an array of users and permissions for project
    """
    req = requests.get("{}/projects/{}/permissions/users".format(system, project.get('key')),
                       auth=auth, verify=SSL_VERIFY)
    result = req.json()
    return result['values']


def add_project_user(system, auth, project, user):
    """
    This adds the passed in user permissions to project in system
    """
    print('Add User Permission {} for {} in {}'.format(user.get('permission'),
                                                       user.get('user').get(
                                                           'name'),
                                                       project.get('key')))
    payload = {'name': user.get('user').get(
        'name'), 'permission': user.get('permission')}
    req = requests.put("{}/projects/{}/permissions/users".format(system, project.get('key')),
                       auth=auth, verify=SSL_VERIFY, params=payload)
    return req.status_code


def get_project_repos(system, auth, project):
    """
    This returns an array of repos for project
    """
    req = requests.get("{}/projects/{}/repos".format(system, project.get('key')),
                       auth=auth, verify=SSL_VERIFY)
    result = []
    for repo in req.json()['values']:
        groups = get_project_repo_groups(system, auth, repo)
        users = get_project_repo_users(system, auth, repo)
        rep = {'repo': repo, 'permissions': {'groups': groups, 'users': users}}
        result.append(rep)
    return result

def get_project_repo(system, auth, project, slug):
    """
    This returns the repo in project with slug
    """
    req = requests.get("{}/projects/{}/repos/{}".format(system, project.get('key'), slug),
                       auth=auth, verify=SSL_VERIFY)
    result = req.json()
    return result


def add_project_repo(system, auth, repo):
    """
    This adds the passed in repo to ts project
    """
    print('Add Repo {} in {}'.format(repo.get('slug'),
                                     repo.get('project').get('key')))
    payload = {'name': repo.get('name'), 'scmId': repo.get(
        'scmId'), 'forkable': repo.get('forkable')}
    req = requests.post("{}/projects/{}/repos".format(system, repo.get('project').get('key')),
                        auth=auth, verify=SSL_VERIFY, json=payload)
    return req.status_code


def get_project_repo_groups(system, auth, repo):
    """
    This returns an array of groups and permissions for repo
    """
    req = requests.get("{}/projects/{}/repos/{}/permissions/groups"
                       .format(system, repo['project']['key'], repo['slug']),
                       auth=auth, verify=SSL_VERIFY)
    result = req.json()
    return result


def add_project_repo_group(system, auth, repo, group):
    """
    This adds the passed in group permissions to repo in system
    """
    print('Add Group Permission {} for Repo {} in {}'
          .format(group.get('permission'), group.get('group').get('name'), repo.get('slug')))
    payload = {'name': group.get('group').get(
        'name'), 'permission': group.get('permission')}
    req = requests.put("{}/projects/{}/repos/{}/permissions/groups"
                       .format(system, repo.get('project').get('key'), repo.get('slug')),
                       auth=auth, verify=SSL_VERIFY, params=payload)
    return req.status_code


def get_project_repo_users(system, auth, repo):
    """
    This returns an array of users and permissions for repo
    """
    req = requests.get("{}/projects/{}/repos/{}/permissions/users"
                       .format(system, repo['project']['key'], repo['slug']),
                       auth=auth, verify=SSL_VERIFY)
    result = req.json()
    return result


def add_project_repo_user(system, auth, repo, user):
    """
    This adds the passed in user permissions to repo in system
    """
    print('Add User Permission {} for Repo {} in {}'
          .format(user.get('permission'), user.get('user').get('name'), repo.get('slug')))
    payload = {'name': user.get('user').get(
        'name'), 'permission': user.get('permission')}
    req = requests.put("{}/projects/{}/repos/{}/permissions/users"
                       .format(system, repo.get('project').get('key'), repo.get('slug')),
                       auth=auth, verify=SSL_VERIFY, params=payload)
    return req.status_code


def clone_project(target, auth, project, details):
    """
    This creates an exact mirror of project with the passed in repos, groups and users
    """
    print(add_project(target, auth, project))
    for group in details.get('groups'):
        add_project_group(target, auth, project, group)
    for user in details.get('users'):
        add_project_user(target, auth, project, user)

    for repo in details.get('repos'):
        rgroups = repo['permissions']['groups']['values']
        rusers = repo['permissions']['users']['values']
        rep = repo['repo']
        add_project_repo(target, auth, rep)
        for rgroup in rgroups:
            add_project_repo_group(target, auth, rep, rgroup)
        for ruser in rusers:
            add_project_repo_user(target, auth, rep, ruser)
        trep = get_project_repo(target, auth, project, rep['slug'])
        clone_repo_source(rep, trep)


def clone_repo_source(repo, target_repo):
    """
    This gets all brnaches and tags from the source remote and pushes to target_url
    """
    print('Migrating Source for Repo', repo['name'])
    dir_name = 'temp/{}/{}'.format(repo['project']['key'], repo['slug'])
    for link in repo.get('links').get('clone'):
        if link.get('name') == 'http':
            remote_url = link.get('href')

    for tlink in target_repo.get('links').get('clone'):
        if tlink.get('name') == 'http':
            target_url = tlink.get('href')

    if os.path.isdir(dir_name):
        shutil.rmtree(dir_name)

    os.makedirs(dir_name)

    repo = git.Repo.init(dir_name)
    origin = repo.create_remote('origin', remote_url)
    origin.fetch()
    for branch in repo.remotes.origin.fetch():
        print('Checking out Branch ', branch.name[7:])
        repo.git.checkout(branch.name[7:])
    origin.set_url(target_url)
    print('Pushing to new Remote')
    origin.push(all=True)
    origin.push(tags=True)


def main():
    """
    Main Function currently only doing exact mirroring from source to target
    """
    print('Preparing Migration')
    print('Source System: {}'.format(SOURCE_API))
    print('Target System: {}'.format(TARGET_API))


    for project in get_projects(SOURCE_API, SOURCE_AUTH):
        print('Mirroring Project {}'.format(project.get('name')))
        groups = get_project_groups(SOURCE_API, SOURCE_AUTH, project)
        users = get_project_users(SOURCE_API, SOURCE_AUTH, project)
        repos = get_project_repos(SOURCE_API, SOURCE_AUTH, project)
        clone_project(TARGET_API, TARGET_AUTH, project,
                      {'groups': groups,
                       'users': users,
                       'repos': repos})

if __name__ == '__main__':
    CONFIG = configparser.ConfigParser()
    CONFIG.read('migrate.cfg')

    SOURCE_API = "{}/rest/api/1.0".format(CONFIG.get('source', 'url'))
    SOURCE_AUTH = (CONFIG.get('source', 'user'),
                   CONFIG.get('source', 'password'))

    TARGET_API = "{}/rest/api/1.0".format(CONFIG.get('target', 'url'))
    TARGET_AUTH = (CONFIG.get('target', 'user'),
                   CONFIG.get('target', 'password'))

    SSL_VERIFY = True
    if not CONFIG.getboolean('general', 'ssl'):
        requests.packages.urllib3.disable_warnings()
        SSL_VERIFY = False

    main()

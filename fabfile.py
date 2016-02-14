import colorama
import os
import shutil
import sys
import json
import requests
from ConfigParser import ConfigParser
from tempfile import mkdtemp
from fabric.api import env, local
from fabric.context_managers import lcd


def new_config(filename='migrate.cfg'):
    config = ConfigParser()
    config.add_section('github')
    config.add_section('gogs')
    config.set('github', 'username', '')
    config.set('github', 'token', '')
    config.set('gogs', 'url', '')
    config.set('gogs', 'api-url', '')
    config.set('gogs', 'username', '')
    config.set('gogs', 'token', '')
    config.write(open(filename, 'w'))
    

def migrate(filename='migrate.cfg'):
    # env
    env.use_ssh_config = True
    env.forward_agent = True

    # load
    config = ConfigParser()
    config.readfp(open(filename))
    GITHUB_API = 'https://api.github.com/user/repos'
    GITHUB_USER = config.get('github', 'username')
    GITHUB_TOKEN = config.get('github', 'token')
    GOGS_API = config.get('gogs', 'api-url')
    GOGS_URL = config.get('gogs', 'url')
    GOGS_USER = config.get('gogs', 'username')
    GOGS_TOKEN = config.get('gogs', 'token')

    # get all github repositories that you own
    r = requests.get(
        GITHUB_API,
        auth=(GITHUB_USER, GITHUB_TOKEN),
        params={
            'affiliation': 'owner'
        }
    )
    github_repos = []
    if r.ok:
        repos_json = json.loads(r.content)
        len(repos_json)
        for repo in repos_json:
            github_repos.append({
                'name': repo['name'],
                'description': repo['description'],
                'private': repo['private'],
                'url': repo['clone_url']
            })

    # clone github repos, create new repo on gogs, then push to gogs
    tempdir = mkdtemp()
    added = 0
    with lcd(tempdir):
        for repo in github_repos:
            # create repo at gogs
            resp = requests.post(
                GOGS_API + 'user/repos',
                headers={
                    'Authorization': 'token {}'.format(GOGS_TOKEN)
                },
                data={
                    'name': repo['name'],
                    'private': repo['private'],
                    'description': repo['description']
                },
                verify=False
            )
            resp_json = json.loads(resp.content)
            if 'ssh_url' not in resp_json.keys():
                print 'Already exists, going to try pushing anyway.'
            ssh_url = GOGS_URL + '{}/{}'.format(GOGS_USER, repo['name'])
            
            # clone locally
            local('git clone {} {}'.format(repo['url'], repo['name']))
            with lcd(os.path.join(tempdir, repo['name'])):
                local('git remote add gogs {}'.format(ssh_url))
                local('git push --all gogs')
                added += 1

            # remove directory
            shutil.rmtree(os.path.join(tempdir, repo['name']))

    print 'Added {} repositories'.format(added)

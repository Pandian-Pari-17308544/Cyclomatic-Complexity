himport socket
import select
import argparse
from flask import Flask, url_for

from flask import request
from flask import Response
from flask import json
from flask import jsonify
import os
from git import Repo

app = Flask(__name__)


# list of tasks
task_list = ['task1', 'task2', 'task3', 'task4', 'task5']



@app.route('/', methods=['GET'])
def get():

    if len(cc_manager.commits) == 0:
        commit_number = 'Done'
    else:
        commit = cc_manager.commits.pop(0)
        commit_number = commit.hexsha
        print("new length of commit_numbers = ", len(cc_manager.commits))

    data = {
        'commit_number': commit_number,
    }

    resp = jsonify(data)
    resp.status_code = 200
    return resp


@app.route('/', methods=['POST'])
def post():

    if request.headers['CONTENT_TYPE'] == 'application/json':

        data = request.json

        print("worker id: ", data['worker_id'])
        print("worker cc: ", data['cc'])

        # add cc result to manager
        cc_manager.add_cc(data['commit_number'], int(data['cc']))

        return "JSON Message: " + json.dumps(request.json)
    else:
        raise NotImplementedError

class CodeComplexityMaster:

    def __init__(self):

        print("Initialising Master...")

        # GIT repository settings
        self.git_repository = "https://github.com/lisa-lab/pylearn2"
        self.root_repo_dir = "./repo"
        self.commits = []

        self.cc_per_commit = {}
        self.repo = None

    def setup_gitrepo(self):

        repo_dir = self.root_repo_dir
        if not os.path.exists(repo_dir):
            os.makedirs(repo_dir)

        if not os.listdir(repo_dir):
            print('cloning repository into directory: {0}'.format(repo_dir))
            Repo.clone_from(self.git_repository, repo_dir)
            print('cloning finished')

        self.repo = Repo(repo_dir)
        assert not self.repo.bare

        self.commits = list(self.repo.iter_commits('master'))
        # self.cc_per_commit = {commit: None for commit in self.commits}
        self.cc_per_commit = {}

        print("Repository setup complete")

    def add_cc(self, commit_number, cc):

        cc_manager.cc_per_commit[commit_number] = cc

        if len(cc_manager.commits) == 0:
            print("COMPLETE, total CC = ", sum(self.cc_per_commit.values()))

        # # check if all commits have returned
        # complete = True
        # for cc in self.cc_per_commit.values():
        #     if cc is None:
        #         complete = False
        #         return
        #
        # # complete is True
        # print("COMPLETE, total CC = ", sum(self.cc_per_commit.values()))


if __name__ == '__main__':

    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--host',
        type=str,
        default='127.0.0.1',
        help='host ip of server.'
    )
    parser.add_argument(
        '--port',
        type=int,
        default=8000,
        help='port of server.'
    )

    FLAGS, unparsed = parser.parse_known_args()

    # global cc_manager
    cc_manager = CodeComplexityMaster()
    cc_manager.setup_gitrepo()

    # run application with set flags
    app.run(host=FLAGS.host, port=FLAGS.port)

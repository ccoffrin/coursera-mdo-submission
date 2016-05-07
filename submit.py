#!/usr/bin/python
# -*- coding: utf-8 -*-

# Python 2/3 compatibility 
from __future__ import print_function

# Python 2:
try:
    from urlparse import urlparse
    from urllib import urlencode
    from urllib2 import urlopen, Request, HTTPError
except:
    pass

# Python 3:
try:
    from urllib.parse import urlparse, urlencode
    from urllib.request import urlopen, Request
    from urllib.error import HTTPError
except:
    pass

import sys
# Python 2:
if sys.version_info < (3, 0):
    def input(str):
        return raw_input(str)


# Start of core script

import json
import time
import os.path
from subprocess import Popen, PIPE
from collections import namedtuple

process_id = os.getpid()

version = '1.0.0'
submitt_url = 'https://www.coursera.org/api/onDemandProgrammingScriptSubmissions.v1'

minizinc_cmd = 'mzn-gecode'

Metadata = namedtuple('Metadata', ['assignment_key', 'name', 'problem_data', 'model_data'])
Problem = namedtuple('Problem', ['sid', 'model_file', 'input_file', 'runtime', 'name'])
Model = namedtuple('Model', ['sid', 'model_file', 'name'])

mzn_solution = '----------'



def load_metadata(metadata_file_name = '_coursera'):
    if not os.path.exists(metadata_file_name):
        print('metadata file "%s" not found' % metadata_file_name)
        quit()

    try:
        metadata_file = open(metadata_file_name, 'r')

        key = metadata_file.readline().strip()
        name = metadata_file.readline().strip()
        problem_count = int(metadata_file.readline().strip())
        problem_data = []
        for i in range(0,problem_count):
            line = metadata_file.readline().strip()
            line_parts = line.split(',')
            line_parts = [x.strip() for x in line_parts]
            assert(len(line_parts) == 5)
            line_parts[3] = int(line_parts[3])
            problem_data.append(Problem(*line_parts))
        model_count = int(metadata_file.readline().strip())
        model_data = []
        for i in range(0,model_count):
            line = metadata_file.readline().strip()
            line_parts = line.split(',')
            line_parts = [x.strip() for x in line_parts]
            assert(len(line_parts) == 3)
            model_data.append(Model(*line_parts))
        metadata_file.close()
    except Exception as e:
        print('problem parsing assignment metadata file')
        print('exception message:')
        print(e)
        quit()

    return Metadata(key, name, problem_data, model_data)


def part_prompt(name, problems, models):
    count = 1;
    print('Hello! These are the assignment parts that you can submit:')
    for i, problem in enumerate(problems):
        print(str(count) + ') ' + problem.name)
        count += 1
    for i, model in enumerate(models):
        print(str(count) + ') ' + model.name)
        count += 1
    print('0) All')

    part_text = input('Please enter which part(s) you want to submit (0-'+ str(count) + '): ')
    selected_problems = []
    selected_models = []

    for item in part_text.split(','):
        try:
            i = int(item)
        except:
            print('Skipping input "' + item + '".  It is not an integer.')
            continue

        if i >= count or i < 0:
            print('Skipping input "' + item + '".  It is out of the valid range (0-' + str(count) + ').')
            continue

        if i == 0:
            selected_problems.extend(problems)
            selected_models.extend(models)
            continue

        if i <= len(problems):
            selected_problems.append(problems[i-1])
        else:
            selected_models.append(models[i-1-len(problems)])
            

    if len(selected_problems) <= 0 and len(selected_models) <= 0:
        print('No valid assignment parts identified.  Please try again. \n')
        return part_prompt(name, problems, models)
    else:
        return selected_problems, selected_models


def get_source(source_file):
    '''collects the source code.'''
    f = open(source_file,'r')
    src = f.read()
    f.close()
    return src


def compute(metadata, model_file_override=None):
    if model_file_override is not None:
        print('Overriding model file with: '+model_file_override)

    selected_problems, selected_models = part_prompt(metadata.name, metadata.problem_data, metadata.model_data)
    
    print(selected_problems, selected_models)

    results = {}

    #submission needs empty dict for every assignment part
    results.update({prob_data.sid : {} for prob_data in metadata.problem_data})
    results.update({model_data.sid : {} for model_data in metadata.model_data})

    for model in selected_models:
        if model_file_override != None:
            model_file = model_file_override
        else:
            model_file = model.model_file
        
        if not os.path.isfile(model_file):
            print('Unable to locate assignment file "'+model_file+'" in the current working directory.')
            continue
        
        submission = get_source(model_file)
        results[model.sid] = {'output':submission}

    for problem in selected_problems:
        if model_file_override != None:
            model_file = model_file_override
        else:
            model_file = problem.model_file
        
        if not os.path.isfile(model_file):
            print('Unable to locate assignment file "'+model_file+'" in the current working directory.')
            continue

        submission = output(problem, model_file)
        if submission != None:
            results[problem.sid] = {'output':submission}

    return results


def run_minizinc(process_id, model_file, data_file, solution_file=None, solve_time_limit=10000, mzn_time_limit=5000, all_solutions=False):
    cmd = [minizinc_cmd, model_file, data_file]
    if all_solutions:
        cmd.append('--all-solutions')
    if isinstance(solve_time_limit, int):
        cmd.append('--fzn-flags')
        cmd.append('-time '+str(solve_time_limit))

    print('running gecode minizinc as a subprocess with the command,')
    print(' '.join(cmd))

    process = Popen(cmd, stdout=PIPE, stderr=PIPE, shell = (os.name == 'nt') )

    stdout = ''
    stderr = ''

    while process.poll() != 0:
        while True:
            line = process.stdout.readline().decode('utf8')
            if not line:
                break
            stdout += line
            sys.stdout.write(line)
        sys.stdout.flush()
        while True:
            line = process.stderr.readline().decode('utf8')
            if not line:
                break
            stderr += line
            sys.stderr.write(stderr)
        sys.stderr.flush()

    return stdout, stderr


def last_solution(solution_stream):
    solutions = solution_stream.split(mzn_solution)
    if len(solutions) < 2: #this means there was no solution
        return solution_stream
    return mzn_solution.join(solutions[-2:])


def output(problem, model_file=None):
    '''Use student code to compute the output for test cases.'''
    
    if model_file == None:
        model_file = problem.model_file
    
    solution = ''

    start = time.clock()
    try:
        stdout, stderr = run_minizinc(process_id, model_file, problem.input_file, solve_time_limit=problem.runtime*1000, mzn_time_limit=3600000, all_solutions=True)
    except Exception as e:
        print('running minizinc as a subprocess on input '+problem.input_file+' with model '+model_file+' raised an exception')
        print('try testing outside of this submission script')
        print('exception message:')
        print(e)
        print('')
        return 'Local Exception =('+'\n\n'+str(e)
    end = time.clock()
    
    solution = last_solution(stdout)

    print('For part: '+problem.name)
    print('Submitting: ')
    print(solution)

    submission_string = solution.strip() + '\n' + str(end - start) + '\n' + 'command line submission'

    return submission_string


def login_dialog(assignment_key, results, credentials_file_location = '_credentials'):
    success = False
    while not success:
        login, token = login_prompt(credentials_file_location)

        code, responce = submit_solution(assignment_key, login, token, results)

        print('\n== Coursera Responce ...')
        #print(code)
        print(responce)
        
        if code != 401:
            success = True
        else:
            print('\ntry logging in again')

def login_prompt(credentials_file_location):
    '''Prompt the user for login credentials. Returns a tuple (login, token).'''
    if os.path.isfile(credentials_file_location):
        try:
            with open(credentials_file_location, 'r') as metadata_file:
                login = metadata_file.readline().strip()
                token = metadata_file.readline().strip()
                metadata_file.close()
        except:
            login, token = basic_prompt()
    else:
        login, token = basic_prompt()
    return login, token


def basic_prompt():
    '''Prompt the user for login credentials. Returns a tuple (login, token).'''
    login = input('User Name (e-mail address): ')
    token = input('Submission Token (from the assignment page): ')
    return login, token


def submit_solution(assignment_key, email_address, token, results):
    '''Submits a solution to the server. Returns (code, responce).'''
    
    print('\n== Connecting to Coursera ...')
    print('Submitting %d of %d parts' % (sum(['output' in v for k,v in results.items()]), len(results)))

    # build json datastructure
    parts = {}
    submission = {
        'assignmentKey': assignment_key,  
        'submitterEmail': email_address,  
        'secret': token,
        'parts': results
    }

    # send submission
    req = Request(submitt_url)
    req.add_header('Cache-Control', 'no-cache')
    req.add_header('Content-type', 'application/json')

    try:
        res = urlopen(req, json.dumps(submission).encode('utf8'))
    except HTTPError as e:
        responce = json.loads(e.read().decode('utf8'))

        if 'details' in responce and responce['details'] != None and \
            'learnerMessage' in responce['details']:
            return e.code, responce['details']['learnerMessage']
        else:
            return e.code, 'Unexpected response code, please contact the ' \
                               'course staff.\nDetails: ' + responce['message']

    code = res.code
    responce = json.loads(res.read().decode('utf8'))

    if code >= 200 and code <= 299:
        return code, 'Your submission has been accepted and will be ' \
                     'graded shortly.'

    return code, 'Unexpected response code, please contact the '\
                 'course staff.\nDetails: ' + responce



def main(args):
    if args.metadata is None:
        metadata = load_metadata()
    else:
        print('Overriding metadata file with: '+args.metadata)
        metadata = load_metadata(args.metadata)

    print('==\n== '+metadata.name+' Solution Submission \n==')
    
    # compute dialog
    results = compute(metadata, args.override)

    if sum(['output' in v for k,v in results.items()]) <= 0:
        return

    # store submissions if requested
    if args.record_submission is not None:
        print('Recording submission as files')
        for sid, submission in results.items():
            if 'output' in submission:
                directory = '_'+sid
                if not os.path.exists(directory):
                    os.makedirs(directory)

                submission_file_name = directory+'/submission.sub'
                print('  writting submission file: '+submission_file_name)
                with open(submission_file_name,'w') as submission_file:
                    submission_file.write(submission['output'])
                    submission_file.close()

    # submit dialog
    if args.credentials is None:
        login_dialog(metadata.assignment_key, results)
    else:
        print('Overriding credentials file with: '+args.credentials)
        login_dialog(metadata.assignment_key, results, args.credentials)


import argparse
def build_parser():
    parser = argparse.ArgumentParser(
        description='''The command line interface for Modeling Discrete 
            Optimization assignment submission on the Coursera Platform.''',
        epilog='''Please file bugs on github at: 
        https://github.com/ccoffrin/coursera-mdo-submission/issues. If you 
        would like to contribute to this tool's development, check it out at: 
        https://github.com/ccoffrin/coursera-mdo-submission''')
    parser.add_argument('-v', '--version', action='version', version='%(prog)s '+version)
    parser.add_argument('-o', '--override', help='overrides the model source file specified in the \'_coursera\' file')
    parser.add_argument('-m', '--metadata', help='overrides the \'_coursera\' metadata file')
    parser.add_argument('-c', '--credentials', help='overrides the \'_credentials\' credentials file')
    parser.add_argument('-rs', '--record_submission', help='records the submission(s) as files', action='store_true')
    return parser

if __name__ == '__main__':
    import sys

    try:
        cmd = [minizinc_cmd, '--help']
        process = Popen(cmd, stdout=PIPE, shell = (os.name == 'nt') )
        stdout, stderr = process.communicate()    
    except OSError as e:
        print('unable to find minizinc command: '+minizinc_cmd)
        print('details: ', e)
        quit()

    parser = build_parser()
    main(parser.parse_args())


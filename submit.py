#!/usr/bin/python
# -*- coding: utf-8 -*-

import urllib
import urllib2
import hashlib
import email.message
import email.encoders

import json
import time
import os.path, sys
from subprocess import Popen, PIPE
from collections import namedtuple

process_id = os.getpid()

submitt_url = 'https://www.coursera.org/api/onDemandProgrammingScriptSubmissions.v1'

minizinc_cmd = 'mzn-gecode'
#minizinc_cmd = 'minizinc'

Metadata = namedtuple("Metadata", ['assignment_key', 'sid_login', 'name', 'problem_data', 'model_data'])

Problem = namedtuple("Problem", ['sid', 'model_file', 'input_file', 'runtime', 'name'])
Model = namedtuple("Model", ['sid', 'model_file', 'name'])

mzn_solution = '----------'

def check_login(metadata, login, password):
    return
    # submission = '0'
    # source = ''

    # print('== Checking Login Credentials ... ')
    # (login, ch, state, ch_aux) = get_challenge(metadata.url, login, metadata.sid_login)
    # if((not login) or (not ch) or (not state)):
    #     print('\n!! Error: %s\n' % login)
    #     return
    # ch_resp = challenge_response(login, password, ch)
    # (result, string) = submit_solution(metadata.url, login, ch_resp, metadata.sid_login, submission, source, state, ch_aux)
    # if string.strip() == 'password verified':
    #     print('== credentials verified')
    # else :
    #     print('\n!! login failed')
    #     print('== %s' % string.strip())
    #     quit()


def load_meta_data():
    try:
        metadata_file = open('_coursera', 'r')
        
        url = metadata_file.readline().strip()
        sid_login = metadata_file.readline().strip()
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
    return Metadata(url, sid_login, name, problem_data, model_data)
    
    
def submit(model_file_override=None, record_submission=False):
    metadata = load_meta_data()
    
    print('==\n== '+metadata.name+' Solution Submission \n==')
    
    
    (login, token) = login_prompt()
    if not login:
        print('!! Submission Cancelled')
        return
    
    print('\n== Connecting to Coursera ... ')
    check_login(metadata, login, token)

    selected_problems, selected_models = part_prompt(metadata.name, metadata.problem_data, metadata.model_data)
    
    for model in selected_models:
        if model_file_override != None:
            model_file = model_file_override
        else:
            model_file = model.model_file
        
        if not os.path.isfile(model_file):
            print('Unable to locate assignment file "'+model_file+'" in the current working directory.')
            continue
        
        submission = get_source(model_file)

        try:
            submission.decode('utf-8')
        except UnicodeError:
            print('Error: the model submission was not UTF-8 and will be skipped.')
            print('Orginal: ')
            print(submission)
            continue
        
        print('For part: '+model.name+' Model')
        print('Submitting: '+model_file)
        
        if record_submission:
            directory = '_'+model.sid
            if not os.path.exists(directory):
                os.makedirs(directory)

            submission_file_name = directory+'/submission.sub'
            print('writting submission file: '+submission_file_name)
            submission_file = open(submission_file_name,'w')
            submission_file.write(submission)
            submission_file.close()

        
        (result, string) = submit_solution(metadata, login, token, model.sid, submission, '')
        print('== %s \n\n' % string.strip())

    
    for problem in selected_problems:
        if model_file_override != None:
            model_file = model_file_override
        else:
            model_file = problem.model_file
        
        if not os.path.isfile(model_file):
            print('Unable to locate assignment file "'+model_file+'" in the current working directory.')
            continue
            
        # (login, ch, state, ch_aux) = get_challenge(metadata.url, login, problem.sid)
        # if not login or not ch or not state:
        #     print('\n!! Error: %s\n' % login)
        #     return
        submission = output(problem, model_file, record_submission)

        if submission != None:
            (result, string) = submit_solution(metadata, login, token, problem.sid, submission, get_source(model_file))
            print('== %s \n\n' % string.strip())


def login_prompt():
    """Prompt the user for login credentials. Returns a tuple (login, password)."""
    if os.path.isfile('_credentials'):
        try:
            metadata_file = open('_credentials', 'r')
            login = metadata_file.readline().strip()
            password = metadata_file.readline().strip()
        except:
            login, password = basic_prompt()
    else:
        login, password = basic_prompt()
    return login, password


def basic_prompt():
    """Prompt the user for login credentials. Returns a tuple (login, password)."""
    login = raw_input('User Name (e-mail address): ')
    password = raw_input('Submission Token (from the assignment page): ')
    return (login, password)


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

    part_text = raw_input('Please enter which part(s) you want to submit (0-'+ str(count-1) + '): ')
    selected_problems = []
    selected_models = []

    for item in part_text.split(','):
        try:
            i = int(item)-1
        except:
            print('Skipping input "' + item + '".  It is not an integer.')
            continue
        if i >= count-1:
            print('Skipping input "' + item + '".  It is out of range (the maximum value is ' + str(count-1) + ').')
            continue
        if i < 0:
            selected_problems.extend(problems)
            selected_models.extend(models)
            continue
        if i < len(problems):
            selected_problems.append(problems[i])
        else:
            selected_models.append(models[i-len(problems)])
            

    if len(selected_problems) <= 0 and len(selected_models) <= 0:
        print('No valid assignment parts identified.  Please try again. \n')
        return part_prompt(name, problems, models)
    else:
        return selected_problems, selected_models

def submit_solution(metadata, email_address, token, sid, output, source):
    """Submits a solution to the server. Returns (result, string)."""
    
    problem_parts = {prob_data.sid : {} for prob_data in metadata.problem_data}
    model_parts = {model_data.sid : {} for model_data in metadata.model_data}
    parts = {}
    parts.update(problem_parts)
    parts.update(model_parts)

    parts[sid]["output"] = output

    submission = {
        "assignmentKey": metadata.assignment_key,  
        "submitterEmail": email_address,  
        "secret": token,
        "parts": parts
    }

    print("SUBMIT IT!")
    print(output) 

    print("********")
    data = json.dumps(submission)
    print(data)
    result = 0
    string = "none!"

    req = urllib2.Request(submitt_url)
    req.add_header('Cache-Control', 'no-cache')
    req.add_header('Content-type', 'application/json')
    # make the request and print the results
    res = urllib2.urlopen(req, data)
    print res.read()


    # source_64_msg = email.message.Message()
    # source_64_msg.set_payload(source)
    # email.encoders.encode_base64(source_64_msg)

    # output_64_msg = email.message.Message()
    # output_64_msg.set_payload(output)
    # email.encoders.encode_base64(output_64_msg)
    # values = { 
    #     'assignment_part_sid': sid,
    #     'email_address': email_address,
    #     # 'submission' : output, \
    #     'submission': output_64_msg.get_payload(),
    #     # 'submission_aux' : source, \
    #     'submission_aux': source_64_msg.get_payload(),
    #     'challenge_response': ch_resp,
    #     'state': state,
    #     }
    # url = submit_url(c_url)
    # data = urllib.urlencode(values)
    # req = urllib2.Request(url, data)
    # response = urllib2.urlopen(req)
    # string = response.read().strip()
    # result = 0
    return (result, string)


def get_source(source_file):
    """Collects the source code (just for logging purposes)."""
    f = open(source_file,'r')
    src = f.read()
    f.close()
    return src
    

def percent_cb(complete, total): 
    sys.stdout.write('.')
    sys.stdout.flush()


def run_minizinc(model_file, data_file, time_limit=60000):
    cmd = [minizinc_cmd, model_file, data_file, '--all-solutions']
    if isinstance(time_limit, int):
        cmd.append('--fzn-flags')
        cmd.append('-time '+str(time_limit))
    
    print('running gecode minizinc as a subprocess with the command,')
    print(' '.join(cmd))
    
    process = Popen(cmd, stdout=PIPE, stderr=PIPE, shell = (os.name == 'nt') )
    
    stdout = ''
    stderr = ''
    
    while process.poll() != 0:
        while True:
            line = process.stdout.readline()
            if not line:
                break
            stdout += line
            sys.stdout.write(line)
        sys.stdout.flush()
        while True:
            line = process.stderr.readline()
            if not line:
                break
            stderr += line
            sys.stderr.write(stderr)
        sys.stderr.flush()
    
    return stdout, stderr


def process_monitor(process, time_limit=None, memory_limit=None):
    status = 0
    message = 'process finished normally'

    time.sleep(1)
    run_time = 1
    while process.poll() == None:
        sys.stdout.write('.')
        sys.stdout.flush()
        time.sleep(5)
        run_time += 5
        if time_limit != None and run_time > time_limit:
            status = 1
            message = 'runtime: '+str(run_time)+' timelimit: '+str(time_limit)+' (seconds) - killing process'
            process.terminate()
            process.wait()
            break

    assert(process.returncode != None)
    return process.returncode, message

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
            line = process.stdout.readline()
            if not line:
                break
            stdout += line
            sys.stdout.write(line)
        sys.stdout.flush()
        while True:
            line = process.stderr.readline()
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

def output(problem, model_file=None, record_submission=False):
    """Use student code to compute the output for test cases."""
    
    if model_file == None:
        model_file = problem.model_file
    
    solution = ''

    start = time.clock()
    try:
        #stdout, stderr = run_minizinc(model_file, problem.input_file, time_limit=3600000)
        stdout, stderr = run_minizinc(process_id, model_file, problem.input_file, solve_time_limit=problem.runtime*1000, mzn_time_limit=3600000, all_solutions=True)
        #stdout, stderr = run_minizinc(model_file, problem.input_file, time_limit=None)
    except Exception as e:
        print('running minizinc as a subprocess on input '+problem.input_file+' with model '+model_file+' raised an exception')
        print('try testing outside of this submission script')
        print('exception message:')
        print(e)
        print('')
        return 'Local Exception =('+'\n\n'+str(e)
    end = time.clock()
    
    solution = last_solution(stdout)
    
    try:
        solution.decode('utf-8')
    except UnicodeError:
        print('Error: the submitted solution was not UTF-8 and will be skipped.')
        print('Orginal: ')
        print(solution)
        return None

    print('For part: '+problem.name)
    print('Submitting: ')
    print(solution)

    submission_string = solution.strip() + '\n' + str(end - start) + '\n' + 'command line submission'

    if record_submission:
        directory = '_'+problem.sid
        if not os.path.exists(directory):
            os.makedirs(directory)

        submission_file_name = directory+'/submission.sub'
        print('writting submission file: '+submission_file_name)
        submission_file = open(submission_file_name,'w')
        submission_file.write(submission_string)
        submission_file.close()

    return submission_string


try:
    cmd = [minizinc_cmd, '--help']
    process = Popen(cmd, stdout=PIPE, shell = (os.name == 'nt') )
    (stdout, stderr) = process.communicate()    
except OSError as e:
    print('unable to find minizinc command: '+minizinc_cmd)
    print('details: ', e)
    quit()



def main(argv):
    model_file_override = None
    record_submission = False

    if len(sys.argv) > 1:
        for cmd_line_arg in sys.argv[1:]:
            if cmd_line_arg.startswith('-override='):
                model_file_override = cmd_line_arg.split('=')[1].strip()
                print('Overridding model file with: '+model_file_override)

            if cmd_line_arg.startswith('-record_submission'):
                record_submission = True
                print('Recording submission as file')

    submit(model_file_override, record_submission)

if __name__ == '__main__':
    import sys
    main(sys.argv)


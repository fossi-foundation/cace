from flask import Flask, render_template, request, Response
from .parameter import ParameterManager
from .web.html_templates import *

import json
import logging
import mpld3
import os
import queue
import sys

parameter_manager = ParameterManager(
    max_runs=None, run_path=None, max_jobs=os.cpu_count()
)
parameter_manager.find_datasheet(os.getcwd(), False)
datasheet = parameter_manager.datasheet['parameters']
paramkey_paramdisplay = {
    i: j.get('display', i) for i, j in datasheet['parameters'].items()
}
paramdisplay_paramkey = {
    j.get('display', i): i for i, j in datasheet['parameters'].items()
}

task_queue = queue.Queue()
figures = {}
debug = False
app = Flask(__name__, template_folder='web', static_folder='web/static')


# Returns the home page with all parameters and previous runs
@app.route('/')
def homepage():
    # Restores console output
    sys.stdout = sys.__stdout__

    # Initialize pnames and parameter_manager
    pnames = parameter_manager.get_all_pnames()
    parameter_manager.results = {}
    parameter_manager.result_types = {}
    data = [{'name': pname} for pname in pnames]

    # Collects all previous runs
    runs = next(os.walk(datasheet['paths']['runs']))[1]
    results = []

    # Parse the markdown summary and store it in the results list
    for run in runs:
        result = []

        with open('runs/' + run + '/summary.md', 'r') as f:
            content = f.read()

        summary_lines = content.split('\n')[7:-2]

        for row in summary_lines:
            row = row.split('|')

            if len(row) == 1:
                continue

            result.append(
                {
                    'parameter_str': row[1].strip(),
                    'tool_str': row[2].strip(),
                    'result_str': row[3].strip(),
                    'min_limit_str': row[4].strip(),
                    'min_value_str': row[5].strip(),
                    'max_limit_str': row[6].strip(),
                    'max_value_str': row[7].strip(),
                    'typ_limit_str': row[8].strip(),
                    'typ_value_str': row[9].strip(),
                    'status_str': row[10].strip(),
                }
            )

        results.append(RESULTS_SUMMARY_TEMPLATE.render(data=result))

    return render_template(
        template_name_or_list='index.html',
        data=data,
        runs=runs,
        results=results,
    )


# Responsible for sending the SSEs back to the client
def generate_sse():
    while True:
        tq_item = task_queue.get()

        # NOTE: This is not for ending the SSE stream. Instead, it is called when a simulation ends
        # Handles the matplotlib plots
        if tq_item['task'] == 'end':
            for i in parameter_manager.running_threads:
                if i.param == tq_item['param']:
                    tq_item['status'] = i.result_type.name
                    if len(i.plots_dict) > 0:
                        figures[i.pname] = i.plots_dict
        # This is the one that ends the SSE stream
        elif tq_item['task'] == 'end_stream':
            if debug:
                print('ending sse stream')
            return

        # Convert the param key to the real param name
        if 'param' in tq_item:
            tq_item['param'] = list(datasheet.keys())[
                list(datasheet.values()).index(tq_item['param'])
            ]

        if debug:
            print(tq_item)

        yield f'data: {json.dumps(tq_item)}\n\n'


# Called by the client to start the SSE stream
@app.route('/stream')
def stream():
    if debug:
        print('starting sse stream')

    # We return the generator which stays alive until the end_stream task is queued
    return Response(generate_sse(), content_type='text/event-stream')


# Starts the requested simulations
@app.route('/runsim', methods=['POST'])
def runsim():
    rd = json.loads(request.get_data())
    if debug:
        print(rd)

    # Set default values for configuration options
    if rd['max_runs'] == '':
        rd['max_runs'] = None
    if rd['run_path'] == '':
        rd['run_path'] = None
    if rd['jobs'] == '':
        rd['jobs'] = os.cpu_count()
    if rd['netlist_source'] == '':
        rd['netlist_source'] = 'best'
    if rd['parallel_parameters'] == '':
        rd['parallel_parameters'] = 4

    params = rd['selected_params']

    # Input the configuration to the parameter manager
    parameter_manager.max_runs = rd['max_runs']
    parameter_manager.run_path = rd['run_path']
    parameter_manager.max_jobs = rd['jobs']
    parameter_manager.set_runtime_options('force', rd['force'])
    parameter_manager.set_runtime_options('noplot', rd['noplot'])
    parameter_manager.set_runtime_options('nosim', rd['nosim'])
    parameter_manager.set_runtime_options('sequential', rd['sequential'])
    parameter_manager.set_runtime_options(
        'netlist_source', rd['netlist_source']
    )
    parameter_manager.set_runtime_options(
        'parallel_parameters', rd['parallel_parameters']
    )

    # Prepare the directory that stores the run results
    parameter_manager.prepare_run_dir()

    # Queue, not run, the selected parameters and set up the callbacks
    for pname in params:
        parameter_manager.queue_parameter(
            pname=pname,
            start_cb=lambda param, steps: (
                task_queue.put(
                    {
                        'task': 'start',
                        'param': param,
                        'steps': steps,
                    }
                )
            ),
            step_cb=lambda param: (
                task_queue.put({'task': 'step', 'param': param})
            ),
            cancel_cb=lambda param: (
                task_queue.put({'task': 'cancel', 'param': param})
            ),
            end_cb=lambda param: (
                task_queue.put({'task': 'end', 'param': param}),
            ),
        )

    # Finally run the parameters
    parameter_manager.run_parameters_async()

    # Send the progress page's content to the client
    task_queue.put(
        {'task': 'progress', 'html': PROGRESS_TEMPLATE.render(params=params)}
    )

    return json.dumps({'success': True})


# Cancels a specific simulation
@app.route('/cancel_sim', methods=['POST'])
def cancel_sim():
    data = request.get_json()
    if debug:
        print(data)

    parameter_manager.cancel_parameter(pname=data['param'])
    return json.dumps({'success': True})


# Cancels all simulations
@app.route('/cancel_sims', methods=['POST'])
def cancel_sims():
    parameter_manager.cancel_parameters()
    return json.dumps({'success': True})


# Ends the SSE stream
@app.route('/end_stream', methods=['POST'])
def end_stream():
    task_queue.put({'task': 'end_stream'})
    return json.dumps({'success': True})


# Sends the run results to the client
@app.route('/fetch_results', methods=['POST'])
def fetch_results():
    parameter_manager.join_parameters()
    result = []
    divs = []

    # Get the MarkDown summary
    summary_lines = parameter_manager.summarize_datasheet().split('\n')[7:-2]
    lengths = {
        param: len(list(datasheet['parameters'][param]['spec'].keys()))
        for param in parameter_manager.get_all_pnames()
    }

    # Parse each line of summary and collect it
    for param in parameter_manager.get_result_types().keys():
        total = 0
        for i in parameter_manager.get_all_pnames():
            if i == param:
                for j in range(lengths[param]):
                    row = summary_lines[total + j].split('|')
                    result.append(
                        {
                            'parameter_str': row[1].strip(),
                            'tool_str': row[2].strip(),
                            'result_str': row[3].strip(),
                            'min_limit_str': row[4].strip(),
                            'min_value_str': row[5].strip(),
                            'max_limit_str': row[6].strip(),
                            'max_value_str': row[7].strip(),
                            'typ_limit_str': row[8].strip(),
                            'typ_value_str': row[9].strip(),
                            'status_str': row[10].strip(),
                        }
                    )

            total += lengths[i]

    divs.append('<br>')

    # Render the matplotlib plots using mpld3
    for pname in figures.keys():
        divs.append(
            f'<details>\n<summary>Figures for {paramkey_paramdisplay[pname]}</summary>'
        )
        for figure in figures[pname]:
            fig = figures[pname][figure].figure
            fig.set_tight_layout(True)
            fig.set_size_inches(fig.get_size_inches() * 1.25)
            divs.append(
                mpld3.fig_to_html(
                    fig, include_libraries=False, template_type='simple'
                )
            )

        divs.append('</details>\n<br>')

    if debug:
        print(divs)

    # Send the results to the client
    task_queue.put(
        {
            'task': 'results',
            'summary': RESULTS_SUMMARY_TEMPLATE.render(data=result),
            'plots': RESULTS_PLOTS_TEMPLATE.render(divs=divs),
        }
    )
    return json.dumps({'success': True})


# Sends the latest list of runs and their summaries to the client
@app.route('/refresh_history', methods=['POST'])
def refresh_history():
    # List all previous runs
    runs = next(os.walk(datasheet['paths']['runs']))[1]

    results = []
    for run in runs:
        result = []

        with open('runs/' + run + '/summary.md', 'r') as f:
            content = f.read()

        summary_lines = content.split('\n')[7:-2]

        # Parse each line of the summary
        for row in summary_lines:
            row = row.split('|')

            if len(row) == 1:
                continue

            result.append(
                {
                    'parameter_str': row[1].strip(),
                    'tool_str': row[2].strip(),
                    'result_str': row[3].strip(),
                    'min_limit_str': row[4].strip(),
                    'min_value_str': row[5].strip(),
                    'max_limit_str': row[6].strip(),
                    'max_value_str': row[7].strip(),
                    'typ_limit_str': row[8].strip(),
                    'typ_value_str': row[9].strip(),
                    'status_str': row[10].strip(),
                }
            )

        results.append(RESULTS_SUMMARY_TEMPLATE.render(data=result))

    # Send all the summaries to the client
    task_queue.put(
        {
            'task': 'history',
            'html': HISTORY_TEMPLATE.render(runs=runs, results=results),
        }
    )
    return json.dumps({'success': True})


# Called to initialize the server
def web():
    try:
        host = 'localhost'
        port = 5000
        print(
            'Open the CACE web interface at: http://' + host + ':' + str(port)
        )

        # Stop console output to prevent unnecessary debug info from getting printed
        sys.stdout = open(os.devnull, 'w')
        debug = '--debug' in sys.argv
        for prog in ['werkzeug', '__cace__']:
            logger = logging.getLogger(prog)
            logger.setLevel(logging.DEBUG if debug else logging.WARNING)

        # Run the server
        app.run(debug=debug, host=host, port=port, use_reloader=False)
    finally:
        task_queue.put({'task': 'close'})

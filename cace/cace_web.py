from flask import Flask, render_template, request, Response
from threading import Timer

from .__version__ import __version__
from .logging import set_log_level
from .parameter import ParameterManager
from .web.html_templates import *

import argparse
import json
import logging
import mpld3
import os
import queue
import sys
import webbrowser


def register_endpoints():
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

        # Create the config file if it doesn't exist
        if not os.path.exists(
            os.path.dirname(parameter_manager.dspath)
            + '/.cace_web_config.json'
        ):
            save_config_file(
                {
                    'max_runs': None,
                    'run_path': None,
                    'jobs': os.cpu_count(),
                    'force': False,
                    'noplot': False,
                    'nosim': False,
                    'sequential': False,
                    'netlist_source': 'best',
                    'parallel_parameters': 4,
                    'typ_thresh': 10,
                }
            )

        # Load the config file and update the parameter manager
        config = load_config_file()
        update_config(config)

        # Get a list of all previous runs
        runs = next(os.walk(datasheet['paths']['runs']))[1]

        results = []

        # Parse the markdown summary and store it in the results list
        for run in runs:
            result = []

            # Get the data from the summary.md file for the specific run
            summary_lines = read_summary_lines(run)

            # If the summary.md file wasn't found we put a danger alert
            if summary_lines == None:
                results.append(
                    DANGER_ALERT_TEMPLATE.render(
                        text='ERROR: summary.md not found for this run!'
                    )
                )

                # Continue to the next run since there is no data to parse anymore
                continue

            # Parse the data from the summary.md file
            for row in summary_lines:
                row = row.split('|')

                if len(row) == 1:
                    continue

                # Append the data to the list of JSONs to send
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

            # We render the table that has the result summary
            results.append(RESULTS_SUMMARY_TEMPLATE.render(data=result))

        # Send to the client all required data and the history JSON
        return render_template(
            template_name_or_list='index.html',
            data=data,
            runs=runs,
            results=results,
            config=json.dumps(config),
        )

    # Called by the client to start the SSE stream
    @app.route('/stream')
    def stream():
        # We return the generator which stays alive until the end_stream task is queued
        return Response(generate_sse(), content_type='text/event-stream')

    # Starts the requested simulations
    @app.route('/runsim', methods=['POST'])
    def runsim():
        rd = json.loads(request.get_data())

        params = rd['selected_params']

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
            {
                'task': 'progress',
                'html': PROGRESS_TEMPLATE.render(params=params),
            }
        )

        return json.dumps({'success': True})

    # Cancels a specific simulation
    @app.route('/cancel_sim', methods=['POST'])
    def cancel_sim():
        data = request.get_json()
        parameter_manager.cancel_parameter(pname=data['param'])
        return json.dumps({'success': True})

    # Cancels all simulations
    @app.route('/cancel_sims')
    def cancel_sims():
        parameter_manager.cancel_parameters()
        return json.dumps({'success': True})

    # Ends the SSE stream
    @app.route('/end_stream')
    def end_stream():
        task_queue.put({'task': 'end_stream'})
        return json.dumps({'success': True})

    # Sends the run results to the client
    @app.route('/fetch_results')
    def fetch_results():
        parameter_manager.join_parameters()
        result = []
        divs = []

        # Get the MarkDown summary
        summary_lines = parameter_manager.summarize_datasheet(save=True).split(
            '\n'
        )[7:-2]
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
    @app.route('/refresh_history')
    def refresh_history():
        # List all previous runs
        runs = next(os.walk(datasheet['paths']['runs']))[1]

        results = []
        for run in runs:
            result = []

            # Read the data from the summary.md file
            summary_lines = read_summary_lines(run)

            # If the summary.md file doesn't exist we put an alert instead
            if summary_lines == None:
                results.append(
                    DANGER_ALERT_TEMPLATE.render(
                        text='ERROR: summary.md not found for this run!'
                    )
                )

                # Skip to the next run because there is no data to parse
                continue

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

    # Saves the  settings information sent from the client
    @app.route('/save_config', methods=['POST'])
    def save_config():
        data = request.get_json()

        # Save the config to the file
        save_config_file(data)

        # Update the config variable
        update_config(data)
        return json.dumps({'success': True})

    # Load and send the config information to the client
    @app.route('/fetch_config')
    def fetch_config():
        # Load the config file
        config = load_config_file()

        # Send the parsed config file
        return json.dumps(config)


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
            return

        # Convert the param key to the real param name
        if 'param' in tq_item:
            tq_item['param'] = list(datasheet['parameters'].keys())[
                list(datasheet['parameters'].values()).index(tq_item['param'])
            ]

        yield f'data: {json.dumps(tq_item)}\n\n'


# Read the summary.md file, return None if not found.
def read_summary_lines(run):
    try:
        # We save the summary.md file when generating the markdown summary
        with open('runs/' + run + '/summary.md', 'r') as f:
            content = f.read()

        # We only want the real data, not the headers etc
        return content.split('\n')[7:-2]
    except FileNotFoundError:
        # This is for putting a warning alert later
        return None


# Updates the parameter manager with the new configuration
def update_config(config):
    parameter_manager.max_runs = config['max_runs']
    parameter_manager.run_path = config['run_path']
    parameter_manager.max_jobs = int(config['jobs'])
    parameter_manager.set_runtime_options('force', config['force'])
    parameter_manager.set_runtime_options('noplot', config['noplot'])
    parameter_manager.set_runtime_options('nosim', config['nosim'])
    parameter_manager.set_runtime_options('sequential', config['sequential'])
    parameter_manager.set_runtime_options(
        'netlist_source', config['netlist_source']
    )
    parameter_manager.set_runtime_options(
        'parallel_parameters', int(config['parallel_parameters'])
    )


# Saves the config file to the same folder as the datasheet
def save_config_file(data):
    with open(
        os.path.dirname(parameter_manager.dspath) + '/.cace_web_config.json',
        'w',
    ) as f:
        f.write(json.dumps(data))


# Loads the config file from the datasheet path, and creates one if not there
def load_config_file():
    with open(
        os.path.dirname(parameter_manager.dspath) + '/.cace_web_config.json'
    ) as f:
        config = json.load(f)
    return config


# Main initialization function
def init():
    # We need this block to make locally defined variables accessible outside as well
    global app
    global parameter_manager
    global paramkey_paramdisplay
    global paramdisplay_paramkey
    global task_queue
    global figures
    global datasheet
    global args

    # Add parser for command line arguments
    parser = argparse.ArgumentParser(
        prog='cace-web',
        description="""This is the web interface for CACE, see more by running \"cace --help\".""",
    )

    parser.add_argument(
        '--version', action='version', version=f'%(prog)s {__version__}'
    )

    parser.add_argument(
        'datasheet', nargs='?', help='input specification datasheet (YAML)'
    )

    parser.add_argument(
        '-l',
        '--log-level',
        type=str,
        choices=['ALL', 'DEBUG', 'INFO', 'WARNING', 'ERROR'],
        default='INFO',
        help="""set the log level for a more fine-grained output""",
    )

    parser.add_argument(
        '--reload-py',
        action='store_true',
        help='hot reload for python',
    )

    parser.add_argument(
        '--reload-html',
        action='store_true',
        help='hot reload for html',
    )

    parser.add_argument(
        '--debug',
        action='store_true',
        help='print debug info',
    )

    # parse the arguments
    args = parser.parse_args()

    # Set the log level
    if args.log_level:
        set_log_level(args.log_level)

    # Default settings
    parameter_manager = ParameterManager(
        max_runs=None, run_path=None, max_jobs=os.cpu_count()
    )

    # Load the datasheet
    if args.datasheet:
        if parameter_manager.load_datasheet(args.datasheet):
            sys.exit(0)
    else:
        if parameter_manager.find_datasheet(os.getcwd()):
            sys.exit(0)

    # Shortcut for parameter_manager.datasheet
    datasheet = parameter_manager.datasheet

    # This is used for converting parameters to their display names
    paramkey_paramdisplay = {
        i: j.get('display', i) for i, j in datasheet['parameters'].items()
    }
    paramdisplay_paramkey = {
        j.get('display', i): i for i, j in datasheet['parameters'].items()
    }

    # Task queue
    task_queue = queue.Queue()

    # Stores the HTML for the matplotlib plots
    figures = {}

    # Set the flask debugging level based on the --debug flag
    logging.getLogger('werkzeug').setLevel(
        logging.DEBUG if args.debug else logging.WARNING
    )

    # Define the Flask app and set the resource folder paths
    app = Flask(__name__, template_folder='web', static_folder='web/static')


# Call this function to start the web server
def web():
    try:
        # Initialize all global variables
        init()

        # Register the endpoints the "/<endpoint>" stuff
        register_endpoints()

        # Configuration for the host and port
        host = 'localhost'
        port = 5000

        # Print this BEFORE we disable output
        print(
            'Open the CACE web interface at: http://' + host + ':' + str(port)
        )

        # Disable output by setting stdout to null
        sys.stdout = open(os.devnull, 'w')

        def open_browser():
            webbrowser.open('http://127.0.0.1:5000')

        # Timer(0.25, open_browser).start()

        # Run the Flask app
        app.run(
            debug=args.reload_html,
            host=host,
            port=port,
            use_reloader=args.reload_py,
        )
    finally:
        # Send a close message to the client when we exit the program
        if 'task_queue' in globals():
            task_queue.put({'task': 'close'})

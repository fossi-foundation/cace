import jinja2

# Template for the table with progress bars
PROGRESS_TEMPLATE = jinja2.Template(
    """
<table id="progress_table">
  <thead>
    <tr>
      <th>Param</th>
      <th>Progress</th>
      <th>Cancel</th>
    </tr>
  </thead>
  <tbody>
    {% for param in params %}
    <tr>
      <td>{{ param }}</td>
      <td>
        <div class="progress" id="{{ param }}" role="progressbar" aria-valuenow="0" aria-valuemax="0" style="width: 300px;">
          <div class="progress-bar progress-bar-striped progress-bar-animated" style="width: 0%"></div>
        </div>
      </td>
      <td>
        <button type="button" class="btn btn-outline-danger" id="{{ param }}cancelbtn" onclick="cancel_sim('{{ param }}');">Cancel</button>
      </td>
    </tr>
    {% endfor %}
    <tr>
      <td>Overall Progress</td>
      <td>
        <div class="progress" id="overall_pb" role="progressbar" aria-valuenow="0" aria-valuemax="{{ params | length }}" style="width: 300px;">
          <div class="progress-bar progress-bar-striped progress-bar-animated" style="width: 0%"></div>
        </div>
      </td>
    </tr>
  </tbody>
</table>
<br>
<button type="button" class="btn btn-success" id="simresultsbtn" onclick="openTab(event, 'Results')" disabled>Simulation Results</button>
<button type="button" class="btn btn-danger" id="cancelbtn" onclick="cancel_sims();">Cancel Simulations</button>
<br>
<br>
"""
)

# Template for the table showing run results
RESULTS_SUMMARY_TEMPLATE = jinja2.Template(
    """
<table>
  <thead>
    <tr>
      <th>Parameter</th>
      <th>Tool</th>
      <th>Result</th>
      <th>Min Limit</th>
      <th>Min Value</th>
      <th>Typ Limit</th>
      <th>Typ Value</th>
      <th>Max Limit</th>
      <th>Max Value</th>
      <th>Status</th>
    </tr>
  </thead>
  <tbody>
    {% for row in data %}
    <tr>
      <td>{{ row.parameter_str }}</td>
      <td>{{ row.tool_str }}</td>
      <td>{{ row.result_str }}</td>
      <td>{{ row.min_limit_str }}</td>
      <td>{{ row.min_value_str }}</td>
      <td>{{ row.max_limit_str }}</td>
      <td>{{ row.max_value_str }}</td>
      <td>{{ row.typ_limit_str }}</td>
      <td>{{ row.typ_value_str }}</td>
      <td>{{ row.status_str }}</td>
    </tr>
    {% endfor %}
  </tbody>
</table>
"""
)

# Template for the mpld3 plots
RESULTS_PLOTS_TEMPLATE = jinja2.Template(
    """
{% for div in divs %}
{{ div | safe }}
{% endfor %}
"""
)

# Template for the history entries
HISTORY_TEMPLATE = jinja2.Template(
    """
<button type="button" class="btn btn-secondary" onclick="refresh_history()"><i class="bi bi-arrow-repeat icon-lg"></i>Refresh</button>
<br />
<br />
<div id="comp-holder" class="comp-parent">
  <div id="compare_left" class="comp-holder">
    {% for i in range(runs|length) %}
    <details id="{{ runs[i] }}_details">
      <summary>{{ runs[i] }}</summary>
      <div class="comp-btn-holder" id="{{ runs[i] }}_compare_holder">
        <button type="button" class="btn btn-primary right-align" onclick="compare('{{ runs[i] }}')"><i class="bi bi-arrow-left-right icon-lg"></i> Compare</button>
      </div>
      <div class="small-table">{{ results[i] | safe }}</div>
    </details>
    {% endfor %}
    <br />
  </div>
</div>
"""
)

# Generic template for a danger warning
DANGER_ALERT_TEMPLATE = jinja2.Template(
    """
<div class="alert alert-danger" role="alert">
  <i class="bi bi-exclamation-octagon icon-lg"></i>{{ text }}
</div>
"""
)

import jinja2

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
        <progress id="{{param}}" value="0" max="100"></progress>
      </td>
      <td>
        <button type="button" class="btn btn-danger" id="{{ param }}cancelbtn" onclick="sendData({ 'task': 'cancel_sim', 'param': '{{ param }}' });">Cancel</button>
      </td>
    </tr>
    {% endfor %}
    <tr>
      <td>Overall Progress</td>
      <td>
        <progress id="overall_pb" value="0" max="{{params | length}}"></progress>
      </td>
    </tr>
  </tbody>
</table>
<br>
<button type="button" class="btn btn-success" id="simresultsbtn" onclick="openTab(event, 'Results')" disabled>Simulation Results</button>
<button type="button" class="btn btn-danger" id="cancelbtn" onclick="sendData({ 'task': 'cancel_sims' });">Cancel Simulations</button>
<br>
<br>
"""
)

RESULTS_SUMMARY_TEMPLATE = jinja2.Template(
    """
<table>
  <thead>
    <tr>
      <th>Parameter</th>
      <th>Tool</th>
      <th>Result</th>
      <th>Minimum Limit</th>
      <th>Minimum Value</th>
      <th>Typical Limit</th>
      <th>Typical Value</th>
      <th>Maximum Limit</th>
      <th>Maximum Value</th>
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

RESULTS_PLOTS_TEMPLATE = jinja2.Template(
    """
{% for div in divs %}
{{ div | safe }}
{% endfor %}
"""
)

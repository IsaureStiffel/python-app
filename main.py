from flask import Flask, request, render_template
import logging
import requests
import os
import pandas as pd
import itertools
from google.analytics.data_v1beta import BetaAnalyticsDataClient
from google.analytics.data_v1beta.types import RunReportRequest

from google.auth.transport.requests import Request
from google.oauth2 import service_account
from googleapiclient.discovery import build

app = Flask(__name__)

logging.basicConfig(level=logging.DEBUG)

@app.route('/fetch-google-analytics-data', methods=['GET'])
def fetch_google_analytics_data():
    os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = 'datasourcelab2-c38acbab07a1.json'
    PROPERTY_ID = '407471832'
    starting_date = "28daysAgo"
    ending_date = "yesterday"

    client = BetaAnalyticsDataClient()
    
    def get_visitor_count(client, property_id):
        request = RunReportRequest(
            property=f"properties/{property_id}",
            date_ranges=[{"start_date": starting_date, "end_date": ending_date}],
            metrics=[{"name": "activeUsers"}]
        )

        response = client.run_report(request)

        # return active_users_metric
        return response

    # Get the visitor count using the function
    response = get_visitor_count(client, PROPERTY_ID)

    if response and response.row_count > 0:
        metric_value = response.rows[0].metric_values[0].value
    else:
        metric_value = "N/A"  # Handle the case where there is no data

    return f'Number of active visitors : {metric_value}'


@app.route("/")
def hello_world():
 prefix_google = """
 <!-- Google tag (gtag.js) -->
<script async
src="https://www.googletagmanager.com/gtag/js?id=G-E44BHZD8C7"></script>
<script>
 window.dataLayer = window.dataLayer || [];
 function gtag(){dataLayer.push(arguments);}
 gtag('js', new Date());
 gtag('config', ' G-E44BHZD8C7');
</script>
 """
 page =  """
 <br></br>
<a href="/logger">
    Go to logger page 
</a>
<br></br>
<a href="/google-request">
    Go to google requests and cookies page 
</a>
<br></br>
<a href="/fetch-google-analytics-data">
    Check Google Analytics Request Visitors 
</a>
"""
 return prefix_google + "Hello World" + page

@app.route("/logger", methods=['GET', 'POST'])
def logger():
    # Log on the Python side (server-side)
    python_log = "This is a python log."
    app.logger.info("This is a python log.")

    # Log on the browser (client-side) using JavaScript
    browser_log = """
    <script>
        console.log("This is a browser log.");
    </script>
    """

    if request.method == 'POST':
        # Récupérer le texte entré dans la boîte de texte
        text_from_textbox = request.form['textbox']

        # Print a message in the browser console with the text from the text box
        browser_log = f"""
        <script>
            console.log('Web browser consol: You are connected to a log page');
            console.log('Text from the text box : {text_from_textbox}');
        </script>
        """
    else:
        # Print a message in the browser console
        browser_log = """
        <script>
            console.log('Web browser consol: You are connected to a log page');
        </script>
        """

    # Formulaire HTML avec une boîte de texte and a button
    form = """
    <form method="POST">
        <label for="textbox">Text Box :</label><br>
        <input type="text" id="textbox" name="textbox"><br><br>
        <input type="submit" value="Soumettre">
    </form>
    """
    return python_log + browser_log + form

@app.route('/google-request', methods=['GET'])
def google_request():
    # Render a form with a button to make the Google request
    return """
    <form method="GET" action="/perform-google-request">
        <input type="submit" value="Make Google Request">
    </form>
    <form method="GET" action="/perform-google-request-cookies">
        <input type="submit" value="Check Google Analytics Request Cookies">
    </form>
    """

@app.route('/perform-google-request', methods=['GET'])
def perform_google_request():
    google_url = "https://www.google.com/"
    google_analytics_url = "https://analytics.google.com/analytics/web/#/p407471832/reports/home"

    try:
        response = requests.get(google_analytics_url)
        response.raise_for_status()  # Raise an exception for HTTP errors

        return response.text
    except requests.exceptions.RequestException as e:
        return f"Error making Google Analytics request: {str(e)}"
    
@app.route('/perform-google-request-cookies', methods=['GET'])
def perform_google_request_cookies():
    google_url = "https://www.google.com/"
    google_analytics_url = "https://analytics.google.com/analytics/web/#/p407471832/reports/home"

    try:
        response = requests.get(google_analytics_url)
        response.raise_for_status()  # Raise an exception for HTTP errors

        # Retrieve cookies of the response
        cookies = response.cookies

        # Send cookies to the template for display
        return render_template('cookies.html', cookies=cookies)
            
    except requests.exceptions.RequestException as e:
        return f"Error making Google Analytics Cookies request: {str(e)}"


if __name__ == '__main__':
    app.run(debug=True)
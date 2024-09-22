import logging
import requests
from flask import Flask, render_template, request
from datetime import datetime

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
)

logger = logging.getLogger(__name__)

app = Flask(__name__)

def format_datetime(datetime_str, utc_offset, abbreviation):
    dt = datetime.fromisoformat(datetime_str)
    formatted_date = dt.strftime("%A %H:%M - %B %d, %Y")
    result = f"{formatted_date} ({utc_offset} {abbreviation})"
    return result

def query_time(ip):
    try:
        response = requests.get(
            url=f"http://worldtimeapi.org/api/ip/{ip}",
            timeout=5
        )

        if response.status_code == 200:
            data = response.json()

            time = data.get("datetime")[slice(11, 16)]

            update_ui = {
                "time": time,
                "timezone": data.get("timezone", "Unknown"),
                "datetime": format_datetime(data.get("datetime", "Unknown"), data.get("utc_offset", "Unknown"), data.get("abbreviation", "Unknown")),
                "utc_offset": data.get("utc_offset", "Unknown"),
                "abbreviation": data.get("abbreviation", "Unknown")
            }
            
            logger.info('Successfully queried public API')

            return update_ui
        else:
            logger.error(f"Error querying API. Status code: {response.status_code}")
            return "Unavailable"  
    except Exception:
        logger.error('Failed to contact public API', exc_info=True)
        return "Unavailable"
    
def get_timezones():
    try:
        response = requests.get(
            url="https://worldtimeapi.org/api/timezone",
            timeout=5
        )

        if response.status_code == 200:
            data = response.json()
            return data
    except Exception:
        logger.error('Failed to contact public API', exc_info=True)
        return "Unavailable"

def get_ip(web_request):
    if 'X-Forwarded-For' in web_request.headers:
        xforwardfor = web_request.headers['X-Forwarded-For'].split(',')[0].strip()
        return xforwardfor
    else:
        return web_request.remote_addr

@app.route("/")
def index():
    ip = get_ip(request)
    update_ui = query_time(ip)
    timezones = get_timezones()
    return render_template('index.html', update_ui=update_ui, timezones=timezones, ip=ip)
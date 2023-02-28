import requests
from bs4 import BeautifulSoup
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

TRAIN_ROW_CELL_PARSE_KEYS = {
    0: 'time_departure',
    1: 'id',
    2: 'time_arrival',
    3: 'time_duration',
    4: 'count_transfer'
}


def parse_train_row(train_row):
    train_data = {}
    train_cells = train_row.find_all('div', {'class': 'col-1-7 cell'})
    for i, cell in enumerate(train_cells):
        cell_data = cell.getText()
        if i in (1, 4):
            cell_data = int(cell_data)
        train_data[TRAIN_ROW_CELL_PARSE_KEYS[i]] = cell_data
    return train_data


def get_trains(start_id, dest_id, departure_date):
    url = f"https://prodaja.hzpp.hr/hr/Ticket/Journey?StartId={start_id}&DestId={dest_id}&ReturnTrip=false&DepartureDate={departure_date}&ReturnDepartureDate={departure_date}"
    response = requests.get(url)
    soup = BeautifulSoup(response.text, features='html.parser')
    soup_train_rows = soup.find('div', {'id': 'tt_Result'}).find_all(
        'div', {'class': 'item row'})
    trains = [parse_train_row(train_row) for train_row in soup_train_rows]
    return trains


@app.route('/trains', methods=['GET'])
def get_train_data():
    start_id = request.args.get('start')
    dest_id = request.args.get('destination')
    departure_date = request.args.get('departure_date')
    if not all([start_id, dest_id, departure_date]):
        return "Missing one or more required parameters", 400
    trains = get_trains(start_id, dest_id, departure_date)
    return jsonify(trains)


@app.route('/stations', methods=['GET'])
def get_stations():
    stations_url = 'http://www.hzpp.hr/CorvusTheme/Timetable/Locs'
    response = requests.get(stations_url)
    stations_str = response.text.replace('var locs = ', '')
    stations = [
        {'id': int(station[0]), 'name': station[1]} for station in eval(stations_str)
    ]
    return {'stations': stations}


if __name__ == '__main__':
    app.run()

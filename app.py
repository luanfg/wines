# -*- coding: utf-8 -*-
from flask import Flask, jsonify, request
import pandas as pd

app = Flask(__name__)

input_file = './wine-raitings-small.csv'

try:
    # Ler o CSV sem definir o índice
    data_frame = pd.read_csv(input_file)
    
    # Verifique se os dados foram lidos corretamente
    print(data_frame.head())
    
except FileNotFoundError:
    print("Arquivo CSV não encontrado.")
    data_frame = pd.DataFrame()
    
data_frame = data_frame.loc[:, ~data_frame.columns.str.contains('^Unnamed')]

def save_data():
    data_frame.to_csv(input_file, index=False)
@app.route('/api/data', methods=['GET'])
def get_data():
    if data_frame.empty:
        return jsonify({"error": "Nenhum dado disponível"}), 500

    data_as_dict = data_frame.to_dict(orient='records')
    return jsonify(data_as_dict)


#atualizar os comentarios sobre os vinhos
@app.route('/api/data/<string:name>/<string:notes>', methods=['PATCH'])
def update_data(name, notes):
    name = name.replace('%20', ' ')
    notes = notes.replace('%20', ' ') 

    if name in data_frame['name'].values:
        data_frame.loc[data_frame['name'] == name, 'notes'] = notes
        save_data()

        modified_row = data_frame.loc[data_frame['name'] == name]

        data_as_dict = modified_row.to_dict(orient='records')
        
        return jsonify(data_as_dict), 200
    else:
        return jsonify({"error": "Nome do vinho não encontrado"}), 404

@app.route('/api/data/<string:name>', methods=['DELETE'])
def delete_data(name):
    global data_frame
    
    name = name.replace('%20', ' ')
    
    if name in data_frame['name'].values:
        data_frame = data_frame[data_frame['name'] != name]
        save_data()
    
        return jsonify({"message": "Registro deletado com sucesso"}), 200
    else:
        return jsonify({"error": "Nome do vinho não encontrado"}), 404

@app.route('/api/data', methods=['POST'])
def insert_data():
    global data_frame

    new_data = request.get_json()

    if data_frame.empty:
        data_frame = pd.DataFrame(columns=new_data.keys())

    new_data_df = pd.DataFrame([new_data])
    data_frame = pd.concat([data_frame, new_data_df], ignore_index=True)

    save_data()

    return jsonify({'message': 'Data added successfully'}), 201

if __name__ == '__main__':
    app.run(debug=True, port=5001)

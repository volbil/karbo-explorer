from flask import Flask, jsonify, render_template
from flask_restful import Api
import core.rest as rest
import core.config as config

app = Flask(__name__,
			static_folder='./frontend/static',
			template_folder='./frontend')
api = Api(app)

api.add_resource(rest.GetInfo, '/api/getinfo')
api.add_resource(rest.BlockByHeight, '/api/height/<int:height>')
api.add_resource(rest.BlocksRange, '/api/range/<int:height>')
api.add_resource(rest.BlockHeader, '/api/header/<string:bhash>')
api.add_resource(rest.BlockByHash, '/api/block/<string:bhash>')
api.add_resource(rest.TransactionInfo, '/api/transaction/<string:thash>')
api.add_resource(rest.TransactionInfoPaymentId, '/api/id/<string:payid>')
api.add_resource(rest.MempoolInfo, '/api/mempool')

@app.errorhandler(404)
def own_404_page(error):
	return jsonify({'error': 'Request failed', 'data': {}})

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def catch_all(path):
	return render_template("index.html")

if __name__ == '__main__':
	app.run(debug=config.debug, host=config.host, port=config.port)

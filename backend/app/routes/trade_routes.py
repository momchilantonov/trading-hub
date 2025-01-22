from flask import Blueprint

trade_bp = Blueprint('trade', __name__)


# Placeholder for trade routes
@trade_bp.route('/', methods=['GET'])
def get_trades():
    return {"message": "Trades endpoint"}, 200

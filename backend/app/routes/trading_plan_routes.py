from flask import Blueprint

trading_plan_bp = Blueprint('trading_plan', __name__)


# Placeholder for trading plan routes
@trading_plan_bp.route('/', methods=['GET'])
def get_trading_plans():
    return {"message": "Trading plans endpoint"}, 200

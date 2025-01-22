from flask import Blueprint
from .auth_routes import auth_bp
from .trading_plan_routes import trading_plan_bp
from .trade_routes import trade_bp
from .journal_routes import journal_bp
from .analysis_routes import analysis_bp

api_bp = Blueprint('api', __name__)


def register_routes(app):
    """Register all blueprints with the app"""
    app.register_blueprint(auth_bp, url_prefix='/api/v1/auth')
    app.register_blueprint(trading_plan_bp, url_prefix='/api/v1/trading-plans')
    app.register_blueprint(trade_bp, url_prefix='/api/v1/trades')
    app.register_blueprint(journal_bp, url_prefix='/api/v1/journal')
    app.register_blueprint(analysis_bp, url_prefix='/api/v1/analysis')

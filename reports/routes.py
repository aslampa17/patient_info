from . import reports_bp

@reports_bp.route("/reports/dashboard")
def dashboard():
    return "<h1>Welcome to Reports</h1>"
"""
Allow tentd to be run as a module

python -m tentd ...
"""

from tentd import app

app.run(debug=True)

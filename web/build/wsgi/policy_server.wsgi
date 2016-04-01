activate_this = "<path>/activate_this.py"
execfile(activate_this, dict(__file__=activate_this))
import sys
sys.path.insert(0, '<root-path>')
from policy_server import policy_app as application



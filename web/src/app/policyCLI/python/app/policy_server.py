#!/usr/bin/env python
import flask
import policy
app = flask.Flask(__name__)

@app.route('/getPolicy')
def getPolicy():
    '''Get the policy for the given identifier'''
    response = "Unrecognised request", 400
    input_args = flask.request.args
    if 'identifier' in input_args:
        response = policy.download(input_args['identifier'])
    return response

if __name__ == '__main__':
  app.run(debug=True)

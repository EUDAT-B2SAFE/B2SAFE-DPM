# Data Policy Manager (B2Save-DPM)
This package contains the code for the web-based data policy manager interface.
The interface allows users to create and download policies. The users needs
to be a valid community manager and needs to register with the DPM. Once
authorised the user can create policies, list all the policies they are
permitted to see and download policies.

## Building the software
The DPM consists of html, javascript, css and python scripts that need
to be assembled for deployment. The assembly is done using the grunt
task manager tool.

1. If you don't have node (http://nodejs.org/) installed then download and
   install it.
2. Install the grunt command line interface
   (http://gruntjs.com/getting-started) globally (you may need to be root to
   be root to do this): 
'''
npm install -g grunt-cli
'''
3. You should now be in a position to build the software. Run:
'''
grunt build
'''
This will run a number of tasks that effectively 'compile' the scripts
and store them in under the build directory.

4. Copy the build/cgi scripts to your web server cgi-bin area. Copy the other directories
   to the web server web page area.
5. Cd `build/admin` and run the script to create the databases used by the dpm:
'''
./populate_db.py resource
./populate_db.py action
'''
6. You should now be able to navigate to the DPM and use it.

Comments:
adilhasan2@gmail.com

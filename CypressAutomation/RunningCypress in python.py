import os
import subprocess

#os.chdir('./CypressAutomation')
#print(os.getcwd())
#print (subprocess.Popen("echo Hello World", shell=True, stdout=subprocess.PIPE).stdout.read())


#process = subprocess.Popen("cd", cwd="./CypressAutomation", shell=True)

subprocess.run('.\node_modules\.bin\cypress run --spec "cypress\integration\examples\PlumeAutomation.js" ', shell=True, capture_output=True)

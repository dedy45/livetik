import base64
content=open("livetik/apps/worker/scripts/manager_template.txt","rb").read()
print(base64.b64encode(content).decode())

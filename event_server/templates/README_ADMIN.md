# Admin Template Note

The admin page is NOT served from `admin.html.source`. 

It's embedded as a string in `/home/ubuntu/structured-transparency/event_server/app.py` starting at line 18.

## To update the admin page:
1. Edit `admin.html.source`
2. Run this command to sync it to app.py:
   ```bash
   python3 << 'PYSCRIPT'
   with open('event_server/templates/admin.html.source', 'r') as f:
       template = f.read()
   with open('event_server/app.py', 'r') as f:
       app_content = f.read()
   import re
   app_content = re.sub(r'admin_html = """.*?"""', f'admin_html = """{template}"""', app_content, flags=re.DOTALL)
   with open('event_server/app.py', 'w') as f:
       f.write(app_content)
   print("Admin HTML synced to app.py")
   PYSCRIPT
   ```
3. Rebuild: `./build.sh`

import os, shutil

BASE = "./vault"
NOTES = os.path.join(BASE, "notes")
ATT = os.path.join(BASE, "attachments")

os.makedirs(NOTES, exist_ok=True)
os.makedirs(ATT, exist_ok=True)

for root, dirs, files in os.walk(BASE):
    for f in files:
        path = os.path.join(root, f)

        if f.endswith(".md"):
            shutil.move(path, os.path.join(NOTES, f))

        elif not f.endswith(".py"):
            shutil.move(path, os.path.join(ATT, f))

print("Vault reorganizado.")

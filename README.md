## Setup

**Install dependencies** TODO: change to requirements.txt
```bash
pip install paramiko textual python-dotenv
```

**Configure environment variables**

Copy the template and fill in real values:

```bash
# .env
JIG2_HOST=raspberrypi1.local
JIG2_USER=pi
JIG2_KEY_PATH=/home/youruser/.ssh/id_rsa
JIG2_PASSWORD=pass

JIG3_HOST=raspberrypi2.local
JIG3_USER=pi
JIG3_KEY_PATH=/home/youruser/.ssh/id_rsa
JIG3_PASSWORD=pass
```

## Running

```bash
python3 main.py
```

Both jigs will attempt to connect on launch. Once connected, click `Run` on any stage to execute it. Input may be provided via the "Response..." field.

## Moving Forward

- Keep it easily scalable for when more jigs are built.
- Create lock around attempting to run multiple stages on the same jig at the same time.
- `ctrl-c` button to interrupt on freeze/fail.
## Setup

**Install dependencies** TODO: change to requirements.txt
```bash
pip install paramiko textual python-dotenv
```

## Libraries used

| Library | Purpose |
|---|---|
| [`paramiko`](https://www.paramiko.org/) | Handles the SSH connections to each Pi — opens the session, runs commands (`exec_command`), and streams stdout/stderr back over a channel. Also used to send input (Continue button) and Ctrl+C (Stop button) directly into the running remote process via the same channel. |
| [`textual`](https://textual.textualize.io/) | The TUI framework — renders the whole dashboard (jig columns, stage panels, buttons, inputs, live log widgets) and handles layout, styling (via `dashboard.tcss`), and event handling (button clicks, input submission). Also provides the background worker system (`@work(thread=True)`) used to run blocking SSH calls off the main UI thread. |
| [`python-dotenv`](https://pypi.org/project/python-dotenv/) | Loads connection credentials (host, user, key path) from a `.env` file into environment variables at startup, so secrets stay out of `config.py` and out of version control. |

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
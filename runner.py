# runner.py — SSH connection + stage execution, no UI knowledge

import paramiko

class StageRunner:
    def __init__(self, host, user, key_path=None, password=None, port=22):
        self.client = paramiko.SSHClient()
        self.client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        self.host = host
        self.user = user
        self.key_path = key_path
        self.password = password
        self.port = port

    def connect(self):
        if self.key_path:
            self.client.connect(
                self.host, port=self.port, username=self.user,
                key_filename=self.key_path
            )
        else:
            self.client.connect(
                self.host, port=self.port, username=self.user,
                password=self.password
            )

    def run_stage(self, command: str):
        """Generator: yields ('channel', channel) first so the caller can
        send input, then ('line', text) as output arrives,
        then ('done', exit_code) when finished."""
        stdin, stdout, stderr = self.client.exec_command(command, get_pty=True)
        channel = stdout.channel
        yield ("channel", channel)

        while True:
            if channel.recv_ready():
                chunk = channel.recv(1024).decode(errors="replace")
                for line in chunk.splitlines():
                    yield ("line", line)

            if channel.exit_status_ready() and not channel.recv_ready():
                yield ("done", channel.recv_exit_status())
                break

    def close(self):
        self.client.close()
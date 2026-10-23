"""Operator-owned Docker session for P01. No shell command or model interface."""

import argparse
import os
from pathlib import Path
import selectors
import stat
import subprocess
import sys
import time

from .contract import CONTRACT, CONTRACT_SHA, ROOT, decode, encode, sha, validate_manifest
from .prepare import read_source, save


COMMAND = ["-I", "-B", "-u", "/app/backend.py"]
PROBE = r'''
import errno,json,os,socket
from pathlib import Path
assert os.getuid()==65532
status=Path('/proc/self/status').read_text()
assert 'NoNewPrivs:\t1' in status
assert int(next(x.split()[1] for x in status.splitlines() if x.startswith('CapEff:')),16)==0
assert not Path('/var/run/docker.sock').exists()
assert not any(k.startswith(('OPENAI_','ANTHROPIC_','AWS_','GOOGLE_','AZURE_')) for k in os.environ)
for path in ['/root/p01-probe','/app/p01-probe','/data/inputs/p01-probe']:
    try:
        with open(path,'xb') as f: f.write(b'x')
    except OSError as e:
        assert e.errno in (errno.EROFS,errno.EACCES)
    else: raise AssertionError('Read-only boundary missing')
p=Path('/data/outputs/.p01-probe'); p.write_bytes(b'x'); p.unlink()
s=socket.socket(); s.settimeout(.25)
try:
    s.connect(('198.51.100.1',443))
except OSError as e:
    assert e.errno==errno.ENETUNREACH
else: raise AssertionError('Network unexpectedly available')
finally: s.close()
print(json.dumps({'uid':os.getuid(),'network':'unreachable','readonly':True,'caps':0,'no_new_privs':True}))
'''


def docker(*args):
    result = subprocess.run(["docker", *args], capture_output=True, timeout=15)
    if result.returncode:
        raise RuntimeError("Docker operation refused or unavailable")
    if len(result.stdout) > 8 * 1024 * 1024:
        raise RuntimeError("Docker response too large")
    return result.stdout


def verify_workspace(root):
    for directory in ("runtime", "inputs", "outputs", "controle"):
        info = (root / directory).lstat()
        if not stat.S_ISDIR(info.st_mode) or getattr(info, "st_file_attributes", 0) & 0x400:
            raise ValueError("Ordinary workspace directories required")
    record = decode(read_source(root, "controle/manifest.json"))
    if (record["format"] != 1 or record["contract_sha256"] != CONTRACT_SHA
            or record["image"] != CONTRACT["image"] or record["platform"] != CONTRACT["platform"]):
        raise ValueError("Frozen contract mismatch")
    sources = ("prepare.py", "container.py", "backend.py", "contract.py")
    if set(record["source_sha256"]) != set(sources):
        raise ValueError("Frozen source inventory mismatch")
    for name in sources:
        if sha(read_source(ROOT, name)) != record["source_sha256"][name]:
            raise ValueError("Frozen implementation changed; prepare a new run")
    for directory, fingerprints in (("runtime", record["runtime"]), ("controle", record["private"])):
        for name, fingerprint in fingerprints.items():
            if sha(read_source(root, directory + "/" + name)) != fingerprint:
                raise ValueError("Frozen file changed")
    if set(p.name for p in (root / "runtime").iterdir()) != set(record["runtime"]):
        raise ValueError("Unexpected runtime file")
    actual = set()
    for parent, directories, files in os.walk(root / "inputs", followlinks=False):
        for name in directories:
            if (Path(parent) / name).is_symlink():
                raise ValueError("Input directory link")
        actual.update((Path(parent) / name).relative_to(root / "inputs").as_posix() for name in files)
    if actual != set(record["inputs"]):
        raise ValueError("Unexpected input file")
    for name, info in record["inputs"].items():
        raw = read_source(root / "inputs", name)
        if dict(bytes=len(raw), sha256=sha(raw)) != info:
            raise ValueError("Frozen input changed")
    manifest = validate_manifest(decode(read_source(root, "runtime/backend-manifest.json")))
    if manifest["run_id"] != record["run_id"] or manifest["inputs"] != record["inputs"] or manifest["outputs"] != record["outputs"]:
        raise ValueError("Backend binding changed")
    for path in (root / "outputs").rglob("*"):
        if path.is_symlink() or not path.is_dir():
            raise ValueError("Outputs must be empty before first start")
    return record


def create_command(root, run_id):
    cfg = CONTRACT["container"]
    args = ["create", "--pull=never", "--name", "orka-sdk-inspect-" + run_id,
            "--label", cfg["label"] + "=" + run_id, "--platform", CONTRACT["platform"],
            "--user", cfg["user"], "--network", "none", "--read-only", "--ipc", "none",
            "--cap-drop", "ALL", "--security-opt", "no-new-privileges", "--pids-limit", str(cfg["pids"]),
            "--memory", str(cfg["memory"]), "--memory-swap", str(cfg["memory"]), "--cpus", "0.5",
            "--tmpfs", cfg["tmpfs"], "--entrypoint", "python", "-i"]
    for folder, target, ro in (("runtime", "/app", True), ("inputs", "/data/inputs", True),
                               ("outputs", "/data/outputs", False)):
        path = str(root / folder)
        if "," in path or "\n" in path:
            raise ValueError("Unrepresentable bind path")
        args += ["--mount", f"type=bind,src={path},dst={target}" + (",readonly" if ro else "")]
    return args + [CONTRACT["image"], *COMMAND]


def verify_container(info, root, run_id, image):
    cfg, host = info["Config"], info["HostConfig"]
    expected = {"/app": (str(root / "runtime"), False), "/data/inputs": (str(root / "inputs"), False),
                "/data/outputs": (str(root / "outputs"), True)}
    observed = {m["Destination"]: (m["Source"], m["RW"]) for m in info["Mounts"]}
    if (len(info["Mounts"]) != 3 or observed != expected
            or any(m["Type"] != "bind" for m in info["Mounts"])
            or info["Image"] != image["Id"] or cfg["Image"] != CONTRACT["image"]
            or cfg["User"] != CONTRACT["container"]["user"] or cfg["Entrypoint"] != ["python"] or cfg["Cmd"] != COMMAND
            or cfg["Env"] != image["Config"]["Env"] or cfg["Labels"].get(CONTRACT["container"]["label"]) != run_id
            or host["NetworkMode"] != "none" or not host["ReadonlyRootfs"] or host["Privileged"]
            or host["CapDrop"] != ["ALL"] or host.get("CapAdd") or host.get("Devices")
            or host["SecurityOpt"] != ["no-new-privileges"] or host["PidsLimit"] != CONTRACT["container"]["pids"]
            or host["Memory"] != CONTRACT["container"]["memory"] or host["MemorySwap"] != host["Memory"]
            or host["NanoCpus"] != 500000000 or host["IpcMode"] != "none" or host.get("PidMode")
            or host["Tmpfs"] != {"/tmp": CONTRACT["container"]["tmpfs"].split(":", 1)[1]}
            or host.get("PortBindings") or host.get("VolumesFrom") or host.get("Binds")
            or info["Platform"] != "linux" or image["Architecture"] != CONTRACT["platform"].split("/")[1]):
        raise ValueError("Effective container restrictions mismatch")


class Session:
    def __init__(self, root):
        self.root = Path(root).resolve(strict=True)
        if os.path.lexists(self.root / "controle/started.json"):
            raise FileExistsError("Run already started; reservation preserved")
        self.record = verify_workspace(self.root)
        self.run_id = self.record["run_id"]
        self.name = "orka-sdk-inspect-" + self.run_id
        self.process = None
        self.buffer = b""
        self.sequence = 0
        self.deadline = time.monotonic() + CONTRACT["limits"]["seconds"]
        self.removed = False
        save(self.root / "controle/started.json", encode(dict(run_id=self.run_id)), 0o600)
        try:
            image = decode(docker("image", "inspect", CONTRACT["image"]))[0]
            docker(*create_command(self.root, self.run_id))
            info = self.inspect()
            verify_container(info, self.root, self.run_id, image)
            save(self.root / "controle/container-before.json", encode(info), 0o600)
            self.process = subprocess.Popen(["docker", "start", "-ai", self.name], stdin=subprocess.PIPE,
                                            stdout=subprocess.PIPE, stderr=subprocess.PIPE, bufsize=0)
            ready = self.receive()
            if ready != dict(ready=True, run_id=self.run_id, contract_sha256=CONTRACT_SHA):
                raise ValueError("Worker binding mismatch")
            probe = decode(docker("exec", self.name, "python", "-I", "-B", "-c", PROBE))
            save(self.root / "controle/isolation.json", encode(probe), 0o600)
            verify_container(self.inspect(), self.root, self.run_id, image)
        except (OSError, ValueError, RuntimeError):
            self.close()
            raise RuntimeError("File worker failed; no retry") from None
        except BaseException:
            self.close()
            raise

    def inspect(self):
        info = decode(docker("inspect", self.name))[0]
        if info["Config"]["Labels"].get(CONTRACT["container"]["label"]) != self.run_id:
            raise ValueError("Container ownership mismatch")
        return info

    def receive(self):
        deadline = min(self.deadline, time.monotonic() + CONTRACT["limits"]["operation_seconds"])
        with selectors.DefaultSelector() as ready:
            ready.register(self.process.stdout, selectors.EVENT_READ)
            while b"\n" not in self.buffer:
                if not ready.select(max(0, deadline - time.monotonic())):
                    raise TimeoutError("File worker deadline")
                data = os.read(self.process.stdout.fileno(), 8192)
                if not data:
                    raise RuntimeError("File worker stopped")
                self.buffer += data
                if len(self.buffer) > 6 * CONTRACT["limits"]["read_bytes"] + 8192:
                    raise ValueError("Worker response too large")
        line, self.buffer = self.buffer.split(b"\n", 1)
        return decode(line)

    def call_raw(self, raw):
        if self.removed or self.process is None:
            raise RuntimeError("Session closed")
        try:
            if len(raw) > CONTRACT["limits"]["request_bytes"]:
                raise ValueError("Request too large")
            if b"\n" in raw or b"\r" in raw:
                raise ValueError("Exactly one JSON frame required")
            self.process.stdin.write(raw + b"\n")
            response = self.receive()
            self.sequence += 1
            if response["run_id"] != self.run_id or response["sequence"] != self.sequence:
                raise ValueError("Uncorrelated worker response")
            with (self.root / "controle/events.jsonl").open("ab") as journal:
                journal.write(encode(dict(request_sha256=sha(raw), **response)) + b"\n")
            return response["resultat"]
        except (OSError, ValueError, RuntimeError):
            self.close()
            raise RuntimeError("File worker failed; no retry") from None
        except BaseException:
            self.close()
            raise

    def call(self, name, arguments):
        return self.call_raw(encode(dict(outil=name, arguments=arguments)))

    def close(self):
        if self.removed:
            return
        if self.process:
            self.process.stdin.close()
            try:
                self.process.wait(timeout=2)
            except subprocess.TimeoutExpired:
                pass
        try:
            info = self.inspect()
        except RuntimeError:
            # Container was never created. A start receipt still prevents reusing this run.
            if self.process is not None:
                raise
            return
        if info["State"]["Running"]:
            docker("kill", self.name)
        docker("wait", self.name)
        info = self.inspect()
        if info["State"]["Running"]:
            raise RuntimeError("Writer stop unconfirmed; reservation retained")
        receipt = self.root / "controle/stopped.json"
        if receipt.exists():
            previous = decode(read_source(self.root, "controle/stopped.json"))
            if previous["run_id"] != self.run_id or previous["state"]["Running"]:
                raise ValueError("Inconsistent stop receipt")
        else:
            save(receipt, encode(dict(run_id=self.run_id, state=info["State"])), 0o600)
        docker("rm", self.name)
        self.removed = True
        if self.process:
            self.process.wait(timeout=5)
            self.process.stdout.close()
            self.process.stderr.close()

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        self.close()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--workspace", type=Path, required=True)
    args = parser.parse_args()
    try:
        with Session(args.workspace) as session:
            for line in sys.stdin.buffer:
                result = session.call_raw(line.rstrip(b"\n"))
                sys.stdout.buffer.write(encode(result) + b"\n")
                sys.stdout.buffer.flush()
    except (OSError, ValueError, RuntimeError):
        parser.exit(2, "Backend refused or stopped\n")


if __name__ == "__main__":
    main()

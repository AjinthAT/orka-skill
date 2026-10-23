"""Linux-only file worker. Exactly three operations; no model, shell or network."""

import argparse
import ctypes
import errno
import os
from pathlib import Path
import platform
import signal
import stat
import sys
import time

if __package__:
    from .contract import CONTRACT, decode, encode, logical, sha, validate_manifest
else:
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    from contract import CONTRACT, decode, encode, logical, sha, validate_manifest


class Refused(Exception):
    def __init__(self, code):
        self.code = code


class OpenHow(ctypes.Structure):
    _fields_ = [("flags", ctypes.c_uint64), ("mode", ctypes.c_uint64), ("resolve", ctypes.c_uint64)]


def open_beneath(root_fd, name, flags, mode=0):
    # openat2(2), Linux asm-generic syscall 437 on these two supported targets.
    if sys.platform != "linux" or platform.machine() not in ("aarch64", "x86_64"):
        raise RuntimeError("Linux openat2 required; no pathname fallback")
    libc = ctypes.CDLL(None, use_errno=True)
    libc.syscall.restype = ctypes.c_long
    how = OpenHow(flags | os.O_CLOEXEC | os.O_NOFOLLOW | os.O_NONBLOCK, mode, 0x01 | 0x04 | 0x08)
    fd = libc.syscall(ctypes.c_long(437), ctypes.c_int(root_fd), ctypes.c_char_p(name.encode("utf-8")),
                      ctypes.byref(how), ctypes.c_size_t(ctypes.sizeof(how)))
    if fd < 0:
        error = ctypes.get_errno()
        raise OSError(error, os.strerror(error))
    return fd


def regular(info):
    if not stat.S_ISREG(info.st_mode) or info.st_nlink != 1:
        raise Refused("fichier_refuse")


class Backend:
    def __init__(self, inputs, outputs, manifest):
        self.manifest = decode(encode(validate_manifest(manifest)))
        self.closed = False
        self.calls = self.written = 0
        self.created = {}
        self.deadline = time.monotonic() + CONTRACT["limits"]["seconds"]
        self.roots = []
        try:
            for path in (inputs, outputs):
                fd = os.open(path, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW | os.O_CLOEXEC)
                self.roots.append(fd)
                probe = open_beneath(fd, ".", os.O_RDONLY | os.O_DIRECTORY)
                os.close(probe)  # Fail at startup if openat2 is unavailable/blocked.
            for name in manifest["inputs"]:
                self.read(name)
        except BaseException:
            self.close()
            raise

    def close(self):
        for fd in self.roots:
            os.close(fd)
        self.roots = []
        self.closed = True

    def read(self, name):
        source = name in self.manifest["inputs"]
        if not source and name not in self.created:
            raise Refused("absent")
        fd = open_beneath(self.roots[0 if source else 1], name, os.O_RDONLY)
        with os.fdopen(fd, "rb") as stream:
            before = os.fstat(stream.fileno())
            regular(before)
            raw = stream.read(CONTRACT["limits"]["read_bytes"] + 1)
            after = os.fstat(stream.fileno())
            regular(after)
        if len(raw) > CONTRACT["limits"]["read_bytes"]:
            raise Refused("quota")
        info = {"sha256": sha(raw), "bytes": len(raw)}
        expected = self.manifest["inputs"][name] if source else self.created[name]
        if (info != expected or (before.st_ino, before.st_dev, before.st_size, before.st_mtime_ns, before.st_ctime_ns)
                != (after.st_ino, after.st_dev, after.st_size, after.st_mtime_ns, after.st_ctime_ns)):
            raise Refused("integrite")
        return dict(chemin=name, contenu=raw.decode("utf-8"), **info)

    def write(self, name, content):
        raw = content.encode("utf-8")
        limits = CONTRACT["limits"]
        if len(raw) > limits["write_bytes"] or self.written + len(raw) > limits["total_write_bytes"]:
            raise Refused("quota")
        fd = open_beneath(self.roots[1], name, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
        # Never unlink an uncertain/partial write: a repeat must still encounter EEXIST.
        with os.fdopen(fd, "wb") as stream:
            regular(os.fstat(stream.fileno()))
            self.written += len(raw)
            stream.write(raw)
            stream.flush()
            os.fsync(stream.fileno())
            info = os.fstat(stream.fileno())
            regular(info)
            if info.st_size != len(raw):
                raise Refused("integrite")
        self.created[name] = {"bytes": len(raw), "sha256": sha(raw)}
        try:
            checked = self.read(name)  # Reopen under the root and verify actual bytes before success.
        except BaseException:
            self.created.pop(name, None)
            self.closed = True
            raise
        return {key: checked[key] for key in ("chemin", "bytes", "sha256")}

    def handle(self, raw):
        self.calls += 1  # Refused and malformed calls also consume a unit.
        try:
            if self.closed:
                raise Refused("ferme")
            if self.calls > CONTRACT["limits"]["calls"] or time.monotonic() >= self.deadline:
                self.closed = True
                raise Refused("quota")
            if type(raw) is not bytes or len(raw) > CONTRACT["limits"]["request_bytes"]:
                raise Refused("arguments_refuses")
            request = decode(raw.decode("utf-8"))
            if type(request) is not dict or set(request) != {"outil", "arguments"}:
                raise Refused("arguments_refuses")
            tools = {tool["name"]: tool for tool in CONTRACT["tools"]}
            name, args = request["outil"], request["arguments"]
            if type(name) is not str or name not in tools:
                raise Refused("outil_inconnu")
            if (type(args) is not dict or set(args) != set(tools[name]["parameters"]["required"])
                    or any(type(value) is not str for value in args.values())):
                raise Refused("arguments_refuses")
            if name == "lister":
                data = {"fichiers": [dict(chemin=p, droit="lecture", disponible=True)
                                     for p in sorted(self.manifest["inputs"])]
                        + [dict(chemin=p, droit="creation", disponible=p in self.created)
                           for p in sorted(self.manifest["outputs"])]}
            else:
                try:
                    path = logical(args["chemin"])
                except ValueError:
                    raise Refused("chemin_refuse") from None
                if name == "ecrire":
                    if path not in self.manifest["outputs"]:
                        raise Refused("chemin_refuse")
                    data = self.write(path, args["contenu"])
                else:
                    if path not in self.manifest["inputs"] and path not in self.manifest["outputs"]:
                        raise Refused("chemin_refuse")
                    data = self.read(path)
            result = dict(ok=True, code="ok", donnees=data)
        except Refused as exc:
            if exc.code == "quota":
                self.closed = True
            result = dict(ok=False, code=exc.code)
        except (ValueError, UnicodeError, TypeError, RecursionError):
            result = dict(ok=False, code="arguments_refuses")
        except TimeoutError:
            self.closed = True
            result = dict(ok=False, code="delai")
        except OSError as exc:
            code = {errno.ENOENT: "absent", errno.EEXIST: "existe", errno.ELOOP: "fichier_refuse",
                    errno.EXDEV: "fichier_refuse", errno.ENOTDIR: "fichier_refuse"}.get(exc.errno, "erreur_io")
            result = dict(ok=False, code=code)
            if code == "erreur_io":
                self.closed = True
        return dict(run_id=self.manifest["run_id"], sequence=self.calls, resultat=result)


def timeout(signum, frame):
    raise TimeoutError("Worker deadline")


def serve(worker, source, destination):
    signal.signal(signal.SIGALRM, timeout)
    try:
        while not worker.closed:
            signal.setitimer(signal.ITIMER_REAL, max(0.001, worker.deadline - time.monotonic()))
            raw = source.readline(CONTRACT["limits"]["request_bytes"] + 2)
            if not raw:
                break
            signal.setitimer(signal.ITIMER_REAL, min(CONTRACT["limits"]["operation_seconds"],
                                                   max(0.001, worker.deadline - time.monotonic())))
            result = worker.handle(raw)
            destination.write(encode(result) + b"\n")
            destination.flush()
            if len(raw) > CONTRACT["limits"]["request_bytes"]:
                break  # Do not parse an oversized frame's tail as another request.
    finally:
        signal.setitimer(signal.ITIMER_REAL, 0)
        worker.close()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--inputs", default="/data/inputs")
    parser.add_argument("--outputs", default="/data/outputs")
    parser.add_argument("--manifest", default="/app/backend-manifest.json")
    args = parser.parse_args()
    try:
        manifest = decode(Path(args.manifest).read_bytes())
        worker = Backend(args.inputs, args.outputs, manifest)
        print(encode(dict(ready=True, run_id=manifest["run_id"], contract_sha256=manifest["contract_sha256"])).decode(), flush=True)
        serve(worker, sys.stdin.buffer, sys.stdout.buffer)
    except (OSError, ValueError, RuntimeError, Refused, TimeoutError):
        print("Backend stopped or refused", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())

"""Starts the built executable against a throwaway OCI config and checks the menu appears.

Usage: python smoke_test.py <path to executable>

No request is sent to OCI: the program starts, shows the section menu and exits. This is
enough to catch missing modules or data files in the bundle.
"""

import os
import subprocess
import sys
import tempfile
import time
from pathlib import Path

from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa

TIMEOUT_SECONDS = 300


def writeDummyConfig(home):
    ociDir = home / ".oci"
    ociDir.mkdir()

    key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    keyFile = ociDir / "key.pem"
    keyFile.write_bytes(
        key.private_bytes(
            serialization.Encoding.PEM,
            serialization.PrivateFormat.TraditionalOpenSSL,
            serialization.NoEncryption(),
        )
    )

    (ociDir / "config").write_text(
        "[DEFAULT]\n"
        "user=ocid1.user.oc1..aaaaaaaaexample\n"
        "fingerprint=aa:bb:cc:dd:ee:ff:00:11:22:33:44:55:66:77:88:99\n"
        "tenancy=ocid1.tenancy.oc1..aaaaaaaaexample\n"
        "region=us-ashburn-1\n"
        f"key_file={keyFile}\n"
    )


def main():
    exe = Path(sys.argv[1]).resolve()

    if not exe.exists():
        sys.exit(f"Executable not found: {exe}")

    with tempfile.TemporaryDirectory() as tmp:
        home = Path(tmp) / "home"
        work = Path(tmp) / "work"
        home.mkdir()
        work.mkdir()
        writeDummyConfig(home)

        env = {**os.environ, "HOME": str(home), "USERPROFILE": str(home)}

        started = time.time()
        # "0" leaves the section menu, the second newline answers "Press Enter to exit"
        result = subprocess.run(
            [str(exe)],
            input="0\n\n",
            capture_output=True,
            text=True,
            cwd=work,
            env=env,
            timeout=TIMEOUT_SECONDS,
        )
        elapsed = time.time() - started

        print(result.stdout)
        print(result.stderr, file=sys.stderr)
        print(f"Startup and exit took {elapsed:.1f} seconds")

        failures = []

        if result.returncode != 0:
            failures.append(f"exit code {result.returncode}")

        if "Select a section" not in result.stdout:
            failures.append("section menu was not shown")

        if not (work / "reports").is_dir():
            failures.append("reports folder was not created")

        if failures:
            sys.exit("Smoke test FAILED: " + ", ".join(failures))

    print("Smoke test passed")


if __name__ == "__main__":
    main()

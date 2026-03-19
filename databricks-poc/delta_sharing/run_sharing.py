"""
run_sharing.py
==============
Launcher for Delta Sharing simulation.
Choose between Option A (Python simulation) or Option B (OSS server).

Run: python delta_sharing/run_sharing.py
"""

import sys
import os
import subprocess

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
JAR_PATH   = os.path.join(SCRIPT_DIR, "delta-sharing-server.jar")

print("=" * 60)
print("  DELTA SHARING SIMULATION")
print("=" * 60)
print()
print("  Option A — Python Simulation (no extra setup)")
print("    Reads Gold Delta tables directly, simulates the")
print("    provider/recipient pattern using PySpark + Pandas.")
print("    Runs immediately.")
print()
print("  Option B — OSS Delta Sharing Server")
print("    Starts a real HTTP Delta Sharing server locally.")
print("    Vendor client reads via the actual sharing protocol.")

# Warn if JAR is missing for Option B
jar_exists = os.path.exists(JAR_PATH)
if not jar_exists:
    print()
    print("  [!] Option B requires the Delta Sharing server JAR.")
    print("      JAR not found at: delta_sharing/delta-sharing-server.jar")
    print("      Download from: github.com/delta-io/delta-sharing/releases")
    print("      File: delta-sharing-server-x.x.x.zip  →  extract .jar here")

print()
print("-" * 60)
choice = input("  Enter choice (A / B): ").strip().upper()
print("-" * 60)

if choice == "A":
    print("\n  Launching Option A — Python Simulation...\n")
    result = subprocess.run(
        [sys.executable, os.path.join(SCRIPT_DIR, "simulate_sharing.py")],
        cwd=os.path.join(SCRIPT_DIR, ".."),
        capture_output=False
    )
    sys.exit(result.returncode)

elif choice == "B":
    if not jar_exists:
        print("\n  [ERROR] Cannot start Option B — JAR not found.")
        print(f"  Expected at: {JAR_PATH}")
        print()
        print("  Steps to set up Option B:")
        print("  1. Go to: github.com/delta-io/delta-sharing/releases")
        print("  2. Download: delta-sharing-server-x.x.x.zip")
        print("  3. Extract the .jar file")
        print("  4. Rename it to: delta-sharing-server.jar")
        print("  5. Place it in: C:/Projects/databricks-poc/delta_sharing/")
        print("  6. Start the server in a NEW terminal:")
        print("       java -jar delta_sharing/delta-sharing-server.jar \\")
        print("            --config delta_sharing/server_config.yaml")
        print("  7. Then re-run this launcher and choose B")
        sys.exit(1)

    print("\n  Starting OSS Delta Sharing Server...")
    print(f"  JAR: {JAR_PATH}")
    print(f"  Config: delta_sharing/server_config.yaml")
    print()
    print("  Server will start at: http://localhost:8080/delta-sharing")
    print("  Press Ctrl+C to stop the server.")
    print()

    # Start server in background and run client
    server_proc = subprocess.Popen(
        ["java", "-jar", JAR_PATH,
         "--config", os.path.join(SCRIPT_DIR, "server_config.yaml")],
        cwd=os.path.join(SCRIPT_DIR, ".."),
    )

    import time
    print("  Waiting 5 seconds for server to start...")
    time.sleep(5)

    if server_proc.poll() is not None:
        print("\n  [ERROR] Server failed to start. Check Java is installed.")
        print("  Run: java -version")
        sys.exit(1)

    print("  Server running (PID: {})".format(server_proc.pid))
    print("\n  Launching vendor client...\n")

    try:
        client_result = subprocess.run(
            [sys.executable, os.path.join(SCRIPT_DIR, "consume_shared_data.py")],
            cwd=os.path.join(SCRIPT_DIR, ".."),
            capture_output=False
        )
    finally:
        print("\n  Stopping Delta Sharing server...")
        server_proc.terminate()
        server_proc.wait()
        print("  Server stopped.")

    sys.exit(client_result.returncode)

else:
    print(f"\n  [ERROR] Invalid choice '{choice}'. Enter A or B.")
    sys.exit(1)

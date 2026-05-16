"""
Workaround: Test if using IPv6 ::1 (localhost) works instead of 127.0.0.1
Cato Networks WFP filters sometimes only affect IPv4 loopback.
"""
import socket
import sys
import os

OUTPUT_FILE = os.path.join(os.path.dirname(__file__), "diag_results_v6.txt")

def log(msg):
    print(msg, flush=True)
    with open(OUTPUT_FILE, "a") as f:
        f.write(msg + "\n")

def test_ipv6_loopback():
    if os.path.exists(OUTPUT_FILE):
        os.remove(OUTPUT_FILE)
    
    log("=== Testing IPv6 loopback (::1) ===")
    try:
        s = socket.socket(socket.AF_INET6, socket.SOCK_STREAM)
        s.settimeout(5)
        s.bind(('::1', 0))
        port = s.getsockname()[1]
        s.listen(1)
        log(f"[OK] Server listening on [::1]:{port}")
    except Exception as e:
        log(f"[FAIL] Cannot bind to ::1: {e}")
        return False

    try:
        c = socket.socket(socket.AF_INET6, socket.SOCK_STREAM)
        c.settimeout(5)
        c.connect(('::1', port))
        log(f"[OK] Client connected to [::1]:{port}")
    except Exception as e:
        log(f"[FAIL] Cannot connect to [::1]:{port}: {e}")
        s.close()
        return False

    try:
        a, addr = s.accept()
        log(f"[OK] Server accepted connection from {addr}")
        a.close()
        c.close()
        s.close()
        log("[OK] IPv6 loopback works!")
        return True
    except Exception as e:
        log(f"[FAIL] Accept failed: {e}")
        return False

def test_localhost_name():
    if os.path.exists(OUTPUT_FILE):
        pass  # don't remove, append
    
    log("\n=== Testing 'localhost' hostname ===")
    try:
        infos = socket.getaddrinfo('localhost', None, socket.AF_UNSPEC, socket.SOCK_STREAM)
        for info in infos:
            log(f"[INFO] localhost resolves to: {info[0].name} {info[4]}")
    except Exception as e:
        log(f"[FAIL] Cannot resolve localhost: {e}")

if __name__ == '__main__':
    ok = test_ipv6_loopback()
    test_localhost_name()
    log(f"\nIPv6 loopback result: {'PASS' if ok else 'FAIL'}")


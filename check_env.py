try:
    from pythonosc import udp_client
    print("SUCCESS: pythonosc is available.")
except ImportError:
    print("FAILURE: pythonosc is NOT installed.")

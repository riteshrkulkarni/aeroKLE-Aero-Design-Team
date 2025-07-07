import time
import argparse
from dronekit import connect

def check_heartbeat(connection_string, baud_rate):
    print(f"Connecting to Vehicle on {connection_string} at {baud_rate} baud...")
    try:
        vehicle = connect(connection_string, baud=baud_rate, wait_ready=False, heartbeat_timeout=60)
        
        # Wait for the heartbeat by checking if vehicle is initialized
        print("Waiting for heartbeat...")
        start_time = time.time()
        timeout = 20  # Timeout in seconds
        
        while not vehicle.is_armable:
            if time.time() - start_time > timeout:
                print("Failed to receive heartbeat within timeout period.")
                return False
            print("Waiting for vehicle to initialize (checking heartbeat)...")
            time.sleep(1)
        
        # Heartbeat received, print vehicle information
        print("Heartbeat received! Pixhawk is connected.")
        print(f"Vehicle Mode: {vehicle.mode.name}")
        print(f"Armed Status: {vehicle.armed}")
        print(f"GPS Status: {vehicle.gps_0}")
        
        # Close the connection
        vehicle.close()
        print("Connection closed.")
        return True
        
    except Exception as e:
        print(f"Error connecting to vehicle: {e}")
        return False

if __name__ == "__main__":
    # Set up argparse for command-line arguments
    parser = argparse.ArgumentParser(description="Check Pixhawk heartbeat using DroneKit")
    parser.add_argument(
        "--connect",
        type=str,
        default="/dev/serial0",
        help="Connection string for the vehicle (e.g., /dev/serial0 or /dev/ttyAMA0)"
    )
    parser.add_argument(
        "--baud",
        type=int,
        default=921600,
        help="Baud rate for the serial connection (default: 921600)"
    )
    
    # Parse arguments
    args = parser.parse_args()
    
    # Run the heartbeat check
    if check_heartbeat(args.connect, args.baud):
        print("Heartbeat check successful.")
    else:
        print("Heartbeat check failed.")
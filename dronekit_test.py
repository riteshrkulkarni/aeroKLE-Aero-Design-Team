import time
from dronekit import connect, VehicleMode, LocationGlobalRelative
from pymavlink import mavutil

# Connect to the vehicle (replace with your connection string)
connection= 'udp:127.0.0.1:14550'
print(f"Connecting to vehicle on: {connection}")
vehicle = connect(connection, wait_ready=True)

def arm_and_takeoff(target_altitude):
    print("Arming motors...")
    while not vehicle.is_armable:
        print("Waiting for vehicle to become armable...")
        time.sleep(1)
    
    vehicle.mode = VehicleMode("GUIDED")
    vehicle.armed = True
    
    while not vehicle.armed:
        print("Waiting for arming...")
        time.sleep(1)
    
    print(f"Taking off to {target_altitude} meters...")
    vehicle.simple_takeoff(target_altitude)
    
    while True:
        print(f"Altitude: {vehicle.location.global_relative_frame.alt}")
        if vehicle.location.global_relative_frame.alt >= target_altitude * 0.95:
            print("Reached target altitude")
            break
        time.sleep(1)

def goto_position(target_lat, target_lon, target_alt):
    print(f"Going to: Lat {target_lat}, Lon {target_lon}, Alt {target_alt}")
    target_location = LocationGlobalRelative(target_lat, target_lon, target_alt)
    vehicle.simple_goto(target_location)
    
    while True:
        current_location = vehicle.location.global_relative_frame
        distance = get_distance_metres(current_location, target_location)
        print(f"Distance to target: {distance:.2f} meters")
        if distance < 1.0:
            print("Reached target location")
            break
        time.sleep(1)

def get_distance_metres(loc1, loc2):
    from math import sqrt
    dlat = loc2.lat - loc1.lat
    dlon = loc2.lon - loc1.lon
    return sqrt((dlat * 1.113195e5) ** 2 + (dlon * 1.113195e5) ** 2)

def send_ned_velocity(velocity_x, velocity_y, velocity_z, duration):
    print(f"Sending NED velocity: {velocity_x}m/s N, {velocity_y}m/s E, {velocity_z}m/s D")
    msg = vehicle.message_factory.set_position_target_local_ned_encode(
        0, 0, 0,
        mavutil.mavlink.MAV_FRAME_LOCAL_NED,
        0b0000111111000111,  # Only velocity components
        0, 0, 0,  # Position
        velocity_x, velocity_y, velocity_z,  # Velocity
        0, 0, 0,  # Acceleration
        0, 0)  # Yaw, yaw rate
    for _ in range(0, duration):
        vehicle.send_mavlink(msg)
        time.sleep(1)

# Main execution
try:
    # Arm and takeoff to 10 meters
    arm_and_takeoff(10)
    
    # Go to a specific GPS location (replace with your coordinates)
    target_lat = vehicle.location.global_frame.lat + 0.0001  # 100m north
    target_lon = vehicle.location.global_frame.lon + 0.0001  # 100m east
    goto_position(target_lat, target_lon, 10)
    
    # Send NED velocity (1 m/s north, 1 m/s east, 0 m/s down for 5 seconds)
    send_ned_velocity(1, 1, 0, 5)
    
    # Return to land
    print("Landing...")
    vehicle.mode = VehicleMode("LAND")
    while vehicle.armed:
        print("Waiting to land...")
        time.sleep(1)
    
finally:
    vehicle.close()
    print("Vehicle connection closed")
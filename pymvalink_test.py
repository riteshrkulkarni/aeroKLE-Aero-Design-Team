import time
from pymavlink import mavutil
from math import sqrt

# Connect to the vehicle (replace with your connection string)
connection = 'udp:127.0.0.1:14550'
print(f"Connecting to vehicle on: {connection}")
vehicle = mavutil.mavlink_connection(connection)
vehicle.wait_heartbeat()
print("Heartbeat received")

def arm_and_takeoff(target_altitude):
    print("Arming motors...")
    vehicle.mav.command_long_send(
        vehicle.target_system, vehicle.target_component,
        mavutil.mavlink.MAV_CMD_COMPONENT_ARM_DISARM, 0,
        1, 0, 0, 0, 0, 0, 0)
    vehicle.motors_armed_wait()
    
    print(f"Taking off to {target_altitude} meters...")
    vehicle.mav.command_long_send(
        vehicle.target_system, vehicle.target_component,
        mavutil.mavlink.MAV_CMD_NAV_TAKEOFF, 0,
        0, 0, 0, 0, 0, 0, target_altitude)
    
    while True:
        msg = vehicle.recv_match(type='GLOBAL_POSITION_INT', blocking=True)
        alt = msg.relative_alt / 1000.0
        print(f"Altitude: {alt}")
        if alt >= target_altitude * 0.95:
            print("Reached target altitude")
            break
        time.sleep(1)

def goto_position(target_lat, target_lon, target_alt):
    print(f"Going to: Lat {target_lat}, Lon {target_lon}, Alt {target_alt}")
    vehicle.mav.command_long_send(
        vehicle.target_system, vehicle.target_component,
        mavutil.mavlink.MAV_CMD_NAV_WAYPOINT, 0,
        0, 0, 0, 0, target_lat, target_lon, target_alt)
    
    while True:
        msg = vehicle.recv_match(type='GLOBAL_POSITION_INT', blocking=True)
        current_lat = msg.lat / 1e7
        current_lon = msg.lon / 1e7
        current_alt = msg.relative_alt / 1000.0
        distance = sqrt(((target_lat - current_lat) * 1.113195e5) ** 2 +
                        ((target_lon - current_lon) * 1.113195e5) ** 2)
        print(f"Distance to target: {distance:.2f} meters")
        if distance < 1.0:
            print("Reached target location")
            break
        time.sleep(1)

def send_ned_velocity(velocity_x, velocity_y, velocity_z, duration):
    print(f"Sending NED velocity: {velocity_x}m/s N, {velocity_y}m/s E, {velocity_z}m/s D")
    vehicle.mav.set_position_target_local_ned_send(
        0, vehicle.target_system, vehicle.target_component,
        mavutil.mavlink.MAV_FRAME_LOCAL_NED,
        0b0000111111000111,  # Only velocity components
        0, 0, 0,  # Position
        velocity_x, velocity_y, velocity_z,  # Velocity
        0, 0, 0,  # Acceleration
        0, 0)  # Yaw, yaw rate
    time.sleep(duration)

# Main execution
try:
    # Set mode to GUIDED
    vehicle.set_mode('GUIDED')
    
    # Arm and takeoff to 10 meters
    arm_and_takeoff(10)
    
    # Go to a specific GPS location (replace with your coordinates)
    msg = vehicle.recv_match(type='GLOBAL_POSITION_INT', blocking=True)
    target_lat = msg.lat / 1e7 + 0.0001  # 100m north
    target_lon = msg.lon / 1e7 + 0.0001  # 100m east
    goto_position(target_lat, target_lon, 10)
    
    # Send NED velocity (1 m/s north, 1 m/s east, 0 m/s down for 5 seconds)
    send_ned_velocity(1, 1, 0, 5)
    
    # Land
    print("Landing...")
    vehicle.set_mode('LAND')
    while vehicle.motors_armed():
        print("Waiting to land...")
        time.sleep(1)
    
finally:
    vehicle.close()
    print("Vehicle connection closed")
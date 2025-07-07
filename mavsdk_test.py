import asyncio
from mavsdk import System
from mavsdk.offboard import VelocityNedYaw, OffboardError

async def run():
    # Connect to the vehicle (replace with your connection string)
    drone = System()
    await drone.connect(system_address="udp://:14540")
    
    print("Waiting for drone to connect...")
    async for state in drone.core.connection_state():
        if state.is_connected:
            print("Drone connected")
            break
    
    print("Waiting for drone to have a global position estimate...")
    async for health in drone.telemetry.health():
        if health.is_global_position_ok and health.is_home_position_ok:
            print("Global position estimate OK")
            break
    
    # Arm and takeoff
    print("Arming...")
    await drone.action.arm()
    
    print("Taking off...")
    await drone.action.takeoff()
    await asyncio.sleep(10)  # Wait for takeoff to complete
    
    # Go to a GPS location
    print("Going to GPS location...")
    await drone.action.goto_location(
        latitude_deg=47.397742 + 0.0001,  # 100m north
        longitude_deg=8.545594 + 0.0001,  # 100m east
        absolute_altitude_m=10,
        yaw_deg=0
    )
    await asyncio.sleep(10)  # Wait to reach location
    
    # Send NED velocity
    print("Setting offboard mode with NED velocity...")
    await drone.offboard.set_velocity_ned(VelocityNedYaw(1.0, 1.0, 0.0, 0.0))  # 1 m/s N, 1 m/s E, 0 m/s D
    try:
        await drone.offboard.start()
        print("Offboard mode started")
        await asyncio.sleep(5)  # Apply velocity for 5 seconds
        await drone.offboard.stop()
        print("Offboard mode stopped")
    except OffboardError as error:
        print(f"Offboard failed with error: {error}")
    
    # Land
    print("Landing...")
    await drone.action.land()
    await asyncio.sleep(10)
    
    print("Disarming...")
    await drone.action.disarm()

# Run the async function
if __name__ == "__main__":
    asyncio.run(run())
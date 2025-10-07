import asyncio
from mavsdk import System
from utils.validate_response import validate_and_parse
from mavsdk.offboard import (OffboardError, PositionNedYaw)

async def connect_to_vehicle_px4(connection_str="udpin://0.0.0.0:14550"):
    print(f"Connecting to vehicle on {connection_str}...")
    drone = System()
    await drone.connect(system_address=connection_str)

    async for state in drone.core.connection_state():
        if state.is_connected:
            print("Connected to vehicle")
            break
    
    async for health in drone.telemetry.health():
            if health.is_global_position_ok and health.is_home_position_ok:
                break

    return drone

async def send_mavlink_command_px4(drone, llm_output: str):
    """Validate the LLM output, map it, and send to vehicle."""
    mapping = validate_and_parse(llm_output)
    cmd = mapping["command"]
    params = mapping["params"]

    if cmd == 400 and mapping["command_name"] == "arm_motors":
        await drone.action.arm()
        print("Sent ARM command")

    elif cmd == 400 and mapping["command_name"] == "disarm_motors":
        await drone.action.disarm()
        print("Sent DISARM command")

    elif cmd == 22:
        await drone.action.arm()
        if "z" in params:
            await drone.action.set_takeoff_altitude(params["z"])
        await drone.action.takeoff()
        print(f"Sent TAKEOFF to {params.get('z', 'default')} meters")

    elif cmd == 21:
        await drone.action.land()
        print("Sent LAND command")

    elif cmd == 20:
        await drone.action.return_to_launch()
        print("Sent RTL command")

    elif cmd == 176:
        mode = params["param1"].upper()
        if mode == "MISSION":
            await drone.mission.start_mission()
        elif mode == "OFFBOARD":
            async for pos in drone.telemetry.position_velocity_ned():
                current_north = pos.position.north_m
                current_east = pos.position.east_m
                current_down = pos.position.down_m
                break
            await drone.offboard.set_position_ned(PositionNedYaw(current_north, current_east, current_down, 0.0))
            try:
                await drone.offboard.start()
            except OffboardError as error:
                print(f"Starting offboard mode failed with error code: {error._result.result}")     
        elif mode == "HOLD":
            await drone.action.hold()
        else:
            print(f"Unsupported mode: {mode}")
        print(f"Sent SET_MODE with mode = {mode}")

    elif cmd == 84:
        async for pos in drone.telemetry.position_velocity_ned():
            current_north = pos.position.north_m
            current_east = pos.position.east_m
            current_down = pos.position.down_m
            break

        await drone.offboard.set_position_ned(PositionNedYaw(current_north, current_east, current_down, 0.0))

        try:
            await drone.offboard.start()
        except OffboardError as error:
            print(f"Starting offboard mode failed with error code: {error._result.result}")
            return
        
        delta_x = params.get("x", 0)
        delta_y = params.get("y", 0)
        delta_z = params.get("z", 0)
        
        pos_msg = PositionNedYaw(
            current_north + delta_x,
            current_east + delta_y,
            current_down + delta_z,
            0  # keep current yaw
        )

        await drone.offboard.set_position_ned(pos_msg)
        print(f"Sent MOVE x={params.get('x',0)}, y={params.get('y',0)}, z={params.get('z',0)}")
        
    else:
        print("Command is not supported for sending.")
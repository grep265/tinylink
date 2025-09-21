from pymavlink import mavutil
from utils.validate_response import validate_and_parse

def connect_to_vehicle(connection_str = "udp:127.0.0.1:14550"):
    print(f"Connecting to vehicle on {connection_str}...")
    master = mavutil.mavlink_connection(connection_str)
    master.wait_heartbeat()
    print("Connected to vehicle (system ID:", master.target_system, ")")
    return master

def send_mavlink_command(master, llm_output: str):
    """Validate the LLM output, map it, and send to vehicle."""
    mapping = validate_and_parse(llm_output)
    cmd = mapping["command"]
    params = mapping["params"]

    if cmd == 400 and mapping["command_name"] == "arm_motors":
        master.mav.command_long_send(
            master.target_system,
            master.target_component,
            cmd,
            0,
            1, 0, 0, 0, 0, 0, 0
        )
        print("Sent ARM command")

    elif cmd == 400 and mapping["command_name"] == "disarm_motors":
        master.mav.command_long_send(
            master.target_system,
            master.target_component,
            cmd,
            0,
            0, 0, 0, 0, 0, 0, 0
        )
        print("Sent DISARM command")

    elif cmd == 22:  
        master.mav.command_long_send(
            master.target_system,
            master.target_component,
            cmd,
            0,
            0, 0, 0, 0, 0, 0, params["z"]
        )
        print(f"Sent TAKEOFF to {params['z']} meters")

    elif cmd == 21:  
        master.mav.command_long_send(
            master.target_system,
            master.target_component,
            cmd,
            0, 0, 0, 0, 0, 0, 0, 0
        )
        print("Sent LAND command")

    elif cmd == 20:  
        master.mav.command_long_send(
            master.target_system,
            master.target_component,
            cmd,
            0, 0, 0, 0, 0, 0, 0, 0
        )
        print("Sent RTL command")
        
    elif cmd == 176:  
        master.set_mode_apm(params['param1'].upper())
        print(f"Sent SET_MODE with mode = {params['param1'].upper()}")

    elif cmd == 84:  
        master.mav.set_position_target_local_ned_send(
            0,
            master.target_system,
            master.target_component,
            mavutil.mavlink.MAV_FRAME_BODY_NED,
            0b0000111111111000,
            params.get("x", 0),
            params.get("y", 0),
            params.get("z", 0),
            0, 0, 0,
            0, 0, 0,
            0, 0
        )
        print(f"Sent MOVE x={params.get('x',0)}, y={params.get('y',0)}, z={params.get('z',0)}")

    else:
        print("Command is not supported for sending.")
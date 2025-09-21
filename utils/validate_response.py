
SUPPORTED_COMMANDS = {
    400: {
        "name": "arm_motors",
        "params": ["param1"]
    },
    22: {
        "name": "takeoff",
        "params": ["z"]
    },
    21: {
        "name": "land",
        "params": []
    },
    20: {
        "name": "rtl",
        "params": []
    },
    176: {
        "name": "set_mode",
        "params": ["param1"]
    },
    84: {
        "name": "move",
        "params": ["x", "y", "z"]
    }
}

SUPPORTED_MODES = {"AUTO", "GUIDED", "RTL", "STABILIZE", "LOITER", "POSHOLD", "ALTHOLD","FBWA", "CRUISE", 
                   "MANUAL", "FBWB", "ACRO","STEERING","CIRCLE"}

def validate_and_parse(llm_output: str):
    """
    Validate LLM output and return a dict ready for MAVLink transmission.
    """
    
    msg = decode_response(llm_output)

    if not msg:
        raise ValueError("Empty or invalid LLM output")
    if "c" not in msg:
        raise ValueError("Missing 'command' field in LLM output")

    cmd_id = msg["c"]
    if cmd_id not in SUPPORTED_COMMANDS:
        raise ValueError(f"Unsupported command")

    cmd_spec = SUPPORTED_COMMANDS[cmd_id]

    for p in cmd_spec["params"]:
        if p not in msg:
            raise ValueError(f"Command '{cmd_spec['name']}' requires parameter '{p}'")
    
    if cmd_id == 176:
        mode = msg["param1"].upper()
        if mode not in SUPPORTED_MODES:
            raise ValueError(f"Unsupported mode: {msg['param1']}")
        msg["param1"] = mode
        
    if cmd_id == 400:
        if "param1" not in msg:
            raise ValueError("Arm/disarm command requires parameter 'param1'")
        param1 = msg["param1"]
        if param1 not in {0, 1}:
            raise ValueError(f"Arm/disarm command requires param1 to be 0 or 1, got {param1}")
        elif param1 == 1:
            msg["param1"] = 1
            cmd_spec["name"] = "arm_motors"
        else:
            msg["param1"] = 0
            cmd_spec["name"] = "disarm_motors"
            
    return {
        "command": cmd_id,
        "command_name": cmd_spec["name"],
        "params": msg
    }

def decode_response(llm_output: str) -> dict:
    """
    Decode the compact LLM output
    """
    cleaned = llm_output.strip().strip("{}").strip()
    
    if not cleaned:
        return {}

    result = {}
    for part in cleaned.split():
        if "=" not in part:
            continue
        key, val = part.split("=", 1)
        if val.isdigit() or (val.startswith("-") and val[1:].isdigit()):
            val = int(val)
        
        if key == "p":
            key = "param1"
        
        result[key] = val
    return result
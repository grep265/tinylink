import time
import argparse
from utils.generate_response import generate_response
from utils.send_command import connect_to_vehicle, send_mavlink_command
from utils.send_command_px4 import connect_to_vehicle_px4,send_mavlink_command_px4
import asyncio

async def main_px4(enable_timing: bool, connection_string: str):
    drone = await connect_to_vehicle_px4(connection_string)

    while True:
        user_input = input("\nType an instruction: ")
        if user_input.lower() in ["exit", "quit"]:
            print("Closing")
            break

        try:
            if enable_timing:
                start_time = time.perf_counter()
                llm_output = generate_response(user_input)
                end_time = time.perf_counter()
                elapsed = end_time - start_time
                print(f"Execution time: {elapsed:.3f} s")
            else:
                llm_output = generate_response(user_input)

            await send_mavlink_command_px4(drone, llm_output)

        except ValueError as e:
            print("Error:", e)
        except Exception as e:
            print("Unexpected Error:", e)

def main_ardupilot(enable_timing: bool, connection_string: str):
    master = connect_to_vehicle(connection_string)
    
    while True:
        user_input = input("\nType an instruction: ")
        if user_input.lower() in ["exit", "quit"]:
            print("Closing")
            break

        try:
            if enable_timing:
                start_time = time.perf_counter()
                llm_output = generate_response(user_input)
                end_time = time.perf_counter()
                elapsed = end_time - start_time
                print(f"Execution time: {elapsed:.3f} s")
            else:
                llm_output = generate_response(user_input)

            send_mavlink_command(master, llm_output)

        except ValueError as e:
            print("Error:", e)
        except Exception as e:
            print("Unexpected Error:", e)
    

def main(enable_timing: bool, connection_string: str, use_px4: bool):
    print("Type 'exit' or 'quit' to quit.")
    
    if use_px4:
        asyncio.run(main_px4(enable_timing,connection_string))
    else:
        main_ardupilot(enable_timing,connection_string)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="AI Assistant")
    parser.add_argument(
        "--time",
        action="store_true",
        help="Display execution time for each command",
    )
    parser.add_argument(
        "--connection",
        type=str,
        default="udp:127.0.0.1:14550",
        help="Connection string in the format udp:IP:PORT",
    )
    parser.add_argument(
        "--px4",
        action="store_true",
        help="For PX4",
    )
    args = parser.parse_args()
    main(enable_timing=args.time,connection_string=args.connection,use_px4=args.px4)
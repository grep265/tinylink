import time
import argparse
from utils.generate_response import generate_response
from utils.send_command import connect_to_vehicle, send_mavlink_command

def main(enable_timing: bool, connection_string: str):
    print("Type 'exit' or 'quit' to quit.")

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
    args = parser.parse_args()
    main(enable_timing=args.time,connection_string=args.connection)
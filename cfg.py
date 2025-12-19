"""Configuration script for Ixia HLT API testing.

This script demonstrates connecting to an IxNetwork server, reserving ports,
and configuring traffic using the Ixia High Level Traffic (HLT) API.
Supports both Python and Tcl execution modes.
"""

from tkinter import Tcl, TclError
import argparse

from helper import init_hl_package, execute_python, execute_tcl, execute_tcl_endpoint


def main(module):
    """Main function to initialize and execute Ixia test configuration.
    
    This function connects to an IxNetwork server, reserves ports, and
    configures L2 traffic between endpoints.
    
    Args:
        module: The execution mode - either "tcl" or "python".
    """
    init_hl_package(module)
    # monkey patch execute function based on the module
    if module == "tcl":
        execute = execute_tcl
    elif module == "python":
        execute = execute_python
    elif module == "isolated_tcl":
        execute = execute_tcl_endpoint

    print("\n\n")
    result = execute("::ixia::connect", "-ixnetwork_tcl_server 10.39.47.41:8012 -device xgshs-606488.ccu.is.keysight.com -port_list {2/1 2/2} -break_locks 1 -reset 1")
    print("result = ", result)


    print("\n\n")
    result = execute("::ixia::traffic_config", "-mode create -traffic_generator ixnetwork -circuit_type raw -name HL-L2 -endpointset_count 1 -emulation_src_handle {1/2/1} -emulation_dst_handle {1/2/2} -src_dest_mesh one_to_one -route_mesh one_to_one -bidirectional 1 -rate_percent 10 -frame_size 512")
    print("result = ", result)
    print("Done")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run cfg with chosen execution module (tcl or python).")
    parser.add_argument("-impl", "--implementation", choices=["tcl", "python", "isolated_tcl"], default="tcl",
                        help="Execution mode: 'tcl' (default), 'python' (HLPy), or 'isolated_tcl'.")
    args = parser.parse_args()

    main(module=args.implementation)
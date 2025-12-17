# HLT_To_HLPy_POC
Repo just to show-case a small POC for conversion of HLT scripts to HLPy scripts without much change

## Purpose

This proof-of-concept demonstrates how you can seamlessly switch between HLT and HLPy implementations by simply changing the helper functions. The main configuration code remains unchanged - only the underlying helper implementation needs to be swapped to transition from HLT to HLPy usage.

## How to Run

To test the POC, simply run the configuration file:

```bash
python cfg.py
```

### Testing Different Execution Paths

To switch between Python (HLPy) and Tcl (HLT) execution paths, modify the `main` function call at the bottom of [cfg.py](cfg.py):

**For Python/HLPy execution:**
```python
if __name__ == "__main__":
    main(module="python")
```

**For Tcl/HLT execution:**
```python
if __name__ == "__main__":
    main(module="tcl")
```

### Example Output (Tcl/HLT Mode)

When running with `module="tcl"`, the output shows HLT running in the background:

```
python3 ./cfg.py
% package require Ixia
Tcl 8.6 is installed on 64bit architecture.
Using products based on HLTSET289
IxTclHal is not be used for current HLTSET.
Loaded IxTclNetwork 26.0.2601.6
Loaded Mpexpr 1.2
HLT release 26.0.2601.5
Loaded ixia_hl_lib-26.0 



% ::ixia::connect -ixnetwork_tcl_server 10.74.45.143:8009 -device xgshs-606488.ccu.is.keysight.com -port_list {2/1 2/2} -break_locks 1 -reset 1
Connecting to IxNetwork Tcl Server 10.74.45.143 -port 8009 -clientId {HLAPI-Tcl} ...
WARNING: IxNetwork Tcl library version 26.0.2601.6 is not matching the IxNetwork client version 10.00.2312.4
result =  {port_handle {{10 {{39 {{51 {{204 {{2/1 1/2/1} {2/2 1/2/2}}}}}}}}} {xgshs-606488 {{ccu {{is {{keysight {{com {{2/1 1/2/1} {2/2 1/2/2}}}}}}}}}}}}} {connection {{tcl_port 8009} {using_tcl_proxy 0} {server_version 10.00.2312.4} {port 8009} {chassis {{xgshs-606488 {{ccu {{is {{keysight {{com {{hostname xgshs-606488.ccu.is.keysight.com} {ip {}} {chassis_protocols_version Ignored} {chassis_type {Ixia XGS2}} {chassis_version {IxOS 10.00.1000.17 Patch3}} {is_master_chassis 1} {chain_type daisy} {chassis_chain {{sequence_id 1}}}}}}}}}}}}}}} {client_version 26.0.2601.6} {username IxNetwork/1N14170253/vhowdhur} {hostname 1N14170253} {license {{server localhost} {type aggregation}}}}} {vport_list {1/2/1 1/2/2}} {vport_protocols_handle {::ixNet::OBJ-/vport:1/protocols ::ixNet::OBJ-/vport:2/protocols}} {guardrail_messages {{1 {WARNING: IxNetwork main module errors - Ignore Version Registry Key is Enabled.}} {2 {MESSAGE: StatViewer Guardrail Info - The statistics Guard Rail option is designed to protect you from adding too many statistics. It is recommended to keep this option enabled, in order to prevent inaccurate statistics while running large scale tests.}}}} {status 1}



% ::ixia::traffic_config -mode create -traffic_generator ixnetwork -circuit_type raw -name HL-L2 -endpointset_count 1 -emulation_src_handle {1/2/1} -emulation_dst_handle {1/2/2} -src_dest_mesh one_to_one -route_mesh one_to_one -bidirectional 1 -rate_percent 10 -frame_size 512
result =  {status 1} {log {}} {stream_id TI0-HL-L2} {traffic_item ::ixNet::OBJ-/traffic/trafficItem:1/configElement:1} {::ixNet::OBJ-/traffic/trafficItem:1/configElement:1 {{headers {::ixNet::OBJ-/traffic/trafficItem:1/configElement:1/stack:"ethernet-1" ::ixNet::OBJ-/traffic/trafficItem:1/configElement:1/stack:"fcs-2"}} {stream_ids ::ixNet::OBJ-/traffic/trafficItem:1/highLevelStream:1} {::ixNet::OBJ-/traffic/trafficItem:1/highLevelStream:1 {{headers {::ixNet::OBJ-/traffic/trafficItem:1/highLevelStream:1/stack:"ethernet-1" ::ixNet::OBJ-/traffic/trafficItem:1/highLevelStream:1/stack:"fcs-2"}}}} {endpoint_set_id 1} {encapsulation_name Ethernet}}}
```

### Example Output (Python/HLPy Mode)

When running with `module="python"`, the output shows HLPy running with Python dictionaries:

```
python3 ./cfg.py
ixiatcl:info: Tcl version: 8.6.12
/opt/ixia/ixnetwork/26.0.2601.6/lib/TclApi/ /opt/ixia/hlapi/26.0.2601.5/ /usr/share/tcltk/tcl8.6 /usr/share/tcltk /usr/lib /usr/local/lib/tcltk /usr/local/share/tcltk /usr/lib/tcltk/x86_64-linux-gnu /usr/lib/tcltk /usr/lib/tcltk/tcl8.6
Tcl 8.6 is installed on 64bit architecture.
Using products based on HLTSET289
IxTclHal is not be used for current HLTSET.
Loaded IxTclNetwork 26.0.2601.6
Loaded Mpexpr 1.2
HLT release 26.0.2601.5
Loaded ixia_hl_lib-26.0 



Executing command: ::ixia::connect with arguments: -ixnetwork_tcl_server 10.74.45.143:8009 -device xgshs-606488.ccu.is.keysight.com -port_list {2/1 2/2} -break_locks 1 -reset 1
Resolved namespace: ixia, function: connect
Parsed arguments: {'ixnetwork_tcl_server': '10.74.45.143:8009', 'device': 'xgshs-606488.ccu.is.keysight.com', 'port_list': ['2/1', '2/2'], 'break_locks': 1, 'reset': 1}
Connecting to IxNetwork Tcl Server 10.74.45.143 -port 8009 -clientId {HLAPI-Tcl} ...
WARNING: IxNetwork Tcl library version 26.0.2601.6 is not matching the IxNetwork client version 10.00.2312.4
result =  {'port_handle': {'10': {'39': {'51': {'204': {'2/1': '1/2/1', '2/2': '1/2/2'}}}}, 'xgshs-606488': {'ccu': {'is': {'keysight': {'com': {'2/1': '1/2/1', '2/2': '1/2/2'}}}}}}, 'connection': {'tcl_port': '8009', 'using_tcl_proxy': '0', 'server_version': '10.00.2312.4', 'port': '8009', 'chassis': {'xgshs-606488': {'ccu': {'is': {'keysight': {'com': {'hostname': 'xgshs-606488.ccu.is.keysight.com', 'ip': '', 'chassis_protocols_version': 'Ignored', 'chassis_type': 'Ixia XGS2', 'chassis_version': 'IxOS 10.00.1000.17 Patch3', 'is_master_chassis': '1', 'chain_type': 'daisy', 'chassis_chain': {'sequence_id': '1'}}}}}}}, 'client_version': '26.0.2601.6', 'username': 'IxNetwork/1N14170253/vhowdhur', 'hostname': '1N14170253', 'license': {'server': 'localhost', 'type': 'aggregation'}}, 'vport_list': '1/2/1 1/2/2', 'vport_protocols_handle': '::ixNet::OBJ-/vport:1/protocols ::ixNet::OBJ-/vport:2/protocols', 'guardrail_messages': {'1': 'WARNING: IxNetwork main module errors - Ignore Version Registry Key is Enabled.', '2': 'MESSAGE: StatViewer Guardrail Info - The statistics Guard Rail option is designed to protect you from adding too many statistics. It is recommended to keep this option enabled, in order to prevent inaccurate statistics while running large scale tests.'}, 'status': '1'}



Executing command: ::ixia::traffic_config with arguments: -mode create -traffic_generator ixnetwork -circuit_type raw -name HL-L2 -endpointset_count 1 -emulation_src_handle {1/2/1} -emulation_dst_handle {1/2/2} -src_dest_mesh one_to_one -route_mesh one_to_one -bidirectional 1 -rate_percent 10 -frame_size 512
Resolved namespace: ixia, function: traffic_config
Parsed arguments: {'mode': 'create', 'traffic_generator': 'ixnetwork', 'circuit_type': 'raw', 'name': 'HL-L2', 'endpointset_count': 1, 'emulation_src_handle': ['1/2/1'], 'emulation_dst_handle': ['1/2/2'], 'src_dest_mesh': 'one_to_one', 'route_mesh': 'one_to_one', 'bidirectional': 1, 'rate_percent': 10, 'frame_size': 512}
result =  {'status': '1', 'log': '', 'stream_id': 'TI0-HL-L2', 'traffic_item': '::ixNet::OBJ-/traffic/trafficItem:1/configElement:1', '::ixNet::OBJ-/traffic/trafficItem:1/configElement:1': {'headers': '::ixNet::OBJ-/traffic/trafficItem:1/configElement:1/stack:"ethernet-1" ::ixNet::OBJ-/traffic/trafficItem:1/configElement:1/stack:"fcs-2"', 'stream_ids': '::ixNet::OBJ-/traffic/trafficItem:1/highLevelStream:1', '::ixNet::OBJ-/traffic/trafficItem:1/highLevelStream:1': {'headers': '::ixNet::OBJ-/traffic/trafficItem:1/highLevelStream:1/stack:"ethernet-1" ::ixNet::OBJ-/traffic/trafficItem:1/highLevelStream:1/stack:"fcs-2"'}, 'endpoint_set_id': '1', 'encapsulation_name': 'Ethernet'}}
Done
```

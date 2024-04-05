import sys
import time
import datetime

from panos_actions import (panos_api_key, panos_op_cmd, panos_config_set,
                           panos_config_delete, panos_commit_cmd, pan_commit_partial, pan_config_snapshot)
from admin import username, password

panorama_ip = "192.168.2.32"

device_sn = "007951000452665"
device_group = "test"
template_stack = "test-tstck"


def main():
    step_id = 0
    # Get api key
    step_id += 1
    step_description = f"Get api key"
    print(f"Step {step_id}: {step_description}")
    try:
        api_key = panos_api_key(fw_ip=panorama_ip, uname=username, pwd=password)
    except Exception as e:
        print(f"Step {step_id} error: {e}")
        sys.exit(1)

    # Configuration snapshot
    step_id += 1
    step_description = f"Configuration snapshot"
    print(f"Step {step_id}: {step_description}")
    time_stamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M")
    filename = f"snap-pre-{time_stamp}.xml"
    snapshot_result = pan_config_snapshot(fw_ip=panorama_ip, fw_key=api_key, filename=filename)
    print(f"Step {step_id} result: {snapshot_result}")

    # Detach device serial number from device-group
    step_id += 1
    step_description = f"Detach device serial number from device-group"
    print(f"Step {step_id}: {step_description}")
    detach_device_dg = f"/config/devices/entry/device-group/entry[@name='{device_group}']/devices/entry[@name='{device_sn}']"
    try:
        api_call = panos_config_delete(fw_ip=panorama_ip, fw_key=api_key, xpath=detach_device_dg)
        print(f"Step {step_id} result: {api_call['msg']}")
    except Exception as e:
        print(f"Step {step_id} error: {e}")
        sys.exit(1)

    # Detach device serial number from template-stack
    step_id += 1
    step_description = f"Detach device serial number from template-stack"
    print(f"Step {step_id}: {step_description}")
    detach_device_tstk = f"/config/devices/entry/template-stack/entry[@name='{template_stack}']/devices/entry[@name='{device_sn}']"
    try:
        api_call = panos_config_delete(fw_ip=panorama_ip, fw_key=api_key, xpath=detach_device_tstk)
        print(f"Step {step_id} result: {api_call['msg']}")
    except Exception as e:
        print(f"Step {step_id} error: {e}")
        sys.exit(1)

    # Remove device serial number from managed devices
    step_id += 1
    step_description = f"Remove device serial number from managed devices"
    print(f"Step {step_id}: {step_description}")
    unmanage_device = f"/config/mgt-config/devices/entry[@name='{device_sn}']"
    try:
        api_call = panos_config_delete(fw_ip=panorama_ip, fw_key=api_key, xpath=unmanage_device)
        print(f"Step {step_id} result: {api_call['msg']}")
    except Exception as e:
        print(f"Step {step_id} error: {e}")
        sys.exit(1)

    # Commit partial
    step_id += 1
    step_description = f"Commit partial"
    print(f"Step {step_id}: {step_description}")
    commit_result = pan_commit_partial(fw_ip=panorama_ip, fw_key=api_key,admin=username)
    print(f"Step {step_id} result: {commit_result}")

    # Delete device-group
    step_id += 1
    step_description = f"Delete device-group"
    print(f"Step {step_id}: {step_description}")
    delete_dgroup = f"/config/devices/entry/device-group/entry[@name='{device_group}']"
    try:
        api_call = panos_config_delete(fw_ip=panorama_ip, fw_key=api_key, xpath=delete_dgroup)
        print(f"Step {step_id} result: {api_call['msg']}")
    except Exception as e:
        print(f"Step {step_id} error: {e}")
        sys.exit(1)

    # Commit partial
    step_id += 1
    step_description = f"Commit partial"
    print(f"Step {step_id}: {step_description}")
    commit_result = pan_commit_partial(fw_ip=panorama_ip, fw_key=api_key,admin=username)
    print(f"Step {step_id} result: {commit_result}")

    # Configuration snapshot
    step_id += 1
    step_description = f"Configuration snapshot"
    print(f"Step {step_id}: {step_description}")
    time_stamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M")
    filename = f"snap-post-{time_stamp}.xml"
    snapshot_result = pan_config_snapshot(fw_ip=panorama_ip, fw_key=api_key, filename=filename)
    print(f"Step {step_id} result: {snapshot_result}")

if __name__ == "__main__":
    main()

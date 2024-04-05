import setuptools
import time
import requests
import xmltodict
import sys

# from tenant_config import password_hash, tenant_config, tenant_delete, branch_config

requests.packages.urllib3.disable_warnings()


def panos_api_key(fw_ip, uname, pwd):
    # function to get API key from username/password
    api_url = f"https://{fw_ip}/api"
    api_prm = {
        "type": "keygen",
        "user": {uname},
        "password": {pwd}
    }
    api_hdr = {}
    api_pld = {}
    response = requests.request("GET", url=api_url, params=api_prm, verify=False, timeout=3)
    key = xmltodict.parse(response.text)["response"]["result"]["key"]
    return key


def panos_op_cmd(fw_ip, fw_key, xml_cmd):
    api_url = f"https://{fw_ip}/api"
    api_prm = {
        "key": fw_key,
        "type": "op",
        "cmd": xml_cmd
    }
    api_hdr = {}
    api_pld = {}
    response = requests.request("GET", url=api_url, params=api_prm, verify=False, timeout=3)
    result = xmltodict.parse(response.text)["response"]
    return result


def panos_config_set(fw_ip, fw_key, xpath, element):
    api_url = f"https://{fw_ip}/api"
    api_prm = {
        "key": fw_key,
        "type": "config",
        "action": "set",
        "xpath": xpath,
        "element": element
    }
    api_hdr = {}
    api_pld = {}
    response = requests.request("GET", url=api_url, params=api_prm, verify=False, timeout=3)
    result = xmltodict.parse(response.text)["response"]
    return result


def panos_config_delete(fw_ip, fw_key, xpath):
    api_url = f"https://{fw_ip}/api"
    api_prm = {
        "key": fw_key,
        "type": "config",
        "action": "delete",
        "xpath": xpath
    }
    api_hdr = {}
    api_pld = {}
    response = requests.request("GET", url=api_url, params=api_prm, verify=False, timeout=3)
    result = xmltodict.parse(response.text)["response"]
    return result


def panos_commit_cmd(fw_ip, fw_key, xml_cmd):
    api_url = f"https://{fw_ip}/api"
    api_prm = {
        "key": fw_key,
        "type": "commit",
        "cmd": xml_cmd
    }
    api_hdr = {}
    api_pld = {}
    response = requests.request("GET", url=api_url, params=api_prm, verify=False, timeout=3)
    result = xmltodict.parse(response.text)["response"]
    return result


def pan_commit_partial(fw_ip, fw_key, admin):
    commit_cmd = f"<commit><partial><admin><member>{admin}</member></admin></partial></commit>"
    try:
        api_call = panos_commit_cmd(fw_ip=fw_ip, fw_key=fw_key, xml_cmd=commit_cmd)
        if api_call["@status"] == "success" and api_call["@code"] == "13":
            return f"Nothing to commit"
        elif api_call["@status"] == "success" and api_call["@code"] == "19":
            job_id = api_call['result']['job']
        else:
            return api_call
    except Exception as e:
        print(f"{e}")
        sys.exit(1)

    check_job = f"<show><jobs><id>{job_id}</id></jobs></show>"
    while True:
        try:
            api_call = panos_op_cmd(fw_ip=fw_ip, fw_key=fw_key, xml_cmd=check_job)
            if api_call["@status"] == "success":
                job_status = api_call['result']['job']['status']
            else:
                return api_call
            if job_status == "FIN": break
        except Exception as e:
            print(f"{e}")
            sys.exit(1)
        time.sleep(30)

    output_message = "\n"
    for line in api_call['result']['job']['details']['line']: output_message += f"\t{line}\n"

    if "Configuration committed successfully" not in output_message:
        print(f"Commit failure {output_message}")
        revert_config = f"<config><partial><admin><member>{admin}</member></admin></partial></config></revert>"
        revert_config = f"<revert><config/></revert>"
        api_call = panos_op_cmd(fw_ip=fw_ip, fw_key=fw_key, xml_cmd=revert_config)
        return f"{api_call['result']['msg']['line']}"

    return f"Commit successful {output_message}"


def pan_config_snapshot(fw_ip, fw_key, filename):
    save_cmd = f"<save><config><to>{filename}</to></config></save>"
    try:
        api_call = panos_op_cmd(fw_ip=fw_ip, fw_key=fw_key, xml_cmd=save_cmd)
        return api_call['result']
    except Exception as e:
        print(f"{e}")
        sys.exit(1)
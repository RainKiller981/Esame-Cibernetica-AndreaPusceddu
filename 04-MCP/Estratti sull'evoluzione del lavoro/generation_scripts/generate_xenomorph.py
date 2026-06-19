import socket
import json
import time
import sys

def receive_full_response(sock, buffer_size=8192):
    chunks = []
    sock.settimeout(180.0)
    while True:
        try:
            chunk = sock.recv(buffer_size)
            if not chunk:
                if not chunks:
                    raise Exception("Connection closed before receiving any data")
                break
            chunks.append(chunk)
            try:
                data = b''.join(chunks)
                json.loads(data.decode('utf-8'))
                return data
            except json.JSONDecodeError:
                continue
        except socket.timeout:
            print("Socket timeout during receive")
            break
        except Exception as e:
            print(f"Error during receive: {e}")
            raise
    if chunks:
        data = b''.join(chunks)
        try:
            json.loads(data.decode('utf-8'))
            return data
        except json.JSONDecodeError:
            raise Exception("Incomplete JSON response received")
    else:
        raise Exception("No data received")

def send_command(sock, command_type, params=None):
    command = {
        "type": command_type,
        "params": params or {}
    }
    sock.sendall(json.dumps(command).encode('utf-8'))
    response_data = receive_full_response(sock)
    response = json.loads(response_data.decode('utf-8'))
    if response.get("status") == "error":
        raise Exception(response.get("message", "Unknown error from Blender"))
    return response.get("result", {})

def main():
    host = "localhost"
    port = 9876
    print(f"Connecting to Blender at {host}:{port}...")
    
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        sock.connect((host, port))
        print("Connected successfully!")
    except Exception as e:
        print(f"Failed to connect: {e}")
        sys.exit(1)

    try:
        # Step 1: Check Hyper3D Status
        print("Checking Hyper3D status...")
        status = send_command(sock, "get_hyper3d_status")
        print(f"Hyper3D Status: {status}")

        # Step 2: Create Rodin Job
        prompt = "Alien Xenomorph, highly detailed, sci-fi creature"
        print(f"Creating Hyper3D generation job for: '{prompt}'...")
        job_result = send_command(sock, "create_rodin_job", {
            "text_prompt": prompt,
            "images": None,
            "bbox_condition": None
        })
        
        print(f"Job creation result: {json.dumps(job_result, indent=2)}")
        
        uuid = job_result.get("uuid")
        jobs = job_result.get("jobs", {})
        sub_key = jobs.get("subscription_key")
        
        if not uuid or not sub_key:
            print("Failed to obtain job UUID or subscription key.")
            sys.exit(1)
            
        print(f"Job created! UUID: {uuid}, Subscription Key: {sub_key}")
        
        # Step 3: Polling status
        print("Starting polling loop...")
        while True:
            time.sleep(10)
            print("Polling job status...")
            poll_result = send_command(sock, "poll_rodin_job_status", {
                "subscription_key": sub_key
            })
            print(f"Poll result: {poll_result}")
            
            # The poll_result usually contains a status or list of statuses
            # e.g., {'status': 'Done'} or a list like [{'status': 'Done'}] or similar
            # Let's inspect poll_result. If it's a string, or dict, let's be careful.
            status_str = ""
            if isinstance(poll_result, dict):
                # Check for "status" or check if it's a list
                status_str = poll_result.get("status", "")
                if not status_str and "status" in poll_result:
                    status_str = str(poll_result["status"])
            elif isinstance(poll_result, list):
                # If list, check if all done
                statuses = [item.get("status") if isinstance(item, dict) else item for item in poll_result]
                print(f"Individual statuses: {statuses}")
                if all(s == "Done" for s in statuses):
                    status_str = "Done"
                elif any(s == "Failed" for s in statuses):
                    status_str = "Failed"
            else:
                status_str = str(poll_result)

            print(f"Current interpreted status: {status_str}")
            if "Done" in status_str or status_str == "Done" or (isinstance(poll_result, dict) and poll_result.get("status") == "Done"):
                print("Generation complete!")
                break
            elif "Failed" in status_str or "Canceled" in status_str:
                print("Generation failed or was canceled.")
                sys.exit(1)
                
        # Step 4: Import the generated asset
        print("Importing the generated Xenomorph asset into Blender...")
        import_result = send_command(sock, "import_generated_asset", {
            "name": "Xenomorph",
            "task_uuid": uuid
        })
        print(f"Import result: {import_result}")
        
        # Step 5: Save screenshot or viewport capture
        print("Capturing viewport screenshot to verify...")
        screenshot_result = send_command(sock, "get_viewport_screenshot", {
            "max_size": 800,
            "filepath": "C:\\Users\\andre\\Desktop\\blender_xenomorph.png",
            "format": "png"
        })
        print(f"Screenshot saved to C:\\Users\\andre\\Desktop\\blender_xenomorph.png. Result: {screenshot_result}")
        
    except Exception as e:
        print(f"Error occurred during execution: {e}")
    finally:
        sock.close()
        print("Socket closed.")

if __name__ == "__main__":
    main()

# KittyByte Backend



## Setup (for local testing)

Assuming you have already cloned the repo

1.  Navigate to backend directory (using cmd) e.g.
   
   ```bash
   cd C:/Users/your_username/Documents/KittyByte-IOT/backend
   ```

2. Install dependencies
   
   ```bash
   pip install -r requirements.txt
   ```

3. Install Docker
   
   [Install Docker Toolbox on Windows | Docker Documentation](https://docker-docs.uclv.cu/toolbox/toolbox_install_windows/)
   
   or directly:
   
   https://github.com/docker-archive/toolbox/releases/download/v19.03.1/DockerToolbox-19.03.1.exe

4. Install ThingsBoard
   
   [Installing ThingsBoard using Docker (Windows) | ThingsBoard Community Edition](https://thingsboard.io/docs/user-guide/install/docker-windows/)
   
   in cmd:
   
   ```bash
   docker volume create mytb-data
   docker volume create mytb-logs
   ```
   
   Create a file called: "docker-compose.yml" and paste the following:
   
   ```yml
   version: '3.0'
   services:
     mytb:
       restart: always
       image: "thingsboard/tb-postgres"
       ports:
         - "8081:9090"
         - "1883:1883"
         - "7070:7070"
         - "5683-5688:5683-5688/udp"
       environment:
         TB_QUEUE_TYPE: in-memory
       volumes:
         - mytb-data:/data
         - mytb-logs:/var/log/thingsboard
   volumes:
     mytb-data:
       external: true
     mytb-logs:
       external: true
   
   
   ```
   
   Run the following in the directory of docker-compose.yml
   
   ```bash
   docker compose up -d && docker compose logs -f mytb
   ```

5. Open Thingsboard at https://localhost:8080

6. Go to **Profiles** on the left and click **"Device profiles"**
   
   Click the **+** button and **"Create new device profile"**
   
   Input any name
   
   Click **"Transport configuration"** select **MQTT**
   
   Click **"Device provisioning"** select **"Check for pre-provisioned devices"**
   
   Copy the **"Provision device key"** and **"Provision device secret"**
   
   Click **"Add"**

7. Put your provision device key and secret into "example.env.dev" 

8. Rename `example.env.dev` to `.env.dev`

9. Start the development server with
   
   ```bash
   python -m uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
   ```

You should now be able to access http://localhost:8000, go to http://localhost:8000/docs for the API docs





AI Gen'd:

- `api/`: Contains API routes and endpoint handlers

- `crud/`: Contains database CRUD operations

- `models/`: Contains SQLAlchemy database models

- `schemas/`: Contains Pydantic schemas for request/response validation

- `utils/`: Contains utility functions and helpers

- `main.py`: Application entry point

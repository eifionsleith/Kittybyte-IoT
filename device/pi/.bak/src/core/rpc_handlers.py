"""
The MQTTService only gets the RPC command, and doesn't decode
it into a dispatchable command, so this will happen here!
"""

from communication.serial.arduino_controller import ArduinoController
from communication.serial.commands import DispenseCommand, BuzzCommand
from services.mqtt_service import RPCCommand


def process_rpc_command(rpc_command: RPCCommand, arduino_controller: ArduinoController):
    method = rpc_command.method

    if method == "dispense":
        return handle_dispense(rpc_command.params, arduino_controller)
    else:
        print("RPC Handler Error: Unknown RPC method - {rpc_command.method}")
        return None

def handle_dispense(params: dict, arduino_controller: ArduinoController):
    """
    Handles the dispense RPC command, triggering the dispense
    logic via the Arduino's actuators

    Args:
        params (dict[str, str]): Paramaters recieved from the RPC call.
                                 Expected: {'qty': int}
        arduino_controller (ArduinoController): Instance to communicate to the Arduino.

    Returns:
        dict: Payload for the RPC response
    """
    print(f"RPC Handler: Executing dispense with params: {params}")

    if arduino_controller is None:
        print("RPC Handler Error: Arduino not connected.")
        return {"status": "error", "message": "Arduino not connected"}

    try:
        quantity = params.get("amount")
        if quantity is None:
            print("RPC Handler: 'amount' parameter missing.")
            return {"status": "error", "message": "'amount' paramater is required"}

        quantity = int(quantity)
        if quantity < 1:
            print("RPC Handler Error: Invalid 'amount' {quantity}, must be positive.")
            return {"status": "error", "message": "Amount must be positive integer."}

    except (ValueError, TypeError) as e:
        print(f"RPC Handler Error: Invalid 'amount' paramater type - {e}")
        return {"status": "error", "message": f"Invalid 'amount' paramater: {params.get('amount')}. Must be integer."}

    try:
        print(f"RPC Handler: Sending DispenseCommand(quantity={quantity}) to Arduino")
        command = DispenseCommand(quantity=quantity)
        success = arduino_controller.send_command(command)

        command = BuzzCommand(duration_ms=1000, frequency=500)
        success = arduino_controller.send_command(command)

        if success:
            print("RPC Handler: Dispense command successful!")
            return {"status": "success", "message": f"dispensed {quantity}"}
        else:
            print(f"RPC Handler Error: Failed to execute dispense command on Arduino")
            return {"status": "error", "message": "Failed to execute dispense command on Arduino"}

    except Exception as e:
        print(f"RPC Handler Error: Exception {e}")
        return {"status": "error", "message": f"Erorr during execution: {e}"}


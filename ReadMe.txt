Explanation

Initialize the RFID reader: The SimpleMFRC522 class is used to interface with the MFRC522 RFID reader.

Network Communication: verify_card(card_id) sends the card ID to the server and checks if the card is authorized.

Relay Control: control_door(open_door) opens or closes the door based on the server response.

Main Workflow: The main() function continuously reads the card, verifies it with the server, controls the door relay, and sends the door status to the server.




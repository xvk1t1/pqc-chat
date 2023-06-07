import socket
import threading

import aescipher
import oqs
import pqc_colors


class PQCClient:
    def __init__(self, server_ip, server_port, kem_alg):
        self.server_ip = server_ip
        self.server_port = server_port
        self.kem_alg = kem_alg
        self.shared_secret = ""
        self.cipher_client = None

    def clean_user_prompt(self):
        for _ in range(15):
            print("\b", end="")

    def print_separator(self):
        print("================================================")

    # Function that handles the messages received from the server
    def receive_messages(self, client_socket):
        while True:
            try:
                cipher_text = client_socket.recv(4096)
                if cipher_text:
                    message = self.cipher_client.decrypt(cipher_text)
                    self.clean_user_prompt()
                    print(
                        f"{pqc_colors.PQCColors.MAGENTA}[{self.server_ip}:{self.server_port}]:{pqc_colors.PQCColors.RESET} {message}"
                    )
                    print(
                        pqc_colors.PQCColors.GREEN
                        + "[Your message]:"
                        + pqc_colors.PQCColors.RESET,
                        end="",
                        flush=True,
                    )

                    if message.lower() == "bye":
                        self.clean_user_prompt()
                        self.print_separator()
                        print(
                            f"Server disconnected --> [{self.server_ip}:{self.server_port}]"
                        )
                        break
                else:
                    self.clean_user_prompt()
                    self.print_separator()
                    print(
                        f"Server disconnected --> [{self.server_ip}:{self.server_port}]"
                    )
                    break

            except ConnectionResetError:
                self.clean_user_prompt()
                self.print_separator()
                print(
                    pqc_colors.PQCColors.RED
                    + "Connection with the server lost."
                    + pqc_colors.PQCColors.RESET
                )
                break

    # Function used to send messages to the server
    def send_message(self, client_socket):
        while True:
            print(
                pqc_colors.PQCColors.GREEN
                + "[Your message]:"
                + pqc_colors.PQCColors.RESET,
                end="",
                flush=True,
            )
            message = input()
            cipher_text = self.cipher_client.encrypt(message)
            client_socket.send(cipher_text)

    def run_client(self):
        # Socket creation and connection to the server
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.connect((self.server_ip, self.server_port))
        print(f"Client connected to server: [{self.server_ip}:{self.server_port}]")
        self.print_separator()

        # Server PQC Key Exchange Mechanism
        client_kem = oqs.KeyEncapsulation(self.kem_alg)

        # Generate a key pair and send the public key to the server
        public_key = client_kem.generate_keypair()
        client_socket.send(public_key)

        # print("Public Key en Client: ", public_key.hex())

        # Receive the shared secret from the server
        cipher_key = client_socket.recv(4096)
        # De-encapsulation of the shared secret received from the server (PQC Algorithm)
        self.shared_secret = client_kem.decap_secret(cipher_key)

        # print("Shared Secret Client: ", self.shared_secret.hex())

        # AES-256 cipher
        self.cipher_client = aescipher.AESCipher(self.shared_secret.hex())

        # Thread creation to run the send_message function
        send_thread = threading.Thread(target=self.send_message, args=(client_socket,))
        send_thread.start()

        self.receive_messages(client_socket)

        client_socket.close()

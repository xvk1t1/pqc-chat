import socket
import threading

import aescipher
import oqs
import pqc_colors


class PQCServer:
    def __init__(self, ip, port, kem_alg):
        self.ip = ip
        self.port = port
        self.kem_alg = kem_alg
        self.shared_secret = ""
        self.cipher_server = None

    def print_user_prompt(self):
        print(
            pqc_colors.PQCColors.GREEN + "[Your message]:" + pqc_colors.PQCColors.RESET,
            end="",
            flush=True,
        )

    def clean_user_prompt(self):
        for _ in range(15):
            print("\b", end="")

    def print_separator(self):
        print("================================================")

    def print_client_disconnected(self, client_address):
        print(f"Client disconnected --> [{client_address[0]}:{client_address[1]}]")

    # Function that handles the messages received from the client
    def receive_messages(self, client_socket, client_address):
        while True:
            try:
                cipher_text = client_socket.recv(4096)
                if cipher_text:
                    message = self.cipher_server.decrypt(cipher_text)
                    self.clean_user_prompt()
                    print(
                        f"{pqc_colors.PQCColors.MAGENTA}[{client_address[0]}:{client_address[1]}]:{pqc_colors.PQCColors.RESET} {message}"
                    )
                    self.print_user_prompt()

                    if message.lower() == "bye":
                        self.clean_user_prompt()
                        self.print_separator()
                        self.print_client_disconnected(client_address)
                        break

                else:
                    self.clean_user_prompt()
                    self.print_separator()
                    self.print_client_disconnected(client_address)
                    break

            except ConnectionResetError:
                self.clean_user_prompt()
                self.print_separator()
                print(
                    f"{pqc_colors.PQCColors.RED}Client connection lost --> [{client_address[0]}:{client_address[1]}]{pqc_colors.PQCColors.RESET}"
                )
                break

        client_socket.close()

    # Function used to send messages to the client
    def send_message(self, client_socket):
        while True:
            self.print_user_prompt()
            message = input()
            cipher_text = self.cipher_server.encrypt(message)
            client_socket.send(cipher_text)

    def run_server(self):
        # Socket creation and configuration
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server_socket.bind((self.ip, self.port))
        server_socket.listen(1)

        print(f"Server listening on [{self.ip}:{self.port}]")
        self.print_separator()

        client_socket, client_address = server_socket.accept()
        print(f"Client connected --> [{client_address[0]}:{client_address[1]}]")
        self.print_separator()

        # Server PQC Key Encapsulation Mechanism
        server_kem = oqs.KeyEncapsulation(self.kem_alg)

        # Public key received from the client
        public_key = client_socket.recv(4096)

        # print("Public Key en Server: ", public_key.hex())

        cipher_key, self.shared_secret = server_kem.encap_secret(public_key)
        client_socket.send(cipher_key)

        # print("Shared Secret Server: ", self.shared_secret.hex())

        self.cipher_server = aescipher.AESCipher(self.shared_secret.hex())

        send_thread = threading.Thread(target=self.send_message, args=(client_socket,))
        send_thread.start()

        self.receive_messages(client_socket, client_address)

        server_socket.close()

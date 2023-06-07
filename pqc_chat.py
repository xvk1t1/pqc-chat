import os
import argparse
import ipaddress
import pqc_server
import pqc_client
import pqc_colors

def server(ip,port,kem_alg):
    # Código del servidor
    # Aquí puedes implementar la lógica del servidor
    print("Starting server...")
    server = pqc_server.PQCServer(ip,port,kem_alg)
    server.run_server()

def client(ip,port,kem_alg):
    # Código del cliente
    # Aquí puedes implementar la lógica del cliente
    print("Starting client...")
    client = pqc_client.PQCClient(ip,port,kem_alg)
    client.run_client()

def validate_ip(ip):
    try:
        ipaddress.IPv4Address(ip)
        return ip
    except ipaddress.AddressValueError:
        raise argparse.ArgumentTypeError(f'Error: {ip} is not a valid IP address')
    
def validate_port(port):
    try:
        port = int(port)
        if 1 <= port <= 65535:
            return port
        else:
            raise ValueError()
    except (ValueError, TypeError):
        raise argparse.ArgumentTypeError(f'Error: {port} is not a valid port number')

def main():

    ascii_art = r'''
 ________  ________  ________                ________  ___  ___  ________  _________       
|\   __  \|\   __  \|\   ____\              |\   ____\|\  \|\  \|\   __  \|\___   ___\     
\ \  \|\  \ \  \|\  \ \  \___|  ____________\ \  \___|\ \  \\\  \ \  \|\  \|___ \  \_|     
 \ \   ____\ \  \\\  \ \  \    |\____________\ \  \    \ \   __  \ \   __  \   \ \  \      
  \ \  \___|\ \  \\\  \ \  \___\|____________|\ \  \____\ \  \ \  \ \  \ \  \   \ \  \     
   \ \__\    \ \_____  \ \_______\             \ \_______\ \__\ \__\ \__\ \__\   \ \__\    
    \|__|     \|___| \__\|_______|              \|_______|\|__|\|__|\|__|\|__|    \|__|    
                    \|__|'''

    print(pqc_colors.PQCColors.YELLOW + ascii_art + pqc_colors.PQCColors.RESET)
    print("\n================================================")
    print("A real-time terminal chat that uses post-quantum cryptography")
    print("by David PG (@xvk1t1) & Diego GC (@dydek)")
    print("================================================")

    # Configurar los argumentos de línea de comandos
    parser = argparse.ArgumentParser()
    parser.add_argument('-m', '--mode', help='Execution mode: server o client', required=True, choices=['server', 'client'])
    parser.add_argument('-a', '--ip', help='IP on wich the server will be deployed // IP that the client will try to connect to', default='127.0.0.1', type=validate_ip)
    parser.add_argument('-p', '--port', help='Connection port', type=validate_port, default=12345)

    args = parser.parse_args()

    kem_alg = "Kyber1024"

    if args.mode == 'server':
        server(args.ip,args.port,kem_alg)
    elif args.mode == 'client':
        client(args.ip,args.port,kem_alg)

    print("Chat session finished, bye!")
    os._exit(0)


if __name__ == '__main__':
    main()
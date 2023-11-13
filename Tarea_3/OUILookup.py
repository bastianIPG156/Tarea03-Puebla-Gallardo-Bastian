import argparse
import requests
import subprocess
import getopt
import sys
import time

def obtener_mac_address(ip):
    try:
        # Implementa la lógica para obtener la dirección MAC por IP aquí
        # En este ejemplo, usamos 'arp' para obtener la dirección MAC asociada con la IP
        arp_result = subprocess.check_output(["arp", "-a", ip]).decode("CP437").strip()
        if len(arp_result) > 0:
            mac_address = arp_result.split()[11]
            correcion_maC = mac_address.replace("-", ":")
            return correcion_maC
        else:
            return None
    except Exception as e:
        return False

def obtener_fabricante(mac,local):
    try:
        
        if local == True:
            fabricante = "Not found"

            startTime = time.time()
            with open("fabricantes3.txt", "r") as archivo_csv:
                mapeo = archivo_csv.readlines()
            
            for linea in mapeo:
                partes = linea.strip().split(',') 
                if partes[0] == mac[:13].upper():
                    fabricante = partes[1]

                    endTime = time.time()
                    tiempo_respuesta = int(round((endTime - startTime) * 1000))
                    Result = str(tiempo_respuesta) + "ms"
                    return fabricante,Result
                
            for linea in mapeo:
                partes = linea.strip().split(',') 
                if partes[0] == mac[:10].upper():
                    fabricante = partes[1]

                    endTime = time.time()
                    tiempo_respuesta = int(round((endTime - startTime) * 1000))
                    Result = str(tiempo_respuesta) + "ms"
                    return fabricante,Result     
                      
                
            for linea in mapeo:
                partes = linea.strip().split(',') 
                if partes[0] == mac[:8].upper():
                    fabricante = partes[1]

                    endTime = time.time()
                    tiempo_respuesta = int(round((endTime - startTime) * 1000))
                    Result = str(tiempo_respuesta) + "ms"
                    return fabricante,Result      
            else:
                return fabricante
          
        else:    
            fabricante = "Not found"
            url = "https://raw.githubusercontent.com/boundary/wireshark/master/manuf"
            startTime = time.time()
            response = requests.get(url)    
            endTime = time.time()



            if response.status_code == 200:
                for line in response.text.splitlines():
                    
                    if line.startswith(mac[:14]):  
                        fabricante = line.split('\t', 1)[1]
                        break
                
                if fabricante == "Not found":
                    for line in response.text.splitlines():  
                        if line.startswith(mac[:8]):
                    
                            fabricante = line.split('\t', 1)[1]
                            break
                
                tiempo_respuesta = int(round((endTime - startTime) * 1000))
                Result = str(tiempo_respuesta) + "ms"
            
                return fabricante,Result 
            else:
                return fabricante
    except Exception as e:
        return f"Error: {e}"


def obtieneArp():
    
    consulta_arp = subprocess.check_output(["arp", "-a"]).decode("CP437")
    
    tabla_arp = []
    lineas = consulta_arp.splitlines()
    for linea in lineas:
        lalinea = linea.split()
        tabla_arp.append(lalinea)

    datos_arp = []
    for linea in tabla_arp:            
        if len(linea) != 0:
            if len(linea[0].split(".")) == 4:
                correcion_mac = linea[1].replace("-", ":")
                datos_arp.append((linea[0], correcion_mac))
    return datos_arp





def parse_args_argparse():
    parser = argparse.ArgumentParser(description="Consulta el fabricante de una tarjeta de red por su dirección IP o MAC.")
    parser.add_argument("-i", "--ip", type=str, help="Dirección IP del host a consultar.")
    parser.add_argument("-m", "--mac", type=str, help="MAC a consultar. P.e. aa:bb:cc:00:00:00.")
    parser.add_argument("-a", "--arp", action="store_true", help="Muestra los fabricantes de los hosts disponibles en la tabla arp.")
    parser.add_argument("-l", "--local", action="store_true", help="Utiliza base de datos local.")
    return parser.parse_args()

def parse_args_getopt(argv):
    ip = None
    mac = None
    arp = False
    local = False

    try:
        opts, args = getopt.getopt(argv, "i:m:a:l")
    except getopt.GetoptError:
        print("Uso: python script.py -i <IP> | -m <MAC> | -a<ARP> | -l <LOCAL>")
        sys.exit(2)

    for opt, arg in opts:
        if opt in ("-i"):
            ip = arg
        elif opt in ("-m"):
            mac = arg
        elif opt in ("-a"):
            arp = True
        elif opt in ("-l"):
            local = True    

    return ip, mac, arp,local

def main():
    if len(sys.argv) > 1 and sys.argv[1] in ("-i", "--ip", "-m", "--mac", "-a", "--arp", "-l","--local"):
        # Usar argparse si se proporcionan argumentos específicos de argparse
        args = parse_args_argparse()
        #tabla_arp = obtener_tabla_arp(url="https://raw.githubusercontent.com/boundary/wireshark/master/manuf")
        ip, mac, arp, local = args.ip, args.mac, args.arp,args.local
    else:
        # Usar getopt si no se proporcionan argumentos específicos de argparse
        ip, mac, arp = parse_args_getopt(sys.argv[1:])

    if ip:
        mac_address = obtener_mac_address(ip)
        if mac_address:
            fabricante = obtener_fabricante(mac_address,local)
            print(f"\nMAC address: {mac_address}\nFabricante: {fabricante}\n")
        else:
            print(f"\nError: IP está fuera de la red del host.\n")
        
    elif mac:
        fabricante = obtener_fabricante(mac,local)
        print(f"\nMAC address: {mac}\nFabricante: {fabricante}\n")

    elif arp:
        tabla_arp = obtieneArp()

        if tabla_arp:
            print(f"\nIP/MAC/Vendor:")
            for entry in tabla_arp:
                fabricante = obtener_fabricante(entry[1],local)
                print(f"{entry[0]} / {entry[1]} / {fabricante}")
            print(f"\n ")

        else:
            print("Error al obtener la tabla ARP")
        

    else:
        print("Por favor, proporciona una opción válida (-i, -m o -a).")

if __name__ == "__main__":
    main()
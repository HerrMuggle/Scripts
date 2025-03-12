import threading
from scapy.all import ARP, Ether, srp

# Lock for writing to the file safely in multiple threads
lock = threading.Lock()

# Function to scan a single IP and save results
def scan_ip(ip):
    arp_request = ARP(pdst=ip)
    broadcast = Ether(dst="ff:ff:ff:ff:ff:ff")
    arp_request_broadcast = broadcast / arp_request
    answered, _ = srp(arp_request_broadcast, timeout=1, verbose=False)

    for sent, received in answered:
        result = f"{received.psrc}\t\t{received.hwsrc}\n"
        print(result.strip())

        # Write to file with threading lock
        with lock:
            with open("ip.txt", "a") as file:
                file.write(result)

# Function to scan a network range using threading
def scan_network(network_range):
    print("\nScanning network, please wait...\n")
    print("IP Address\t\tMAC Address")
    print("-" * 40)

    # Clear previous output file
    with open("ip.txt", "w") as file:
        file.write("IP Address\t\tMAC Address\n")
        file.write("-" * 40 + "\n")

    # Extract the subnet prefix (e.g., 192.168.1.)
    subnet_prefix = ".".join(network_range.split(".")[:3]) + "."

    threads = []
    for i in range(1, 255):  # Scanning from .1 to .254
        ip = f"{subnet_prefix}{i}"
        thread = threading.Thread(target=scan_ip, args=(ip,))
        threads.append(thread)
        thread.start()

    # Wait for all threads to finish
    for thread in threads:
        thread.join()

    print("\nScan complete! Results saved to ip.txt")

# Example usage
network_range = input("Enter network range (e.g., 192.168.1.0/24): ")
scan_network(network_range)

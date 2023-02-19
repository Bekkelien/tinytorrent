
import socket

import asyncio
import socket
from struct import pack, unpack
from src.protocol import Handshake
from bitstring import BitArray
from src.config import Config

<<<<<<< HEAD
=======
#peer_ips = [['109.68.118.81', 41080], ['46.0.80.146', 51602], ['158.62.11.99', 10242], ['102.150.37.178', 6881], ['116.206.229.136', 27721], ['96.241.182.66', 37000], ['213.197.95.141', 19759], ['185.146.212.131', 16540], ['120.204.169.205', 3629], ['91.228.35.84', 6881], ['46.214.35.217', 24763], ['93.66.127.151', 54273], ['62.4.35.96', 41972], ['185.170.226.238', 60890], ['177.39.153.146', 6881], ['77.70.29.115', 12641], ['93.171.214.215', 37736], ['136.158.1.208', 35870], ['5.59.147.103', 28581], ['46.204.12.117', 36736], ['189.123.54.74', 42140], ['66.115.189.171', 54987], ['136.35.123.84', 56886], ['81.103.210.154', 6881], ['82.79.100.235', 55960], ['109.178.192.250', 29716], ['198.44.136.155', 60758], ['50.25.62.64', 14356], ['198.52.148.243', 51413], ['91.135.222.3', 6881], ['109.184.248.23', 6881], ['86.120.125.12', 8999], ['213.55.241.233', 21348], ['80.70.111.130', 58929], ['112.211.37.164', 26099], ['94.225.70.91', 17385], ['2.83.181.2', 6881], ['46.98.212.20', 32427], ['128.71.162.216', 45566], ['95.92.181.70', 33596], ['188.6.189.158', 8940], ['95.176.153.20', 41635], ['69.248.154.19', 47283], ['133.218.15.169', 59907], ['84.3.70.160', 16881], ['185.25.123.186', 6881], ['217.72.11.174', 57190], ['36.5.86.79', 6881], ['76.71.157.107', 45877], ['31.132.212.155', 17672], ['188.143.60.14', 32377], ['92.60.179.111', 48155], ['81.171.5.232', 50169], ['151.46.25.200', 46007], ['99.172.25.125', 51413], ['5.48.228.238', 51413], ['103.137.206.130', 17656], ['45.26.158.99', 34052], ['31.46.69.230', 45372], ['94.213.190.171', 60928], ['217.64.151.29', 65065], ['91.160.221.128', 43107], ['195.181.172.149', 10259], ['190.22.1.103', 40608], ['113.145.205.70', 6881], ['93.139.74.28', 22122], ['185.84.172.196', 23751], ['183.80.212.78', 3800], ['197.232.36.108', 40404], ['136.158.63.86', 6881], ['31.183.195.162', 6881], ['81.182.76.82', 39058], ['146.212.113.73', 23641], ['204.137.220.15', 32187], ['216.10.216.25', 6881], ['94.241.63.229', 25977], ['31.60.239.65', 6881], ['125.162.64.229', 6881], ['91.231.122.32', 6881], ['151.251.7.17', 6886], ['109.252.139.130', 54719], ['185.221.140.30', 20154], ['88.10.40.128', 6881], ['171.76.83.48', 6881], ['189.122.164.205', 11143], ['95.167.172.90', 33518], ['41.223.73.244', 6881], ['46.235.97.87', 64071], ['188.168.215.35', 35239], ['89.178.96.136', 6881], ['83.246.166.3', 6881], ['91.105.184.122', 40138], ['83.28.236.193', 51411], ['109.93.191.84', 60381], ['185.125.113.16', 28358], ['96.252.82.210', 43593], ['77.125.30.180', 6881], ['178.57.52.192', 6881], ['192.145.116.35', 61548], ['190.167.7.195', 23529], ['188.163.37.63', 10646], ['151.37.208.25', 15238], ['185.65.135.145', 59348], ['178.222.145.119', 30171], ['143.90.227.102', 11158], ['213.227.68.204', 61515], ['136.158.46.238', 49032], ['94.79.36.210', 6881], ['79.155.49.66', 18832], ['83.29.132.103', 62593], ['2.62.254.50', 54681], ['91.145.141.175', 6881], ['84.237.180.9', 33108], ['98.213.224.241', 51509], ['188.156.190.86', 41252], ['82.64.86.122', 6887], ['79.163.181.194', 60847], ['176.63.4.129', 6881], ['31.223.108.233', 30279], ['78.90.31.226', 1226], ['62.117.111.195', 36158], ['166.48.211.154', 35172], ['2.137.184.236', 53651], ['88.124.58.171', 26863], ['50.52.37.122', 1276], ['77.254.6.101', 6881], ['191.6.90.121', 6881], ['103.36.19.150', 35235], ['185.213.155.177', 56935], ['81.182.208.126', 22897], ['201.229.87.53', 42294], ['85.236.189.108', 62287], ['5.178.12.148', 41963], ['157.49.238.34', 28565], ['178.66.157.94', 23328], ['45.133.5.90', 26734], ['94.25.60.197', 23214], ['109.144.212.73', 60606], ['90.114.223.241', 17260], ['46.53.252.49', 16948], ['109.202.37.100', 51413], ['73.119.242.186', 48635], ['78.153.5.183', 51413], ['85.249.20.226', 43788], ['90.191.210.61', 46514], ['83.24.89.39', 10557], ['138.94.191.161', 6881], ['185.144.160.84', 40063], ['178.40.245.237', 51413], ['178.209.136.112', 29969], ['49.15.232.83', 6881], ['185.159.157.9', 20301], ['176.59.192.206', 65191], ['178.91.194.125', 25741], ['92.39.213.248', 6881], ['195.158.232.68', 44341], ['197.59.37.66', 25006], ['95.189.76.182', 21406], ['45.153.209.96', 6881], ['81.182.3.58', 61422], ['88.112.152.95', 51318], ['82.197.107.202', 16881], ['118.71.233.100', 3800], ['46.188.121.38', 41172], ['194.195.93.24', 20141], ['62.216.209.91', 6881], ['5.187.86.128', 19450], ['72.134.140.27', 56153], ['178.205.49.178', 22072], ['73.70.133.172', 4220], ['177.53.6.123', 46559], ['109.191.244.17', 51413], ['105.196.68.67', 41238], ['180.191.222.31', 51951], ['197.60.118.112', 49160], ['94.181.44.243', 51413], ['71.87.80.125', 6881], ['94.190.55.42', 28383], ['212.3.193.155', 45781], ['81.90.124.158', 6881], ['178.178.96.154', 6881], ['107.150.23.167', 44538], ['185.85.160.179', 6881], ['31.135.182.162', 33561], ['119.76.1.89', 61586], ['73.69.209.12', 17981], ['96.55.252.160', 35145], ['27.71.120.137', 42056], ['37.234.252.187', 32359], ['176.52.76.213', 28166], ['77.108.7.29', 51413], ['162.206.221.216', 33674], ['46.146.231.187', 36385], ['149.86.49.3', 49312], ['91.157.118.63', 50133], ['62.165.222.8', 21124], ['193.226.239.206', 26873], ['175.141.173.205', 61364], ['79.112.165.165', 24276], ['95.54.117.134', 26402], ['77.110.144.234', 51413], ['97.125.172.66', 34621], ['88.164.109.88', 12644], ['37.145.63.95', 52908], ['152.32.107.18', 8999], ['89.109.50.32', 55386], ['93.44.188.167', 42093], ['216.149.208.13', 19979], ['37.57.120.84', 19801], ['185.152.123.22', 19565], ['80.128.71.11', 32868], ['2.92.126.216', 9059], ['89.22.17.29', 26985], ['46.233.236.171', 26188], ['77.49.67.15', 58682], ['194.165.115.37', 51413], ['189.112.223.123', 6881], ['80.76.104.117', 54673], ['73.114.189.187', 38194], ['46.149.86.107', 34181], ['123.163.26.238', 1036], ['105.99.110.117', 59325], ['41.142.63.247', 13455], ['195.189.180.38', 57583], ['187.20.171.15', 60443], ['62.148.157.2', 6881], ['109.93.155.193', 23580], ['213.44.161.84', 6881], ['94.208.82.94', 30331], ['81.64.7.167', 16881], ['178.204.28.201', 46422], ['31.10.172.239', 6881], ['109.131.128.103', 38157], ['217.228.129.131', 55553], ['91.120.96.120', 60526], ['23.138.176.127', 47150], ['82.65.244.73', 41440], ['73.167.80.63', 36488], ['79.139.171.75', 37687], ['118.210.175.140', 28018], ['109.173.4.60', 49253], ['37.79.33.140', 6597], ['58.186.71.82', 3800], ['86.49.225.207', 63782], ['187.22.124.136', 6881], ['5.128.91.17', 6535], ['94.254.177.3', 43800], ['124.122.133.81', 26156], ['217.16.134.201', 22673], ['78.21.98.11', 21910], ['62.240.24.94', 52111], ['177.131.117.199', 16386], ['95.168.47.128', 54330], ['178.184.102.155', 61030], ['2.58.46.154', 59825], ['188.233.126.111', 25863], ['194.35.185.167', 51413], ['5.178.15.220', 41963], ['188.6.92.63', 22162], ['79.111.131.47', 33022], ['5.255.183.181', 49612], ['47.224.250.87', 27001], ['91.245.254.6', 51413], ['98.213.228.92', 38960], ['159.224.231.93', 45580], ['85.230.198.93', 6881], ['188.186.100.0', 24447], ['5.90.37.71', 20471], ['210.237.43.168', 24238], ['203.220.212.253', 6881], ['156.67.97.16', 33467], ['88.103.133.246', 64221], ['84.42.73.35', 64310], ['102.217.40.126', 6881], ['128.0.226.137', 53323], ['27.92.233.37', 47238], ['62.122.119.236', 6881], ['37.144.211.6', 6881], ['188.253.237.98', 51041], ['114.225.17.33', 45345], ['183.83.228.200', 18520], ['223.16.92.88', 6881], ['213.55.240.165', 54409], ['176.115.97.205', 64684], ['178.87.103.103', 14082], ['41.225.42.166', 46365], ['95.31.166.20', 36246], ['77.85.83.239', 20311], ['182.180.62.223', 43360], ['37.169.45.42', 51413], ['51.158.36.158', 51413], ['46.148.186.202', 55552], ['109.252.62.233', 32354], ['147.78.161.23', 8652], ['176.41.57.188', 61375], ['46.149.83.11', 34270], ['46.22.56.178', 35314], ['58.186.167.6', 49137], ['83.63.61.118', 6881], ['31.40.132.1', 6888], ['187.16.116.54', 6881], ['27.147.190.192', 57403], ['82.64.86.122', 6890], ['79.164.24.122', 39262], ['188.239.125.2', 7999], ['37.47.81.196', 6881], ['114.190.250.89', 42153], ['46.107.170.8', 33585], ['78.81.186.2', 15984], ['105.105.166.114', 62771], ['185.178.95.234', 44336], ['1.52.218.140', 3800], ['78.92.142.155', 23089], ['180.191.181.60', 7921], ['114.23.255.43', 53250], ['86.58.36.77', 45538], ['81.183.59.235', 37007], ['93.170.117.11', 60683], ['188.157.12.154', 50184], ['178.90.235.137', 49459], ['91.121.116.106', 2000], ['185.17.128.26', 21830], ['188.43.108.201', 51413], ['193.148.18.52', 22746], ['187.65.198.166', 64013], ['87.103.208.60', 57026], ['93.37.208.56', 49160], ['49.49.235.76', 6881], ['73.207.161.181', 56979], ['172.248.212.255', 6881], ['27.147.201.151', 53732], ['188.36.33.237', 64438], ['175.37.216.46', 12213], ['94.25.227.250', 52600], ['109.222.36.82', 51413], ['92.53.144.26', 52367], ['88.147.152.251', 6881], ['81.107.167.247', 6881], ['85.106.97.61', 54127], ['31.61.166.224', 60351], ['136.158.27.192', 13718], ['37.200.90.119', 6881], ['89.134.28.192', 52029], ['218.86.190.209', 51413], ['86.121.92.157', 57025], ['93.51.18.111', 51413], ['36.85.34.45', 6881], ['95.53.6.17', 64200], ['178.36.116.168', 40273], ['112.204.161.0', 21024], ['101.181.44.71', 18107], ['77.38.151.252', 52048], ['31.211.44.97', 61164], ['36.8.212.240', 33182], ['46.123.254.194', 22987], ['188.163.27.167', 15904], ['74.135.12.134', 6883], ['90.101.161.105', 17862], ['185.53.146.14', 40096], ['89.36.76.142', 6881], ['165.0.96.129', 58109], ['5.55.44.249', 12950], ['84.143.226.154', 16881], ['102.65.70.93', 56727], ['176.63.23.139', 10171], ['81.65.158.55', 51413], ['2.82.148.124', 61867], ['89.212.242.180', 43254], ['68.99.210.103', 34290], ['85.67.53.105', 55900], ['83.243.68.194', 57490], ['191.96.106.121', 1337], ['37.235.153.240', 10017], ['5.14.188.222', 11910], ['62.217.186.207', 6881], ['94.233.240.115', 45475], ['88.210.29.232', 40239], ['27.79.54.192', 3800], ['46.191.188.255', 49462], ['213.230.112.9', 6881], ['146.70.171.100', 59286], ['122.172.87.193', 6881], ['45.160.89.215', 48734], ['5.29.217.111', 41871], ['176.56.5.246', 37865], ['103.251.227.225', 15082]]
#
#metadata={  
#        'pieces': 1012,
#        'size': 265289728,
#        'files': {'length': 265283496, 'path': ['gimp-2.10.32-setup-1.exe']},
#        'bitfield_spare_bits': 4,
#        'bitfield_length': 1016
#        }
#

>>>>>>> 7da47cbc27898a00d48b00302a499abfcf909517
# Configuration settings
config = Config().get_config()

peer_ip_handshake_ok = []

def handshake_validate(response, info_hash=b'\x86"kA\x98Z$Z\xc0\xc9\xa8\x94n\x1emfC\xffd\xf3')-> bool:
    if 49 <= len(response) <= 67:
        print("Handshake response of type: compact peer formate is not supported")
    
    elif len(response) >= 68:
        response = unpack('>1s19s8s20s20s', response[0:68])

        # Parse handshake response (Bytes) b'data'
        handshake_pstrlen = response[0]
        handshake_pstr = response[1]
        handshake_reserved = response[2] # TODO            
        handshake_info_hash = response[3]
        handshake_client_id = response[4] # TODO
        
        if (Handshake.pstrlen + Handshake.pstr) != handshake_pstrlen + handshake_pstr:
            print("Handshake response failed unknown protocol:", handshake_pstr.decode("utf-8", "ignore"))
            return False


        # Validate
        if info_hash == handshake_info_hash:
            print("Handshake accepted")
            return True


async def handshake_tasks(peer_ips, metadata, peer_id) -> None:

    print("Sending handshake to peers:", len(peer_ips))

    message = pack('>1s19s8s20s20s', Handshake.pstrlen,
                                        Handshake.pstr,
                                        Handshake.reserved,
                                        metadata['info_hash'],
                                        peer_id.encode())

    tasks = []
    for peer_ip in peer_ips:
        tasks.append(asyncio.create_task(handshake_send_recv(peer_ip, message)))

    await asyncio.gather(*tasks)


async def handshake_send_recv(peer_ip, message) -> bytes:

    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.settimeout(config['tcp']['timeout'])

    #print("Connecting to peer:", peer_ip[0], "::" , peer_ip[1])

    try:

        reader, writer = await asyncio.wait_for(asyncio.open_connection(*peer_ip), timeout=config['tcp']['timeout'])
        writer.write(message) # Response from server
        response_handshake = await asyncio.wait_for(reader.read(config['tcp']['handshake_buffer']), timeout=config['tcp']['timeout'])


        # A bit messy to have 2 recv in one function
        try:
            writer.write(message) # Response from server
            response_bitfield = await asyncio.wait_for(reader.read(config['tcp']['handshake_buffer']), timeout=config['tcp']['timeout'])
            bitfield_id = unpack('>b', response_bitfield[4:5])[0]

        except:
            bitfield_id = None

        # TODO CLEANUP THIS
        if handshake_validate(response_handshake):
            peer_state ='unknown'

            if bitfield_id == 5:
                bitfield_payload = response_bitfield[5:]

                # Test if this is working
                if len(BitArray(bitfield_payload).bin) == metadata['bitfield_length']:
                    if BitArray(bitfield_payload).bin.count('1') == metadata['pieces']:
                        peer_state = 'seeder' # Peer has 100% of data 
                    else:
                        peer_state = 'leecher' # Peer has x% of data 

        peer_ip_handshake_ok.append([peer_ip,peer_state])


    except asyncio.TimeoutError:
        print("Connection to peer timed out")

    except Exception as ConnectionError:
        print("Connection to peer failed", ConnectionError)

async def run_handshakes(peer_ips, metadata):
    await handshake_tasks(peer_ips, metadata, peer_id="-TI2080-MH5k6JGjhlNb")


# TESTING
from src.manager import TrackerManager
from src.read_torrent import TorrentFile
from pathlib import Path

PATH = Path('./src/files/')
file = 'gimp.torrent'

metadata = TorrentFile(PATH / file).read()
tracker = TrackerManager(metadata)
peer_ips = tracker.get_clients()


asyncio.run(run_handshakes(peer_ips,metadata))
print(peer_ip_handshake_ok)


# This is Codec 8 Extended version of Teltonika
import binascii

from loguru import logger

from memory import Memory


def parse(packet: bytes, address):
    """
    Parses a packet and returns a dictionary with the parsed data.

    Key Responsibilities:

    1. **Packet Identification**: Determines whether the packet is an IMEI packet (17 bytes) or another type.
    2. **IMEI Parsing**: If the packet is an IMEI, it decodes and maps the IMEI to a MAC address.
    3. **Further Parsing**: If the packet is not an IMEI, it continues parsing other fields, such as MAC, codec ID, AVL data, and CRC.

    Methods:

    1. **Memory.add_to_memory**: If the packet is an IMEI packet, it maps the IMEI to a MAC address and stores it in the memory.
    2. **Sub-parsers**: The packet is parsed further based on its structure using methods like get_AVL_data, get_IO_element, etc.
    """
    source_address = address[0] + ":" + str(address[1])
    # packet = binascii.hexlify(packet)
    parsed = {}
    if len(packet) == 17:  # It's IMEI
        logger.debug("len 17 bytes")
        # unhexed = binascii.unhexlify(packet)
        parsed['IMEI_length'] = int.from_bytes(packet[0:2], byteorder='big')
        parsed["IMEI"] = packet[2:].decode("utf-8")

        Memory.add_to_memory(Memory.imei_to_mac(
            parsed["IMEI"]), source_address)

    else:
        # check if first 4 bytes are zero
        if packet[0:4] == b'\x00\x00\x00\x00':

            parsed['MAC'] = Memory.get_mac_by_address(source_address)
            CB = 0  # Current Byte
            parsed['preamble'] = binascii.hexlify(
                packet[CB:CB+4]).decode('utf-8')
            CB += 4
            parsed['data_field_length'] = int.from_bytes(
                packet[CB:CB+4], byteorder='big')
            CB += 4
            parsed['codec_ID'] = binascii.hexlify(
                packet[CB:CB+1]).decode('utf-8')
            CB += 1
            parsed['number_of_data_1'] = int.from_bytes(
                packet[CB:CB+1], byteorder='big')
            CB += 1
            parsed['AVL_data'], CB = get_AVL_data(
                packet, CB, parsed['number_of_data_1'])
            parsed['number_of_data_2'] = int.from_bytes(
                packet[CB:CB+1], byteorder='big')
            CB += 1
            parsed['CRC-16'] = binascii.hexlify(
                packet[CB:CB+4]).decode('utf-8')

        else:
            logger.error("Unknown Packet")
            logger.error(binascii.hexlify(packet))

    logger.debug(parsed)
    return parsed


def get_AVL_data(packet: bytes, CB: int, number_of_data_1: int = None):
    """
    This method extracts AVL data from the packet, which includes timestamps, priorities, GPS, and I/O elements.

    Key Responsibilities:

    1. **Data Extraction**: Iterates through the packet, extracting the AVL data items (timestamp, priority, GPS, I/O elements).
    2. **Sub-parsers**: Calls other methods like get_GPS_element and get_IO_element to extract specific fields.

    Methods:

    1. **get_GPS_element**: Extracts GPS data (longitude, latitude, altitude, speed, etc.).
    2. **get_IO_element**: Extracts I/O event data
    """
    AVL_data = []
    for i in range(number_of_data_1):
        AVL_data_item = {}
        AVL_data_item['timestamp'] = int.from_bytes(
            packet[CB:CB+8], byteorder='big')
        CB += 8
        AVL_data_item['priority'] = int.from_bytes(
            packet[CB:CB+1], byteorder='big')
        CB += 1
        AVL_data_item['GPS_element'], CB = get_GPS_element(packet, CB)
        AVL_data_item['IO_element'], CB = get_IO_element(packet, CB)
        AVL_data.append(AVL_data_item)
    return AVL_data, CB


def get_IO_element(packet: bytes, CB: int):
    """
    This method parses the I/O event data from the packet.

    Key Responsibilities:

    1.**Extracting I/O Event Data**: Extracts details such as event IDs and the number of I/O entries for different byte sizes (1-byte, 2-byte, etc.).
    2.**Sub-parsers**: Calls methods like get_one_byte_IO_list, get_two_byte_IO_list, etc., to further decode the I/O entries.

    Methods:

    1.**get_one_byte_IO_list, get_two_byte_IO_list, etc.**: These methods are responsible for parsing specific I/O entries based on their byte length.
    """
    IO_element = {}
    IO_element['event_IO_ID'] = int.from_bytes(
        packet[CB:CB+2], byteorder='big')
    CB += 2
    IO_element['n_of_total_ID'] = int.from_bytes(
        packet[CB:CB+2], byteorder='big')
    CB += 2
    IO_element['n1_of_one_byte_IO'] = int.from_bytes(
        packet[CB:CB+2], byteorder='big')
    CB += 2
    IO_element['one_byte_IO_list'], CB = get_one_byte_IO_list(
        packet, CB, IO_element['n1_of_one_byte_IO'])
    IO_element['n2_of_two_byte_IO'] = int.from_bytes(
        packet[CB:CB+2], byteorder='big')
    CB += 2
    IO_element['two_byte_IO_list'], CB = get_two_byte_IO_list(
        packet, CB, IO_element['n2_of_two_byte_IO'])
    IO_element['n4_of_four_byte_IO'] = int.from_bytes(
        packet[CB:CB+2], byteorder='big')
    CB += 2
    IO_element['four_byte_IO_list'], CB = get_four_byte_IO_list(
        packet, CB, IO_element['n4_of_four_byte_IO'])
    IO_element['n8_of_eight_byte_IO'] = int.from_bytes(
        packet[CB:CB+2], byteorder='big')
    CB += 2
    IO_element['eight_byte_IO_list'], CB = get_eight_byte_IO_list(
        packet, CB, IO_element['n8_of_eight_byte_IO'])
    IO_element['nX_of_X_byte_IO'] = int.from_bytes(
        packet[CB:CB+2], byteorder='big')
    CB += 2
    IO_element['X_byte_IO_list'], CB = get_X_byte_IO_list(
        packet, CB, IO_element['nX_of_X_byte_IO'])

    return IO_element, CB


def get_one_byte_IO_list(packet: bytes, CB: int, n1_of_one_byte_IO: int):
    one_byte_IO_list = []
    for i in range(n1_of_one_byte_IO):
        one_byte_IO_list.append({
            'IO_ID': int.from_bytes(packet[CB:CB+2], byteorder='big'),
            'IO_value': int.from_bytes(packet[CB+2:CB+3], byteorder='big')
        })
        CB += 3
    return one_byte_IO_list, CB


def get_two_byte_IO_list(packet: bytes, CB: int, n2_of_two_byte_IO: int):
    two_byte_IO_list = []
    for i in range(n2_of_two_byte_IO):
        two_byte_IO_list.append({
            'IO_ID': int.from_bytes(packet[CB:CB+2], byteorder='big'),
            'IO_value': int.from_bytes(packet[CB+2:CB+4], byteorder='big')
        })
        CB += 4
    return two_byte_IO_list, CB


def get_four_byte_IO_list(packet: bytes, CB: int, n4_of_four_byte_IO: int):
    four_byte_IO_list = []
    for i in range(n4_of_four_byte_IO):
        four_byte_IO_list.append({
            'IO_ID': int.from_bytes(packet[CB:CB+2], byteorder='big'),
            'IO_value': int.from_bytes(packet[CB+2:CB+6], byteorder='big')
        })
        CB += 6
    return four_byte_IO_list, CB


def get_eight_byte_IO_list(packet: bytes, CB: int, n8_of_eight_byte_IO: int):
    eight_byte_IO_list = []
    for i in range(n8_of_eight_byte_IO):
        eight_byte_IO_list.append({
            'IO_ID': int.from_bytes(packet[CB:CB+2], byteorder='big'),
            'IO_value': int.from_bytes(packet[CB+2:CB+10], byteorder='big')
        })
        CB += 10
    return eight_byte_IO_list, CB


def get_X_byte_IO_list(packet: bytes, CB: int, nX_of_X_byte_IO: int):
    X_byte_IO_list = []
    for i in range(nX_of_X_byte_IO):
        X_byte_IO_list.append({
            'IO_ID': int.from_bytes(packet[CB:CB+2], byteorder='big'),
            'IO_length': int.from_bytes(packet[CB+2:CB+4], byteorder='big'),
            # 'IO_value': int.from_bytes(packet[CB+4:CB+4+int.from_bytes(packet[CB+2:CB+4], byteorder='big')], byteorder='big')
            'IO_value': binascii.hexlify(packet[CB+4:CB+4+int.from_bytes(packet[CB+2:CB+4], byteorder='big')]).decode("utf-8")

        })
        CB += 2 + 2 + int.from_bytes(packet[CB+2:CB+4], byteorder='big')
    return X_byte_IO_list, CB


def get_GPS_element(packet: bytes, CB: int):
    GPS_element = {}
    GPS_element['longitude'] = int.from_bytes(
        packet[CB:CB+4], byteorder='big', signed=True)/1e7
    CB += 4
    GPS_element['latitude'] = int.from_bytes(
        packet[CB:CB+4], byteorder='big', signed=True)/1e7
    CB += 4
    GPS_element['altitude'] = int.from_bytes(
        packet[CB:CB+2], byteorder='big', signed=True)
    CB += 2
    GPS_element['angle'] = int.from_bytes(packet[CB:CB+2], byteorder='big')
    CB += 2
    GPS_element['satellites'] = int.from_bytes(
        packet[CB:CB+1], byteorder='big')
    CB += 1
    GPS_element['speed'] = int.from_bytes(packet[CB:CB+2], byteorder='big')
    CB += 2
    return GPS_element, CB

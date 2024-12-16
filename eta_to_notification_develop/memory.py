from loguru import logger


class Memory():

    """
    The `Memory` class provides a mechanism to manage the mapping between MAC addresses and generic addresses. It includes methods to generate a fake MAC address 
    from an IMEI, store mappings in a static dictionary, and retrieve stored MAC addresses. This can be useful in contexts like simulation environments or 
    testing where such mappings are required.

    Key Responsibilities:
    1. **MAC Address Generation**: Create a fake MAC address from an IMEI number.
    2. **Address-to-MAC Mapping**: Store and retrieve the mapping between an address and its corresponding MAC address.
    3. **Error Handling**: Provide a default fallback MAC address (`00:00:00:00:00:00`) when a requested mapping is not found.

    Methods:
    """

    MAC_ADDRESS_MAP = {}
    # generate a fake MAC address from IMEI number

    @staticmethod
    def imei_to_mac(imei: str):
        """
        Generates a  MAC address based on the last 12 characters of the given IMEI number.

        The method takes the last 12 characters of the IMEI, pads with zeroes if needed, and formats 
        them as a MAC address (e.g., 'AA:BB:CC:DD:EE:FF').

        Args:
            imei (str): The IMEI number from which to generate the MAC address.

        Returns:
            str: A fake MAC address derived from the IMEI number.
        """
        cropped_imei = imei[-12:].ljust(12, '0')
        return ':'.join(cropped_imei[i:i+2] for i in range(0, len(cropped_imei), 2))

    @staticmethod
    def add_to_memory(MAC: str, address: str):
        """
        Adds a new address-to-MAC mapping to the static dictionary.

        Args:
            MAC (str): The MAC address to be associated with the address.
            address (str): The address to which the MAC address is mapped.

        Returns:
            None
        """
        Memory.MAC_ADDRESS_MAP[address] = MAC

    @staticmethod
    def get_mac_by_address(address: str):
        """
        Retrieves the MAC address associated with a given address.

        If the address is not found in the dictionary, logs an error and returns a 
        default MAC address ('00:00:00:00:00:00').

        Args:
            address (str): The address for which to retrieve the MAC address.

        Returns:
            str: The associated MAC address or a default fallback if not found.
        """
        try:
            return Memory.MAC_ADDRESS_MAP[address]
        except Exception as e:
            logger.error(e)
            return '00:00:00:00:00:00'

from loguru import logger


class Memory():

    MAC_ADDRESS_MAP = {}
    # generate a fake MAC address from IMEI number

    @staticmethod
    def imei_to_mac(imei: str):
        # considering only the last 12 characters
        cropped_imei = imei[-12:].ljust(12, '0')
        return ':'.join(cropped_imei[i:i+2] for i in range(0, len(cropped_imei), 2))

    @staticmethod
    def add_to_memory(MAC: str, address: str):
        Memory.MAC_ADDRESS_MAP[address] = MAC

    @staticmethod
    def get_mac_by_address(address: str):
        try:
            return Memory.MAC_ADDRESS_MAP[address]
        except Exception as e:
            logger.error(e)
            return '00:00:00:00:00:00'

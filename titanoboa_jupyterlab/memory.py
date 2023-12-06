from shared_memory_dict import SharedMemoryDict


class Memory:
    addresses: dict[str, str] = SharedMemoryDict(name='addresses', size=1024)
    signatures: dict[str, str] = SharedMemoryDict(name='signatures', size=1024)

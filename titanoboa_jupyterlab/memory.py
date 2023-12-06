from shared_memory_dict import SharedMemoryDict


class SharedMemory:
    """
    A shared memory object that can be used to communicate between the Jupyter server and the BrowserSigner.
    The API and the Kernel run in separate processes, so we need to use shared memory to communicate between them.
    """

    def __init__(self):
        """ Initialize the shared memory object. """
        # this is a dictionary that maps the BrowserSigner's unique id to the address it is signing for
        self.addresses = SharedMemoryDict(name='addresses', size=1024)

        # this is a dictionary that maps the BrowserSigner's unique id to the transaction being signed
        self.signatures = SharedMemoryDict(name='signatures', size=1024)

    def close(self):
        """ Close the shared memory objects. """
        for shared_dict in [self.addresses, self.signatures]:
            shared_dict.shm.close()

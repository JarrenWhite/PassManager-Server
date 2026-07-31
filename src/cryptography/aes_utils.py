from typing import Optional, Tuple


# TODO - Placeholder class. Requires completion.

class AESUtils():

    def encrypt_request(
        self,
        plaintext: bytes,
        aes_key: bytes,
        add: Optional[bytes] = None,
    ) -> Tuple[bool, bytes]:
        """
        Encrypts request data using AES-256-GCM

        Returns:
            (bool)  True if encryption successful, false otherwise
            (bytes) Payload formatted as: nonce (12 bytes) || auth_tag (16 bytes) || ciphertext (variable)
        """
        return True, b''


    def decrypt_request(
        self,
        payload: bytes,
        key: bytes,
        add: Optional[bytes] = None,
    ) -> Tuple[bool, bytes]:
        """
        Decrypts and verifies request data encrypted with AES-256-GCM

        Returns:
            (bool)  True if decryption successful, false otherwise
            (bytes) The decrypted plaintext
        """
        return True, b''

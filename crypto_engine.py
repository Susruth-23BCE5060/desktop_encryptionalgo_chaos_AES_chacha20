'''import hashlib
import os
from Crypto.Cipher import AES, ChaCha20
from Crypto.Random import get_random_bytes

# --- 1. The Chaos Engine (The "Special Thing") ---
class ChaosEngine:
    """
    Generates a deterministic sequence of numbers based on the Logistic Map.
    Equation: x_new = r * x * (1 - x)
    """
    def __init__(self, password):
        # We turn the password into a number between 0.0 and 1.0 to start the chaos.
        # This ensures the same password always creates the same chaos pattern.
        hash_val = int(hashlib.sha256(password.encode()).hexdigest(), 16)
        self.x = (hash_val % 10**9) / 10**9  
        self.r = 3.99  # The "Chaos" control parameter (must be close to 4.0)

    def get_next_decision(self):
        # Iterate the chaos map
        self.x = self.r * self.x * (1 - self.x)
        return self.x

# --- 2. The Hybrid Cipher Class ---
class HybridCipher:
    def __init__(self, password):
        self.password = password
        # Generate two distinct 32-byte keys from the single password
        self.aes_key = hashlib.sha256(("AES_SALT" + password).encode()).digest()
        self.chacha_key = hashlib.sha256(("CHA_SALT" + password).encode()).digest()
        
        # Initialize Chaos Engine
        self.chaos = ChaosEngine(password)
        self.BLOCK_SIZE = 64 * 1024  # We process files in 64KB chunks

    def encrypt_file(self, file_path, status_callback=None):
        output_path = file_path + ".chaos"
        file_size = os.path.getsize(file_path)
        processed_bytes = 0
        
        with open(file_path, 'rb') as fin, open(output_path, 'wb') as fout:
            # Write a generic header to identify our file type
            fout.write(b'CHAOS_V1') 
            
            while True:
                chunk = fin.read(self.BLOCK_SIZE)
                if not chunk:
                    break
                
                # Ask Chaos Engine: AES or ChaCha?
                decision_val = self.chaos.get_next_decision()
                
                if decision_val > 0.5:
                    # --- OPTION A: AES-256 ---
                    # Create a new AES cipher for this chunk
                    cipher = AES.new(self.aes_key, AES.MODE_GCM)
                    ciphertext, tag = cipher.encrypt_and_digest(chunk)
                    
                    # Write format: [ID=0] [Nonce 16b] [Tag 16b] [Length 4b] [Ciphertext]
                    fout.write(b'\x00') 
                    fout.write(cipher.nonce)
                    fout.write(tag)
                    # We save the length of the chunk so we know how much to read back
                    fout.write(len(ciphertext).to_bytes(4, byteorder='big')) 
                    fout.write(ciphertext)
                    
                    if status_callback: status_callback(f"Block Encrypted: AES-256")

                else:
                    # --- OPTION B: ChaCha20 ---
                    # Create a new ChaCha cipher for this chunk
                    cipher = ChaCha20.new(key=self.chacha_key)
                    ciphertext = cipher.encrypt(chunk)
                    
                    # Write format: [ID=1] [Nonce 8b] [Length 4b] [Ciphertext]
                    fout.write(b'\x01')
                    fout.write(cipher.nonce)
                    fout.write(len(ciphertext).to_bytes(4, byteorder='big'))
                    fout.write(ciphertext)
                    
                    if status_callback: status_callback(f"Block Encrypted: ChaCha20")
                
                processed_bytes += len(chunk)

        return output_path

    def decrypt_file(self, file_path, status_callback=None):
        # Remove the .chaos extension for the output
        output_path = file_path.replace(".chaos", "")
        if output_path == file_path:
            output_path += ".restored"

        with open(file_path, 'rb') as fin, open(output_path, 'wb') as fout:
            header = fin.read(8)
            if header != b'CHAOS_V1':
                raise ValueError("Invalid File Format: Not a ChaosShield file.")

            while True:
                # 1. Read the Algorithm ID (1 byte)
                algo_id = fin.read(1)
                if not algo_id: 
                    break # End of file
                
                if algo_id == b'\x00': # --- AES ---
                    nonce = fin.read(16)
                    tag = fin.read(16)
                    length_bytes = fin.read(4)
                    chunk_len = int.from_bytes(length_bytes, 'big')
                    ciphertext = fin.read(chunk_len)
                    
                    cipher = AES.new(self.aes_key, AES.MODE_GCM, nonce=nonce)
                    plaintext = cipher.decrypt_and_verify(ciphertext, tag)
                    fout.write(plaintext)
                    if status_callback: status_callback("Block Decrypted: AES-256")

                elif algo_id == b'\x01': # --- ChaCha ---
                    nonce = fin.read(8)
                    length_bytes = fin.read(4)
                    chunk_len = int.from_bytes(length_bytes, 'big')
                    ciphertext = fin.read(chunk_len)
                    
                    cipher = ChaCha20.new(key=self.chacha_key, nonce=nonce)
                    plaintext = cipher.decrypt(ciphertext)
                    fout.write(plaintext)
                    if status_callback: status_callback("Block Decrypted: ChaCha20")
        
        return output_path'''
import hashlib
import os
from Crypto.Cipher import AES, ChaCha20

# --- 1. The Chaos Engine ---
class ChaosEngine:
    def __init__(self, password):
        # Derive initial seed from password
        hash_val = int(hashlib.sha256(password.encode()).hexdigest(), 16)
        self.x = (hash_val % 10**9) / 10**9  
        self.r = 3.99 # Control parameter

    def get_next_decision(self):
        # Iterate the Logistic Map: x = r * x * (1 - x)
        self.x = self.r * self.x * (1 - self.x)
        return self.x

# --- 2. The Hybrid Cipher ---
class HybridCipher:
    def __init__(self, password):
        self.password = password
        self.aes_key = hashlib.sha256(("AES_SALT" + password).encode()).digest()
        self.chacha_key = hashlib.sha256(("CHA_SALT" + password).encode()).digest()
        self.chaos = ChaosEngine(password)
        
        # Block size 1MB
        self.BLOCK_SIZE = 1024 * 1024 

    def encrypt_file(self, file_path, progress_callback=None, log_callback=None):
        output_path = file_path + ".chaos"
        file_size = os.path.getsize(file_path)
        processed_bytes = 0
        block_count = 1
        
        with open(file_path, 'rb') as fin, open(output_path, 'wb') as fout:
            fout.write(b'CHAOS_V2') 
            
            while True:
                chunk = fin.read(self.BLOCK_SIZE)
                if not chunk: break
                
                # Get Chaos Value
                decision = self.chaos.get_next_decision()
                
                # LOGGING THE CHAOS VALUE HERE
                if log_callback:
                    algo_name = "AES-256" if decision > 0.5 else "ChaCha20"
                    log_callback(f"Block {block_count}: x = {decision:.6f} -> {algo_name}")

                if decision > 0.5: # AES
                    cipher = AES.new(self.aes_key, AES.MODE_GCM)
                    ciphertext, tag = cipher.encrypt_and_digest(chunk)
                    fout.write(b'\x00') 
                    fout.write(cipher.nonce)
                    fout.write(tag)
                    fout.write(len(ciphertext).to_bytes(4, 'big')) 
                    fout.write(ciphertext)
                else: # ChaCha
                    cipher = ChaCha20.new(key=self.chacha_key)
                    ciphertext = cipher.encrypt(chunk)
                    fout.write(b'\x01')
                    fout.write(cipher.nonce)
                    fout.write(len(ciphertext).to_bytes(4, 'big'))
                    fout.write(ciphertext)
                
                processed_bytes += len(chunk)
                block_count += 1
                if progress_callback:
                    progress_callback(processed_bytes / file_size)

        return output_path

    def decrypt_file(self, file_path, progress_callback=None, log_callback=None):
        output_path = file_path.replace(".chaos", "")
        if output_path == file_path: output_path += ".restored"
        
        file_size = os.path.getsize(file_path)
        processed_bytes = 0
        block_count = 1

        with open(file_path, 'rb') as fin, open(output_path, 'wb') as fout:
            header = fin.read(8)
            processed_bytes += 8
            if header not in [b'CHAOS_V1', b'CHAOS_V2']:
                raise ValueError("Invalid File Format")

            while True:
                algo_id = fin.read(1)
                if not algo_id: break
                processed_bytes += 1
                
                # During decryption, we just report what was found
                if log_callback:
                    found_algo = "AES-256" if algo_id == b'\x00' else "ChaCha20"
                    log_callback(f"Block {block_count}: Decrypting with {found_algo}")

                if algo_id == b'\x00': # AES
                    nonce = fin.read(16)
                    tag = fin.read(16)
                    length = int.from_bytes(fin.read(4), 'big')
                    ciphertext = fin.read(length)
                    
                    cipher = AES.new(self.aes_key, AES.MODE_GCM, nonce=nonce)
                    plaintext = cipher.decrypt_and_verify(ciphertext, tag)
                    fout.write(plaintext)
                    processed_bytes += (16 + 16 + 4 + length)

                elif algo_id == b'\x01': # ChaCha
                    nonce = fin.read(8)
                    length = int.from_bytes(fin.read(4), 'big')
                    ciphertext = fin.read(length)
                    
                    cipher = ChaCha20.new(key=self.chacha_key, nonce=nonce)
                    plaintext = cipher.decrypt(ciphertext)
                    fout.write(plaintext)
                    processed_bytes += (8 + 4 + length)

                block_count += 1
                if progress_callback:
                    progress_callback(min(processed_bytes / file_size, 1.0))
        
        return output_path
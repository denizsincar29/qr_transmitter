from os import path
import qrcode
from base64 import b64encode as enbase
from io import BytesIO
import numpy as np
import cv2


chunk_size=1740

def metadata(filename):
    """
    Encode the metadata string for the sender.

    Args:
        filename (str): The name of the file to be sent.

    Returns:
        bytes: The encoded metadata bytes or b"bigerror" if file is too big.
    """

    size=path.getsize(filename)
    try:
        return b'meta'+size.to_bytes(4)+chunk_size.to_bytes(2)+(size//chunk_size +1).to_bytes(2)+b'\x00\x00\x00\x00'+path.basename(filename).encode("UTF-8")
    except OverflowError:
        return b'bigerror'

def demetadata(metadata_bytes):
    """
    Decode the metadata bytes for the receiver.

    Args:
        metadata_bytes (bytes): The encoded metadata bytes to be decoded.

    Raises:
        OverflowError: If the file size is too big.

        ValueError: If the metadata bytes are invalid.

        EOFError: If the metadata bytes are too small.

    Returns:
        Tuple[int, int, str]: A tuple containing the file size, number of chunks and filename.
    """
    global chunk_size  # global is bad, but i'm too lazy to make class.
    if metadata_bytes==b'bigerror':
        raise OverflowError("the size is too big")
    if metadata_bytes[:4] != b"meta":
        raise ValueError("Invalid metadata bytes")
    if len(metadata_bytes)<=16:
        raise EOFError(f"Very small metadata. Min length must be 17 (with 1 char filename), but {len(metadata_bytes)} bytes given")
    
    file_size = int.from_bytes(metadata_bytes[4:8], byteorder="big")
    chunk_size=int.from_bytes(metadata_bytes[8:10], byteorder="big")
    nchunks = int.from_bytes(metadata_bytes[10:12], byteorder="big")
    filename = metadata_bytes[16:].decode("utf-8")
    return file_size, nchunks, filename

def enchunk(filename, infinite=True):
    """
    Breaks the file into chunks of specified size and encodes each chunk.

    Args:
        filename (str): The name of the file to be chunked and encoded.
        infinite (bool, optional): Whether or not to loop the chunks. Defaults to True.

    Yields:
        bytes: The encoded chunk of data.
    """

    with open(filename, 'rb') as f:
        index=1
        while True:
            chunk = f.read(chunk_size)
            if not chunk:
                if not infinite: break
                index=1
                f.seek(0)
                chunk = f.read(chunk_size)
            yield index.to_bytes(2, byteorder='big')+chunk
            index+=1

def decode_chunk(chunk):
    """
    Decode a chunk of data.

    Args:
        chunk (bytes): The chunk of data to decode.

    Returns:
        tuple(int, Bytes): A tuple containing the index of the chunk and the decoded chunk.
    """
    return int.from_bytes(chunk[:2], byteorder='big'), chunk[2:]

def dechunk(chunks, metadata):
    """
    Decodes and combines the received chunks of data.

    Args:
        chunks (dict): A dictionary of indices and related chunks received for the receiver.
        metadata (bytes): The metadata of the file to be written.

    Raises:
        ValueError: If a chunk is missing.
        TypeError: If the metadata is not of type bytes.

    Returns:
        None
    """

    if not isinstance(metadata, bytes):
        raise TypeError("metadata must be bytes.")
    size, qty, filename=demetadata(metadata)
    with open(filename, 'wb') as f:
        for i in range(1, qty+1):
            if i not in chunks:
                raise ValueError(f"Chunk {i} is missing")
            f.write(chunks[i])
    if size!=path.getsize(filename):
        raise ValueError(f"Data corrupted! Size of the file doesn't match the size in metadata. Metadata says {size} bytes, but received {path.getsize(filename)} bytes.")


def enqrcode(data: str):
    f=BytesIO()    
    qr=qrcode.QRCode(box_size=10, border=4)
    qr.add_data(enbase(data))
    qr.make(fit=True)
    qr.make_image(fill_color="black", back_color="white").save(f)
    f.seek(0)
    return cv2.imdecode(np.asarray(bytearray(f.read()), dtype="uint8"), cv2.IMREAD_COLOR)


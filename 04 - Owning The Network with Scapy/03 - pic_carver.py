import re
import zlib
import cv2
from scapy.all import *

pictures_directory = "/home/justin/pic_carver/pictures"
faces_directory    = "/home/justin/pic_carver/faces"
pcap_file          = "bhp.pcap"

def get_http_headers(http_payload):
    try:
        header_raw = http_payload[:http_payload.index(b"\r\n\r\n") + 4]
        header_text = header_raw.decode(errors='ignore')
        headers = dict(re.findall(r"(?P<name>.*?): (?P<value>.*?)\r\n", header_text))
    except Exception:
        return None

    if "Content-Type" not in headers:
        return None

    return headers

def extract_image(headers, http_payload):
    image = None
    image_type = None

    try:
        if "image" in headers.get('Content-Type', ''):
            image_type = headers['Content-Type'].split("/")[1].split(";")[0]
            image_data = http_payload[http_payload.index(b"\r\n\r\n") + 4:]

            # Decompress if needed
            try:
                if "Content-Encoding" in headers:
                    if headers['Content-Encoding'] == "gzip":
                        image_data = zlib.decompress(image_data, 16 + zlib.MAX_WBITS)
                    elif headers['Content-Encoding'] == "deflate":
                        image_data = zlib.decompress(image_data)
            except zlib.error:
                pass

            image = image_data
    except Exception:
        return None, None

    return image, image_type

def face_detect(path, file_name):
    img = cv2.imread(path)
    if img is None:
        return False

    cascade = cv2.CascadeClassifier("haarcascade_frontalface_alt.xml")
    rects = cascade.detectMultiScale(img, scaleFactor=1.3, minNeighbors=4, minSize=(20, 20))

    if len(rects) == 0:
        return False

    # Convert rects to corner points and draw rectangles
    for (x, y, w, h) in rects:
        cv2.rectangle(img, (x, y), (x + w, y + h), (127, 255, 0), 2)

    # Save the annotated image
    output_path = f"{faces_directory}/{pcap_file}-{file_name}"
    cv2.imwrite(output_path, img)

    return True


def http_assembler(pcap_file):
    carved_images = 0
    faces_detected = 0

    packets = rdpcap(pcap_file)
    sessions = packets.sessions()

    for session in sessions:
        http_payload = b""
        for packet in sessions[session]:
            try:
                if packet.haslayer(scapy.TCP) and (packet[scapy.TCP].dport == 80 or packet[scapy.TCP].sport == 80):
                    http_payload += bytes(packet[scapy.TCP].payload)
            except:
                continue

        headers = get_http_headers(http_payload)
        if headers is None:
            continue

        image, image_type = extract_image(headers, http_payload)
        if image and image_type:
            filename = f"{pcap_file}-pic_carver_{carved_images}.{image_type}"
            filepath = f"{pictures_directory}/{filename}"

            with open(filepath, "wb") as f:
                f.write(image)

            carved_images += 1

            try:
                if face_detect(filepath, filename):
                    faces_detected += 1
            except:
                pass

    return carved_images, faces_detected

# Run
carved_images, faces_detected = http_assembler(pcap_file)
print(f"Extracted: {carved_images} images")
print(f"Detected: {faces_detected} faces")

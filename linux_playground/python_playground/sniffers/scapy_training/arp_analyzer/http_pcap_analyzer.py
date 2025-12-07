"""
After we're having the pcap file, We'll analyze that .pcap file for details.

The recapper analyzer will obtain the image out of the conversation.
"""


from scapy.all import TCP, rdpcap
import collections
import os
import re
import sys
import zlib
from linux_playground.utils.protocol_utils.http_utils import HTTP_PROTCOL_HEADER_NAMES, HTTP_PROTOCOL_CONTENT_TYPE_TYPES
from linux_playground.utils.path_utils.specific_paths import package_reports_path, relative_path


Response = collections.namedtuple('Response', ['header', 'payload'])


def get_http_header(payload):
    try:
        # gets the first 3 header \r\n\r\n which is the carriage return...
        # from 0:3 which supposed to be exactly the http HEADER last header.
        header_raw = payload[:payload.index(b'\r\n\r\n')+2]
    except ValueError as ve:
        sys.stdout.write('-')
        sys.stdout.flush()
        return None
    
    header = dict(re.findall(r'(?P<name>.*?): (?P<value>.*?)\r\n', header_raw.decode()))
    if HTTP_PROTCOL_HEADER_NAMES.CONTENT_TYPE.value not in header:
        return None
    return header


def extract_content(Response: Response, content_name=HTTP_PROTOCOL_CONTENT_TYPE_TYPES.IMAGE.value):
    content, content_type = None, None
    if content_name in Response.header[HTTP_PROTCOL_HEADER_NAMES.CONTENT_TYPE.value]:
        content_type = Response.header[HTTP_PROTCOL_HEADER_NAMES.CONTENT_TYPE.value].split('/')[1]
    elif Response.header['Content-Encoding'] == 'deflate':
        content = zlib.decompress(Response.payload)
    
    return content, content_type

def extract_image(headers, http_payload):
    image = None
    image_type = None

    try:
        if "image" in headers['Content-Type']:
            # grab the image type and image body
            image_type = headers['Content-Type'].split("/")[1]
            image = http_payload[http_payload.index("\r\n\r\n") + 4:]
            # if we detect compression decompress the image
            try:
                if "Content-Encoding" in list(headers.keys()):
                    if headers['Content-Encoding'] == "gzip":
                        image = zlib.decompress(image, 16 + zlib.MAX_WBITS)
                    elif headers['Content-Encoding'] == "deflate":
                        image = zlib.decompress(image)
            except:
                pass
    except:
        return None, None
    return image, image_type



class Recapper:
    def __init__(self, fname):
        self._fname = fname
        # reading pcap file 
        pcap = rdpcap(fname)
        self.sessions = pcap.sessions()
        self.responses = list()

    def get_responses(self):
        for session in self.sessions:
            payload = b''
            for packet in self.sessions[session]:
                try:
                    if packet[TCP].dport == 80 or packet[TCP].sport == 80:
                        payload += bytes(packet[TCP].payload)
                except IndexError as ie:
                    sys.stdout.write('x')
                    sys.stdout.flush()

            if payload:
                header = get_http_header(payload)
                if header is None:
                    continue
                self.responses.append(Response(header=header, payload=payload))
    


    def write(self, content_name, save_directory_path=package_reports_path):
        for i, response in enumerate(self.responses):
            content, content_type = extract_content(response, content_name)
            if content and content_type: 
                fname = os.path.join(save_directory_path, f'ex_{content_name}_{i}.{content_type}')
                print(f"Writing {fname}")
                with open(fname, 'wb') as f:
                    f.write(content)


if __name__ == '__main__':
    pfile = os.path.join(package_reports_path, relative_path(os.path.join('..', 'scapy_arp_sniffer', 'arper.pcap')))
    recapper = Recapper(fname=pfile)
    recapper.get_responses()
    recapper.write(content_name='image')

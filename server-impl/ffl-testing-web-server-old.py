import struct
import socket
import base64
from flask import Flask, request, send_file, make_response
from PIL import Image
import io
import argparse

try:
    import fpnge
    FPNGE_AVAILABLE = True
except ImportError as e:
    print(e)
    FPNGE_AVAILABLE = False

try:
    import mysql.connector
    MYSQL_AVAILABLE = False
except ImportError as e:
    print(e)
    MYSQL_AVAILABLE = False

app = Flask(__name__)

# Define the RenderRequest struct
class RenderRequest:
    def __init__(self, data, resolution=1024, tex_resolution=1024, view_type=0, expression=0, resource_type=1, mipmap_enable=False, background_color=[1, 1, 1, 0]):
        self.data = bytes(data)
        self.data_length = len(data)
        self.resolution = resolution
        actual_tex_resolution = tex_resolution
        mipmap_tex_resolution = tex_resolution * -1
        self.tex_resolution = mipmap_tex_resolution if mipmap_enable else actual_tex_resolution
        #self.is_head_only = is_head_only
        # NOTE: if you want to still use
        # this script then uhhhhhhhhhh
        # you can redefine these here
        self.verify_charinfo = False
        self.verify_crc16 = True
        self.light_enable = True
        self.expression = expression
        self.resource_type = 1
        self.view_type = view_type  # (1 if is_head_only else 0)
        self.shader_type = (resource_type % 3 if resource_type > 1 else 0)
        # encode bg color to vec4
        #self.background_color = [component / 255.0 for component in background_color]
        self.background_color = background_color
        self.camera_rotate = [0, 0, 0]
        self.model_rotate = [0, 0, 0]
        self.clothes_color = -1
        self.export_as_gltf = False

    def pack(self):
        return struct.pack(
            '96sHB?HhBBBBIhhhhhhBBBBBB???bBB',
            self.data,                 # data: 96s
            self.data_length,          # dataLength: H (uint16_t)
            1 << 0,                    # modelType: B (uint8_t)
            self.export_as_gltf,       # exportAsGLTF: ? (bool)
            self.resolution,           # resolution: H (uint16_t)
            self.tex_resolution,       # texResolution: h (int16_t)
            self.view_type,            # viewType: B (uint8_t)
            self.resource_type,        # resourceType: B (uint8_t)
            self.shader_type,          # shaderType: B (uint8_t)
            self.expression,           # expression: B (uint8_t)
            0,                         # expressionFlag: I (uint32_t)
            self.camera_rotate[0],     # cameraRotate.x: h (int16_t)
            self.camera_rotate[1],     # cameraRotate.y: h (int16_t)
            self.camera_rotate[2],     # cameraRotate.z: h (int16_t)
            self.model_rotate[0],      # modelRotate.x: h (int16_t)
            self.model_rotate[1],      # modelRotate.y: h (int16_t)
            self.model_rotate[2],      # modelRotate.z: h (int16_t)
            self.background_color[0],  # backgroundColor[0]: B (uint8_t)
            self.background_color[1],  # backgroundColor[1]: B (uint8_t)
            self.background_color[2],  # backgroundColor[2]: B (uint8_t)
            self.background_color[3],  # backgroundColor[3]: B (uint8_t)
            0,                         # aaMethod: B (uint8_t)
            0,                         # drawStageMode: B (uint8_t)
            self.verify_charinfo,      # verifyCharInfo: ? (bool)
            self.verify_crc16,         # verifyCRC16: ? (bool)
            self.light_enable,         # lightEnable: ? (bool)
            self.clothes_color,        # clothesColor: b (int8_t)
            0,                         # instanceCount: B (uint8_t)
            0                          # instanceRotationMode: B (uint8_t)
        )


def load_rgba_buffer(buffer_data, width, height):
    return [struct.unpack_from('4B', buffer_data, offset=i * 4) for i in range(width * height)]

def send_render_request(request, host='localhost', port=12346):
    packed_request = request.pack()

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((host, port))
        s.sendall(packed_request)

        # Receive the data for buffer and buffer2
        buffer_size = request.resolution * request.resolution * 4  # RGBA

        received_data = bytearray()
        while len(received_data) < buffer_size:
            packet = s.recv(buffer_size - len(received_data))
            if not packet:
                break
            received_data.extend(packet)

        s.close()

    if len(received_data) < buffer_size:
        return None

    buffer_data = received_data[:buffer_size]

    return buffer_data

def normalize_nnid(nnid):
    return nnid.lower().translate(str.maketrans('', '', '-_.'))

def fetch_data_from_db(nnid):
    if not MYSQL_AVAILABLE:
        return None

    try:
        connection = mysql.connector.connect(
            host='localhost',
            user='miis',
            password='miis',
            database='miis'
        )
        cursor = connection.cursor()
        normalized_nnid = normalize_nnid(nnid)
        cursor.execute("SELECT data FROM nnid_to_mii_data_map WHERE normalized_nnid = %s LIMIT 1;", (normalized_nnid,))
        result = cursor.fetchone()
        cursor.close()
        connection.close()

        if result:
            return result[0]  # return the binary data
    except mysql.connector.Error as err:
        print(f"Error: {err}")
        return None

    return None

def is_base64(s):
    try:
        if isinstance(s, str):
            s = bytes(s, 'utf-8')
        if len(s) % 4 == 0:
            base64.b64decode(s, validate=True)
            return True
    except Exception:
        pass
    return False

def is_hex(s):
    try:
        int(s, 16)
        return True
    except ValueError:
        return False


#valid_sizes = [72, 74, 76, 92,]

@app.route('/miis/image.png', methods=['GET'])
def render_image():
    data = request.args.get('data')
    type_ = request.args.get('type', 'face')
    expression = request.args.get('expression', '0')
    width = request.args.get('width', '1024')
    tex_resolution = request.args.get('texResolution', width)
    nnid = request.args.get('nnid')
    #color_index = request.args.get('clothesColor', 'default')  # Default to purple
    resource_type = request.args.get('resourceType', '1')
    mipmap_enable = request.args.get('mipmapEnable', '0')

    if not data and not nnid:
        return make_response('specify data as FFLStoreData in Base64, or nnid as an nnid', 400)

    if nnid:
        if not MYSQL_AVAILABLE:
            return make_response('oh sh!t sorry for gaslighting you man, the nnid_to_mii_data_map mysql database is not set up sorry', 500)
        store_data = fetch_data_from_db(nnid)
        if not store_data:
            return make_response('did not find that nnid bro', 404)
    else:
        # remove spaces so you can use hex with spaces
        data = data.replace(' ', '')
        # test hex first bc for some reason
        # hex will comfortably decode as base64
        if is_hex(data):
            store_data = bytes.fromhex(data)
        elif is_base64(data):
            store_data = base64.b64decode(data)
        else:
            return make_response('we tried decoding data as base64 and hex and failed at both', 400)

    #if len(store_data) != 96:
    #    return make_response('fflstoredata must be 96 bytes please', 400)

    view_type = ['face',
                'face_only',
                'all_body',
                'fflmakeicon',
                'variableiconbody'].index(type_, 0)

    mipmap_enable = mipmap_enable == '1'

    try:
        expression = int(expression)
    except ValueError:
        return make_response('expression should be a value under the number 18', 400)
    expression = 0 if expression > 18 else expression

    try:
        width = int(width)
    except ValueError:
        return make_response('width = resolution, int, no limit on this lmao,', 400)

    if width > 4095:
        return make_response('ok little n**a i set the limit to 4K', 400)

    """
    if color_index == 'default':
        # TODO GET FAVORITE COLOR FROM FFLiMiiDataCore
        color_index = 20
    else:
        try:
            color_index = int(color_index)
        except ValueError:
            return make_response('clothesColor is not a number', 400)
    """

    try:
        tex_resolution = int(tex_resolution)
    except ValueError:
        return make_response('texResolution is not a number', 400)

    try:
        resource_type = int(resource_type)
    except ValueError:
        return make_response('resource type is not a number', 400)

    render_request = RenderRequest(store_data, width, tex_resolution, view_type, expression, resource_type, mipmap_enable)

    # Send the render request and receive buffer and buffer2 data
    try:
        buffer_data = send_render_request(render_request)
    except ConnectionRefusedError:
        return make_response('upstream tcp server is down :(', 502)

    if buffer_data is None:
        # TODO: rethink this
        return make_response('''incomplete data from backend :( render probably failed bc FFLInitCharModelCPUStep failed... probably because data is invalid
<details>
<summary>
TODO: to make this error better here are the steps where the error is discarded:
</summary>
<pre>
* RootTask::calc_ responds to socket
* Model::initialize makes model nullptr
* Model::setCharModelSource_ calls initializeCpu_
* Model::initializeCpu_ calls FFLInitCharModelCPUStep
  - FFLResult is discarded here
* FFLInitCharModelCPUStep...
* FFLiInitCharModelCPUStep...
* FFLiCharModelCreator::ExecuteCPUStep
* FFLiDatabaseManager::PickupCharInfo
now, PickupCharInfo calls:
* GetCharInfoFromStoreData, fails if StoreData is not big enough or its CRC16 fails - pretty simple.
* FFLiiVerifyCharInfo or FFLiIsNullMiiID are called.
  - i think FFLiIsNullMiiID is for if a mii is marked as deleted by setting its ID to null
  - FFLiiVerifyCharInfo -> FFLiVerifyCharInfoWithReason
    + FFLiVerifyCharInfoReason is discarded here
    + <b>FFLiVerifyCharInfoWithReason IS THE MOST LIKELY REASON</b>
</pre>
</details>
''', 500)

    blended_buffer = load_rgba_buffer(buffer_data, width, width)
    result_image_pil = Image.new('RGBA', (width, width))
    result_image_pil.putdata(blended_buffer)

    img_io = io.BytesIO()
    if FPNGE_AVAILABLE:
        png = fpnge.fromPIL(result_image_pil)
        img_io.write(png)
    else:
        result_image_pil.save(img_io, 'PNG')

    img_io.seek(0)
    return send_file(img_io, mimetype='image/png')

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Render Request Web Server")
    parser.add_argument('--host', type=str, default='0.0.0.0', help="Host for the web server")
    parser.add_argument('--port', type=int, default=5000, help="Port for the web server")
    args = parser.parse_args()

    print('\033[1m---> remember that the renderer API is at \033[4m/miis/image.png\033[0m\033[1m <---\033[0m\n')

    app.run(host=args.host, port=args.port)

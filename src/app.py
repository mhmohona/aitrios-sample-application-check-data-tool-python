"""
Copyright 2023 Sony Semiconductor Solutions Corp. All rights reserved.

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""

import json
from flask import Flask, jsonify, request
from flask_cors import CORS

from data_loader import get_console_data
from data_deserializer import get_deserialize_data

app = Flask(__name__)
CORS(app)  # setting CORS


@app.route("/")
def hello():
    return "Flask server is running"


@app.route("/api/getDevices", methods=["GET"])
def get_devices():
    try:
        devices_data = get_console_data.get_devices()
        return jsonify(devices_data), 200

    except Exception as error:
        error_message = {"result": "ERROR", "message": str(error)}
        return jsonify(error_message), 400


@app.route("/api/getImageDirectories", methods=["GET"])
def get_image_directories():
    try:
        device_id = request.args.get("deviceId")
        if device_id == "":
            error_response = {
                "result": "ERROR",
                "message": "Device ID is not specified.",
            }
            return jsonify(error_response), 400

        directories_data = get_console_data.get_image_directories(device_id)
        return jsonify(directories_data), 200

    except Exception as error:
        error_message = {"result": "ERROR", "message": str(error)}
        return jsonify(error_message), 400


@app.route("/api/getImagesAndInferences", methods=["GET"])
def get_images_and_inferences():
    try:
        device_id = request.args.get("deviceId")
        sub_directory_name = request.args.get("imagePath")
        number_of_images = request.args.get("numberOfImages")
        if device_id == "" or sub_directory_name == "" or number_of_images == "":
            error_response = {
                "result": "ERROR",
                "message": "Required parameter is not specified.",
            }
            return jsonify(error_response), 400

        images_list = get_console_data.get_images(
            device_id, sub_directory_name, int(number_of_images)
        )
        output_list = []
        for image in images_list:
            image_timestamp = image["name"].replace(".jpg", "")
            base64_image = "data:image/jpg;base64," + image["contents"]
            inference_data = get_console_data.get_inference_result(
                device_id, image_timestamp
            )
            try:
                deserialize_data = get_deserialize_data.get_deserialize_data(
                    inference_data[0]["O"]
                )
                output = {
                    "image": base64_image,
                    "inferenceData": json.dumps([deserialize_data]),
                    "timestamp": image_timestamp,
                }
                output_list.append(output)
            except Exception as error:
                error_message = {"result": "ERROR", "message": str(error)}
                return jsonify(error_message), 400

        return jsonify(output_list), 200

    except Exception as error:
        error_message = {"result": "ERROR", "message": str(error)}
        return jsonify(error_message), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0")

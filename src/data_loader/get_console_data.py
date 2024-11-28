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

from datetime import datetime, timezone, timedelta
from data_loader.common.get_client import get_console_client


def get_devices():
    try:
        client_obj = get_console_client()
        response = client_obj.device_management.get_devices()
        id_list = []
        for device_list in response["devices"]:
            id_list.append(device_list["device_id"])
        return id_list
    except Exception as error:
        raise Exception(str(error))


def get_image_directories(device_id):
    try:
        client_obj = get_console_client()
        response = client_obj.insight.get_image_directories(device_id)
        if len(response[0]["devices"][0]["Image"]) == 0:
            raise Exception("Cannot get direcotries.")
        return response[0]["devices"][0]["Image"]
    except Exception as error:
        raise Exception(str(error))


def get_images(device_id, sub_directory_name, number_of_images):
    try:
        client_obj = get_console_client()

        start_datetime = convert_timestamp_to_datetime(sub_directory_name)
        start_time = start_datetime.strftime("%Y%m%d%H%M")

        # Retrieve images for 10 hours from the specified time.
        # If 10 hours later exceeds the current time, use the current time.
        tenhours_later_datetime = start_datetime + timedelta(hours=10)
        current_datetime = datetime.now(timezone.utc)
        end_datetime = (
            tenhours_later_datetime
            if tenhours_later_datetime < current_datetime
            else current_datetime
        )
        end_time = end_datetime.strftime("%Y%m%d%H%M")

        response = client_obj.insight.get_images(
            device_id=device_id,
            sub_directory_name=sub_directory_name,
            number_of_images=number_of_images,
            order_by="DESC",
            skip=0,
            from_datetime=start_time,
            to_datetime=end_time,
        )
        if len(response["images"]) == 0:
            raise Exception("Cannot get images.")
        return response["images"]
    except Exception as error:
        raise Exception(str(error))


def get_inference_result(device_id, image_timestamp):
    try:
        client_obj = get_console_client()
        response = client_obj.insight.get_inference_results(
            device_id=device_id,
            number_of_inference_results=1,
            raw=1,
            time=image_timestamp,
        )
        if len(response[0]["inference_result"]["Inferences"]) == 0:
            print("Cannot get inference results.")
            raise Exception("Cannot get inference results.")
        return response[0]["inference_result"]["Inferences"]
    except Exception as error:
        raise Exception(str(error))


def convert_timestamp_to_datetime(timestamp):
    converted_datetime = datetime(
        year=int(timestamp[:4]),
        month=int(timestamp[4:6]),
        day=int(timestamp[6:8]),
        hour=int(timestamp[8:10]),
        minute=int(timestamp[10:12]),
        second=int(timestamp[12:14]),
        microsecond=int(timestamp[14:] + "000"),
        tzinfo=timezone.utc,
    )

    return converted_datetime

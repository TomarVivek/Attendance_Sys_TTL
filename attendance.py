import cv2
import json
import requests
import tkinter as tk
from datetime import datetime, timezone
from multiprocessing import Process

from pyzbar import pyzbar

vid = cv2.VideoCapture(0)
width = int(vid.get(cv2.CAP_PROP_FRAME_WIDTH))
height = int(vid.get(cv2.CAP_PROP_FRAME_HEIGHT))
global window
file = open("logging.txt", "a")


def insert_data(time_type, barcodeData, time):
    file.write("hitting " + time_type + " for " + barcodeData + " at " + time + "\n")
    if time_type == "in_time":
        resp = requests.get("http://13.232.181.16/items/attendance?filter[roll][_eq]="+ str(barcodeData) +"&filter[day(in_time)][_eq]=" + str(
            datetime.now().day) + "&filter[month(in_time)][_eq]=" + str(datetime.now().month) +
                            "&filter[year(in_time)][_eq]=" + str(datetime.now().year) +
                            "&filter[out_time][_null]=null").text
        res = json.loads(resp)
        print(res, len(res["data"]))
        if len(res["data"]):#there is in time but no time for same entry
            inTime = res["data"][0]["in_time"]
            timeDiff = (datetime.strptime(time, "%Y-%m-%d %H:%M:%S")-datetime.strptime(inTime, "%Y-%m-%dT%H:%M:%S.%fZ"))
            if timeDiff.total_seconds() < 15*60:#the in time is within 15 minutes then skip
                file.write("skipped for " + time_type + " for " + barcodeData + " at " + time + "\n")
                return

        in_data = {'roll': barcodeData, time_type: time}
        data = requests.post('http://13.232.181.16/items/attendance', json=in_data)
    else:
        resp = requests.get("http://13.232.181.16/items/attendance?filter[roll][_eq]=" + str(
            barcodeData) + "&filter[out_time][_null]=null")

        res = json.loads(resp.text)
        if len(res["data"]) > 0:
            id = res["data"][0]["id"]
            res["data"][0]["out_time"] = time
            resp2 = requests.patch('http://13.232.181.16/items/attendance/' + id, json=res["data"][0])
        else:
            file.write("Skipped for " + barcodeData + " " + time_type + "\n")


def mouse_click(event, x, y, flags, param):
    global time_type
    time_type = ""
    if event == cv2.EVENT_LBUTTONDOWN:
        if x < 320:
            time_type = "in_time"
        else:
            time_type = "out_time"
        window.destroy()
        Process(target=insert_data,
                args=(time_type, barcodeData, datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S"))).start()
        file.write(barcodeData + " " + time_type + "" + datetime.now().strftime("%Y-%m-%d %H:%M:%S") + "\n")


def capture():
    while True:
        ret, frame = vid.read()
        barcodes = pyzbar.decode(frame)
        cv2.namedWindow('Output')
        cv2.setMouseCallback('Output', mouse_click)
        global barcode
        for barcode in barcodes:
            (x, y, w, h) = barcode.rect
            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 0, 255), 2)
            global barcodeData
            barcodeData = barcode.data.decode("utf-8")
            barcodeType = barcode.type

            frame = cv2.line(frame, (int(width / 2), 0), (int(width / 2), int(height)), (255, 255, 255), 2)
            frame = cv2.putText(frame, barcodeData, (x + 10, y + 10), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 4)
            frame = cv2.putText(frame, "IN", (int(width / 4), 50), cv2.FONT_HERSHEY_SIMPLEX, 1.3, (0, 255, 255), 5)
            frame = cv2.putText(frame, "OUT", (int(3 * width / 4), 50), cv2.FONT_HERSHEY_SIMPLEX, 1.3, (0, 255, 255), 5)

            cv2.imshow("Output", frame)
            global window
            window = tk.Tk()
            window.withdraw()
            window.geometry("6x6")
            window.mainloop()

        cv2.imshow("Output", frame)

        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

    vid.release()
    cv2.destroyAllWindows()


if __name__ == '__main__':
    capture()
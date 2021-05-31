import cv2
from queue import Queue
from threading import Thread
import time
import face_recognition
import glob
from os.path import join
import numpy as np
import PIL

video=cv2.VideoCapture(0)
baseline_image=None
# A thread that produces data
def motion_detection(out_q):
    while True:
        global baseline_image
        global video
        # Produce some data
        check, frame = video.read()
        status=0
        gray_frame=cv2.cvtColor(frame,cv2.COLOR_BGR2GRAY)
        gray_frame=cv2.GaussianBlur(gray_frame,(25,25),0)
        color_frame = cv2.cvtColor(frame,cv2.COLOR_BGR2RGB)

        if baseline_image is None:
            baseline_image=gray_frame
            continue

        delta=cv2.absdiff(baseline_image,gray_frame)
        min = 60
        threshold=cv2.threshold(delta, min, 255, cv2.THRESH_BINARY)[1]
        (contours,_)=cv2.findContours(threshold,cv2.RETR_EXTERNAL,
                                                    cv2.CHAIN_APPROX_SIMPLE)


        # box_frame = None
        # for contour in contours:
        #     if cv2.contourArea(contour) < 10000:
        #         continue
        #     status=1
        #     (x, y, w, h)=cv2.boundingRect(contour)
        #     box_frame = cv2.rectangle(frame,(x, y), (x+w, y+h), (0,255,0), 1)
        #
        # frame_dict = {'gray_frame' : gray_frame,
        #               'delta_frame' : delta,
        #               'thresh_frame' : threshold,
        #               'color_frame' : color_frame,
        #               'box_frame' : box_frame}
        #
        # out_q.put(frame_dict)
        # print("out_q: " + str(out_q.qsize()))
        box_frame = None
        motion = False
        for contour in contours:
            if cv2.contourArea(contour) > 10000:
                (x, y, w, h)=cv2.boundingRect(contour)
                box_frame = cv2.rectangle(frame,(x, y), (x+w, y+h), (0,255,0), 1)
                #
                frame_dict = {'gray_frame' : gray_frame,
                              'delta_frame' : delta,
                              'thresh_frame' : threshold,
                              'color_frame' : color_frame,
                              'box_frame' : box_frame}
                motion = True
        if(motion):
            out_q.put(frame_dict)
            print("Motion!")
            # print("out_q: " + str(out_q.qsize()))

# A thread that consumes data
def facial_recognition(in_q, known_faces, known_faces_enc):
    while True:
        # Get some data
        # print("in_q: " + str(in_q.qsize()))
        frames = in_q.get()
        # Process the data
        # print("Facial Recognition")
        # color_frame = np.asarray(frames['color_frame'])
        color_frame = frames['color_frame']
        small_frame = cv2.resize(frames['color_frame'], (0, 0), fx=0.25, fy=0.25)
        cv2.imwrite("./motion_captures/motion.jpg", color_frame)

        # print(np_color_frame.shape)
        # image = PIL.Image.fromarray(np_color_frame, "RGB")
        # image.save("./motion_captures/motion.jpg")


        compare_enc = face_recognition.face_encodings(small_frame)
        if(len(compare_enc) != 0):
            print("found matching face")
            for matches in compare_enc:
                results = face_recognition.compare_faces(known_faces_enc, matches)
            if True in matches:
                first_match_index = matches.index(True)
                # name = known_faces[first_match_index]
        # else:
        #     print("no matching face")
        # Indicate completion
        in_q.task_done()

    # Create the shared queue and launch both threads
if __name__ == "__main__":
    known_faces_enc = []

    image_types = ('*.img', '*.jpg', '*.jpeg', '*.png')
    image_paths = []
    known_face_names = []
    for files in image_types:
        image_paths.extend(glob.glob((join("known_faces/", files))))

    for p in image_paths:
        print(p)
        known_face_names.append(p)
        face_img = face_recognition.load_image_file(p)
        # print(face_img.shape)
        # image = PIL.Image.fromarray(face_img, "RGB")
        # image = image.save("test/known.jpg")
        known_faces_enc.append(face_recognition.face_encodings(face_img)[0])    # [0] first face
    q = Queue()
    facial_recog = Thread(target = facial_recognition, args =(q, known_face_names, known_faces_enc, ))
    motion = Thread(target = motion_detection, args =(q, ))
    motion.start()
    facial_recog.start()
    print("Threads Started")
    # Wait for all produced items to be consumed
    q.join()

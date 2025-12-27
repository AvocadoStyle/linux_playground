import cv2

# פותח מצלמה (0 = מצלמת ברירת מחדל)
cap = cv2.VideoCapture(0)

if not cap.isOpened():
    raise RuntimeError("Cannot open camera")

# מאפייני וידאו
width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
fps = 20.0

# codec + writer
fourcc = cv2.VideoWriter_fourcc(*"XVID")
out = cv2.VideoWriter("output.avi", fourcc, fps, (width, height))

print("Recording... press 'q' to stop")

while True:
    ret, frame = cap.read()
    if not ret:
        break

    out.write(frame)              # כתיבה לקובץ
    cv2.imshow("Recording", frame)

    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

cap.release()
out.release()
cv2.destroyAllWindows()

print("Saved to output.avi")

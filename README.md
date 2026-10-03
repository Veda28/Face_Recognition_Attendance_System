# Face Recognition Attendance Management System

A Windows desktop app for registering students with face images and recording attendance either by face recognition or manual entry.

## Dependencies

Install these third-party packages:

- `numpy`
- `opencv-contrib-python` (provides OpenCV and the `cv2.face` LBPH recognizer)
- `Pillow`

The app also uses `tkinter`, `csv`, `os`, `pathlib`, `datetime`, and `time`; these are part of Python and are not installed with pip. The Windows Python installer normally includes Tkinter.

## Setup

Use Python 3.13 and PowerShell from the project folder:

```powershell
py -3.13 -m venv .venv
.\.venv\Scripts\python.exe -m pip install numpy==2.2.6 opencv-contrib-python==4.12.0.88 Pillow==12.3.0
.\.venv\Scripts\python.exe .\AMS_Run.py
```

`opencv-contrib-python` is required for the LBPH face recognizer. Allow camera access in Windows and close other apps using the camera.

## Use

1. **Register a student:** Enter a numeric enrollment ID and name, then click **Take Images**. Capture starts automatically and collects up to 70 samples. Existing IDs can add more samples under the same name. A face matching another registered student is rejected.
2. **Train the model:** Click **Train Images** after adding or retaking face samples. Attendance recognition requires a trained model for the current student roster.
3. **Automatic attendance:** Enter the subject and click **Fill Attendance**. A stable face match is added automatically. The capture window reports success and returns to the subject window. The same student is recorded at most once per subject per day.
4. **Manual attendance:** Choose a subject, enter each student's enrollment and name, then click **Enter Data**. A camera is not needed.
5. **View records:** Click **Check Registered Students**, sign in to open the admin dashboard, then select **All Attendance**, **Manual Attendance**, or **Automatic Attendance**.

The admin credentials are currently hard-coded in `AMS_Run.py`. Change them before sharing the application.

## Data files

- `StudentDetails/StudentDetails.csv`: registered enrollment IDs and names.
- `TrainingImage/`: captured face samples, named with student name, enrollment ID, and sample number.
- `TrainingImageLabel/Trainner.yml`: trained LBPH model.
- `Attendance/Manual_Attendance.csv`: manually entered attendance.
- `Attendance/Automatic_Attendance.csv`: face-recognized attendance.

Attendance is stored in the two CSV files above. The current app does not require MySQL, PyMySQL, or pandas.

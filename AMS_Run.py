import tkinter as tk
from tkinter import *
from tkinter import messagebox
import cv2
import csv
import os
import numpy as np
from PIL import Image, ImageTk
import datetime
import time
from pathlib import Path

PROJECT_DIR = Path(__file__).resolve().parent
ATTENDANCE_DIR = PROJECT_DIR / "Attendance"
MANUAL_ATTENDANCE_CSV = ATTENDANCE_DIR / "Manual_Attendance.csv"
AUTOMATIC_ATTENDANCE_CSV = ATTENDANCE_DIR / "Automatic_Attendance.csv"
STUDENT_DETAILS_CSV = PROJECT_DIR / "StudentDetails" / "StudentDetails.csv"
ATTENDANCE_DIR.mkdir(parents=True, exist_ok=True)


def open_attendance_sheets():
    from tkinter import ttk

    viewer = tk.Toplevel(window)
    viewer.title("Attendance Sheets")
    viewer.geometry("1000x700")
    viewer.configure(background="grey80")

    toolbar = tk.Frame(viewer, bg="grey80")
    toolbar.pack(fill="x", padx=12, pady=(12, 4))
    tk.Label(toolbar, text="Show", bg="grey80", font=("times", 12, "bold")).pack(side="left", padx=(0, 8))
    view_filter = tk.StringVar(value="All")
    filter_picker = ttk.Combobox(toolbar, textvariable=view_filter, values=("All", "Automatic", "Manual"),
                                 state="readonly", width=14)
    filter_picker.pack(side="left")
    tk.Label(viewer, text="Attendance files", bg="grey80", font=("times", 15, "bold")).pack(pady=(6, 4))
    files_table = ttk.Treeview(viewer, columns=("file", "type"), show="headings", height=8,
                               selectmode="browse")
    files_table.heading("file", text="File")
    files_table.heading("type", text="Type")
    files_table.column("file", width=650)
    files_table.column("type", width=150, anchor="center")
    files_table.pack(fill="x", padx=12, pady=4)

    tk.Label(viewer, text="Selected sheet", bg="grey80", font=("times", 15, "bold")).pack(pady=(10, 4))
    preview = ttk.Treeview(viewer, columns=("type", "subject", "enrollment", "name", "date", "time"),
                           show="headings", height=14)
    headings = ("Type", "Subject / File", "Enrollment", "Name", "Date", "Time")
    for column, heading in zip(preview["columns"], headings):
        preview.heading(column, text=heading)
        preview.column(column, width=145, anchor="center")
    preview.pack(fill="both", expand=True, padx=12, pady=4)
    file_paths = {}

    def source_for(path):
        return "Manual" if any(parent.name.casefold().startswith("manuall") for parent in path.parents) \
            or path.name.startswith("Manual_") else "Automatic"

    def records_for(paths):
        records = []
        for path in paths:
            try:
                with path.open(newline="", encoding="utf-8-sig") as csv_file:
                    rows = list(csv.reader(csv_file))
            except (OSError, csv.Error, UnicodeError) as error:
                messagebox.showerror("Could not read attendance sheet", f"{path.name}: {error}", parent=viewer)
                continue
            if not rows:
                continue
            indexes = {header.strip().casefold(): index for index, header in enumerate(rows[0])}
            for row in rows[1:]:
                if not row or not any(value.strip() for value in row):
                    continue

                def field(name):
                    index = indexes.get(name)
                    return row[index].strip() if index is not None and index < len(row) else ""

                records.append((source_for(path), field("subject") or path.stem, field("enrollment"),
                                field("name"), field("date"), field("time")))
        return records

    def display_records(records):
        preview.delete(*preview.get_children())
        for record in records:
            preview.insert("", "end", values=record)

    def refresh_files(event=None):
        files_table.delete(*files_table.get_children())
        preview.delete(*preview.get_children())
        file_paths.clear()
        selected_type = view_filter.get()
        paths = [path for path in sorted(ATTENDANCE_DIR.rglob("*.csv"), key=lambda item: item.name.lower())
                 if selected_type == "All" or source_for(path) == selected_type]
        for index, path in enumerate(paths):
            item_id = f"attendance_{index}"
            file_paths[item_id] = path
            files_table.insert("", "end", iid=item_id,
                               values=(str(path.relative_to(ATTENDANCE_DIR)), source_for(path)))
        display_records(records_for(paths))

    def load_sheet(event=None):
        selected = files_table.selection()
        if selected:
            display_records(records_for([file_paths[selected[0]]]))

    def open_selected_file(event=None):
        selected = files_table.selection()
        if selected:
            os.startfile(str(file_paths[selected[0]]))

    files_table.bind("<<TreeviewSelect>>", load_sheet)
    files_table.bind("<Double-1>", open_selected_file)
    filter_picker.bind("<<ComboboxSelected>>", refresh_files)
    tk.Button(viewer, text="Open Selected CSV", command=open_selected_file, fg="white", bg="black",
              font=("times", 12, "bold")).pack(pady=8)
    refresh_files()
    if not files_table.get_children():
        tk.Label(viewer, text="No attendance CSV files found yet.", bg="grey80").pack(pady=6)


# Window is our Main frame of system
window = tk.Tk()
window.title("FAMS-Face Recognition Based Attendance Management System")

window.geometry('1280x720')
window.configure(background='grey80')

# GUI for manually fill attendance


def manually_fill():
    global sb
    sb = tk.Tk()
    # sb.iconbitmap('AMS.ico')
    sb.title("Enter subject name...")
    sb.geometry('580x320')
    sb.configure(background='grey80')

    def err_screen_for_subject():

        def ec_delete():
            ec.destroy()
        global ec
        ec = tk.Tk()
        ec.geometry('300x100')
        # ec.iconbitmap('AMS.ico')
        ec.title('Warning!!')
        ec.configure(background='snow')
        Label(ec, text='Please enter your subject name!!!', fg='red',
              bg='white', font=('times', 16, ' bold ')).pack()
        Button(ec, text='OK', command=ec_delete, fg="black", bg="lawn green", width=9, height=1, activebackground="Red",
               font=('times', 15, ' bold ')).place(x=90, y=50)

    def fill_attendance():
        global subb
        subb = SUB_ENTRY.get().strip()
        if not subb:
            err_screen_for_subject()
            return
        csv_name = MANUAL_ATTENDANCE_CSV
        try:
            if not csv_name.exists() or csv_name.stat().st_size == 0:
                with open(csv_name, "w", newline="", encoding="utf-8") as csv_file:
                    csv.writer(csv_file).writerow(["Subject", "ID", "ENROLLMENT", "NAME", "DATE", "TIME"])
        except OSError as error:
            messagebox.showerror("Could not create attendance CSV", str(error), parent=sb)
            return
        else:
            sb.destroy()
            MFW = tk.Tk()
            # MFW.iconbitmap('AMS.ico')
            MFW.title("Manually attendance of " + str(subb))
            MFW.geometry('880x470')
            MFW.configure(background='grey80')

            def del_errsc2():
                errsc2.destroy()

            def err_screen1():
                global errsc2
                errsc2 = tk.Tk()
                errsc2.geometry('330x100')
                # errsc2.iconbitmap('AMS.ico')
                errsc2.title('Warning!!')
                errsc2.configure(background='grey80')
                Label(errsc2, text='Please enter Student & Enrollment!!!', fg='black', bg='white',
                      font=('times', 16, ' bold ')).pack()
                Button(errsc2, text='OK', command=del_errsc2, fg="black", bg="lawn green", width=9, height=1,
                       activebackground="Red", font=('times', 15, ' bold ')).place(x=90, y=50)

            def testVal(inStr, acttyp):
                if acttyp == '1':  # insert
                    if not inStr.isdigit():
                        return False
                return True

            ENR = tk.Label(MFW, text="Enter Enrollment", width=15, height=2, fg="black", bg="grey",
                           font=('times', 15))
            ENR.place(x=30, y=100)

            STU_NAME = tk.Label(MFW, text="Enter Student name", width=15, height=2, fg="black", bg="grey",
                                font=('times', 15))
            STU_NAME.place(x=30, y=200)

            global ENR_ENTRY
            ENR_ENTRY = tk.Entry(MFW, width=20, validate='key',
                                 bg="white", fg="black", font=('times', 23))
            ENR_ENTRY['validatecommand'] = (
                ENR_ENTRY.register(testVal), '%P', '%d')
            ENR_ENTRY.place(x=290, y=105)

            def remove_enr():
                ENR_ENTRY.delete(first=0, last=22)

            STUDENT_ENTRY = tk.Entry(
                MFW, width=20, bg="white", fg="black", font=('times', 23))
            STUDENT_ENTRY.place(x=290, y=205)

            def remove_student():
                STUDENT_ENTRY.delete(first=0, last=22)

            # get important variable
            def enter_data_DB():
                enrollment = ENR_ENTRY.get().strip()
                student = STUDENT_ENTRY.get().strip()
                if not enrollment or not enrollment.isdigit() or not student:
                    err_screen1()
                    return

                entry_time = datetime.datetime.now()
                try:
                    with open(csv_name, "r", newline="", encoding="utf-8") as csv_file:
                        record_count = sum(1 for row in csv.reader(csv_file)
                                           if len(row) > 2 and row[1].strip().isdigit())
                    with open(csv_name, "a", newline="", encoding="utf-8") as csv_file:
                        csv.writer(csv_file).writerow([
                            subb,
                            record_count + 1,
                            enrollment,
                            student,
                            entry_time.strftime('%Y-%m-%d'),
                            entry_time.strftime('%H:%M:%S'),
                        ])
                except OSError as error:
                    messagebox.showerror("Could not save attendance", str(error), parent=MFW)
                    return

                ENR_ENTRY.delete(first=0, last=22)
                STUDENT_ENTRY.delete(first=0, last=22)
                Notifi.configure(text="Attendance added to CSV.", bg="Green", fg="white",
                                 width=33, font=('times', 16, 'bold'))
                Notifi.place(x=180, y=380)

            def create_csv():
                import tkinter
                root = tkinter.Tk()
                root.title("Attendance of " + subb)
                root.configure(background='grey80')
                with open(csv_name, newline="", encoding="utf-8") as file:
                    reader = csv.reader(file)
                    r = 0

                    for col in reader:
                        c = 0
                        for row in col:
                            # i've added some styling
                            label = tkinter.Label(root, width=18, height=1, fg="black", font=('times', 13, ' bold '),
                                                  bg="white", text=row, relief=tkinter.RIDGE)
                            label.grid(row=r, column=c)
                            c += 1
                        r += 1
                Notifi.configure(text="CSV saved successfully.", bg="Green", fg="white",
                                 width=33, font=('times', 16, 'bold'))
                Notifi.place(x=180, y=380)
                root.mainloop()

            Notifi = tk.Label(MFW, text="CSV created Successfully", bg="Green", fg="white", width=33,
                              height=2, font=('times', 19, 'bold'))

            c1ear_enroll = tk.Button(MFW, text="Clear", command=remove_enr, fg="white", bg="black", width=10,
                                     height=1,
                                     activebackground="white", font=('times', 15, ' bold '))
            c1ear_enroll.place(x=690, y=100)

            c1ear_student = tk.Button(MFW, text="Clear", command=remove_student, fg="white", bg="black", width=10,
                                      height=1,
                                      activebackground="white", font=('times', 15, ' bold '))
            c1ear_student.place(x=690, y=200)

            DATA_SUB = tk.Button(MFW, text="Enter Data", command=enter_data_DB, fg="black", bg="SkyBlue1", width=20,
                                 height=2,
                                 activebackground="white", font=('times', 15, ' bold '))
            DATA_SUB.place(x=170, y=300)

            MAKE_CSV = tk.Button(MFW, text="Convert to CSV", command=create_csv, fg="black", bg="SkyBlue1", width=20,
                                 height=2,
                                 activebackground="white", font=('times', 15, ' bold '))
            MAKE_CSV.place(x=570, y=300)

            attf = tk.Button(MFW,  text="Check Sheets", command=open_attendance_sheets, fg="white", bg="black",
                             width=12, height=1, activebackground="white", font=('times', 14, ' bold '))
            attf.place(x=730, y=410)

            MFW.mainloop()

    SUB = tk.Label(sb, text="Enter Subject : ", width=15, height=2,
                   fg="black", bg="grey80", font=('times', 15, ' bold '))
    SUB.place(x=30, y=100)

    global SUB_ENTRY

    SUB_ENTRY = tk.Entry(sb, width=20, bg="white",
                         fg="black", font=('times', 23))
    SUB_ENTRY.place(x=250, y=105)

    fill_manual_attendance = tk.Button(sb, text="Fill Attendance", command=fill_attendance, fg="black", bg="SkyBlue1", width=20, height=2,
                                       activebackground="white", font=('times', 15, ' bold '))
    fill_manual_attendance.place(x=250, y=160)
    sb.mainloop()

# For clear textbox


def clear():
    txt.delete(first=0, last=22)


def clear1():
    txt2.delete(first=0, last=22)


def del_sc1():
    sc1.destroy()


def err_screen():
    global sc1
    sc1 = tk.Tk()
    sc1.geometry('300x100')
    # sc1.iconbitmap('AMS.ico')
    sc1.title('Warning!!')
    sc1.configure(background='grey80')
    Label(sc1, text='Enrollment & Name required!!!', fg='black',
          bg='white', font=('times', 16)).pack()
    Button(sc1, text='OK', command=del_sc1, fg="black", bg="lawn green", width=9,
           height=1, activebackground="Red", font=('times', 15, ' bold ')).place(x=90, y=50)

# Error screen2


def del_sc2():
    sc2.destroy()


def err_screen1():
    global sc2
    sc2 = tk.Tk()
    sc2.geometry('300x100')
    # sc2.iconbitmap('AMS.ico')
    sc2.title('Warning!!')
    sc2.configure(background='grey80')
    Label(sc2, text='Please enter your subject name!!!', fg='black',
          bg='white', font=('times', 16)).pack()
    Button(sc2, text='OK', command=del_sc2, fg="black", bg="lawn green", width=9,
           height=1, activebackground="Red", font=('times', 15, ' bold ')).place(x=90, y=50)

# For take images for datasets


def take_img():
    Enrollment = txt.get().strip()
    Name = txt2.get().strip()
    if not Enrollment or not Name:
        err_screen()
        return
    if not Enrollment.isdigit():
        messagebox.showwarning("Invalid enrollment", "Enrollment must contain digits only.", parent=window)
        return

    try:
        registered_students = {}
        if STUDENT_DETAILS_CSV.exists():
            with STUDENT_DETAILS_CSV.open(newline="", encoding="utf-8-sig") as student_file:
                rows = list(csv.reader(student_file))
            headers = [value.strip().casefold() for value in rows[0]] if rows else []
            enrollment_column = headers.index("enrollment") if "enrollment" in headers else 0
            name_column = headers.index("name") if "name" in headers else 1
            if "enrollment" in headers and "name" in headers:
                rows = rows[1:]
            for row in rows:
                if len(row) > max(enrollment_column, name_column) and row[enrollment_column].strip().isdigit():
                    registered_students[int(row[enrollment_column].strip())] = row[name_column].strip()

        registered_name = registered_students.get(int(Enrollment))
        existing_images = list((PROJECT_DIR / "TrainingImage").glob(f"*.{Enrollment}.*"))
        image_names = {path.name.split(".")[0].strip().casefold() for path in existing_images}
        known_name = registered_name or (next(iter(image_names)) if len(image_names) == 1 else None)
        if known_name and known_name.casefold() != Name.casefold():
            messagebox.showwarning("Enrollment already registered",
                                   f"Enrollment {Enrollment} belongs to {known_name}. Use that student's name.",
                                   parent=window)
            return
        if len(image_names) > 1 or (image_names and Name.casefold() not in image_names):
            messagebox.showwarning("Enrollment already has images",
                                   f"Existing face samples for enrollment {Enrollment} use a different name.",
                                   parent=window)
            return

        detector = cv2.CascadeClassifier(str(PROJECT_DIR / "haarcascade_frontalface_default.xml"))
        if detector.empty():
            messagebox.showerror("Face detector unavailable", "Could not load the face cascade.", parent=window)
            return

        registration_recognizer = None
        if registered_students:
            model_path = PROJECT_DIR / "TrainingImageLabel" / "Trainner.yml"
            if not model_path.exists():
                messagebox.showwarning("Train the face model first",
                                       "Click Train Images before adding more students.", parent=window)
                return
            registration_recognizer = cv2.face.LBPHFaceRecognizer_create()
            try:
                registration_recognizer.read(str(model_path))
                model_ids = {int(value) for value in registration_recognizer.getLabels().ravel()}
            except (cv2.error, OSError, ValueError) as error:
                messagebox.showerror("Face model unavailable", str(error), parent=window)
                return
            if model_ids != set(registered_students):
                messagebox.showwarning("Retrain the face model",
                                       "Click Train Images to update the model for the current registered students.",
                                       parent=window)
                return

        existing_sample_numbers = [int(path.stem.rsplit(".", 1)[-1]) for path in existing_images
                                   if path.stem.rsplit(".", 1)[-1].isdigit()]
        sample_number = max(existing_sample_numbers, default=0)
        first_new_sample = sample_number + 1

        camera = cv2.VideoCapture(0, cv2.CAP_DSHOW)
        if not camera.isOpened():
            camera.release()
            messagebox.showerror("Camera unavailable", "Could not open the camera.", parent=window)
            return

        capture_window = tk.Toplevel(window)
        capture_window.title(f"Register Face - {Name} ({Enrollment})")
        capture_window.geometry("850x620")
        capture_window.configure(background="grey80")
        tk.Label(capture_window, text=f"Capturing face samples for {Name} | ID {Enrollment}",
                 bg="grey80", font=("times", 16, "bold")).pack(pady=8)
        camera_view = tk.Label(capture_window, bg="black", width=640, height=400)
        camera_view.pack(padx=12, pady=6)
        capture_status = tk.Label(capture_window, text="Auto-capture starts when one face is in view (up to 70 images).",
                      bg="grey80",
                                  font=("times", 13, "bold"))
        capture_status.pack(pady=4)

        capture_state = {"active": True, "callback": None, "count": 0,
                 "candidate_id": None, "candidate_frames": 0}
        created_images = []

        def stop_capture():
            if capture_state["active"]:
                capture_state["active"] = False
                if capture_state["callback"] is not None:
                    try:
                        capture_window.after_cancel(capture_state["callback"])
                    except tk.TclError:
                        pass
                camera.release()

        def finish_capture():
            stop_capture()
            if not created_images:
                capture_window.destroy()
                messagebox.showwarning("No face captured", "No face images were saved.", parent=window)
                return
            now = datetime.datetime.now()
            write_header = not STUDENT_DETAILS_CSV.exists() or STUDENT_DETAILS_CSV.stat().st_size == 0
            with STUDENT_DETAILS_CSV.open("a", newline="", encoding="utf-8") as student_file:
                writer = csv.writer(student_file)
                if write_header:
                    writer.writerow(["Enrollment", "Name", "Date", "Time"])
                if registered_name is None:
                    writer.writerow([Enrollment, Name, now.strftime("%Y-%m-%d"), now.strftime("%H:%M:%S")])
            capture_window.destroy()
            result = (f"Added face samples {first_new_sample}-{sample_number} for {Name} ({Enrollment})."
                      if first_new_sample > 1 else f"Images saved for {Name} ({Enrollment}).")
            Notification.configure(text=result, bg="SpringGreen3", width=55, font=('times', 16, 'bold'))
            Notification.place(x=250, y=400)
            messagebox.showinfo("Capture successful", result + " Click Train Images before attendance.", parent=window)

        def cancel_capture():
            stop_capture()
            capture_window.destroy()
            for image_path in created_images:
                image_path.unlink(missing_ok=True)

        def update_capture_preview(frame):
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            preview_image = Image.fromarray(rgb_frame)
            preview_image.thumbnail((800, 450))
            photo = ImageTk.PhotoImage(image=preview_image, master=camera_view)
            camera_view.configure(image=photo, width=preview_image.width, height=preview_image.height)
            camera_view.image = photo

        def capture_next_frame():
            nonlocal sample_number
            if not capture_state["active"]:
                return
            ret, frame = camera.read()
            if not ret or frame is None:
                stop_capture()
                capture_window.destroy()
                messagebox.showerror("Camera frame unavailable", "The camera stopped providing images.",
                                     parent=window)
                return
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            faces = detector.detectMultiScale(gray, 1.3, 5)
            duplicate_student = None
            if len(faces) == 1 and registration_recognizer is not None:
                x, y, width, height = faces[0]
                matched_id, confidence = registration_recognizer.predict(gray[y:y + height, x:x + width])
                if matched_id != int(Enrollment) and matched_id in registered_students and confidence < 90:
                    if capture_state["candidate_id"] == matched_id:
                        capture_state["candidate_frames"] += 1
                    else:
                        capture_state["candidate_id"] = matched_id
                        capture_state["candidate_frames"] = 1
                    if capture_state["candidate_frames"] >= 2:
                        duplicate_student = (matched_id, registered_students[matched_id])
                else:
                    capture_state["candidate_id"] = None
                    capture_state["candidate_frames"] = 0
            else:
                capture_state["candidate_id"] = None
                capture_state["candidate_frames"] = 0

            if duplicate_student:
                stop_capture()
                for image_path in created_images:
                    image_path.unlink(missing_ok=True)
                capture_window.destroy()
                duplicate_id, duplicate_name = duplicate_student
                messagebox.showwarning("Face already registered",
                                       f"The camera recognized {duplicate_name} (ID {duplicate_id}), "
                                       f"not {Name} (ID {Enrollment}). Registration was stopped; no images were saved.",
                                       parent=window)
                return

            if len(faces) == 1 and capture_state["candidate_frames"] == 0:
                sample_number += 1
                capture_state["count"] += 1
                image_path = PROJECT_DIR / "TrainingImage" / f"{Name}.{Enrollment}.{sample_number}.jpg"
                if cv2.imwrite(str(image_path), gray):
                    created_images.append(image_path)
                    capture_status.configure(text=f"Saved {capture_state['count']}/70 images. Look toward the camera.")
                else:
                    capture_status.configure(text="Could not save a face image.")
                x, y, width, height = faces[0]
                cv2.rectangle(frame, (x, y), (x + width, y + height), (0, 200, 0), 2)
            elif len(faces) > 1:
                capture_status.configure(text="Only one person should be in the camera view.")
            elif len(faces) == 0:
                capture_status.configure(text="No face detected. Position your face in view.")
            else:
                candidate_name = registered_students.get(capture_state["candidate_id"], "registered student")
                capture_status.configure(text=f"Checking whether this is already registered: {candidate_name}...")

            update_capture_preview(frame)

            if capture_state["count"] >= 70:
                finish_capture()
            else:
                capture_state["callback"] = capture_window.after(30, capture_next_frame)

        controls = tk.Frame(capture_window, bg="grey80")
        controls.pack(pady=8)
        tk.Button(controls, text="Cancel", command=cancel_capture, fg="white", bg="black",
                  font=("times", 13, "bold")).pack(side="left", padx=8)
        capture_window.protocol("WM_DELETE_WINDOW", cancel_capture)
        capture_next_frame()
    except (OSError, cv2.error, ValueError) as error:
        messagebox.showerror("Image capture failed", str(error), parent=window)


def show_attendance_capture(subject, recognizer, face_cascade, student_lookup, parent, parent_status):
    from tkinter import ttk

    camera = cv2.VideoCapture(0, cv2.CAP_DSHOW)
    if not camera.isOpened():
        camera.release()
        messagebox.showerror("Camera unavailable", "Could not open the camera.", parent=parent)
        return

    capture_window = tk.Toplevel(parent)
    capture_window.title("Automatic Attendance - " + subject)
    capture_window.geometry("900x720")
    capture_window.configure(background="grey80")

    tk.Label(capture_window, text=f"Subject: {subject}", bg="grey80",
             font=("times", 18, "bold")).pack(pady=8)
    camera_view = tk.Label(capture_window, bg="black", width=640, height=400)
    camera_view.pack(padx=12, pady=6)
    current_student = tk.Label(capture_window, text="Looking for a registered face...", bg="grey80",
                               font=("times", 15, "bold"))
    current_student.pack(pady=5)

    columns = ("Enrollment", "Name", "Date", "Time")
    roster = ttk.Treeview(capture_window, columns=columns, show="headings", height=8)
    for column in columns:
        roster.heading(column, text=column)
        roster.column(column, width=180, anchor="center")
    roster.pack(fill="x", padx=16, pady=8)

    recognized = {}
    capture_active = True
    callback_id = None
    candidate_id = None
    candidate_frames = 0
    confidence_threshold = 60
    close_scheduled = False

    def stop_camera():
        nonlocal capture_active
        if capture_active:
            capture_active = False
            if callback_id is not None:
                capture_window.after_cancel(callback_id)
            camera.release()

    def close_capture():
        stop_camera()
        if capture_window.winfo_exists():
            capture_window.destroy()
        if parent.winfo_exists():
            parent.deiconify()
            parent.lift()
            parent.focus_force()

    def save_record(record):
        try:
            needs_header = not AUTOMATIC_ATTENDANCE_CSV.exists() or AUTOMATIC_ATTENDANCE_CSV.stat().st_size == 0
            if not needs_header:
                with AUTOMATIC_ATTENDANCE_CSV.open(newline="", encoding="utf-8-sig") as csv_file:
                    rows = list(csv.reader(csv_file))
                if rows:
                    headers = [value.strip().casefold() for value in rows[0]]
                    subject_index = headers.index("subject") if "subject" in headers else None
                    enrollment_index = headers.index("enrollment") if "enrollment" in headers else None
                    date_index = headers.index("date") if "date" in headers else None
                    if None not in (subject_index, enrollment_index, date_index):
                        if any(
                            len(row) > max(subject_index, enrollment_index, date_index)
                            and row[subject_index].strip().casefold() == subject.casefold()
                            and row[enrollment_index].strip() == str(record[1])
                            and row[date_index].strip() == record[3]
                            for row in rows[1:]
                        ):
                            return False
            with AUTOMATIC_ATTENDANCE_CSV.open("a", newline="", encoding="utf-8") as csv_file:
                writer = csv.writer(csv_file)
                if needs_header:
                    writer.writerow(["Subject", "Enrollment", "Name", "Date", "Time"])
                writer.writerow(record)
        except OSError as error:
            messagebox.showerror("Could not save attendance", str(error), parent=capture_window)
            return None
        return True

    def capture_frame():
        nonlocal callback_id, candidate_id, candidate_frames, close_scheduled
        if not capture_active:
            return
        ret, frame = camera.read()
        if not ret or frame is None:
            current_student.configure(text="Camera stopped providing frames.")
            stop_camera()
            return

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = face_cascade.detectMultiScale(gray, 1.2, 5)
        current_message = "No face detected. Look toward the camera."
        if len(faces):
            current_message = "Face detected; checking registration..."
        else:
            candidate_id = None
            candidate_frames = 0
        now = datetime.datetime.now()
        for x, y, width, height in faces:
            student_id, confidence = recognizer.predict(gray[y:y + height, x:x + width])
            student_name = student_lookup.get(int(student_id)) if confidence < confidence_threshold else None
            if student_name is None:
                candidate_id = None
                candidate_frames = 0
                if confidence < confidence_threshold:
                    label = f"Candidate ID {student_id}"
                    current_message = f"Candidate ID {student_id} is not registered; no attendance saved."
                else:
                    label = f"ID {student_id} ({confidence:.1f})"
                    current_message = (f"Candidate ID {student_id}, confidence {confidence:.1f}; "
                                       f"needs < {confidence_threshold}. Not saved.")
                color = (0, 0, 255)
            else:
                label = f"{student_id} - {student_name}"
                color = (0, 200, 0)
                if candidate_id == student_id:
                    candidate_frames += 1
                else:
                    candidate_id = student_id
                    candidate_frames = 1
                if student_id not in recognized and candidate_frames >= 3:
                    record = [subject, student_id, student_name,
                              now.strftime("%Y-%m-%d"), now.strftime("%H:%M:%S")]
                    saved = save_record(record)
                    if saved is not None:
                        recognized[student_id] = record
                        roster.insert("", "end", values=record[1:])
                        if saved:
                            current_message = (f"Attendance filled successfully: ID {student_id} | "
                                               f"{student_name} | {subject}")
                            parent_status.configure(text="Attendance filled successfully.",
                                                    bg="Green", fg="white", width=40,
                                                    font=('times', 15, 'bold'))
                            parent_status.place(x=20, y=250)
                            if not close_scheduled:
                                close_scheduled = True
                                capture_window.after(700, close_capture)
                        else:
                            current_message = (f"Already recorded today: ID {student_id} | "
                                               f"{student_name} | {subject}")
                            parent_status.configure(text="Attendance already added for this subject today.",
                                                    bg="orange", fg="black", width=50,
                                                    font=('times', 13, 'bold'))
                            parent_status.place(x=20, y=250)
                            if not close_scheduled:
                                close_scheduled = True
                                capture_window.after(700, close_capture)
                elif student_id in recognized:
                    current_message = f"Attendance filled successfully: ID {student_id} | {student_name} | {subject}"
                else:
                    current_message = f"Face matched, confirming ID {student_id} | {student_name}..."

            cv2.rectangle(frame, (x, y), (x + width, y + height), color, 2)
            cv2.putText(frame, label, (x, max(25, y - 8)), cv2.FONT_HERSHEY_SIMPLEX,
                        0.7, color, 2)

        current_student.configure(text=current_message)
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        image = Image.fromarray(rgb_frame)
        image.thumbnail((800, 450))
        try:
            photo = ImageTk.PhotoImage(image=image, master=camera_view)
            camera_view.configure(image=photo, width=image.width, height=image.height)
            camera_view.image = photo
        except tk.TclError as error:
            stop_camera()
            messagebox.showerror("Camera preview failed", str(error), parent=capture_window)
            return
        callback_id = capture_window.after(30, capture_frame)

    controls = tk.Frame(capture_window, bg="grey80")
    controls.pack(pady=8)
    tk.Button(controls, text="Finish", command=close_capture, fg="white", bg="black",
              font=("times", 14, "bold")).pack(side="left", padx=8)
    capture_window.protocol("WM_DELETE_WINDOW", close_capture)
    capture_frame()


# for choose subject and fill attendance
def subjectchoose():
    def Fillattendances():
        subject = tx.get().strip()
        now = time.time()  # For calculate seconds of video
        future = now + 20
        if time.time() < future:
            if not subject:
                err_screen1()
            else:
                model_path = PROJECT_DIR / "TrainingImageLabel" / "Trainner.yml"
                newest_image_time = max(
                    (path.stat().st_mtime for path in (PROJECT_DIR / "TrainingImage").glob("*.jpg")),
                    default=0,
                )
                if model_path.exists() and newest_image_time > model_path.stat().st_mtime:
                    messagebox.showwarning("Retrain the face model",
                                           "New face photos were added. Click Train Images before attendance.",
                                           parent=windo)
                    return

                recognizer = cv2.face.LBPHFaceRecognizer_create()  # cv2.createLBPHFaceRecognizer()
                try:
                    recognizer.read(str(model_path))
                except Exception as error:
                    messagebox.showerror("Face model unavailable",
                                         f"Train the face model before taking attendance.\n{error}",
                                         parent=windo)
                    return

                harcascadePath = "haarcascade_frontalface_default.xml"
                faceCascade = cv2.CascadeClassifier(harcascadePath)
                if faceCascade.empty():
                    messagebox.showerror("Face detector unavailable",
                                         f"Could not load {harcascadePath}.", parent=windo)
                    return
                try:
                    with STUDENT_DETAILS_CSV.open(newline="", encoding="utf-8-sig") as student_file:
                        student_rows = [row for row in csv.reader(student_file)
                                        if row and any(value.strip() for value in row)]
                    if not student_rows:
                        messagebox.showerror("Student roster is empty",
                                             "StudentDetails.csv has no registered students. Use Take Images to register a student, then click Train Images before attendance.",
                                             parent=windo)
                        return

                    header = [value.strip().lstrip("\ufeff").casefold() for value in student_rows[0]]
                    has_header = "enrollment" in header and "name" in header
                    if has_header:
                        enrollment_column = header.index("enrollment")
                        name_column = header.index("name")
                        student_rows = student_rows[1:]
                    else:
                        enrollment_column, name_column = 0, 1
                    student_lookup = {
                        int(row[enrollment_column]): row[name_column].strip()
                        for row in student_rows
                        if len(row) > max(enrollment_column, name_column)
                        and row[enrollment_column].strip().isdigit()
                    }
                    if not student_lookup:
                        messagebox.showerror("No valid student records",
                                             "StudentDetails.csv contains no valid enrollment/name rows. Register a student before attendance.",
                                             parent=windo)
                        return
                except (OSError, csv.Error, ValueError, IndexError) as error:
                    messagebox.showerror("Could not read registered students", str(error), parent=windo)
                    return

                show_attendance_capture(subject, recognizer, faceCascade, student_lookup, windo, Notifica)

    # windo is frame for subject chooser
    windo = tk.Tk()
    # windo.iconbitmap('AMS.ico')
    windo.title("Enter subject name...")
    windo.geometry('580x320')
    windo.configure(background='grey80')
    Notifica = tk.Label(windo, text="Attendance filled Successfully", bg="Green", fg="white", width=33,
                        height=2, font=('times', 15, 'bold'))

    attf = tk.Button(windo,  text="Check Sheets", command=open_attendance_sheets, fg="white", bg="black",
                     width=12, height=1, activebackground="white", font=('times', 14, ' bold '))
    attf.place(x=430, y=255)

    sub = tk.Label(windo, text="Enter Subject : ", width=15, height=2,
                   fg="black", bg="grey", font=('times', 15, ' bold '))
    sub.place(x=30, y=100)

    tx = tk.Entry(windo, width=20, bg="white",
                  fg="black", font=('times', 23))
    tx.place(x=250, y=105)

    fill_a = tk.Button(windo, text="Fill Attendance", fg="white", command=Fillattendances, bg="SkyBlue1", width=20, height=2,
                       activebackground="white", font=('times', 15, ' bold '))
    fill_a.place(x=250, y=160)
    windo.mainloop()


def admin_panel():
    win = tk.Tk()
    # win.iconbitmap('AMS.ico')
    win.title("LogIn")
    win.geometry('880x420')
    win.configure(background='grey80')

    def log_in():
        username = un_entr.get()
        password = pw_entr.get()

        if username == 'veda':
            if password == 'veda123':
                win.destroy()
                import tkinter
                from tkinter import ttk

                root = tkinter.Tk()
                root.title("Registered Students and Attendance")
                root.geometry("1100x700")
                root.configure(background='grey80')

                notebook = ttk.Notebook(root)
                notebook.pack(fill="both", expand=True, padx=12, pady=12)

                def make_table_tab(title, columns):
                    tab = ttk.Frame(notebook)
                    notebook.add(tab, text=title)
                    table = ttk.Treeview(tab, columns=columns, show="headings")
                    for column in columns:
                        table.heading(column, text=column)
                        table.column(column, width=160, anchor="center")
                    scrollbar = ttk.Scrollbar(tab, orient="vertical", command=table.yview)
                    table.configure(yscrollcommand=scrollbar.set)
                    table.pack(side="left", fill="both", expand=True)
                    scrollbar.pack(side="right", fill="y")
                    return table

                attendance_columns = ("Subject", "Enrollment", "Name", "Date", "Time")
                all_attendance_table = make_table_tab("All Attendance", ("Type",) + attendance_columns)
                manual_attendance_table = make_table_tab("Manual Attendance", attendance_columns)
                automatic_attendance_table = make_table_tab("Automatic Attendance", attendance_columns)

                attendance_rows = []
                attendance_paths = sorted(ATTENDANCE_DIR.rglob("*.csv"), key=lambda path: path.name.lower())
                for attendance_path in attendance_paths:
                    source_type = ("Manual" if any(parent.name.casefold().startswith("manuall")
                                                    for parent in attendance_path.parents)
                                   or attendance_path.name.startswith("Manual_") else "Automatic")
                    try:
                        with attendance_path.open(newline="", encoding="utf-8-sig") as attendance_file:
                            sheet_rows = list(csv.reader(attendance_file))
                    except (OSError, csv.Error, UnicodeError) as error:
                        messagebox.showerror("Could not read attendance sheet",
                                             f"{attendance_path.name}: {error}", parent=root)
                        continue
                    if not sheet_rows:
                        continue
                    sheet_headers = [value.strip().casefold() for value in sheet_rows[0]]
                    column_indexes = {name: index for index, name in enumerate(sheet_headers)}
                    for row in sheet_rows[1:]:
                        if not row or not any(value.strip() for value in row):
                            continue

                        def value_for(name):
                            index = column_indexes.get(name)
                            return row[index].strip() if index is not None and index < len(row) else ""

                        attendance_rows.append((source_type, value_for("subject") or attendance_path.stem,
                                                value_for("enrollment"), value_for("name"),
                                                value_for("date"), value_for("time")))
                for record in attendance_rows:
                    row_type, *values = record
                    all_attendance_table.insert("", "end", values=(row_type, *values))
                    target_table = manual_attendance_table if row_type == "Manual" else automatic_attendance_table
                    target_table.insert("", "end", values=values)

                root.mainloop()
            else:
                valid = 'Incorrect ID or Password'
                Nt.configure(text=valid, bg="red", fg="white",
                             width=38, font=('times', 19, 'bold'))
                Nt.place(x=120, y=350)

        else:
            valid = 'Incorrect ID or Password'
            Nt.configure(text=valid, bg="red", fg="white",
                         width=38, font=('times', 19, 'bold'))
            Nt.place(x=120, y=350)

    Nt = tk.Label(win, text="Attendance filled Successfully", bg="Green", fg="white", width=40,
                  height=2, font=('times', 19, 'bold'))
    # Nt.place(x=120, y=350)

    un = tk.Label(win, text="Enter username : ", width=15, height=2, fg="black", bg="grey",
                  font=('times', 15, ' bold '))
    un.place(x=30, y=50)

    pw = tk.Label(win, text="Enter password : ", width=15, height=2, fg="black", bg="grey",
                  font=('times', 15, ' bold '))
    pw.place(x=30, y=150)

    def c00():
        un_entr.delete(first=0, last=22)

    un_entr = tk.Entry(win, width=20, bg="white", fg="black",
                       font=('times', 23))
    un_entr.place(x=290, y=55)

    def c11():
        pw_entr.delete(first=0, last=22)

    pw_entr = tk.Entry(win, width=20, show="*", bg="white",
                       fg="black", font=('times', 23))
    pw_entr.place(x=290, y=155)

    c0 = tk.Button(win, text="Clear", command=c00, fg="white", bg="black", width=10, height=1,
                   activebackground="white", font=('times', 15, ' bold '))
    c0.place(x=690, y=55)

    c1 = tk.Button(win, text="Clear", command=c11, fg="white", bg="black", width=10, height=1,
                   activebackground="white", font=('times', 15, ' bold '))
    c1.place(x=690, y=155)

    Login = tk.Button(win, text="LogIn", fg="black", bg="SkyBlue1", width=20,
                      height=2,
                      activebackground="Red", command=log_in, font=('times', 15, ' bold '))
    Login.place(x=290, y=250)
    win.mainloop()


# For train the model
def trainimg():
    global detector
    detector = cv2.CascadeClassifier(str(PROJECT_DIR / "haarcascade_frontalface_default.xml"))
    if detector.empty():
        Notification.configure(text="Could not load the face detector.", bg="red", width=45)
        Notification.place(x=350, y=400)
        return
    try:
        registered_ids = get_registered_enrollment_ids()
        if not registered_ids:
            Notification.configure(text="Register students before training the model.",
                                   bg="SpringGreen3", width=50, font=('times', 18, 'bold'))
            Notification.place(x=350, y=400)
            return
        faces, student_ids = getImagesAndLabels(PROJECT_DIR / "TrainingImage", registered_ids)
    except (OSError, csv.Error, ValueError, IndexError) as error:
        Notification.configure(text=f"Could not load registered face images: {error}",
                               bg="SpringGreen3", width=60, font=('times', 14, 'bold'))
        Notification.place(x=350, y=400)
        return
    if not faces:
        Notification.configure(text="No face images found for registered students.",
                               bg="SpringGreen3", width=55, font=('times', 15, 'bold'))
        Notification.place(x=350, y=400)
        return

    recognizer = cv2.face.LBPHFaceRecognizer_create()
    recognizer.train(faces, np.asarray(student_ids))
    try:
        model_path = PROJECT_DIR / "TrainingImageLabel" / "Trainner.yml"
        model_path.parent.mkdir(parents=True, exist_ok=True)
        recognizer.save(str(model_path))
    except (OSError, cv2.error) as error:
        Notification.configure(text=f"Could not save the face model: {error}", bg="SpringGreen3",
                               width=60, font=('times', 14, 'bold'))
        Notification.place(x=350, y=400)
        return

    Notification.configure(text=f"Model trained for {len(set(student_ids))} registered student(s).",
                           bg="olive drab", width=50, font=('times', 18, 'bold'))
    Notification.place(x=250, y=400)


def get_registered_enrollment_ids():
    if not STUDENT_DETAILS_CSV.exists():
        return set()
    with STUDENT_DETAILS_CSV.open(newline="", encoding="utf-8-sig") as student_file:
        rows = [row for row in csv.reader(student_file) if row and any(value.strip() for value in row)]
    if not rows:
        return set()
    headers = [value.strip().lstrip("\ufeff").casefold() for value in rows[0]]
    if "enrollment" in headers:
        enrollment_column = headers.index("enrollment")
        rows = rows[1:]
    else:
        enrollment_column = 0
    return {
        int(row[enrollment_column].strip())
        for row in rows
        if len(row) > enrollment_column and row[enrollment_column].strip().isdigit()
    }


def getImagesAndLabels(path, allowed_ids=None, face_detector=None):
    face_samples = []
    student_ids = []
    active_detector = face_detector if face_detector is not None else detector
    for image_path in Path(path).glob("*.jpg"):
        filename_parts = image_path.name.split(".")
        if len(filename_parts) < 4 or not filename_parts[1].isdigit():
            continue
        enrollment_id = int(filename_parts[1])
        if allowed_ids is not None and enrollment_id not in allowed_ids:
            continue
        try:
            image = np.array(Image.open(image_path).convert("L"), dtype="uint8")
        except OSError:
            continue
        for x, y, width, height in active_detector.detectMultiScale(image):
            face_samples.append(image[y:y + height, x:x + width])
            student_ids.append(enrollment_id)
    return face_samples, student_ids


window.grid_rowconfigure(0, weight=1)
window.grid_columnconfigure(0, weight=1)
# window.iconbitmap('AMS.ico')


def on_closing():
    from tkinter import messagebox
    if messagebox.askokcancel("Quit", "Do you want to quit?"):
        window.destroy()


window.protocol("WM_DELETE_WINDOW", on_closing)

message = tk.Label(window, text="Face-Recognition-Based-Attendance-Management-System", bg="black", fg="white", width=50,
                   height=3, font=('times', 30, ' bold '))

message.place(x=80, y=20)

Notification = tk.Label(window, text="All things good", bg="Green", fg="white", width=15,
                        height=3, font=('times', 17))

lbl = tk.Label(window, text="Enter Enrollment : ", width=20, height=2,
               fg="black", bg="grey", font=('times', 15, 'bold'))
lbl.place(x=200, y=200)


def testVal(inStr, acttyp):
    if acttyp == '1':  # insert
        if not inStr.isdigit():
            return False
    return True


txt = tk.Entry(window, validate="key", width=20, bg="white",
               fg="black", font=('times', 25))
txt['validatecommand'] = (txt.register(testVal), '%P', '%d')
txt.place(x=550, y=210)

lbl2 = tk.Label(window, text="Enter Name : ", width=20, fg="black",
                bg="grey", height=2, font=('times', 15, ' bold '))
lbl2.place(x=200, y=300)

txt2 = tk.Entry(window, width=20, bg="white",
                fg="black", font=('times', 25))
txt2.place(x=550, y=310)

clearButton = tk.Button(window, text="Clear", command=clear, fg="white", bg="black",
                        width=10, height=1, activebackground="white", font=('times', 15, ' bold '))
clearButton.place(x=950, y=210)

clearButton1 = tk.Button(window, text="Clear", command=clear1, fg="white", bg="black",
                         width=10, height=1, activebackground="white", font=('times', 15, ' bold '))
clearButton1.place(x=950, y=310)

AP = tk.Button(window, text="Check Registered students", command=admin_panel, fg="black",
               bg="SkyBlue1", width=19, height=1, activebackground="white", font=('times', 15, ' bold '))
AP.place(x=990, y=410)

takeImg = tk.Button(window, text="Take Images", command=take_img, fg="black", bg="SkyBlue1",
                    width=20, height=3, activebackground="white", font=('times', 15, ' bold '))
takeImg.place(x=90, y=500)

trainImg = tk.Button(window, text="Train Images", fg="black", command=trainimg, bg="SkyBlue1",
                     width=20, height=3, activebackground="white", font=('times', 15, ' bold '))
trainImg.place(x=390, y=500)

FA = tk.Button(window, text="Automatic Attendance", fg="black", command=subjectchoose,
               bg="SkyBlue1", width=20, height=3, activebackground="white", font=('times', 15, ' bold '))
FA.place(x=690, y=500)

quitWindow = tk.Button(window, text="Manually Fill Attendance", command=manually_fill, fg="black",
                       bg="SkyBlue1", width=20, height=3, activebackground="white", font=('times', 15, ' bold '))
quitWindow.place(x=990, y=500)

window.mainloop()
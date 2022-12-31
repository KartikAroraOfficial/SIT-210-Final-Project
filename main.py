import sys
from PyQt5.uic import loadUi
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QLabel, QDialog, QApplication, QListWidget, QListWidgetItem, QVBoxLayout, QWidget
import data_handler
import time
import mysql.connector
import threading
import smtplib
import matplotlib
import matplotlib.pyplot as plt
matplotlib.use('QT5Agg')
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
import paho.mqtt.client as mqtt
import datetime



# Set the SMTP server and login credentials
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
SMTP_USERNAME = "your_gmail_address@gmail.com"
SMTP_PASSWORD = "your_gmail_password"

# Set the sender and recipient addresses
sender = "sender@gmail.com"

# replace the above line with the hospital's email address, I'm not leaving my email and password here for obvious reasons.


# current patient's data 
aid = ""
patients = []

spo2=0.0
temp=0.0
hr = 0.0



#-------------------------------------------- List patients/ Entry Screen ------------------------------------------
class list_patients(QListWidget):
    def __init__(self):
        super(list_patients, self).__init__()
        loadUi("list_patients.ui", self)
        self.pushButton.clicked.connect(self.gotoadd_patients)
        self.pushButton_2.clicked.connect(self.search)
        self.listWidget.itemDoubleClicked.connect(self.patient_clicked)
        all = data_handler.get_all()

        if(all != 0):
            for patient in all:
                self.listWidget.addItem(patient[0] + " | " + patient[1])

    def gotoadd_patients(self):
        screen2 = add_patient()
        widget.addWidget(screen2)
        widget.setCurrentIndex(widget.currentIndex()+1)

    def search(self):
        self.listWidget.clear()
        global patients
        name = self.lineEdit.text()
        patients = data_handler.search(name)
        if(patients == 0):
            self.label_2.setText("No patient(s) found")
            self.label_2.repaint()
        else:
            self.label_2.setText("Results")
            self.label_2.repaint()
            for patient in patients:
                self.listWidget.addItem(patient[0] + " | " + patient[1])

    def patient_clicked(self, item):
        aid = patients[self.currentRow()][1]
        print(aid)
        time.sleep(1)
        screen3 = patient_details()
        widget.addWidget(screen3)
        widget.setCurrentIndex(widget.currentIndex()+1)


# ---------------------------------------- Add Patient screen class ---------------------------------------------------------


class add_patient(QDialog):
    def __init__(self):
        super(add_patient, self).__init__()
        loadUi("add_patient.ui", self)
        self.pushButton.clicked.connect(self.gotoList)
        # self.label_1.setText("No entries should be empty")
        self.pushButton_2.clicked.connect(self.goback)

    def gotoList(self):
        name = self.I_Name.text()
        a_id = self.I_Aadhar.text()
        dev_no = self.I_Device.text()
        age = self.I_Age.text()
        sex = self.I_Sex.text()
        mail = self.I_Mail.text()
        # self.label_1.setText("No entries should be empty")

        status = data_handler.add_patient(name=name, aid=a_id, mail=mail, did=dev_no, age=age, sex=sex)

        

        if(status == 0):
            time.sleep(1)
            self.label_1.setText("No entries should be empty")
            self.label_1.show()
            self.label_1.repaint()

        elif(status == 2):
            time.sleep(1)
            self.label_1.setText("Patient already exists")
            self.label_1.show()
            self.label_1.repaint()

        elif(status == 3):
            self.label_1.setText("Patient added successfully")
            self.label_1.show()
            self.label_1.repaint()

            time.sleep(3)
            self.goback()

    def goback(self):
        global widget
        mainwindow = list_patients()
        widget.addWidget(mainwindow)
        widget.setCurrentIndex(widget.currentIndex()+1)

# ------------------------------------------------- Patient Details class ----------------------------------------------------

class patient_details(QDialog):
    def __init__(self):
        global aid
        super(patient_details, self).__init__()
        loadUi("patient_details.ui", self)
        patient = data_handler.patient_det(str(aid))
        print(patient)
        print(aid)
        name = patient[0]
        age = patient[4]
        self.label.setText(name)
        self.label_3.setText(age)
        self.label_4.setText( self.diagnose )
        self.pushButton_4.clicked.connect(self.sendEmail)
        self.pushButton.clicked.connect(self.go_back)
        self.pushButton_3.clicked.connect(self.remove_patient)
        self.pushButton_2.clicked.connect(self.view_plot)
        self.label_

    def remove_patient(self):
        data_handler.remove_pat(aid)
        time.sleep(0.5)
        self.go_back()

    def go_back(self):
        mainwindow = list_patients()
        widget.addWidget(mainwindow)
        widget.setCurrentIndex(widget.currentIndex()+1)
    
    def sendEmail(self):
        patient = data_handler.patient_det(str(aid))
        subject ='Health Update from Karti\'s eMPS App'
        body = self.textEdit.text()
        recipient = patient[3]
        msg = f"Subject: {subject}\n\n{body}"
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()
        server.login(SMTP_USERNAME, SMTP_PASSWORD)
        server.sendmail(sender, recipient, msg)
        server.quit()

    def view_plot(self):
        cnx = mysql.connector.connect(user='root', password='rootbar', host='localhost', database='mydatabase')

        # Retrieve the heart rate and datetime data from the database
        cursor = cnx.cursor()
        query = 'SELECT dt, heart FROM dataArd'
        cursor.execute(query)
        results = cursor.fetchall()

        # Extract the datetime and heart rate data from the results
        datetimes = [result[0] for result in results]
        heart_rates = [result[1] for result in results]

        # Create the PyQt window
        window = QtWidgets.QMainWindow()

        # Create the graph widget
        figure = plt.figure()
        canvas = FigureCanvas(figure)

        # Plot the heart rate data
        axes = figure.add_subplot(111)
        axes.plot(datetimes, heart_rates)

        # Set the x-axis to use the datetime data
        axes.xaxis_date()

        # Add the graph widget to the window
        layout = QtWidgets.QVBoxLayout()
        layout.addWidget(canvas)
        central_widget = QtWidgets.QWidget()
        central_widget.setLayout(layout)
        window.setCentralWidget(central_widget)

        # Show the window
        window.show()
        # Close the database connection
        cnx.close()


    def diagnose(self):
        # Define the normal ranges for each vital sign
        spo2_normal_range = (95, 100)
        temp_normal_range = (98.6, 99.1)
        hr_normal_range = (60, 100)
        hr_tachycardia_range = (100, 120)  # Heart rate above 100 bpm is considered tachycardia
        hr_bradycardia_range = (40, 60)  # Heart rate below 60 bpm is considered bradycardia

        # Initialize a variable to store the diagnosis
        diagnosis = ''

        # Check if the values are within the normal range for each vital sign
        if (spo2 >= spo2_normal_range[0]) and (spo2 <= spo2_normal_range[1]) and (temp >= temp_normal_range[0]) and (temp <= temp_normal_range[1]) and (hr >= hr_normal_range[0]) and (hr <= hr_normal_range[1]):
            diagnosis = 'Good health'
        else:
            if (spo2 < spo2_normal_range[0]) and (hr > hr_normal_range[1]):
                diagnosis = 'Shortness of breath or other symptoms of hypoxia'
            elif (spo2 >= spo2_normal_range[0]) and (hr < hr_normal_range[0]):
                diagnosis = 'Low blood pressure or other symptoms of hypotension'
            elif (spo2 < spo2_normal_range[0]) and (hr < hr_normal_range[0]):
                diagnosis = 'Hypoxia and hypotension'
            elif (spo2 < spo2_normal_range[0]):
                diagnosis = 'Possible respiratory or circulatory issues'
            elif (hr >= hr_tachycardia_range[0]) and (hr <= hr_tachycardia_range[1]):
                diagnosis = 'Tachycardia, possible cardiac issues or other underlying condition'
            elif (hr >= hr_bradycardia_range[0]) and (hr <= hr_bradycardia_range[1]):
                diagnosis = 'Bradycardia, possible cardiac issues or other underlying condition'
            elif (temp < temp_normal_range[0]):
                diagnosis = 'Low body temperature, possible hypothermia'
            elif (temp > temp_normal_range[1]):
                diagnosis = 'High body temperature, possible fever or infection'
            else:
                diagnosis = 'Unable to diagnose based on available data'

        return diagnosis

    
    def mean_dev(self):
        con = mysql.connector.connect(
            host='localhost',
            user='root',
            password='rootbar',
            database='mydatabase'
        )

        mycur = con.cursor()
        mycur.execute("SELECT AVG(heart) FROM dataArd")
        hr_avg = mycur.fetchone()[0]
        return abs(hr - hr_avg)



# ------------------------------------------------------- MQTT receiver and Database updater -------------------------
running = True
message = ''
prev_message =''

# Set the MQTT broker address and topic
MQTT_BROKER = "broker.mqttdashboard.com"
MQTT_TOPIC = "ePMS"

# Connect to the MySQL database
db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="rootbar",
    database="mydatabase"
)


def on_connect(client, userdata, flags, rc):
    print("Connected with result code "+str(rc))
    client.subscribe(MQTT_TOPIC)


def mqtt_receiver():
    client.connect(MQTT_BROKER, 1883, 60)
    if running:
        client.loop_forever()

def on_message(client, userdata, msg):
    # Store the received message in a global variable
    global message
    message = msg.payload

def database_updater():
    while running:
        if message != prev_message:
            global temp, hr, spo2, aid
            prev_message = message
            mycursor = db.cursor()
            did = data_handler.patient_det(aid)[3]
            d_id = int(message.split()[1])
            l_temp = float(message.split()[2])
            l_hr = float(message.split()[3])
            l_spo2 = float(message.split()[4])      

            if (did == d_id):
                temp = l_temp
                hr = l_hr
                spo2 = l_spo2
        
            now = datetime.datetime.utcnow()
            query = "INSERT INTO dataArd(dt, heart, temp, spo) VALUES (%s, %s, %s)"
            mycursor.execute(query, (now.strftime('%Y-%m-%d %H:%M:%S'), l_hr, l_temp, l_spo2))

            mycursor.close()
            time.sleep(3)
        

client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message
client.connect(MQTT_BROKER, 1883, 60)

mqtt_thread = threading.Thread(target=mqtt_receiver, daemon=True)
data_updater_thread = threading.Thread(target=database_updater, daemon=True)


# ----------------------------------------------- Main Body --------------------------------------------------

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle('ukui')
    widget = QtWidgets.QStackedWidget()
    mainwindow = list_patients()
    widget.addWidget(mainwindow)

    mqtt_thread.start()
    data_updater_thread.start()
    widget.show()


    try:
        running = False
        mqtt_thread.join()
        data_updater_thread.join()
        db.close()
        sys.exit(app.exec_())
    except:
        print("Exiting")

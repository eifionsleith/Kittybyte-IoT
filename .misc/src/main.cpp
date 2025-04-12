#include <ESP8266WiFi.h>
#include <ESP8266WebServer.h>
#include <WiFiUdp.h>
#include <NTPClient.h>
#include <Servo.h>

// Replace with network credentials
const char* ssid     = "YOUR_SSID";
const char* password = "YOUR_PASSWORD";

// NTP Client Settings
WiFiUDP ntpUDP;
NTPClient timeClient(ntpUDP, "pool.ntp.org", 0, 60000); // UTC, update every minute

// Web server runs on port 80
ESP8266WebServer server(80);

// Servo setup
Servo feederServo;
const int servoPin = D5; // Change to  wiring pin

// How long (in ms) to activate the servo per gram of food dispensed.
// Adjust this constant according to  hardware calibration.
const unsigned int msPerGram = 50; 

// Maximum number of feeding schedules allowed
const int MAX_SCHEDULES = 5;

// Structure for a feeding schedule
struct FeedingSchedule {
  int hour;
  int minute;
  int grams;
  bool fedToday;  // flag to indicate if feeding has already happened for this schedule today
};

FeedingSchedule schedules[MAX_SCHEDULES];
int scheduleCount = 0;

// HTML for the main page form
const char* htmlPage = R"rawliteral(
<!DOCTYPE html>
<html>
  <head>
    <title>IoT AI Cat Feeder</title>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <style>
      body { font-family: Arial; margin: 20px; }
      input[type=number], input[type=time] { width: 100%%; padding: 8px; margin: 4px 0 10px 0; }
      input[type=submit] { padding: 10px 20px; }
      .schedule { background: #f4f4f4; padding: 10px; margin: 10px 0; }
    </style>
  </head>
  <body>
    <h2>IoT AI Cat Feeder: Add Feeding Schedule</h2>
    <form action="/add" method="POST">
      <label for="time">Feeding Time (HH:MM):</label>
      <input type="time" id="time" name="time" required><br>
      <label for="grams">Feeding Amount (grams):</label>
      <input type="number" id="grams" name="grams" min="1" required><br>
      <input type="submit" value="Add Schedule">
    </form>
    <h3>Current Schedules</h3>
    <div>
      %%SCHEDULE_LIST%%
    </div>
  </body>
</html>
)rawliteral";

// Utility function to generate the list of schedules in HTML
String generateScheduleList() {
  String list = "";
  if(scheduleCount == 0) {
    list = "<p>No schedules added yet.</p>";
  } else {
    for (int i = 0; i < scheduleCount; i++) {
      char buf[100];
      sprintf(buf, "<div class=\"schedule\"><strong>Time:</strong> %02d:%02d, <strong>Amount:</strong> %d grams</div>",
              schedules[i].hour, schedules[i].minute, schedules[i].grams);
      list += buf;
    }
  }
  return list;
}

// Handler for the root path
void handleRoot() {
  String page = htmlPage;
  page.replace("%%SCHEDULE_LIST%%", generateScheduleList());
  server.send(200, "text/html", page);
}

// Handler to add a new schedule with enhanced error feedback
void handleAddSchedule() {
  if (server.method() == HTTP_POST) {
    if (scheduleCount >= MAX_SCHEDULES) {
      server.send(200, "text/html", "<p>Maximum number of schedules reached.</p><a href=\"/\">Go Back</a>");
      return;
    }
    
    // Retrieve the time and grams parameters from the POST request
    String timeStr = server.arg("time"); // format HH:MM
    String gramsStr = server.arg("grams");

    // Basic validation of time format and grams input
    if (timeStr.length() < 5) {
      server.send(200, "text/html", "<p>Invalid time format. Please use HH:MM.</p><a href=\"/\">Go Back</a>");
      return;
    }
    if (gramsStr.length() == 0 || gramsStr.toInt() <= 0) {
      server.send(200, "text/html", "<p>Invalid grams value. Please enter a number greater than 0.</p><a href=\"/\">Go Back</a>");
      return;
    }
    
    int hour = timeStr.substring(0, 2).toInt();
    int minute = timeStr.substring(3, 5).toInt();
    int grams = gramsStr.toInt();
    
    // Add new schedule to our array
    schedules[scheduleCount].hour = hour;
    schedules[scheduleCount].minute = minute;
    schedules[scheduleCount].grams = grams;
    schedules[scheduleCount].fedToday = false;
    scheduleCount++;

    server.sendHeader("Location", "/");
    server.send(303);
  } else {
    server.send(405, "text/plain", "Method Not Allowed");
  }
}

// Non-blocking feeding state variables
bool feedingInProgress = false;
bool waitingAfterFeeding = false;
unsigned long feedStartTime = 0;
unsigned long feedDuration = 0;
unsigned long waitStartTime = 0;
const unsigned long waitDuration = 500; // 500ms pause after servo returns

// Function to initiate non-blocking feeding using the servo
void feedCat(int grams) {
  if (!feedingInProgress) {
    Serial.printf("Feeding cat: dispensing %d grams of food.\n", grams);
    feederServo.write(90);  // Start dispensing (rotate servo)
    feedDuration = grams * msPerGram;
    feedStartTime = millis();
    feedingInProgress = true;
    waitingAfterFeeding = false;
  }
}

// Non-blocking feeding state machine to be updated in loop()
void updateFeeding() {
  if (feedingInProgress) {
    unsigned long currentMillis = millis();
    // Check if dispensing time is over
    if (!waitingAfterFeeding && (currentMillis - feedStartTime >= feedDuration)) {
      feederServo.write(0);  // Return servo to initial position
      waitingAfterFeeding = true;
      waitStartTime = currentMillis;
    }
    // Check if waiting period is over
    if (waitingAfterFeeding && (currentMillis - waitStartTime >= waitDuration)) {
      feedingInProgress = false;
      waitingAfterFeeding = false;
    }
  }
}

// Function to check schedules and feed if needed using provided current time
void checkFeedingSchedules(int currentHour, int currentMinute) {
  for (int i = 0; i < scheduleCount; i++) {
    if (!schedules[i].fedToday && currentHour == schedules[i].hour && currentMinute == schedules[i].minute) {
      Serial.printf("Schedule matched at %02d:%02d for %d grams.\n", schedules[i].hour, schedules[i].minute, schedules[i].grams);
      feedCat(schedules[i].grams);
      schedules[i].fedToday = true;
    }
  }
}

// Reset fedToday flags after midnight (or at a fixed time after last feed)
void resetDailyFlags(int currentHour, int currentMinute) {
  // For example, reset at 00:01 (1 minute after midnight)
  if (currentHour == 0 && currentMinute == 1) {
    for (int i = 0; i < scheduleCount; i++) {
      schedules[i].fedToday = false;
    }
    Serial.println("Daily feeding flags reset.");
  }
}

void setup() {
  Serial.begin(115200);
  delay(100);

  // Connect to WiFi network
  Serial.printf("Connecting to %s", ssid);
  WiFi.begin(ssid, password);
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  Serial.println("\nWiFi connected");
  Serial.print("IP address: ");
  Serial.println(WiFi.localIP());

  // Initialize NTP client
  timeClient.begin();
  timeClient.update();
  
  // Attach servo and set initial position
  feederServo.attach(servoPin);
  feederServo.write(0);

  // Configure web server routes
  server.on("/", handleRoot);
  server.on("/add", handleAddSchedule);
  server.begin();
  Serial.println("Web server started");
}

void loop() {
  server.handleClient();

  // Update NTP time once per loop iteration
  timeClient.update();
  unsigned long epochTime = timeClient.getEpochTime();
  int currentHour = (epochTime % 86400L) / 3600;
  int currentMinute = (epochTime % 3600) / 60;

  // Check and execute feeding schedules with the current time
  checkFeedingSchedules(currentHour, currentMinute);
  resetDailyFlags(currentHour, currentMinute);

  // Update non-blocking feeding state machine
  updateFeeding();

  // Small delay to prevent busy looping
  delay(100);
}

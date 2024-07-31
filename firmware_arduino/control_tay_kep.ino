#include<ModbusRtu.h>                               //Library for using Modbus in Arduino
Modbus bus;                                    //Define Object bus for class modbus 
uint16_t modbus_array[] = {0,0,0,0,0,0,0,0,0,0};    //Array initilized with three 0 values
int status_kep = 0; //0 - status_kep
float value_D; //1 - D_value_hiện tại
float value_I; //2 - I value hiện tại
// 3 - Kich thuoc vat kẹp
float value_I_max = 5; // 5 - I max
// 6 - I/O status
float value_V = 0; // 7- trạng thái

//Khai báo chân GPIO
#define PIN_IN1 5
#define PIN_IN2 6
#define PIN_PWM 7
#define PIN_ENCODER 12
#define PIN_ACS712 11

int pwm_d = 200; // vận tốc default cho động cơ pwm
unsigned long previousMillis = 0;
const long interval = 1;
//cac bien thoi gian
long prevT =0;
double Time;
double times=0;
float pos=0;
float pos_p=0;

void setup() {
  Serial.begin(9600);   //setup Serial
  // while (!Serial);
  Serial.print("Start Slave modbus");
  delay(5000);  
  bus = Modbus(1,1,2); //modbus slave có ID=1, cổng serial_1, chân điều khiển RE,DE = pin2
  bus.begin(9600);Serial.print("Check dong dien:");
    
  //setup PIN cho encoder
  pinMode(PIN_IN1,OUTPUT);
  pinMode(PIN_IN2,OUTPUT);
  pinMode(PIN_PWM,OUTPUT);

  //setup pin cho cảm biến dòng điện ASC712
  pinMode(PIN_ACS712,INPUT);
  pinMode(PIN_ENCODER,INPUT);
  delay(1000);
  read_mA();

  Serial.println(value_I);
  value_I_max = value_I;

  delay(1000);
}

void loop() {
  xuLy_modbus();
  dieu_khien_tay_kep();
  Task_sensor();
}

void xuLy_modbus() {
  bus.poll(modbus_array,sizeof(modbus_array)/sizeof(modbus_array[0]));  
  status_kep = modbus_array[0];
  Serial.println(modbus_array[0]);
  delay(50);
}

void dieu_khien_tay_kep() {
  if(status_kep == 0) { // dừng kẹp
    set_motor_pwm(0);
  }
  if(status_kep == 2) { // mở kẹp
    if((value_I - value_I_max) > 0.5) {
      set_motor_pwm(0);
    }else {
      set_motor_pwm(-pwm_d);
    }
  }
  if(status_kep == 1) { // kẹp vào
    if((value_I - value_I_max) > 0.5) {
      set_motor_pwm(50);
    }else {
      set_motor_pwm(pwm_d);
    }
  }
}

// điều khiển tốc độ motor
void set_motor_pwm(int pwm) {
  if (pwm < 0) {  
    analogWrite(PIN_IN1, -pwm);
    digitalWrite(PIN_IN2, LOW);
  }
  if(pwm == 0) {
    // stop 
    digitalWrite(PIN_IN1, LOW);
    analogWrite(PIN_IN2, LOW);
  }
    if(pwm > 0) {
    // forward 
    digitalWrite(PIN_IN1, LOW);
    analogWrite(PIN_IN2, pwm);
  }
}

void Task_sensor() {
    read_mA();
    modbus_array[2] = value_I;
    modbus_array[1] = value_V;

    unsigned long currentMillis = millis();
    if (currentMillis - previousMillis >= interval) {
      // save the last time you blinked the LED
      previousMillis = currentMillis;
      pos = analogRead(PIN_ENCODER)/2;
      if(pos>90){pos=0;}
      Time=millis()-prevT;//ms
      prevT=millis();
      value_V=500*(pos-pos_p)/(3*Time)*100;//rpm
      pos_p=pos;
    }
}

void read_mA(){
  float average = 0;
  for(int i = 0; i < 50; i++) {
    average = average + (.0264 * analogRead(PIN_ACS712) -13.51);//for the 5A mode,  
    delay(1);
 }
 value_I = (average/50)*100;
}

#include "I2Cdev.h"
#include "MPU6050.h"
#include "math.h"

#if I2CDEV_IMPLEMENTATION == I2CDEV_ARDUINO_WIRE
    #include "Wire.h"
#endif

MPU6050 accelgyro;
int16_t ax, ay, az;
int16_t gx, gy, gz;
float g = 9.8;
float acc_range = 2*g;
float gyr_range = 250.0;
long N = 65536;
float acc_lc = acc_range/N;	//Acceleration least count
float gyr_lc = gyr_range/N;	//Gyro least count

void setup() {
    // join I2C bus (I2Cdev library doesn't do this automatically)
    #if I2CDEV_IMPLEMENTATION == I2CDEV_ARDUINO_WIRE
        Wire.begin();
    #elif I2CDEV_IMPLEMENTATION == I2CDEV_BUILTIN_FASTWIRE
        Fastwire::setup(400, true);
    #endif
    Serial.begin(115200);
    accelgyro.initialize();
    //digital low-pass filter configuration (DLPF) mode
    // accelgyro.setDLPFMode(3);
}

void loop(){
	delay(20);
	accelgyro.getMotion6(&ax, &ay, &az, &gx, &gy, &gz);
  //print in order as "ax ay az gx gy gz"
	Serial.print(
    String(ax*acc_lc,5)+" "+
    String(ay*acc_lc,5)+" "+
    String(az*acc_lc,5)+" "+
    String(gx*acc_lc,5)+" "+
    String(gy*acc_lc,5)+" "+
    String(gz*acc_lc,5)+"\n");
}

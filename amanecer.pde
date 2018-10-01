import core.viveP5.*;
import processing.net.*;
Client myClient;
Vive vive;
PShader amanecer;
float dataIn;
void setup() { 
  size(1028, 1028, P3D);
  vive = new Vive(this);
  noStroke();
  myClient = new Client(this, "127.0.0.1", 5204);
  amanecer = loadShader("amanecer.glsl");
  amanecer.set("resolution", float(width), float(height));
} 
void draw() { 
  vive.setBackground(0,0,0);
  if(myClient.available()>0){
    VRdraw();  
  }
}

void VRdraw(){     
    dataIn=myClient.read();
    amanecer.set("time",millis()/1000.0);
    amanecer.set("mouse",dataIn,float(mouseX/100));
    shader(amanecer);
    rect(0,0,width,height);
}
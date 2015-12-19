#define SAMPLES_COUNT 20
#define SAMPLE_SIZE 3

#define LED_PIN 13 

unsigned char buffer1[SAMPLES_COUNT * SAMPLE_SIZE]; 
unsigned char buffer2[SAMPLES_COUNT * SAMPLE_SIZE];
unsigned char readyToSend = 0;
unsigned char *currentBuffer;
unsigned char *serialBuffer;
unsigned char *swapBuffer;

unsigned int currentSample = 0;
unsigned short c0 , c1;
unsigned int packet;
unsigned char channelsCount = 0;

unsigned int count1 = 0; //Prueba
unsigned int count2 = 0; //Prueba

char incomingByte;

TcChannel *timer = &(TC0->TC_CHANNEL)[0];

void setup() 
{
    // LED On
    pinMode(LED_PIN, OUTPUT);
    digitalWrite(LED_PIN, 0);

    // Memory iniatialization
    currentBuffer = buffer1; 
    serialBuffer = buffer2;

    // Communications Setup
    analogReadResolution(12);
    Serial.begin(115200);

    // ADC Setup
    NVIC_EnableIRQ(ADC_IRQn);
    ADC->ADC_IDR = 0xFFFFFFFF;
    ADC->ADC_IER = 0xC0;
    ADC->ADC_CHDR = 0xFFFF;
    ADC->ADC_CHER = 0xC0;
    ADC->ADC_CGR = 0x15555555;
    ADC->ADC_COR = 0x00000000;
    ADC->ADC_MR = (ADC->ADC_MR & 0xFFFFFFF0) | (1 << 1) | ADC_MR_TRGEN;

    // Timer Setup
    pmc_enable_periph_clk(TC_INTERFACE_ID);
    timer->TC_CCR = TC_CCR_CLKDIS;
    timer->TC_IDR = 0xFFFFFFFF;
    timer->TC_SR;
    timer->TC_CMR = TC_CMR_TCCLKS_TIMER_CLOCK1 | TC_CMR_WAVE | TC_CMR_WAVSEL_UP_RC | TC_CMR_EEVT_XC0 | TC_CMR_ACPA_CLEAR | TC_CMR_ACPC_CLEAR | TC_CMR_BCPB_CLEAR | TC_CMR_BCPC_CLEAR;
    timer->TC_RC = 42000;    // 42000 -- 4200/42MHz= 0.001 clock // 0.001s= 1ms== 1khz
    timer->TC_RA = 21000;
    timer->TC_CMR = (timer->TC_CMR & 0xFFF0FFFF) | TC_CMR_ACPA_CLEAR | TC_CMR_ACPC_SET;
}

void ADC_Handler (void)
{
    // Channel 0 Reading
    if (ADC->ADC_ISR & ADC_ISR_EOC6)
    {  
        c1 = *(ADC->ADC_CDR+6);
        //c1 = count2;                   // Prueba
        count2 ++;                     // Prueba
        channelsCount ++;          
    }

    // Channel 1 Reading
    if (ADC->ADC_ISR & ADC_ISR_EOC7)
    {
        c0 = *(ADC->ADC_CDR + 7);
       // c0 = count1;                  // Prueba
        count1 ++;                    // Prueba
        channelsCount ++;
    }
    
    if (channelsCount == 2) 
    {
        packet = (c0 & 0x000FFF | (c1 << 12) & 0xFFF000);
        currentBuffer[currentSample] = (unsigned char) ((packet & 0x00FF0000) >> 16);
        currentBuffer[currentSample + 1] = (unsigned char) ((packet & 0x0000FF00) >> 8);
        currentBuffer[currentSample + 2] = (unsigned char) (packet & 0x000000FF);
        currentSample = currentSample + 3;
        channelsCount = 0;
        if (currentSample >= SAMPLES_COUNT * SAMPLE_SIZE)
        {
            readyToSend = 1;
            currentSample = 0;
            swapBuffer = currentBuffer;
            currentBuffer = serialBuffer;
            serialBuffer = swapBuffer;
        }
  }
}

void loop() {
    if (Serial.available() > 0)
    {    
        incomingByte = Serial.read();
        if (incomingByte == 'S')
        {        
            currentSample = 0;
            readyToSend = 0; 
            timer->TC_CCR = TC_CCR_CLKEN | TC_CCR_SWTRG;
        }
        if (incomingByte == 'F')
        {
            timer->TC_CCR = TC_CCR_CLKDIS;
        }
    }
    if (readyToSend == 1)
    { 
        readyToSend = 0;
        Serial.write(serialBuffer, SAMPLES_COUNT * SAMPLE_SIZE);
    }
}

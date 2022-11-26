
#include <DHT.h>
#include <WiFi.h>
#include <PubSubClient.h>
 
#define PIN_LED     25

#define DHTPIN 26   

#define DHTTYPE DHT22   

#define TOPICO_SUBSCRIBE_LED         "topico_liga_desliga_led"
#define TOPICO_PUBLISH_TEMPERATURA   "topico_sensor_temperatura" 
#define TOPICO_PUBLISH_DISTANCIA     "topico_sensor_distancia" 
#define TOPICO_PUBLISH_UMIDADE       "topico_sensor_umidade" 
 
#define ID_MQTT  "esp32_mqtt"     
 
DHT dht(DHTPIN, DHTTYPE);
 
const char* SSID = " "; 
const char* PASSWORD = " "; 
 
const char* BROKER_MQTT = "iot.eclipse.org"; 
int BROKER_PORT = 1883; 
   
WiFiClient espClient; 
PubSubClient MQTT(espClient); 
 
float faz_leitura_temperatura(void);
float faz_leitura_umidade(void);
void initWiFi(void);
void initMQTT(void);
void mqtt_callback(char* topic, byte* payload, unsigned int length);
void reconnectMQTT(void);
void reconnectWiFi(void);
void VerificaConexoesWiFIEMQTT(void);
 

float faz_leitura_temperatura(void)
{
    float t = dht.readTemperature();
    float result;
     
    if (! (isnan(t)) )
        result = t;
    else
        result = -99.99;
 
    return result;
}
 
float faz_leitura_umidade(void)
{
    float h = dht.readHumidity();    
    float result;
     
    if (! (isnan(h)) )
        result = h;
    else
        result = -99.99;
 
    return result;
}
 
void initWiFi(void) 
{
    delay(10);
    Serial.println("------Conexao WI-FI------");
    Serial.print("Conectando-se na rede: ");
    Serial.println(SSID);
    Serial.println("Aguarde");
      
    reconnectWiFi();
}
 
void initMQTT(void) 
{
    MQTT.setServer(BROKER_MQTT, BROKER_PORT);   
    MQTT.setCallback(mqtt_callback);         
}
 
void mqtt_callback(char* topic, byte* payload, unsigned int length) 
{
    String msg;
  
    /* obtem a string do payload recebido */
    for(int i = 0; i < length; i++) 
    {
       char c = (char)payload[i];
       msg += c;
    }
 
    Serial.print("Chegou a seguinte string via MQTT: ");
    Serial.println(msg);
    
    /* toma ação dependendo da string recebida */
    if (msg.equals("1"))
    {
        digitalWrite(PIN_LED, HIGH);
        Serial.print("LED aceso mediante comando MQTT");
    }
  
    if (msg.equals("0"))
    {
        digitalWrite(PIN_LED, LOW);    
        Serial.print("LED apagado mediante comando MQTT"); 
    }
}
 
void reconnectMQTT(void) 
{
    while (!MQTT.connected()) 
    {
        Serial.print("* Tentando se conectar ao Broker MQTT: ");
        Serial.println(BROKER_MQTT);
        if (MQTT.connect(ID_MQTT)) 
        {
            Serial.println("Conectado com sucesso ao broker MQTT!");
            MQTT.subscribe(TOPICO_SUBSCRIBE_LED); 
        } 
        else
        {
            Serial.println("Falha ao reconectar no broker.");
            Serial.println("Havera nova tentatica de conexao em 2s");
            delay(2000);
        }
    }
}
 
void VerificaConexoesWiFIEMQTT(void)
{
    if (!MQTT.connected()) 
        reconnectMQTT(); 
      
     reconnectWiFi(); 
}
 
/* Função: reconecta-se ao WiFi
 * Parâmetros: nenhum
 * Retorno: nenhum
 */
void reconnectWiFi(void) 
{

    if (WiFi.status() == WL_CONNECTED)
        return;
          
    WiFi.begin(SSID, PASSWORD); 
      
    while (WiFi.status() != WL_CONNECTED) 
    {
        delay(100);
        Serial.print(".");
    }
    
    Serial.println();
    Serial.print("Conectado com sucesso na rede ");
    Serial.print(SSID);
    Serial.println("IP obtido: ");
    Serial.println(WiFi.localIP());
}
  
void setup() 
{
    Serial.begin(115200);  
 
    /* Configuração do pino ligado ao LED como output 
       e inicialização do mesmo em LOW */
    pinMode(PIN_LED, OUTPUT);
    digitalWrite(PIN_LED,LOW);
 
    /* Inicializacao do sensor de temperatura */
    dht.begin();  
 
    /* Inicializa a conexao wi-fi */
    initWiFi();
 
    /* Inicializa a conexao ao broker MQTT */
    initMQTT();
}
 
void loop() 
{
    char temperatura_str[10] = {0};
    char umidade_str[10]     = {0};
     
    VerificaConexoesWiFIEMQTT();
 
    sprintf(temperatura_str,"%.2fC", faz_leitura_temperatura());
    sprintf(umidade_str,"%.2f", faz_leitura_umidade());

    MQTT.publish(TOPICO_PUBLISH_TEMPERATURA, temperatura_str);
    MQTT.publish(TOPICO_PUBLISH_UMIDADE, umidade_str);

    MQTT.loop();

    delay(2000);
}
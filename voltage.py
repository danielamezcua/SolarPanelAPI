import Adafruit_GPIO.SPI as SPI
import Adafruit_MCP3008
import subprocess
#Software SPI configuration:
CLK  = 18
MISO = 23
MOSI = 24
CS   = 25
mcp = Adafruit_MCP3008.MCP3008(clk=CLK, cs=CS, miso=MISO, mosi=MOSI)
print(mcp.read_adc(0) * 2.5)

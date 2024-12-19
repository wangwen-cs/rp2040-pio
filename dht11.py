import time
import rp2 
from rp2 import PIO, asm_pio
from machine import Pin


@asm_pio(set_init=PIO.OUT_HIGH, autopush=True, push_thresh=8)
def DHT11():
    # pull down pins for 20ms (32000 cycles)
    set(pindirs, 1)
    set(pins, 0)
    
    set(y, 31)
    label ('waity')
    set(x, 19) 
    label ('waitx')
    nop() [24]
    nop() [23] 
    jmp(x_dec, 'waitx')
    jmp(y_dec, 'waity')
     
    # 1-0-1
    set(pindirs, 0)
    wait(0, pin, 0)
    wait(1, pin, 0)
    wait(0, pin, 0)
    
    #read loop 5 bytes x 8 bits
    set(y, 4)
    label('5bytes')
    set(x, 7)
    # read 1 bit
    label('8bits')
    wait(1, pin, 0)

    # wait for 30us
    nop()   [23]
    nop()   [23]
    
    in_(pins, 1)
    wait(0, pin, 0)
    jmp(x_dec, '8bits')
    irq(0)
    jmp(y_dec, '5bytes')

    label('halt')
    jmp('halt')


dht11_buffer = []

def read_handler(sm):
    global dht11_buffer
    print(f'irq {sm.irq().flags()}')
    val = sm.get()
    dht11_buffer.append(val)
    if len(dht11_buffer) == 5:
        print(dht11_buffer)
        dht11_buffer.clear()


def main():
    dht_data = Pin(2, Pin.IN, Pin.PULL_UP) # GPIO 2 for data pin

    sm = rp2.StateMachine(0, DHT11, freq=1600000, set_base=dht_data, in_base=dht_data)
    sm.irq(handler=read_handler)
    time.sleep(2)

    sm.active(1)


    while True:
        sm.restart()
        time.sleep(2)


if __name__ == '__main__':
    main()

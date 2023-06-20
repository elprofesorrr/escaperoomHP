import network
import socket
import time
import machine
import utime
import _thread
from picozero import RGBLED
import json
from machine import Pin

#inital ledpins
ledred = Pin(7, Pin.OUT)
ledgreen = Pin(6, Pin.OUT)
analog_value = machine.ADC(28)
button = Pin(8, Pin.IN, Pin.PULL_DOWN)
button2 = Pin(17, Pin.IN, Pin.PULL_DOWN)
reading = 0

#inital rgb
rgb2 = RGBLED(red = 13, green = 14, blue = 15)
rgb1 = RGBLED(red = 10, green = 11, blue = 12)
readingbutton = 0

# wifi connection
ssid = ''
password = ''

wlan = network.WLAN(network.STA_IF)
wlan.active(True)
wlan.connect(ssid, password)


max_wait = 10
while max_wait > 0:
    if wlan.status() < 0 or wlan.status() >= 3:
        break
    max_wait -= 1
    print('waiting for connection...')
    time.sleep(1)

if wlan.status() != 3:
    raise RuntimeError('network connection failed')
else:
    print('connected')
    status = wlan.ifconfig()
    print( 'ip = ' + status[0] )

#socket connection
addr = socket.getaddrinfo('0.0.0.0', 8080)[0][-1]

s = socket.socket()
s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
s.bind(addr)
s.listen(1)

print('listening on', addr)

# function for value potmeter to rgb value 
def anologtocolor(value):
    if value >= 0 and value <= 1000:
        return 0
    elif value > 1000 and value <= 2000:
        return 25
    elif value > 2000 and value <= 3000:
        return 50
    elif value > 3000 and value <= 4000:
        return 75
    elif value > 4000 and value <= 5000:
        return 100
    elif value > 5000 and value <= 6000:
        return 125
    elif value > 6000 and value <= 7000:
        return 150
    elif value > 7000 and value <= 8000:
        return 175
    elif value > 8000 and value <= 9000:
        return 200
    elif value > 9000 and value <= 10000:
        return 250
    else:
        return 255

# safe to the file
def save_file(stored_value, extra_values):
    saved_data = {
        'stored_value': stored_value,
        'extra_values': extra_values
    }
    with open('saved_data.json', 'w') as file:
        json.dump(saved_data, file)

# safe the question
def save_questions(vraag, extra, index, stored_value, extra_values, data):
    stored_value[index] = data.get(vraag).replace('+', ' ').replace('%2C', ',').replace('%21', '!').replace('%2F', '/').replace('%22', '"').replace('%2B', '+').replace('%3D', '=')
    extra_values[(index-1)] = data.get(extra, '')
    analog1 = int(extra_values[(index-1)].replace('/\\r\\nAccept-Encoding:/g', ''))

    save_file(stored_value, extra_values)
    
    return stored_value, extra_values

#return element of file
def read_specific_element(arraytype, element_index):
    try:
        with open('saved_data.json', 'r') as file:
            saved_data = json.load(file)
            if arraytype is 1:
                stored_value = saved_data.get('stored_value', [])
                if isinstance(stored_value, list) and 0 <= element_index < len(stored_value):
                    return stored_value[element_index]
                else:
                    return None
            else:
                extra_values = saved_data.get('extra_values', [])
                if isinstance(extra_values, list) and 0 <= element_index < len(extra_values):
                    return extra_values[element_index]
                else:
                    return '0'
    except :
        if arraytype == 1:
            return None
        else:
            return '0'

# fill the stored_value
def fill_storedValue():
    stored_value = ["", "", "", "", "", "", "", ""]
    for index, item in enumerate(stored_value):
        stored_value[index] = read_specific_element(1, index)
    return stored_value

# fill the extra_values
def fill_extraValue():
    extra_values = [0, 0, 0, 0, 0, 0]
    for index, item in enumerate(extra_values):
        extra_values[index] = int(read_specific_element(0, index))
    return extra_values

#return the question
def returnQuestion(stored, cl):
        cl.send('HTTP/1.0 200 OK\r\nContent-type: text/plain\r\n\r\n')
        cl.send(stored)
        cl.close()

#read the html file
def read_html_file(name):
    with open(name, 'r') as file:
        return file.read()

# webserver function
def webserver(analog_value):
    
    #variables
    knopa = 0
    knopb = 0
    knopagoal = 2
    on = 0
    list_analog = [200,150,50]
    list_button = [1,5,7]
    stored_value = fill_storedValue()
    extra_values = fill_extraValue()
    

    while True:
        
        #set rgb leds
        rgb1.color = (list_analog[0], list_analog[1], list_analog[2])
        rgb2.color = (list_button[0], list_button[1], list_button[2])

        try:
            
            # make connections
            cl, addr = s.accept()
            request = cl.recv(1024)
            reading = button.value()
            readingbutton = button2.value()
            request = str(request)
            
            # check the request on a part of the request 
            home = request.find('/home')
            admin = request.find('/admin')
            analog = request.find('/analog')
            end = request.find('/end')
            endbutton = request.find('/bed')
            
            safe1 = request.find('/save')
            safe2 = request.find('/safe2')
            safe3 = request.find('/safe3')
            bsafe1 = request.find('/bsave')
            bsafe2 = request.find('/bsafe2')
            bsafe3 = request.find('/bsafe3')
            reset = request.find('/reset')
            
            button_index = request.find('/button') 
            
            submit = request.find('/submit')
            submit2 = request.find('/submit2')
            submit3 = request.find('/submit3')
            submit4 = request.find('/submit4')
            submit5 = request.find('/submit5')
            submit6 = request.find('/submit6')
            submit7 = request.find('/submit7')
            submit8 = request.find('/submit8')
            
            getresult = request.find('/get-result1')
            get_result2 = request.find('/get-result2')
            get_result3 = request.find('/get-result3')
            get_result4 = request.find('/get-result4')
            get_result5 = request.find('/get-result5')
            get_result6 = request.find('/get-result6')
            get_story = request.find('/get-story')
            get_end = request.find('/get-end')
            get_answers = request.find('/get-answers')
            
            step2 = request.find('/step2')
            step3 = request.find('/step3')
            step4 = request.find('/step4')
            step5 = request.find('/step5')
            step6 = request.find('/step6')
            
            # set the correct answers
            analog1 = int(read_specific_element(0, 0))
            analog2 = int(read_specific_element(0, 1))
            analog3 = int(read_specific_element(0, 2))
            buttonval1 = int(read_specific_element(0, 3))
            buttonval2 = int(read_specific_element(0, 4))
            buttonval3 = int(read_specific_element(0, 5))
            
            # if the request includes submit
            if submit != -1:
                query_start = request.find('?')
                query_end = request.find(' ', query_start)
                query = request[query_start + 1:query_end]
                data = {}
                
                for param in query.split('&'):
                    key, value = param.split('=')
                    data[key] = value
                
                # chech which question/story/end
                if submit2 != -1:
                    stored_value, extra_values = save_questions('Vraag+1', 'Vraag+1_extra', 1, stored_value, extra_values, data)
                elif submit3 != -1:
                    stored_value, extra_values = save_questions('Vraag+2', 'Vraag+2_extra', 2, stored_value, extra_values, data)
                elif submit4 != -1:
                    stored_value, extra_values = save_questions('Vraag+3', 'Vraag+3_extra', 3, stored_value, extra_values, data)                 
                elif submit5 != -1:
                    stored_value, extra_values = save_questions('Vraag+4', 'Vraag+4_extra', 4, stored_value, extra_values, data)
                elif submit6 != -1:
                    stored_value, extra_values = save_questions('Vraag+5', 'Vraag+5_extra', 5, stored_value, extra_values, data)
                elif submit7 != -1:
                    stored_value, extra_values = save_questions('Vraag+6', 'Vraag+6_extra', 6, stored_value, extra_values, data)
                elif submit8 != -1:
                    stored_value[7] = data.get('end', '').replace('+', ' ').replace('%2C', ',').replace('%21', '!')
                    save_file(stored_value, extra_values)
                else:
                    stored_value[0] = data.get('Verhaal', '').replace('+', ' ').replace('%2C', ',').replace('%21', '!')
                    save_file(stored_value, extra_values)

            # if the request includes get_story or the other questions
            if get_story != -1:
                returnQuestion(read_specific_element(1, 0), cl)
                continue
            if getresult != -1:
                returnQuestion(read_specific_element(1, 1), cl)
                continue
            if get_result2 != -1:
                returnQuestion(read_specific_element(1, 2), cl)
                continue
            if get_result3 != -1:
                returnQuestion(read_specific_element(1, 3), cl)
                continue
            if get_result4 != -1:
                returnQuestion(read_specific_element(1, 4), cl)
                continue    
            if get_result5 != -1:
                returnQuestion(read_specific_element(1, 5), cl)
                continue
            if get_result6 != -1:
                returnQuestion(read_specific_element(1, 6), cl)
                continue
            if get_end != -1:
                returnQuestion(read_specific_element(1, 7), cl)
                continue
            
            # if the request includes get_answers
            if get_answers != -1:
                anwers = str(read_specific_element(0, 0)) + str(read_specific_element(0, 1)) + str(read_specific_element(0, 2)) + str(read_specific_element(0, 3)) + str(read_specific_element(0, 4)) + str(read_specific_element(0, 5))
                returnQuestion(anwers, cl)
                continue
            
            # return the analog value
            if analog is not -1:
                analog_reading = analog_value.read_u16()
                collor = anologtocolor(analog_reading)
                response = str(collor) + '     saved value:  ' + str(list_analog)
                cl.send('HTTP/1.0 200 OK\r\nContent-type: text/plain\r\n\r\n')
                cl.send(response)
                cl.close()
                continue
            
            # return the button value
            if button_index is not -1: 
                analog_reading = analog_value.read_u16()
                response = ' button 1 pressed ' + str(knopa) + ' values:  ' + str(list_button)
                if reading != 0:
                    knopa += 1
                # check the second button 
                if readingbutton != 0:
                    knopb += 1
                    # check the ansers with the correct answers
                    if list_analog[0] == analog1 and list_analog[1] == analog2 and list_analog[2] == analog3 and list_button[0] == buttonval1 and list_button[1] == buttonval2 and list_button[2] == buttonval3:
                        ledgreen.value(1)
                        ledred.value(0)
                        on = 1
                    else:
                        ledgreen.value(0)
                        ledred.value(1)
                        knopa = 0
                cl.send('HTTP/1.0 200 OK\r\nContent-type: text/plain\r\n\r\n')
                cl.send(response)
                cl.close()
                continue
            
            # to end page
            if endbutton is not -1: 
                if on == 1 and list_analog[0] == analog1 and list_analog[1] == analog2 and list_analog[2] == analog3 and list_button[0] == buttonval1 and list_button[1] == buttonval2 and list_button[2] == buttonval3:
                    cl.send('HTTP/1.1 303 See Other\r\nLocation: /end\r\n\r\n')
                else:
                    cl.send('HTTP/1.1 303 See Other\r\nLocation: /step6\r\n\r\n')
                continue
            
            #safe functions of the analog or button and reset
            if safe1 is not -1:
                analog_reading = analog_value.read_u16()
                collor = anologtocolor(analog_reading)
                list_analog[0] = collor
            if safe2 is not -1:
                analog_reading = analog_value.read_u16()
                collor = anologtocolor(analog_reading)
                list_analog[1] = collor            
            if safe3 is not -1:
                analog_reading = analog_value.read_u16()
                collor = anologtocolor(analog_reading)
                list_analog[2] = collor   
            if bsafe1 is not -1:
                list_button[0] = knopa
            if bsafe2 is not -1:
                list_button[1] = knopa   
            if bsafe3 is not -1:
                list_button[2] = knopa
            if reset is not -1:
                knopa = 0
            
            #resend to other page
            if submit != -1:
                cl.send('HTTP/1.1 303 See Other\r\nLocation: /admin\r\n\r\n')
            #sent to page
            else: 
                if admin  != -1:
                    response =  read_html_file("admin.html")
                elif step2 != -1:
                    response = read_html_file("vraag2.html")
                elif step3 != -1:
                    response = read_html_file("vraag3.html")
                elif step4 != -1:
                    response = read_html_file("vraag4.html")
                elif step5 != -1:
                    response = read_html_file("vraag5.html")
                elif step6 != -1:
                    response = read_html_file("vraag6.html")
                elif end != -1:
                    response = read_html_file("end.html")
                else:
                    response = read_html_file("home.html")

                cl.send('HTTP/1.0 200 OK\r\nContent-type: text/html\r\n\r\n')
                cl.send(response)
                cl.close()

        except OSError as e:
            cl.close()
            print('connection closed')

#main loop
while True:
    webserver(analog_value)
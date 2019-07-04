from flask import Flask,render_template,jsonify,request
import time
import logging
import os
import smpplib.gsm
import smpplib.client
import smpplib.consts


app = Flask(__name__)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))


# handler = logging.FileHandler(BASE_DIR + '/log/flask.log')
# handler.setLevel(logging.DEBUG)
# logging_format = logging.Formatter(
#     '%(asctime)s %(levelname)s %(filename)s line: %(lineno)s - %(message)s')
# handler.setFormatter(logging_format)
#
# app.logger.addHandler(handler)

logging.basicConfig(level='DEBUG')


def sendMessage(myServer, myPort, system_id, password, phoneNumber, text ):
    # if you want to know what's happening
    # logging.basicConfig(level='DEBUG')

    # Two parts, UCS2, SMS with UDH
    parts, encoding_flag, msg_type_flag = smpplib.gsm.make_parts( text )

    try:
        client = smpplib.client.Client(myServer, myPort)

        # Print when obtain message_id
        client.set_message_sent_handler(
            lambda pdu: logging.info('sent {} {}\n'.format(pdu.sequence, pdu.message_id)))
        client.set_message_received_handler(
            lambda pdu: logging.info('delivered {}\n'.format(pdu.receipted_message_id)))

        client.connect()

        client.bind_transceiver(system_id=system_id, password=password)

        for part in parts:
            pdu = client.send_message(
                source_addr_ton=smpplib.consts.SMPP_TON_INTL,
                #source_addr_npi=smpplib.consts.SMPP_NPI_ISDN,
                # Make sure it is a byte string, not unicode:
                source_addr='',

                dest_addr_ton=smpplib.consts.SMPP_TON_INTL,
                #dest_addr_npi=smpplib.consts.SMPP_NPI_ISDN,
                # Make sure thease two params are byte strings, not unicode:
                destination_addr=phoneNumber,
                short_message=part,

                data_coding=encoding_flag,
                esm_class=msg_type_flag,
                registered_delivery=True,
            )
        time.sleep(1)
        client.disconnect()
        # client.listen()
        # t = threading.Thread(target=listen, args=(client,))
        # t.start()

    except Exception as e:
        logging.info(str(e))


# ================ Route =======================


@app.route("/")
def index():

    return render_template("index.html")


@app.route("/send", methods=['post'])
def send():
    myServer = request.form['host']
    myPort = int(request.form['port'])
    system_id = request.form['username']
    password = request.form['password']
    phoneNumber = request.form['phone']
    text = request.form['text']

    sendMessage(myServer, myPort, system_id, password, phoneNumber, text)

    return jsonify({
        'code':  0,
        'msg' : 'Submitted'
    })

if __name__ == "__main__":
    app.run(host='127.0.0.1', debug=True, port=8070)



    



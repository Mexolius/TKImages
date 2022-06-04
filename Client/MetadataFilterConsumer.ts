// create a rabbitmq queue consumer

import client, {Connection, Channel, ConsumeMessage, } from 'amqplib';
import handleRequest from './MetadataFilter/metadata'
import MetadataOptions from './MetadataFilter/metadataOptions.interface'
import fs from 'fs';
import ini from 'ini';
import MetadataRequest from './MetadataFilter/metadataRequest';

const read_ini_file = (file_name: string): any => {
    return ini.parse(fs.readFileSync(file_name, 'utf-8'))
}

(async () => {
    let {
      RABBITMQ: {queue_prefix, address, port, username, password},
      QUEUES: {metadata},
    } = read_ini_file("Client/config.ini")

    let r_queue = `${queue_prefix}.${metadata}`;
    let w_queue = `${queue_prefix}.results`;
    
    const consumer = (channel: Channel) => async (msg: ConsumeMessage | null): Promise<void> => {
        console.log("Message consumed.")
        if (msg !== null) {
            let msg_decoded = JSON.parse(msg.content.toString());

            console.log(msg_decoded)

            let options: MetadataOptions = {
              exposureTime: msg_decoded.params["exposure time"],
              fNumber: msg_decoded.params["f number"],
              focalLength: msg_decoded.params["focal length"],
              flash: msg_decoded.params["flash"],
              pixelXDimMin: msg_decoded.params["min pixel width"],
              pixelXDimMax: msg_decoded.params["max pixel width"],
              pixelYDimMin: msg_decoded.params["min pixel height"],
              pixelYDimMax: msg_decoded.params["max pixel height"],
              name: 'metadata'
            } 

            let result_paths = await handleRequest(new MetadataRequest({paths: msg_decoded.paths, options: options}));

            console.log("Responding with:", result_paths)

            channel.sendToQueue(w_queue, Buffer.from(JSON.stringify({paths: result_paths})));
        }
    }
    const connection = await client.connect(`amqp://${username}:${password}@${address}:${port}`);
    const channel = await connection.createChannel();
    await channel.assertQueue(r_queue, {durable: false}).then(() => console.log('Read queue Asserted.'));
    await channel.assertQueue(w_queue, {durable: false}).then(() => console.log('Write queue Asserted.'));
    await channel.consume(r_queue, consumer(channel)).then(() => console.log('Consumer Bound.'));
})().catch((err) => console.error("DUPA", err));


const minio = require('minio'),
  path = require('path'),
  uuid = require('uuid'),
  util = require('util'),
  stream = require('stream'),
  fs = require('fs');

class minio_storage {

  constructor() {
    let address = process.env.MINIO_STORAGE_CONNECTION_URL;
    let access_key = process.env.MINIO_STORAGE_ACCESS_KEY;
    let secret_key = process.env.MINIO_STORAGE_SECRET_KEY;

    this.client = new minio.Client(
      {
        endPoint: address.split(':')[0],
        port: parseInt(address.split(':')[1], 10),
        accessKey: access_key,
        secretKey: secret_key,
        useSSL: false
      }
    );
  }

  unique_name(file) {
    let name = path.parse(file);
    let uuid_name = uuid.v4().split('-')[0];
    return path.join(name.dir, util.format('%s.%s%s', name.name, uuid_name, name.ext));
  }

  upload(bucket, file, filepath) {
    let uniqueName = this.unique_name(file);
    return [uniqueName, this.client.fPutObject(bucket, uniqueName, filepath)];
  };

  download(bucket, file, filepath) {
    return this.client.fGetObject(bucket, file, filepath);
  };

  downloadDirectory(bucket, prefix, downloadPath) {
    const self = this;
    const objectsStream = this.client.listObjects(bucket, prefix, true);
  
    return new Promise((resolve, reject) => {
      objectsStream.on('data', function(obj) {
        const fileName = obj.name;
        const filePath = path.join(downloadPath, fileName);
  
        console.log(`Preparing to download ${fileName} to ${filePath}`);
  
        fs.mkdir(path.dirname(filePath), { recursive: true }, (err) => {
          if (err) {
            console.error('Error creating directory:', err);
            reject(err);
            return;
          }
  
          self.download(bucket, fileName, filePath)
            .then(() => {
              console.log(`Successfully downloaded ${fileName} to ${filePath}`);
            })
            .catch((err) => {
              console.error(`Error downloading ${fileName}:`, err);
              reject(err);
            });
        });
      });
  
      objectsStream.on('error', function(err) {
        console.error('Error while listing objects:', err);
        reject(err);
      });
  
      objectsStream.on('end', function() {
        console.log('Completed downloading directory');
        resolve();
      });
    });
  }  

  uploadStream(bucket, file) {
    var write_stream = new stream.PassThrough();
    let uniqueName = this.unique_name(file);
    let promise = this.client.putObject(bucket, uniqueName, write_stream, write_stream.size);
    return [write_stream, promise, uniqueName];
  };

  downloadStream(bucket, file) {
    var read_stream = new stream.PassThrough();
    return this.client.getObject(bucket, file);
  };

  static get_instance() {
    if(!this.instance) {
      this.instance = new storage();
    }
    return this.instance;
  }


};
exports.storage = minio_storage;

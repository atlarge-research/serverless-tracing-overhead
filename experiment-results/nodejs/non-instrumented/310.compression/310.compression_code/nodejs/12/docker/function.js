const fs = require('fs');
const path = require('path');
const uuid = require('uuid');
const util = require('util');
const archiver = require('archiver');
const storage = require('./storage');
const storage_handler = new storage.storage();

const mkdir = util.promisify(fs.mkdir);
const stat = util.promisify(fs.stat);
const readdir = util.promisify(fs.readdir);

async function parseDirectory(directory) {
  let size = 0;
  const files = await readdir(directory);
  for (const file of files) {
    const filePath = path.join(directory, file);
    const fileStat = await stat(filePath);
    if (fileStat.isFile()) {
      size += fileStat.size;
    }
  }
  return size;
}

async function compressDirectory(sourceDir, archivePath) {
  return new Promise((resolve, reject) => {
    const output = fs.createWriteStream(archivePath);
    const archive = archiver('zip', { zlib: { level: 9 } });

    output.on('close', () => {
      resolve(archive.pointer());
    });

    archive.on('error', (err) => {
      reject(err);
    });

    archive.pipe(output);
    archive.directory(sourceDir, false);
    archive.finalize();
  });
}

exports.handler = async function(event) {
  try {
    const bucket = event.bucket.bucket;
    const input_prefix = event.bucket.input;
    const output_prefix = event.bucket.output;
    const key = event.object.key;
    const download_path = `/tmp/${key}-${uuid.v4()}`;
    await mkdir(download_path, { recursive: true });

    const s3DownloadBegin = Date.now();
    await storage_handler.downloadDirectory(bucket, path.join(input_prefix, key), download_path);
    const s3DownloadStop = Date.now();
    const downloadTime = (s3DownloadStop - s3DownloadBegin) / 1000;

    const size = await parseDirectory(download_path);

    const compressBegin = Date.now();
    const archivePath = path.join('/tmp', `${key}.zip`);
    const archiveSize = await compressDirectory(download_path, archivePath);
    const compressEnd = Date.now();
    const processTime = (compressEnd - compressBegin) / 1000;

    const s3UploadBegin = Date.now();
    const keyName = await storage_handler.upload(bucket, path.join(output_prefix, `${key}.zip`), archivePath);
    const s3UploadStop = Date.now();
    const uploadTime = (s3UploadStop - s3UploadBegin) / 1000;

    return {
      result: {
        bucket: bucket,
        key: keyName
      },
      measurement: {
        download_time: downloadTime,
        download_size: size,
        upload_time: uploadTime,
        upload_size: archiveSize,
        compute_time: processTime
      }
    };
  } catch (err) {
    console.error('Handler error:', err);
    throw err;
  }
};

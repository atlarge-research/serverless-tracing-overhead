const fs = require('fs');

export function readJsonConfig(jsonFilePath) {
  try {
    const fileContents = fs.readFileSync(jsonFilePath, 'utf-8');

      return JSON.parse(fileContents);

  } catch (error) {
    console.error('Error reading or parsing the JSON file:', error);
    return null;
  }
}

export function recordTime(filePath, testConfig, time, scenarioStatus) {
    time = Math.floor(Date.now() / 1000);

    let logText = scenarioStatus + time.toString() + "-" + testConfig;

    fs.writeFile(filePath, logText, (error) => {
        if (error) {
            console.error('Error writing to the file:', error);
        } else {
            console.log('The current UNIX time has been written to', filePath);
        }
    });
}

fs.writeFile(filePath, currentUnixTime.toString(), (error) => {
  if (error) {
    console.error('Error writing to the file:', error);
  } else {
    console.log('The current UNIX time has been written to', filePath);
  }
});
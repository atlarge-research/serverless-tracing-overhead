import http from 'k6/http';
import {check} from 'k6';

const configFile = "test-config.json"

const languages = ['python', 'java', 'go'];
// const languages = ['python'];
const appTypes = ['standard', 'otel', 'elastic'];
// const appTypes = ['standard'];
const endpoints = ['json', 'db', 'updates', 'queries'];
// const endpoints = ['json'];

const rpsRates = JSON.parse(open(configFile))

export let options = {
    scenarios: {},
};

const testDuration = 60; // In seconds
let startTime = 0; // In seconds
const gracefulStop = 0 // In seconds

languages.forEach(lang => {
    appTypes.forEach(type => {
        const appName = `${lang}-${type}`;
        endpoints.forEach(endpoint => {
            const scenarioName = `${appName}-${endpoint}`;
            options.scenarios[scenarioName] = {
                executor: 'constant-arrival-rate',
                rate: rpsRates["rps"][endpoint][lang],
                duration: `${testDuration}s`,
                startTime: `${startTime}s`,
                timeUnit: '1s',
                preAllocatedVUs: 500,
                maxVUs: 2000,
                exec: 'testEndpoint',
                env: { APP_NAME: appName, ENDPOINT: endpoint },
                tags: { testName: `${appName}-${endpoint}` },
                gracefulStop: `${gracefulStop}s`
            };
            startTime += testDuration + gracefulStop;
        });
    });
});

// Function to test a specific endpoint
export function testEndpoint() {
    const url = `http://${__ENV.APP_NAME}:8080/${__ENV.ENDPOINT}`;
    let res = http.get(url);
    check(res, {
        'is status 200': (r) => r.status === 200,
    });
}
//
// export function setup() {
//     const startTime = Date.now();
//     return { startTime };
// }
//
// export function teardown(data) {
//     const startTime = data.startTime
//     const endTime = Date.now()
//     console.log("data:", data)
//
//     const outputFile = Date.now() + "_" + "test-output";
//
//     recordTime(outputFile, data, startTime, "Start")
//     recordTime(outputFile, data, endTime, "End")
//
//     console.log(`Test scenario end time (UNIX): ${endTime}`);
// }

// const fs = require('fs');
//
// export function readJsonConfig(jsonFilePath) {
//   try {
//     const fileContents = fs.readFile(jsonFilePath, 'utf-8');
//
//     return JSON.parse(fileContents);
//
//   } catch (error) {
//     console.error('Error reading or parsing the JSON file:', error);
//     return null;
//   }
// }
//
// export function recordTime(filePath, data, time, scenarioStatus) {
//     time = Math.floor(Date.now() / 1000);
//
//     let logText = scenarioStatus + "_" + time.toString() + "_" + data.toString();
//
//     // logText.write(outputFile, logText, { append: true });
//     // text.write(filePath, logText, { append: true });
//     file.writeString(filePath, logText);
// }
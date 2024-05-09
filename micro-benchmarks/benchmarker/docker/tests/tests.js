import http from 'k6/http';
import {check} from 'k6';

const configFile = "test-config.json"

const languages = ['python', 'java', 'go'];
const appTypes = ['standard', 'otel', 'elastic'];
const endpoints = ['json', 'db', 'updates', 'queries'];

const queriesAmount = 10;

const rpsRates = JSON.parse(open(configFile))

export let options = {
    scenarios: {},
};

const testDuration = 60; // In seconds
let startTime = 0;       // In seconds
const gracefulStop = 15  // In seconds

endpoints.forEach(endpoint => {
    languages.forEach(lang => {
        appTypes.forEach(type => {
            const appName = `${lang}-${type}`;
            const scenarioName = `${appName}-${endpoint}`;
            const rps = rpsRates[appName][endpoint];
            options.scenarios[scenarioName] = {
                executor: 'constant-arrival-rate',
                rate: rps,
                duration: `${testDuration}s`,
                startTime: `${startTime}s`,
                timeUnit: '1s',
                preAllocatedVUs: 500,
                maxVUs: 2000,
                exec: 'testEndpoint',
                env: { APP_NAME: appName, ENDPOINT: endpoint },
                tags: {
                    testName: `${appName}-${endpoint}`,
                    appName: `${appName}`,
                    endpoint: `${endpoint}`,
                    rps: `${rps}`,
                    language: `${lang}`
                },
                gracefulStop: `${gracefulStop}s`
            };
            startTime += testDuration + gracefulStop;
        });
    });
});

export function testEndpoint() {
    let url;
    if (__ENV.ENDPOINT === "queries") {
        url = `http://${__ENV.APP_NAME}:8080/${__ENV.ENDPOINT}?queries=${queriesAmount}`
    } else {
        url = `http://${__ENV.APP_NAME}:8080/${__ENV.ENDPOINT}`;
    }
    let res = http.get(url);
    check(res, {
        'is status 200': (r) => r.status === 200,
    });
}

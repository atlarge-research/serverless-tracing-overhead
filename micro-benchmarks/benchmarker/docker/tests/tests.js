import http from 'k6/http';
import { check } from 'k6';

// Define the base details for the applications and endpoints
const languages = ['python-flask', 'java-spring', 'go'];
const appTypes = ['standard', 'otel', 'elastic'];
const endpoints = ['json', 'db', 'updates', 'queries'];

// Define RPS for each language
const rpsRates = {
    'python-flask': 1000,
    'java-spring': 2000,
    'go': 2000
};

export let options = {
    scenarios: {},
};

const testDuration = 60; // In seconds
let startTime = 0; // In seconds
const gracefulStop = 30 // In seconds

languages.forEach(lang => {
    appTypes.forEach(type => {
        const appName = `${lang}-${type}`;
        endpoints.forEach(endpoint => {
            const scenarioName = `${appName}-${endpoint}`;
            options.scenarios[scenarioName] = {
                executor: 'constant-arrival-rate',
                rate: rpsRates[lang],
                duration: `${testDuration}s`,
                startTime: `${startTime}s`,
                timeUnit: '1s',
                preAllocatedVUs: 500,
                maxVUs: 2000,
                exec: 'testEndpoint',
                env: { APP_NAME: appName, ENDPOINT: endpoint },
                tags: { testName: `${appName}_${endpoint}` },
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


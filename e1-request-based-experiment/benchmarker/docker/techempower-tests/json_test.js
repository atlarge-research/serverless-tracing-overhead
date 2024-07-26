import http from 'k6/http';
import { check, sleep } from 'k6';
import { PORTS, HOST, ENDPOINTS, scenarioHelperConcurrency } from './common.js'

let startTime = { value: 0 };

function generateScenarios(appName, appPort) {
    let duration = 1;
    const concurrencyLevels = [16, 64, 256, 512];

    return scenarioHelperConcurrency(concurrencyLevels, duration, appPort, appName, startTime);
}

let options = {
    scenarios: {},
};

Object.assign(
    options.scenarios,
    generateScenarios('python', PORTS.python),
    generateScenarios('pythonOtel', PORTS.pythonOtel),
    generateScenarios('go', PORTS.go),
    generateScenarios('goOtel', PORTS.goOtel),
);
export { options };

const endpoint = "json"

export function test() {
    let res = http.get(`${HOST}:${__ENV.PORT}/${ENDPOINTS.json}`);
    check(res, {
        'is status 200': (r) => r.status === 200,
        'is content type application/json': (r) => r.headers['Content-Type'] === 'application/json',
        'is response correct': (r) => r.body === '{"message":"Hello, World!"}' || JSON.parse(r.body).message === 'Hello, World!',
    });
}


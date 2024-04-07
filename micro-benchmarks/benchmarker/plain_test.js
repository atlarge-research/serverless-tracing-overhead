import http from 'k6/http';
import { check, sleep } from 'k6';
import {PORTS, HOST, scenarioHelperConcurrency} from './common.js'


let startTime = { value: 0 };

function generateScenarios(appName, appPort) {
    let duration = 1;
    const concurrencyLevels = [256, 1024, 4096];

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

const endpoint = "plain"



export function test() {
    let res = http.get(`${HOST}:${__ENV.PORT}/${endpoint}`);
    check(res, {
        'is status 200': (r) => r.status === 200,
    });
}


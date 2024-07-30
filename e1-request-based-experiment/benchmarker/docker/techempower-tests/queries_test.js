import http from 'k6/http';
import { check, sleep } from 'k6';
import { PORTS, HOST, ENDPOINTS, scenarioHelperQueryCount } from './common.js'

let startTime = { value: 0 };

function generateScenarios(appName, appPort) {
    let duration = 1;
    const concurrency = 512;
    const queryCounts = [1,5,10,15,20];

    return scenarioHelperQueryCount(queryCounts, duration, appPort, appName, startTime, concurrency)
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

export function test() {
    let res = http.get(`${HOST}:${__ENV.PORT}/${ENDPOINTS.queries}?queries=${__ENV.QUERY_COUNT}`);
    check(res, {
        'is status 200': (r) => r.status === 200,
    });
}


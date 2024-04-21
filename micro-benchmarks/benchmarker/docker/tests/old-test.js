import http from 'k6/http';
import { check, sleep } from 'k6';

export const PORTS = {
    python: 5000,
    pythonOtel: 5001,
    pythonElastic: 5002,
    go: 5100,
    goOtel: 5101,
    goElastic: 5102,
};

let RPSConfig = new Map()
RPSConfig["python"] = 600
RPSConfig["go"] = 2000

let configs = [
    {
        name: "python",
        language: "python",
        port: PORTS.python
    },
    {
        name: "python-otel",
        language: "python",
        port: PORTS.pythonOtel
    },
    {
        name: "python-elastic",
        language: "python",
        port: PORTS.pythonElastic
    },
    {
        name: "go",
        language: "go",
        port: PORTS.go
    },
    {
        name: "go-otel",
        language: "go",
        port: PORTS.goOtel
    },
    {
        name: "go-elastic",
        language: "go",
        port: PORTS.goElastic
    },
]

function generateScenarios(configs, endpoint) {
    let scenarios = {}
    let testDuration = 2; // In minutes
    let rps = 0;
    let startTime = 0;

    configs.forEach((config) => {
        rps = RPSConfig[config.language]

        let scenarioName = `${config.name}`;
        scenarios[scenarioName] = {
            executor: 'constant-arrival-rate',
            rate: rps,
            timeUnit: '1s',
            duration: `${testDuration}m`,
            preAllocatedVUs: rps,
            maxVUs: rps * 2,
            exec: 'test',
            env: { PORT: `${config.port}`, ENDPOINT: `${endpoint}` },
            startTime: `${startTime}m`,
            tags: { testName: `${config.name}_${endpoint}_${rps}` },
        };

        startTime += testDuration;
    });
    return scenarios
}

let options = {
    scenarios: {},
};

Object.assign(
    options.scenarios,
    // generateScenarios(configs, "json"),
    generateScenarios(configs, "db"),
    // generateScenarios(configs, "queries"),
    // generateScenarios(configs, "updates"),
);
export { options };

const HOST = "http://localhost"

export function test() {
    let res = http.get(`${HOST}:${__ENV.PORT}/${__ENV.ENDPOINT}`);
    check(res, {
        'is status 200': (r) => r.status === 200,
    });
}
